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
