# Mining News Telegram Bot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a first working Python MVP that collects mining industry news, creates short Russian drafts, sends them to a moderator, and publishes only approved drafts to a Telegram channel.

**Architecture:** The app is split into small modules: configuration, database, source collection, filtering, draft generation, Telegram moderation, and scheduler. The first version stores state in SQLite and reads secrets from environment variables or `.env`.

**Tech Stack:** Python 3.11+, `python-telegram-bot`, `feedparser`, `httpx`, `beautifulsoup4`, `pydantic-settings`, `apscheduler`, `openai`, `pytest`, SQLite.

---

## File Structure

- `pyproject.toml`: project metadata, dependencies, pytest configuration.
- `.gitignore`: excludes local secrets, database files, caches, and virtual environments.
- `.env.example`: shows required environment variables without real secrets.
- `config/sources.example.yml`: example source list.
- `src/mining_news_bot/__init__.py`: package marker.
- `src/mining_news_bot/settings.py`: loads environment variables.
- `src/mining_news_bot/models.py`: shared data objects.
- `src/mining_news_bot/database.py`: SQLite schema and draft persistence.
- `src/mining_news_bot/sources.py`: reads source config.
- `src/mining_news_bot/collector.py`: collects RSS news items.
- `src/mining_news_bot/filtering.py`: mining-topic keyword filter.
- `src/mining_news_bot/generator.py`: creates Telegram draft text.
- `src/mining_news_bot/telegram_bot.py`: moderation buttons and channel publishing.
- `src/mining_news_bot/scheduler.py`: scheduled source checks.
- `src/mining_news_bot/main.py`: application entry point.
- `tests/`: focused unit tests for the modules above.

## Task 1: Project Scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `src/mining_news_bot/__init__.py`

- [ ] **Step 1: Create project metadata**

Create `pyproject.toml`:

```toml
[project]
name = "mining-news-bot"
version = "0.1.0"
description = "Telegram moderation bot for mining industry news"
requires-python = ">=3.11"
dependencies = [
  "apscheduler>=3.10.4",
  "beautifulsoup4>=4.12.3",
  "feedparser>=6.0.11",
  "httpx>=0.27.0",
  "openai>=1.30.0",
  "pydantic-settings>=2.2.1",
  "python-dotenv>=1.0.1",
  "python-telegram-bot>=21.0",
  "pyyaml>=6.0.1",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.2.0",
  "pytest-asyncio>=0.23.6",
  "respx>=0.21.1",
]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 2: Create local ignores**

Create `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
.pytest_cache/
*.pyc
*.db
*.sqlite
*.sqlite3
logs/
```

- [ ] **Step 3: Create environment example**

Create `.env.example`:

```dotenv
TELEGRAM_BOT_TOKEN=123456:replace_me
TELEGRAM_CHANNEL_ID=@your_channel
TELEGRAM_MODERATOR_CHAT_ID=123456789
OPENAI_API_KEY=replace_me
DATABASE_PATH=bot.sqlite3
SOURCES_PATH=config/sources.yml
CHECK_TIMES=09:00,14:00,19:00
TIMEZONE=Europe/Moscow
```

- [ ] **Step 4: Create package marker**

Create `src/mining_news_bot/__init__.py`:

```python
"""Mining news Telegram bot package."""
```

- [ ] **Step 5: Verify scaffold**

Run: `python -m pip install -e ".[dev]"`

Expected: dependencies install successfully and `python -m pytest` reports that no tests were collected or all existing tests pass.

- [ ] **Step 6: Commit scaffold**

Run:

```bash
git add pyproject.toml .gitignore .env.example src/mining_news_bot/__init__.py
git commit -m "chore: scaffold mining news bot"
```

## Task 2: Settings

**Files:**
- Create: `tests/test_settings.py`
- Create: `src/mining_news_bot/settings.py`

- [ ] **Step 1: Write failing settings test**

Create `tests/test_settings.py`:

```python
from mining_news_bot.settings import Settings


