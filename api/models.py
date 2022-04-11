from django.contrib.gis.db import models
from django.utils import timezone
from taggit.managers import TaggableManager


LANGUAGE_EN = "en"
LANGUAGE_RU = "ru"
LANGUAGE_UA = "ua"

INTERFACE_TWITTER = "twitter"
INTERFACE_WEBSITE = "website"
INTERFACE_API = "api"


LANGUAGES = (
    (LANGUAGE_EN, "English"),
    (LANGUAGE_RU, "Russian"),
    (LANGUAGE_UA, "Ukrainian"),
)

INTERFACES = (
    (INTERFACE_TWITTER, "Twitter"),
    (INTERFACE_WEBSITE, "Website"),
    (INTERFACE_API, "API"),
)


class Source(models.Model):
    """Represents a single event / piece of information from twitter,
    external API, web, etc."""

    interface = models.CharField(max_length=50, choices=INTERFACES)
    source = models.CharField(max_length=250)
    headline = models.CharField(max_length=250, blank=True)
    text = models.TextField()
    language = models.CharField(max_length=2, choices=LANGUAGES)
    pinned = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)
    tags = TaggableManager(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["timestamp"], name="timestamp_idx"),
        ]

    def __str__(self):
        return f"""id: {self.id}, language: {self.language}, text: {self.text}"""

    def __repr__(self):
        return (
            f"""{self.__class__.__name__}(interface="{self.interface}", """
            f"""source="{self.source}, headline="{self.headline}\"""",
            f"""text="{self.text}\", language="{self.language}", """,
            f"""timestamp={self.timestamp})""",
        )


class Translation(models.Model):
    """Represents a translation for a source. One source may have
    multiple translations."""

    language = models.CharField(max_length=2, choices=LANGUAGES)
    text = models.TextField()
    source = models.ForeignKey(
        Source, on_delete=models.CASCADE, related_name="translations"
    )

    def __str__(self):
        return f"""id: {self.id}, language: {self.language}, text: {self.text}"""

    def __repr__(self):
        return (
            f"""{self.__class__.__name__}(language="{self.language}", """
            f"""text="{self.text}\""""
        )


class Location(models.Model):
    """Represents a geographic location. One source may have
    multiple locations."""

    name = models.CharField(max_length=250)
    # in Factal: SRID=4326;POINT (30.7233095 46.482526)
    point = models.PointField(blank=True, null=True)
    # in Factal: SRID=4326;POLYGON ((30.6116849 46.319522, 30.6116849 46.60042199999999, 30.8118901 46.60042199999999, 30.8118901 46.319522, 30.6116849 46.319522)) # noqa
    polygon = models.PolygonField(blank=True, null=True)
    source = models.ForeignKey(
        Source, on_delete=models.CASCADE, related_name="locations"
    )

    class Meta:
        indexes = [
            models.Index(fields=["name"], name="name_idx"),
        ]

    def __str__(self):
        return (
            f"""id: {self.id}, name: {self.name}, latitude: {self.latitude}, """,
            f"""longitude: {self.longitude}""",
        )

    def __repr__(self):
        return (
            f"""{self.__class__.__name__}(name="{self.name}", """
            f"""latitude={self.latitude}, longitude={self.longitude}"""
        )
