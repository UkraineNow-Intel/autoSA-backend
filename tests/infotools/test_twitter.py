import tweepy

from infotools.twitter import twitter

TWEET = tweepy.Tweet(
    {
        "text": "Some text here",
        "id": "345",
        "geo": {"place_id": "123"},
    }
)

PLACES_WITH_POINT = {
    "123": tweepy.Place(
        {
            "geo": {
                "type": "point",
                "coordinates": [-40.5, 30.1],
            },
            "country_code": "US",
            "name": "Los Angeles",
            "id": "123",
            "place_type": "city",
            "country": "United States",
            "full_name": "Los Angeles, CA",
        }
    )
}

PLACES_WITH_POLYGON = {
    "123": tweepy.Place(
        {
            "geo": {
                "type": "polygon",
                "coordinates": [
                    [
                        [100.0, 0.0],
                        [101.0, 0.0],
                        [101.0, 1.0],
                        [100.0, 1.0],
                        [100.0, 0.0],
                    ]
                ],
            },
            "country_code": "US",
            "name": "Manhattan",
            "id": "123",
            "place_type": "city",
            "country": "United States",
            "full_name": "Manhattan, NY",
        }
    )
}


def test_read_config():
    twitter_accounts = twitter._read_config()
    assert isinstance(twitter_accounts, list)
    assert len(twitter_accounts) > 0


def test_parse_point():
    """Parse point out of tweet"""
    locations = twitter._parse_locations(TWEET, PLACES_WITH_POINT)
    assert len(locations) == 1
    assert locations == [
        {
            "name": "Los Angeles, CA",
            "point": {
                "type": "point",
                "coordinates": [-40.5, 30.1],
            },
        }
    ]


def test_parse_polygon():
    """Parse polygon out of tweet"""
    locations = twitter._parse_locations(TWEET, PLACES_WITH_POLYGON)
    assert len(locations) == 1
    assert locations == [
        {
            "name": "Manhattan, NY",
            "polygon": {
                "type": "polygon",
                "coordinates": [
                    [
                        [100.0, 0.0],
                        [101.0, 0.0],
                        [101.0, 1.0],
                        [100.0, 1.0],
                        [100.0, 0.0],
                    ]
                ],
            },
        }
    ]
