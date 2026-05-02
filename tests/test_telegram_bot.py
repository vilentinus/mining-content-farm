from mining_news_bot.telegram_bot import build_moderation_keyboard


def test_moderation_keyboard_contains_publish_and_reject():
    keyboard = build_moderation_keyboard(42)

    buttons = keyboard.inline_keyboard[0]
    assert buttons[0].text == "Опубликовать"
    assert buttons[0].callback_data == "publish:42"
    assert buttons[1].text == "Отклонить"
    assert buttons[1].callback_data == "reject:42"
