from django.db import models
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
    """Represents a single event / piece of information from twitter, external API, web, etc."""

    interface = models.CharField(max_length=50, choices=INTERFACES)
    source = models.CharField(max_length=250)
    headline = models.CharField(max_length=250, blank=True)
    text = models.TextField()
    language = models.CharField(max_length=2, choices=LANGUAGES)
    timestamp = models.DateTimeField(default=timezone.now)
    tags = TaggableManager(blank=True)

    def __str__(self):
        return f"""id: {self.id}, language: {self.language}, text: {self.text}"""

    def __repr__(self):
        return f"""{self.__class__.__name__}(interface="{self.interface}", source="{self.source}, headline="{self.headline}", text="{self.text}", language="{self.language}", timestamp={self.timestamp})"""


class Translation(models.Model):
    """Represents a translation for a source. One source may have multiple translations."""

    language = models.CharField(max_length=2, choices=LANGUAGES)
    text = models.TextField()
    source = models.ForeignKey(Source, on_delete=models.CASCADE)

    def __str__(self):
        return f"""id: {self.id}, language: {self.language}, text: {self.text}"""

    def __repr__(self):
        return f"""{self.__class__.__name__}(language="{self.language}", text="{self.text}\""""