def test_settings_parse_check_times():
    settings = Settings(
        telegram_bot_token="token",
        telegram_channel_id="@channel",
        telegram_moderator_chat_id=123,
        openai_api_key="key",
        check_times="09:00,14:00,19:00",
    )

    assert settings.parsed_check_times == ["09:00", "14:00", "19:00"]
```

- [ ] **Step 2: Run failing test**

Run: `python -m pytest tests/test_settings.py -v`

Expected: FAIL because `mining_news_bot.settings` does not exist yet.

- [ ] **Step 3: Implement settings**

Create `src/mining_news_bot/settings.py`:

```python
from functools import cached_property

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    telegram_bot_token: str
    telegram_channel_id: str
    telegram_moderator_chat_id: int
    openai_api_key: str
    database_path: str = "bot.sqlite3"
    sources_path: str = "config/sources.yml"
    check_times: str = "09:00,14:00,19:00"
    timezone: str = "Europe/Moscow"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @cached_property
    def parsed_check_times(self) -> list[str]:
        return [item.strip() for item in self.check_times.split(",") if item.strip()]
```

- [ ] **Step 4: Verify settings**

Run: `python -m pytest tests/test_settings.py -v`

Expected: PASS.

- [ ] **Step 5: Commit settings**

Run:

```bash
git add tests/test_settings.py src/mining_news_bot/settings.py
git commit -m "feat: add settings loader"
```

## Task 3: Models and Database

**Files:**
- Create: `tests/test_database.py`
- Create: `src/mining_news_bot/models.py`
- Create: `src/mining_news_bot/database.py`

- [ ] **Step 1: Write failing database test**

Create `tests/test_database.py`:

```python
from mining_news_bot.database import Database
from mining_news_bot.models import NewsItem


def test_database_saves_and_finds_processed_url(tmp_path):
    db = Database(tmp_path / "test.sqlite3")
    db.initialize()

    item = NewsItem(
        title="Mining company launches new project",
        url="https://example.com/news/1",
        source_name="Example",
        published_at="2026-05-02",
        summary="Short source text",
    )
    draft_id = db.create_draft(item, "Короткий черновик")

    assert draft_id == 1
    assert db.has_processed_url("https://example.com/news/1") is True
    assert db.has_processed_url("https://example.com/news/2") is False
```

- [ ] **Step 2: Run failing test**

Run: `python -m pytest tests/test_database.py -v`

Expected: FAIL because database/model modules do not exist yet.

- [ ] **Step 3: Implement models**

Create `src/mining_news_bot/models.py`:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    name: str
    url: str
    type: str
    enabled: bool = True
    region: str | None = None
    category: str | None = None


@dataclass(frozen=True)
class NewsItem:
    title: str
    url: str
    source_name: str
    published_at: str | None
    summary: str
```

- [ ] **Step 4: Implement database**

Create `src/mining_news_bot/database.py`:

```python
import sqlite3
from pathlib import Path

from mining_news_bot.models import NewsItem


class Database:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS drafts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_url TEXT NOT NULL UNIQUE,
                    source_name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    published_at TEXT,
                    source_summary TEXT NOT NULL,
                    draft_text TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    telegram_message_id INTEGER,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    moderated_at TEXT
                )
                """
            )

    def has_processed_url(self, url: str) -> bool:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM drafts WHERE source_url = ? LIMIT 1",
                (url,),
            ).fetchone()
            return row is not None

    def create_draft(self, item: NewsItem, draft_text: str) -> int:
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO drafts (
                    source_url, source_name, title, published_at, source_summary, draft_text
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    item.url,
                    item.source_name,
                    item.title,
                    item.published_at,
                    item.summary,
                    draft_text,
                ),
            )
            return int(cursor.lastrowid)
```

- [ ] **Step 5: Verify database**

Run: `python -m pytest tests/test_database.py -v`

Expected: PASS.

- [ ] **Step 6: Commit database**

