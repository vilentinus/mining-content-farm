from mining_news_bot.settings import Settings


def test_settings_parse_check_times():
    settings = Settings(
        telegram_bot_token="token",
        telegram_channel_id="@channel",
        telegram_moderator_chat_id=123,
        openai_api_key="key",
        check_times="09:00,14:00,19:00",
    )

    assert settings.parsed_check_times == ["09:00", "14:00", "19:00"]


def test_default_check_times_are_morning_and_evening():
    settings = Settings(
        telegram_bot_token="token",
        telegram_channel_id="@channel",
        telegram_moderator_chat_id=123,
        openai_api_key="key",
    )

    assert settings.parsed_check_times == ["09:00", "19:00"]
