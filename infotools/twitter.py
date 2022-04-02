"""
We need to continously be collecting data from twitter accounts.

Requires TWITTER_BEARER_TOKEN setting to be filled for this to work.
"""

from typing import Union

import pandas as pd
import tweepy
from tweepy.user import User
from tweepy.client import Response
from tweepy.tweet import Tweet

from .settings import TWITTER_BEARER_TOKEN, TWITTER_SOURCE_ACCOUNTS
from .utils import represents_int

client = tweepy.Client(TWITTER_BEARER_TOKEN)


class TwitterAccount:
    """Simple wrapper to represent a twitter account.

    Parameters
    ----------
    username_or_id: str or int
        An existing twitter account's username with or without the '@' symbol or a twitter id.

    Examples
    --------
    Constructing a TwitterAccount

    >>> user  = TwitterAccount('ZackPlauche') # Via username without the '@'
    >>> user2 = TwitterAccount('@ZackPlauche') # Via atname (username with the '@')
    >>> user3 = TwitterAccount(1227703724778364928) # Via id as int
    >>> user4 = TwitterAccount('1227703724778364928') # Via id as str

    Access a Twitter account's data

    >>> user.username
    ZackPlauche
    >>> user.atname
    @ZackPlauche
    >>> user.name
    Zack Plauché
    >>> user.id
    1227703724778364928

    Get a user's tweets

    >>> tweets = user.get_tweets()  # Get latest 5 tweets in a list.
    >>> hundred_tweets = user.get_tweets(100)  # Get latest 100 tweets (maximum 100, min 5)
    >>> latest_tweet = user.get_latest_tweet()
    """

    def __init__(self, username_or_id):
        user = get_twitter_acccount(username_or_id)
        self.user = user
        self.username = user.username
        self.atname = f"@{user.username}"
        self.id = user.id
        self.name = user.name

    def __repr__(self):
        return f"<TwitterAccount: {self.name} (@{self.username})>"

    def get_tweets(self, max_results=5, **kwargs) -> list[Tweet]:
        """Gets latest tweets from a twitter account limited by max_results.

        Parameters
        ----------
        max_results: int, defaults to 5
            The max number of a user's latest tweets to be returned. Must be a
            minimum of 5, maximum of 100 according to tweepy's api.

        Additional kwargs can be found from the tweepy docs here:
        https://docs.tweepy.org/en/stable/client.html#tweepy.Client.get_users_tweets
        """
        tweet_fields = [
            "author_id",
            "created_at",
        ]  # Needed to have author reference and datetime data on the returned tweets
        return client.get_users_tweets(
            id=self.id, max_results=max_results, tweet_fields=tweet_fields, **kwargs
        ).data

    def get_latest_tweet(self) -> Tweet:
        return self.get_tweets(5)[0]


def get_twitter_acccount(username_or_id: Union[str, int]) -> User:
    """Get a twitter account from username or id twitter account identifiers.

    Paramters
    ---------
    username_or_id: int or str
        The username or numeric id for a Twitter account. username can be with
        or without the '@' symbol. id can be either str or int types.
    """

    if not isinstance(username_or_id, (str, int)):
        raise ValueError(f"identifer {username_or_id} must be str or int.")

    if represents_int(username_or_id):
        twitter_id = username_or_id
        response: Response = client.get_user(id=twitter_id)
    else:
        username = username_or_id if not username_or_id.startswith('@') else username_or_id[1:]
        response: Response = client.get_user(username=username)
    
    # Check to make sure a twitter account with this username exists.
    if response.errors:
        raise ValueError(response.errors[0]["detail"])

    user: User = response.data
    return user


def get_latest_tweets_from_sources(max_results=5) -> list[Tweet]:
    """Get latest tweets from all TWITTER_SOURCE_ACCOUNTS"""
    accounts = [TwitterAccount(username) for username in TWITTER_SOURCE_ACCOUNTS]
    latest_tweets = [
        tweet for account in accounts for tweet in account.get_tweets(max_results)
    ]
    return latest_tweets


def latest_tweets_to_dataframe() -> pd.DataFrame:
    """Get latest tweets from TWITTER_SOURCE_ACCOUNTS and return them in a dataframe format."""
    tweets = get_latest_tweets_from_sources()
    df = pd.DataFrame([tweet.data for tweet in tweets])
    df["author"] = df["author_id"].apply(
        lambda author_id: TwitterAccount(author_id).atname
    )
    del df["author_id"]
    return df


def latest_tweets_to_csv(csv_filename: str) -> None:
    df = latest_tweets_to_dataframe()
    df.to_csv(csv_filename, index=False)