Run:

```bash
git add tests/test_database.py src/mining_news_bot/models.py src/mining_news_bot/database.py
git commit -m "feat: add draft database"
```

## Task 4: Source Configuration and RSS Collector

**Files:**
- Create: `config/sources.example.yml`
- Create: `tests/test_sources_and_collector.py`
- Create: `src/mining_news_bot/sources.py`
- Create: `src/mining_news_bot/collector.py`

- [ ] **Step 1: Write failing source and collector tests**

Create `tests/test_sources_and_collector.py`:

```python
from pathlib import Path

from mining_news_bot.collector import parse_rss_entries
from mining_news_bot.sources import load_sources


def test_load_sources_ignores_disabled_sources(tmp_path):
    config = tmp_path / "sources.yml"
    config.write_text(
        """
sources:
  - name: Active RSS
    url: https://example.com/rss
    type: rss
    enabled: true
  - name: Disabled RSS
    url: https://example.com/disabled
    type: rss
    enabled: false
""",
        encoding="utf-8",
    )

    sources = load_sources(config)

    assert len(sources) == 1
    assert sources[0].name == "Active RSS"


def test_parse_rss_entries_returns_news_items():
    rss = Path("tests/fixtures/sample.xml").read_text(encoding="utf-8")

    items = parse_rss_entries(rss, source_name="Example")

    assert len(items) == 1
    assert items[0].title == "New copper mine opens"
    assert items[0].url == "https://example.com/copper"
```

Also create `tests/fixtures/sample.xml`:

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>Example</title>
    <item>
      <title>New copper mine opens</title>
      <link>https://example.com/copper</link>
      <pubDate>Sat, 02 May 2026 09:00:00 +0300</pubDate>
      <description>A company opened a copper mining project.</description>
    </item>
  </channel>
</rss>
```

- [ ] **Step 2: Run failing tests**

Run: `python -m pytest tests/test_sources_and_collector.py -v`

Expected: FAIL because source and collector modules do not exist yet.

- [ ] **Step 3: Implement source loading**

Create `src/mining_news_bot/sources.py`:

```python
from pathlib import Path

import yaml

from mining_news_bot.models import Source


def load_sources(path: str | Path) -> list[Source]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    sources = []
    for raw in data.get("sources", []):
        source = Source(
            name=raw["name"],
            url=raw["url"],
            type=raw["type"],
            enabled=raw.get("enabled", True),
            region=raw.get("region"),
            category=raw.get("category"),
        )
        if source.enabled:
            sources.append(source)
    return sources
```

- [ ] **Step 4: Implement RSS parser and fetcher**

Create `src/mining_news_bot/collector.py`:

```python
import feedparser
import httpx

from mining_news_bot.models import NewsItem, Source


def parse_rss_entries(rss_text: str, source_name: str) -> list[NewsItem]:
    feed = feedparser.parse(rss_text)
    items: list[NewsItem] = []
    for entry in feed.entries:
        url = entry.get("link", "").strip()
        title = entry.get("title", "").strip()
        if not url or not title:
            continue
        items.append(
            NewsItem(
                title=title,
                url=url,
                source_name=source_name,
                published_at=entry.get("published"),
                summary=entry.get("summary", ""),
            )
        )
    return items


async def collect_from_source(source: Source) -> list[NewsItem]:
    if source.type != "rss":
        return []
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        response = await client.get(source.url)
        response.raise_for_status()
        return parse_rss_entries(response.text, source.name)
```

- [ ] **Step 5: Create example source config**

Create `config/sources.example.yml`:

```yaml
sources:
  - name: Mining.com
    url: https://www.mining.com/feed/
    type: rss
    enabled: true
    region: world
    category: industry
