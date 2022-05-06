from infotools.telegram import telegram


def test_read_config():
    telegram_accounts = telegram._read_config()
    assert isinstance(telegram_accounts, list)
    assert len(telegram_accounts) > 0
