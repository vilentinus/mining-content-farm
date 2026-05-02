from pathlib import Path

from dotenv import dotenv_values


REQUIRED_ENV_KEYS = [
    "OPENAI_API_KEY",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHANNEL_ID",
    "TELEGRAM_MODERATOR_CHAT_ID",
]


def validate_env_values(values: dict[str, str | None]) -> list[str]:
    issues: list[str] = []
    for key in REQUIRED_ENV_KEYS:
        if not values.get(key):
            issues.append(f"{key} is missing")

    moderator_chat_id = values.get("TELEGRAM_MODERATOR_CHAT_ID")
    if moderator_chat_id and not moderator_chat_id.lstrip("-").isdigit():
        issues.append("TELEGRAM_MODERATOR_CHAT_ID must be a numeric chat ID")

    return issues


def main() -> None:
    env_path = Path(".env")
    if not env_path.exists():
        print("ENV: .env file not found")
        return

    values = dotenv_values(env_path)
    issues = validate_env_values(values)

    if issues:
        print("ENV: problems found")
        for issue in issues:
            print(f"- {issue}")
    else:
        print("ENV: required values are present")

    print("")
    print("Notes:")
    print("- TELEGRAM_MODERATOR_CHAT_ID is not the bot username.")
    print("- To get it, write any message to the bot, then check recent updates or use a Telegram ID helper bot.")
    print("- TELEGRAM_CHANNEL_ID is the public channel username like @your_channel or a numeric channel ID.")


if __name__ == "__main__":
    main()
