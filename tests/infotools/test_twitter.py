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


PLACES_WITH_BBOX = {
    "123": tweepy.Place(
        {
            "country": "United States",
            "country_code": "US",
            "full_name": "Pueblo, CO",
            "geo": {
                "bbox": [-104.69356, 38.200638, -104.5519919, 38.338462],
                "properties": {},
                "type": "Feature",
            },
            "id": "9d7b47e751be1551",
            "name": "Pueblo",
            "place_type": "city",
        }
    )
}


def test_read_config():
    twitter_accounts = twitter._read_config()
    assert isinstance(twitter_accounts, list)
    assert len(twitter_accounts) > 0


def test_parse_point():
    """Parse point out of tweet"""
    locations = twitter._format_locations(TWEET, PLACES_WITH_POINT)
    assert len(locations) == 1
    assert locations == [
        {
            "name": "Los Angeles, CA",
            "origin": "geotag",
            "point": {
                "type": "point",
                "coordinates": [-40.5, 30.1],
            },
        }
    ]


def test_parse_polygon():
    """Parse polygon out of tweet"""
    locations = twitter._format_locations(TWEET, PLACES_WITH_POLYGON)
    assert len(locations) == 1
    assert locations == [
        {
            "name": "Manhattan, NY",
            "origin": "geotag",
            "point": {
                "type": "Point",
                "coordinates": [100.5, 0.5],
            },
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


def test_parse_bbox():
    """Parse polygon out of tweet with bbox"""
    locations = twitter._format_locations(TWEET, PLACES_WITH_BBOX)
    assert len(locations) == 1
    assert locations == [
        {
            "name": "Pueblo, CO",
            "origin": "geotag",
            "point": {"coordinates": [-104.62277595, 38.26955], "type": "Point"},
            "polygon": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-104.69356, 38.200638],
                        [-104.69356, 38.338462],
                        [-104.5519919, 38.338462],
                        [-104.5519919, 38.200638],
                        [-104.69356, 38.200638],
                    ]
                ],
            },
        }
    ]
