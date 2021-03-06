import uuid

from django.contrib.gis.db import models
from django.utils import timezone
from psqlextra.models import PostgresModel
from taggit.managers import TaggableManager

LANGUAGE_EN = "en"
LANGUAGE_RU = "ru"
LANGUAGE_UK = "uk"

INTERFACE_TWITTER = "twitter"
INTERFACE_WEBSITE = "website"
INTERFACE_API = "api"
INTERFACE_TELEGRAM = "telegram"

LOCATION_ORIGIN_GEOTAG = "geotag"
LOCATION_ORIGIN_TEXT = "text"
LOCATION_ORIGIN_OPERATOR = "operator"

LANGUAGES = (
    (LANGUAGE_EN, "English"),
    (LANGUAGE_RU, "Russian"),
    (LANGUAGE_UK, "Ukrainian"),
)

INTERFACES = (
    (INTERFACE_TWITTER, "Twitter"),
    (INTERFACE_TELEGRAM, "Telegram"),
    (INTERFACE_WEBSITE, "Website"),
    (INTERFACE_API, "API"),
)

LOCATION_ORIGINS = (
    (LOCATION_ORIGIN_GEOTAG, "Geotagged source"),
    (LOCATION_ORIGIN_TEXT, "Parsed from text"),
    (LOCATION_ORIGIN_OPERATOR, "Geolocated by operator"),
)


class Source(PostgresModel):
    """Represents a single event / piece of information from twitter,
    external API, web, etc."""

    interface = models.CharField(max_length=50, choices=INTERFACES)
    # "origin" field may contain different things, depending on interface,
    # for example, Twitter username, Telegram channel name, website
    # domain name, api domain name:
    # twitter   | @SomeUserName
    # telegram  | some_channel_name
    # website   | cnn.com
    # api       | factal.com
    origin = models.CharField(max_length=250)
    # external_id can come from the external API or website,
    # and should be unique. We need this to avoid duplicating
    # tweets / telegram messages. For the scraped data, I don't
    # know if posts have any unique ids, if not, we have to figure
    # out and create our own.
    external_id = models.CharField(max_length=250, default=uuid.uuid4, unique=True)
    # url of original telegram message, tweet, website page
    url = models.CharField(max_length=2000, blank=True, default="")
    # image or video if present
    media_url = models.CharField(max_length=2000, blank=True, default="")
    headline = models.CharField(max_length=250, blank=True, default="")
    text = models.TextField()
    language = models.CharField(max_length=2, choices=LANGUAGES, default=LANGUAGE_EN)
    pinned = models.BooleanField(default=False)
    # when published
    timestamp = models.DateTimeField(default=timezone.now)
    timestamp_created = models.DateTimeField(auto_now_add=True)
    timestamp_updated = models.DateTimeField(auto_now=True)
    # deleted flag
    deleted = models.BooleanField(default=False)
    tags = TaggableManager(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["timestamp"], name="timestamp_idx"),
            models.Index(fields=["origin"], name="origin_idx"),
            models.Index(fields=["url"], name="url_idx"),
        ]


class Translation(PostgresModel):
    """Represents a translation for a source. One source may have
    multiple translations."""

    language = models.CharField(max_length=2, choices=LANGUAGES)
    text = models.TextField()
    source = models.ForeignKey(
        Source, on_delete=models.CASCADE, related_name="translations"
    )


class Location(PostgresModel):
    """Represents a geographic location. One source may have
    multiple locations."""

    name = models.CharField(max_length=250)
    # in Factal: SRID=4326;POINT (30.7233095 46.482526)
    point = models.PointField(blank=True, null=True)
    # in Factal: SRID=4326;POLYGON ((30.6116849 46.319522, 30.6116849 46.60042199999999, 30.8118901 46.60042199999999, 30.8118901 46.319522, 30.6116849 46.319522)) # noqa
    polygon = models.PolygonField(blank=True, null=True)
    # where did this location come from?
    origin = models.CharField(
        max_length=50, choices=LOCATION_ORIGINS, default=LOCATION_ORIGIN_GEOTAG
    )
    source = models.ForeignKey(
        Source, on_delete=models.CASCADE, related_name="locations"
    )

    class Meta:
        indexes = [
            models.Index(fields=["name"], name="name_idx"),
        ]
