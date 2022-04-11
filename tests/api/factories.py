import datetime as dt
import factory
from api import models
from django.utils.crypto import get_random_string


class SourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Source

    interface = models.INTERFACE_API
    origin = "www.example.com"
    external_id = get_random_string(32)
    url = "http://www.example.com/some/url/page.html"
    headline = "Test headline"
    text = "Something happened"
    language = models.LANGUAGE_EN
    pinned = False
    timestamp = dt.datetime.utcnow()

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        tag_values = extracted or ["tag1", "tag2"]
        self.tags.add(*tag_values)


class TranslationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Translation

    language = models.LANGUAGE_UA
    text = "Щось трапилося"
    source = factory.SubFactory(SourceFactory)
