import datetime as dt
import uuid

import factory
from taggit import models as taggit_models

from api import models

try:
    import zoneinfo
except (ImportError, ModuleNotFoundError):
    from backports import zoneinfo


TZ_UTC = zoneinfo.ZoneInfo("UTC")


def uuid_as_str():
    return uuid.uuid4().hex


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = taggit_models.Tag

    name = "tag1"
    slug = "tag1"


class SourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Source

    interface = models.INTERFACE_API
    origin = "www.example.com"
    external_id = factory.LazyFunction(uuid_as_str)
    url = "http://www.example.com/some/url/page.html"
    headline = "Test headline"
    text = "Something happened"
    language = models.LANGUAGE_EN
    pinned = False
    timestamp = dt.datetime.utcnow().replace(tzinfo=TZ_UTC)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        tag_values = extracted or ["tag1", "tag2"]
        self.tags.add(*tag_values)


class TranslationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Translation

    language = models.LANGUAGE_UK
    text = "Щось трапилося"
    source = factory.SubFactory(SourceFactory)
