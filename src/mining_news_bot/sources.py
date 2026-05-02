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
