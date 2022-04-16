"""
Requires TWITTER_BEARER_TOKEN setting.
"""
import datetime as dt
import textwrap
import pytz
import tweepy


USER_FIELDS = "id,created_at,name,username,verified,location,url"
TWEET_FIELDS = "id,created_at,text,author_id,geo,source,lang,attachments,entities"
PLACE_FIELDS = "id,name,country_code,place_type,full_name,country,contained_within,geo"
MEDIA_FIELDS = "media_key,type,url,preview_image_url,alt_text"
EXPANSIONS = "author_id,attachments.media_keys,geo.place_id"
MAX_QUERY_LEN = 512


def _generate_sources(response):
    """Generate dicts suitable for converting to sources.
    Returns iterable.
    param response: class tweepy.Response"""
    users = {
        user.id: user for user in response.includes.get("users", [])
    }
    medias = {
        media.media_key: media for media in response.includes.get("media", [])
    }
    if not response.data:
        return None
    for tweet in response.data:
        user = users[tweet.author_id]
        attachments = getattr(tweet, "attachments", None) or {}
        media_keys = attachments.get("media_keys", None) or []
        source_data = {
            "interface": "twitter",
            "origin": user.username,
            "external_id": tweet.id,
            "language": tweet.lang or "en",
            "url": f"https://twitter.com/{user.username}/status/{tweet.id}",
            "text": tweet.text,
            "timestamp": tweet.created_at,
        }
        if media_keys:
            media_key = media_keys[0]
            media = medias[media_key]
            source_data["media_url"] = media.url
        yield source_data


def _split_queries(twitter_accounts):
    query = " OR ".join([f"from:{acc.lstrip('@')}" for acc in twitter_accounts])
    queries = textwrap.wrap(query, width=MAX_QUERY_LEN)
    for i, query in enumerate(queries):
        queries[i] = query.lstrip("OR ").rstrip(" OR")
    return queries


def _get_default_start_time():
    """By default, retrieve from 24 hours back until now."""
    return (dt.datetime.utcnow() - dt.timedelta(hours=1)).replace(
        tzinfo=pytz.UTC
    )


def search_recent_tweets(
    settings,
    start_time=None,
    end_time=None,
):
    client = tweepy.Client(settings["TWITTER_BEARER_TOKEN"])
    queries = _split_queries(settings["TWITTER_ACCOUNTS"])
    start_time = start_time or _get_default_start_time()
    for query in queries:
        for response in tweepy.Paginator(
            client.search_recent_tweets,
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
            for source_sata in _generate_sources(response):
                yield source_sata
