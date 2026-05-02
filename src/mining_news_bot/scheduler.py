import logging
from collections.abc import Awaitable, Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.ext import Application

from mining_news_bot.collector import collect_from_source
from mining_news_bot.database import Database
from mining_news_bot.filtering import is_mining_related
from mining_news_bot.generator import DraftGenerator
from mining_news_bot.sources import load_sources
from mining_news_bot.telegram_bot import send_draft_to_moderator

logger = logging.getLogger(__name__)


def parse_check_time(value: str) -> tuple[int, int]:
    hour, minute = value.split(":", 1)
    return int(hour), int(minute)


async def check_sources_once(
    *,
    application: Application,
    database: Database,
    generator: DraftGenerator,
    sources_path: str,
    moderator_chat_id: int,
    max_drafts_per_run: int = 30,
    max_drafts_per_source: int = 3,
) -> None:
    created_count = 0
    for source in load_sources(sources_path):
        if created_count >= max_drafts_per_run:
            return
        source_created_count = 0
        try:
            items = await collect_from_source(source)
        except Exception:
            logger.exception("Failed to collect source %s", source.name)
            continue

        for item in items:
            if created_count >= max_drafts_per_run:
                return
            if source_created_count >= max_drafts_per_source:
                break
            if database.has_processed_url(item.url):
                continue
            if not is_mining_related(item):
                continue
            try:
                draft_text = await generator.generate(item)
                draft_id = database.create_draft(item, draft_text)
                created_count += 1
                source_created_count += 1
                await send_draft_to_moderator(
                    application,
                    moderator_chat_id,
                    draft_id,
                    draft_text,
                )
            except Exception:
                logger.exception("Failed to process item %s", item.url)


def configure_scheduler(
    *,
    check_times: list[str],
    timezone: str,
    job: Callable[[], Awaitable[None]],
) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=timezone)
    for check_time in check_times:
        hour, minute = parse_check_time(check_time)
        scheduler.add_job(job, "cron", hour=hour, minute=minute)
    return scheduler
