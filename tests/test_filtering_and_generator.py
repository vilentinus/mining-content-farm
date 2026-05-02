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


def test_topic_filter_accepts_quarry_news():
    item = NewsItem(
        title="Quarry operator adds new crushing equipment",
        url="https://example.com/quarry",
        source_name="Example",
        published_at=None,
        summary="The company upgraded equipment at an aggregates quarry.",
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
