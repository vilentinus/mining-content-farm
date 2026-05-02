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
