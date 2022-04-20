from infotools.twitter import twitter


def test_read_config():
    twitter_accounts = twitter._read_config()
    assert isinstance(twitter_accounts, list)
    assert len(twitter_accounts) > 0