```

- [ ] **Step 6: Verify sources and collector**

Run: `python -m pytest tests/test_sources_and_collector.py -v`

Expected: PASS.

- [ ] **Step 7: Commit sources and collector**

Run:

```bash
git add config/sources.example.yml tests/test_sources_and_collector.py tests/fixtures/sample.xml src/mining_news_bot/sources.py src/mining_news_bot/collector.py
git commit -m "feat: add RSS source collection"
```

## Task 5: Topic Filter and Draft Generator

**Files:**
- Create: `tests/test_filtering_and_generator.py`
- Create: `src/mining_news_bot/filtering.py`
- Create: `src/mining_news_bot/generator.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_filtering_and_generator.py`:

```python
from mining_news_bot.filtering import is_mining_related
from mining_news_bot.generator import build_prompt
from mining_news_bot.models import NewsItem


def test_topic_filter_accepts_mining_news():
    item = NewsItem(
        title="Gold miner starts new mine",
        url="https://example.com/gold",
        source_name="Example",
        published_at=None,
        summary="The company started production at a gold mine.",
    )

    assert is_mining_related(item) is True


def test_topic_filter_rejects_unrelated_news():
    item = NewsItem(
        title="Bank changes mortgage rates",
        url="https://example.com/bank",
        source_name="Example",
        published_at=None,
        summary="A bank changed consumer mortgage terms.",
    )

    assert is_mining_related(item) is False


def test_prompt_requires_source_link_and_no_extra_facts():
    item = NewsItem(
        title="Copper project receives permit",
        url="https://example.com/copper",
        source_name="Example",
        published_at="2026-05-02",
        summary="A copper project received a permit.",
    )

    prompt = build_prompt(item)

    assert "https://example.com/copper" in prompt
    assert "не добавляй факты" in prompt.lower()
```

- [ ] **Step 2: Run failing tests**

Run: `python -m pytest tests/test_filtering_and_generator.py -v`

Expected: FAIL because filtering and generator modules do not exist yet.

- [ ] **Step 3: Implement topic filter**

Create `src/mining_news_bot/filtering.py`:

```python
from mining_news_bot.models import NewsItem


MINING_KEYWORDS = {
    "mine",
    "mining",
    "miner",
    "gold",
    "copper",
    "nickel",
    "coal",
    "iron ore",
    "uranium",
    "rare earth",
    "карьер",
    "шахт",
    "добыч",
    "горнодобы",
    "горн",
    "уголь",
    "золото",
    "медь",
    "никель",
    "руда",
    "уран",
    "гок",
    "обогат",
}


def is_mining_related(item: NewsItem) -> bool:
    haystack = f"{item.title} {item.summary}".lower()
    return any(keyword in haystack for keyword in MINING_KEYWORDS)
```

- [ ] **Step 4: Implement draft prompt and generator**

Create `src/mining_news_bot/generator.py`:

```python
from openai import AsyncOpenAI

from mining_news_bot.models import NewsItem


def build_prompt(item: NewsItem) -> str:
    return f"""
Ты готовишь короткий пост для Telegram-канала о горной промышленности.

Правила:
- Пиши на русском языке.
- Формат: заголовок, затем 3-5 коротких предложений, затем ссылка на источник.
- Используй только информацию из исходного материала.
- Не добавляй факты, прогнозы или выводы, которых нет в источнике.
- Не используй кликбейт.
- Сохраняй важные названия компаний, месторождений, стран, дат и чисел.

Источник: {item.source_name}
Дата: {item.published_at or "не указана"}
Ссылка: {item.url}
Заголовок: {item.title}
Текст источника: {item.summary}
""".strip()


class DraftGenerator:
    def __init__(self, api_key: str, model: str = "gpt-4.1-mini") -> None:
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate(self, item: NewsItem) -> str:
        response = await self.client.responses.create(
            model=self.model,
            input=build_prompt(item),
        )
        return response.output_text.strip()
