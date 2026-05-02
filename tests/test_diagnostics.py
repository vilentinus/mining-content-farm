from mining_news_bot.diagnostics import validate_env_values


def test_validate_env_values_reports_missing_channel():
    issues = validate_env_values(
        {
            "OPENAI_API_KEY": "key",
            "TELEGRAM_BOT_TOKEN": "token",
            "TELEGRAM_MODERATOR_CHAT_ID": "123",
        }
    )

    assert "TELEGRAM_CHANNEL_ID is missing" in issues


def test_validate_env_values_rejects_bot_username_as_moderator_chat_id():
    issues = validate_env_values(
        {
            "OPENAI_API_KEY": "key",
            "TELEGRAM_BOT_TOKEN": "token",
            "TELEGRAM_CHANNEL_ID": "@channel",
            "TELEGRAM_MODERATOR_CHAT_ID": "@content_mining_farm_bot",
        }
    )

    assert "TELEGRAM_MODERATOR_CHAT_ID must be a numeric chat ID" in issues
