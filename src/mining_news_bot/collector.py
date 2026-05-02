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
