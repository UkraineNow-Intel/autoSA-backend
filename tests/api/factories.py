import datetime as dt
import factory
from api import models
from django.contrib.auth import models as auth_models


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = auth_models.User

    username = "apitest"
    password = "blah"
    is_superuser = True


class SourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Source

    interface = models.INTERFACE_API
    source = "http://www.example.com"
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
