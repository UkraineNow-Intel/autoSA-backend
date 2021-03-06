"""
Requires TWITTER_BEARER_TOKEN setting.
"""
import json
import os
import textwrap

import tweepy
from django.contrib.gis.geos import GEOSGeometry, Polygon

from api.models import LOCATION_ORIGIN_GEOTAG
from infotools.utils import read_config

USER_FIELDS = "id,created_at,name,username,verified,location,url"
TWEET_FIELDS = "id,created_at,text,author_id,geo,source,lang,attachments,entities,referenced_tweets"
PLACE_FIELDS = "id,name,country_code,place_type,full_name,country,contained_within,geo"
MEDIA_FIELDS = "media_key,type,url,preview_image_url,alt_text"
EXPANSIONS = "author_id,attachments.media_keys,geo.place_id,referenced_tweets.id"
MAX_QUERY_LEN = 512


def _format_locations(tweet, places: dict):
    """Parse geo data from geotagged tweets"""
    if not tweet.geo:
        return []
    place = places.get(tweet.geo["place_id"], None)
    if not place or not place.geo:
        return []
    if place.geo["type"].lower() == "point":
        return [
            {
                "name": place.full_name,
                "point": place.geo,
                "origin": LOCATION_ORIGIN_GEOTAG,
            }
        ]
    if place.geo["type"].lower() == "polygon":
        polygon = GEOSGeometry(json.dumps(place.geo))
        point_data = json.loads(polygon.centroid.geojson)
        return [
            {
                "name": place.full_name,
                "point": point_data,
                "polygon": place.geo,
                "origin": LOCATION_ORIGIN_GEOTAG,
            }
        ]
    if place.geo.get("bbox", None):
        polygon = Polygon.from_bbox(place.geo["bbox"])
        polygon_data = json.loads(polygon.geojson)
        point_data = json.loads(polygon.centroid.geojson)
        return [
            {
                "name": place.full_name,
                "point": point_data,
                "polygon": polygon_data,
                "origin": LOCATION_ORIGIN_GEOTAG,
            }
        ]
    return []


def _format_source(tweet, users: dict, medias: dict, places: dict):
    """Format tweet into a dict that we can use to create a Source.
    param tweet: Tweet object
    param user: dict of {id: User object}
    param medias: dict of {media_key: Media object}
    """
    user = users[tweet.author_id]
    attachments = getattr(tweet, "attachments", None) or {}
    media_keys = attachments.get("media_keys", None) or []
    language = tweet.lang if tweet.lang in ("en", "ua", "ru") else "en"
    media_url = ""
    source_data = {
        "interface": "twitter",
        "origin": user.username,
        "external_id": tweet.id,
        "language": language,
        "url": f"https://twitter.com/{user.username}/status/{tweet.id}",
        "text": tweet.text,
        "timestamp": tweet.created_at,
        "locations": _format_locations(tweet, places),
    }
    if media_keys:
        media_key = media_keys[0]
        media = medias[media_key]
        media_url = media.url
    source_data["media_url"] = media_url or ""
    return source_data


def _generate_sources(response):
    """Generate dicts suitable for converting to sources.
    Returns iterable.
    param response: class tweepy.Response"""
    users = {user.id: user for user in response.includes.get("users", [])}
    medias = {media.media_key: media for media in response.includes.get("media", [])}
    places = {place.id: place for place in response.includes.get("places", [])}
    if not response.data:
        return None
    for tweet in response.data:
        yield _format_source(tweet, users, medias, places)


def _split_queries(twitter_accounts):
    query = " OR ".join([f"from:{acc.lstrip('@')}" for acc in twitter_accounts])
    queries = textwrap.wrap(query, width=MAX_QUERY_LEN)
    for i, query in enumerate(queries):
        queries[i] = query.lstrip("OR ").rstrip(" OR")
    return queries


def _read_config():
    curr_dir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    config = read_config(os.path.join(curr_dir, "config.ini"))
    return config.get("main", "twitter_accounts").strip().split("\n")


def search_recent_messages(
    settings,
    start_time=None,
    end_time=None,
):
    twitter_accounts = _read_config()

    api_client = tweepy.Client(settings["TWITTER_BEARER_TOKEN"])
    queries = _split_queries(twitter_accounts)
    for query in queries:
        for response in tweepy.Paginator(
            api_client.search_recent_tweets,
            query=query,
            start_time=start_time,
            end_time=end_time,
            max_results=100,
            tweet_fields=TWEET_FIELDS,
            user_fields=USER_FIELDS,
            place_fields=PLACE_FIELDS,
            media_fields=MEDIA_FIELDS,
            expansions=EXPANSIONS,
        ):
            for source_data in _generate_sources(response):
                yield source_data


if __name__ == "__main__":
    # code to help debug the client
    import datetime as dt
    from pprint import pprint

    import pytz

    from website.settings.base import TWITTER_BEARER_TOKEN

    twitter_settings = {
        "TWITTER_BEARER_TOKEN": TWITTER_BEARER_TOKEN,
    }

    end_time = dt.datetime.utcnow().replace(
        minute=0, second=0, microsecond=0, tzinfo=pytz.UTC
    )
    start_time = end_time - dt.timedelta(hours=1)
    messages = list(
        search_recent_messages(
            twitter_settings,
            start_time=start_time,
            end_time=end_time,
        )
    )
    for msg in messages:
        pprint(msg)
    print(f"Total messages: {len(messages)}")
