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