```

- [ ] **Step 5: Verify filter and generator prompt**

Run: `python -m pytest tests/test_filtering_and_generator.py -v`

Expected: PASS.

- [ ] **Step 6: Commit filter and generator**

Run:

```bash
git add tests/test_filtering_and_generator.py src/mining_news_bot/filtering.py src/mining_news_bot/generator.py
git commit -m "feat: add topic filter and draft generator"
```

## Task 6: Telegram Moderation

**Files:**
- Modify: `src/mining_news_bot/database.py`
- Create: `tests/test_telegram_bot.py`
- Create: `src/mining_news_bot/telegram_bot.py`

- [ ] **Step 1: Write failing moderation tests**

Create `tests/test_telegram_bot.py`:

```python
from mining_news_bot.telegram_bot import build_moderation_keyboard


def test_moderation_keyboard_contains_publish_and_reject():
    keyboard = build_moderation_keyboard(42)

    buttons = keyboard.inline_keyboard[0]
    assert buttons[0].text == "Опубликовать"
    assert buttons[0].callback_data == "publish:42"
    assert buttons[1].text == "Отклонить"
    assert buttons[1].callback_data == "reject:42"
```

- [ ] **Step 2: Run failing test**

Run: `python -m pytest tests/test_telegram_bot.py -v`

Expected: FAIL because `telegram_bot.py` does not exist yet.

- [ ] **Step 3: Add database status helpers**

Add these methods to `src/mining_news_bot/database.py` inside `Database`:

```python
    def get_draft(self, draft_id: int) -> sqlite3.Row | None:
        with self.connect() as connection:
            return connection.execute(
                "SELECT * FROM drafts WHERE id = ?",
                (draft_id,),
            ).fetchone()

    def mark_published(self, draft_id: int, telegram_message_id: int | None = None) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                UPDATE drafts
                SET status = 'published',
                    telegram_message_id = ?,
                    moderated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (telegram_message_id, draft_id),
            )

    def mark_rejected(self, draft_id: int) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                UPDATE drafts
                SET status = 'rejected',
                    moderated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (draft_id,),
            )
```

- [ ] **Step 4: Implement Telegram helpers**

Create `src/mining_news_bot/telegram_bot.py`:

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from mining_news_bot.database import Database
from mining_news_bot.settings import Settings


def build_moderation_keyboard(draft_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Опубликовать", callback_data=f"publish:{draft_id}"),
                InlineKeyboardButton("Отклонить", callback_data=f"reject:{draft_id}"),
            ]
        ]
    )


async def send_draft_to_moderator(
    application: Application,
    moderator_chat_id: int,
    draft_id: int,
    draft_text: str,
) -> None:
    await application.bot.send_message(
        chat_id=moderator_chat_id,
        text=draft_text,
        reply_markup=build_moderation_keyboard(draft_id),
        disable_web_page_preview=False,
    )


def build_callback_handler(settings: Settings, database: Database) -> CallbackQueryHandler:
    async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if query is None or query.data is None:
            return
        await query.answer()
        action, raw_draft_id = query.data.split(":", 1)
        draft_id = int(raw_draft_id)
        draft = database.get_draft(draft_id)
        if draft is None:
            await query.edit_message_text("Черновик не найден.")
            return
        if action == "publish":
            message = await context.bot.send_message(
                chat_id=settings.telegram_channel_id,
                text=draft["draft_text"],
                disable_web_page_preview=False,
            )
            database.mark_published(draft_id, message.message_id)
            await query.edit_message_text(f"Опубликовано:\\n\\n{draft['draft_text']}")
        elif action == "reject":
            database.mark_rejected(draft_id)
            await query.edit_message_text(f"Отклонено:\\n\\n{draft['draft_text']}")

    return CallbackQueryHandler(handle_callback)
```

- [ ] **Step 5: Verify Telegram helpers**

Run: `python -m pytest tests/test_telegram_bot.py -v`

Expected: PASS.

- [ ] **Step 6: Commit Telegram moderation**

Run:

```bash
git add tests/test_telegram_bot.py src/mining_news_bot/database.py src/mining_news_bot/telegram_bot.py
git commit -m "feat: add Telegram moderation"
```

