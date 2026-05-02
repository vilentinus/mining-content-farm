import asyncio
import logging

from telegram.ext import Application

from mining_news_bot.database import Database
from mining_news_bot.generator import DraftGenerator
from mining_news_bot.scheduler import check_sources_once, configure_scheduler
from mining_news_bot.settings import Settings
from mining_news_bot.telegram_bot import build_callback_handler


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


async def run() -> None:
    settings = Settings()
    database = Database(settings.database_path)
    database.initialize()

    application = Application.builder().token(settings.telegram_bot_token).build()
    application.add_handler(build_callback_handler(settings, database))

    generator = DraftGenerator(api_key=settings.openai_api_key)

    async def scheduled_job() -> None:
        await check_sources_once(
            application=application,
            database=database,
            generator=generator,
            sources_path=settings.sources_path,
            moderator_chat_id=settings.telegram_moderator_chat_id,
        )

    scheduler = configure_scheduler(
        check_times=settings.parsed_check_times,
        timezone=settings.timezone,
        job=scheduled_job,
    )
    scheduler.start()

    await application.initialize()
    await application.start()
    if application.updater is None:
        raise RuntimeError("Telegram updater is not available")
    await application.updater.start_polling()
    try:
        await asyncio.Event().wait()
    finally:
        scheduler.shutdown()
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
