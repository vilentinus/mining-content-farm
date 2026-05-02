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