## Task 7: Scheduler and Main Entrypoint

**Files:**
- Create: `tests/test_scheduler.py`
- Create: `src/mining_news_bot/scheduler.py`
- Create: `src/mining_news_bot/main.py`

- [ ] **Step 1: Write failing scheduler test**

Create `tests/test_scheduler.py`:

```python
from mining_news_bot.scheduler import parse_check_time


def test_parse_check_time():
    assert parse_check_time("09:30") == (9, 30)
```

- [ ] **Step 2: Run failing test**

Run: `python -m pytest tests/test_scheduler.py -v`

Expected: FAIL because `scheduler.py` does not exist yet.

- [ ] **Step 3: Implement scheduler**

Create `src/mining_news_bot/scheduler.py`:

```python
import logging

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
) -> None:
    for source in load_sources(sources_path):
        try:
            items = await collect_from_source(source)
        except Exception:
            logger.exception("Failed to collect source %s", source.name)
            continue

        for item in items:
            if database.has_processed_url(item.url):
                continue
            if not is_mining_related(item):
                continue
            try:
                draft_text = await generator.generate(item)
                draft_id = database.create_draft(item, draft_text)
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
    job,
) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=timezone)
    for check_time in check_times:
        hour, minute = parse_check_time(check_time)
        scheduler.add_job(job, "cron", hour=hour, minute=minute)
    return scheduler
```

- [ ] **Step 4: Implement main**

Create `src/mining_news_bot/main.py`:

```python
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
```

- [ ] **Step 5: Verify scheduler and full tests**

Run: `python -m pytest -v`

Expected: PASS.

- [ ] **Step 6: Commit scheduler and entrypoint**

Run:

```bash
git add tests/test_scheduler.py src/mining_news_bot/scheduler.py src/mining_news_bot/main.py
git commit -m "feat: add scheduled bot runner"
```

## Task 8: Operator Documentation

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create README**

Create `README.md`:

```markdown
# Mining News Telegram Bot

Бот помогает вести Telegram-канал с новостями горной промышленности.

Он проверяет настроенные источники, готовит короткие черновики новостей и отправляет их модератору. В канал публикуются только те посты, которые модератор одобрил кнопкой "Опубликовать".

## Первый запуск

1. Установите Python 3.11 или новее.
2. Создайте виртуальное окружение:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Установите зависимости:

   ```powershell
   python -m pip install -e ".[dev]"
   ```

4. Скопируйте `.env.example` в `.env` и заполните реальные значения.
5. Скопируйте `config/sources.example.yml` в `config/sources.yml` и настройте источники.
6. Запустите бота:

   ```powershell
   python -m mining_news_bot.main
   ```

## Что нужно подготовить в Telegram

- Создать Telegram-бота через BotFather.
- Добавить бота администратором в канал.
- Узнать ID канала или использовать публичный username канала.
- Написать боту от аккаунта модератора, чтобы он мог отправлять вам черновики.

## Важное ограничение

Бот не публикует новости сам. Он отправляет черновик модератору, а публикация происходит только после нажатия кнопки "Опубликовать".
```

- [ ] **Step 2: Verify all tests**

Run: `python -m pytest -v`

Expected: PASS.

- [ ] **Step 3: Commit README**

Run:

```bash
git add README.md
git commit -m "docs: add operator guide"
```

## Self-Review

- Spec coverage: The plan covers source configuration, RSS collection, duplicate storage, topic filtering, draft generation, Telegram moderation, scheduled checks, secrets outside git, and operator documentation.
- Intentional limitation: The plan implements RSS first. Generic webpage scraping is listed in the design but not included in the first implementation because RSS gives a safer MVP. Webpage-specific parsers can be added after the first bot works.
- Placeholder scan: No task uses TBD, TODO, placeholder language, or unspecified implementation instructions.
- Type consistency: `NewsItem`, `Source`, `Database`, `DraftGenerator`, and scheduler function names are consistent across tasks.
