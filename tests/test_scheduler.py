from mining_news_bot.scheduler import parse_check_time
from mining_news_bot.scheduler import check_sources_once
from mining_news_bot.models import NewsItem, Source


def test_parse_check_time():
    assert parse_check_time("09:30") == (9, 30)


async def test_check_sources_once_limits_total_and_per_source(monkeypatch):
    sources = [
        Source(name="Source A", url="https://example.com/a", type="rss"),
        Source(name="Source B", url="https://example.com/b", type="rss"),
    ]
    items_by_source = {
        "Source A": [
            NewsItem(f"A {index}", f"https://example.com/a/{index}", "Source A", None, "mining")
            for index in range(5)
        ],
        "Source B": [
            NewsItem(f"B {index}", f"https://example.com/b/{index}", "Source B", None, "mining")
            for index in range(5)
        ],
    }
    sent_draft_ids: list[int] = []

    class FakeDatabase:
        def __init__(self) -> None:
            self.created = 0

        def has_processed_url(self, url: str) -> bool:
            return False

        def create_draft(self, item: NewsItem, draft_text: str) -> int:
            self.created += 1
            return self.created

    class FakeGenerator:
        async def generate(self, item: NewsItem) -> str:
            return f"Draft for {item.title}"

    async def fake_collect_from_source(source: Source) -> list[NewsItem]:
        return items_by_source[source.name]

    async def fake_send_draft_to_moderator(application, moderator_chat_id, draft_id, draft_text):
        sent_draft_ids.append(draft_id)

    monkeypatch.setattr("mining_news_bot.scheduler.load_sources", lambda path: sources)
    monkeypatch.setattr("mining_news_bot.scheduler.collect_from_source", fake_collect_from_source)
    monkeypatch.setattr("mining_news_bot.scheduler.send_draft_to_moderator", fake_send_draft_to_moderator)

    await check_sources_once(
        application=object(),
        database=FakeDatabase(),
        generator=FakeGenerator(),
        sources_path="sources.yml",
        moderator_chat_id=123,
        max_drafts_per_run=3,
        max_drafts_per_source=2,
    )

    assert sent_draft_ids == [1, 2, 3]
