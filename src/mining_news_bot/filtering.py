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
