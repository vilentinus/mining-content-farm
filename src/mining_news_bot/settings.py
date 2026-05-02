from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    telegram_bot_token: str
    telegram_channel_id: str
    telegram_moderator_chat_id: int
    openai_api_key: str
    database_path: str = "bot.sqlite3"
    sources_path: str = "config/sources.yml"
    check_times: str = "09:00,19:00"
    timezone: str = "Europe/Moscow"
    max_drafts_per_run: int = 30
    max_drafts_per_source: int = 3

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @cached_property
    def parsed_check_times(self) -> list[str]:
        return [item.strip() for item in self.check_times.split(",") if item.strip()]
