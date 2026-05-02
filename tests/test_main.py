import logging

from mining_news_bot.main import configure_logging


def test_configure_logging_suppresses_http_library_info_logs():
    configure_logging()

    assert logging.getLogger("httpx").level == logging.WARNING
    assert logging.getLogger("telegram").level == logging.WARNING
