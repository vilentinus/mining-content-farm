from mining_news_bot.scheduler import parse_check_time


def test_parse_check_time():
    assert parse_check_time("09:30") == (9, 30)
