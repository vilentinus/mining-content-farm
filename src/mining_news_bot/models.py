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
