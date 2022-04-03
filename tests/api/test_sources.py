import datetime as dt
try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo
from django.urls import reverse
from django.contrib.auth import models
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from taggit.models import Tag
from api.models import Source, INTERFACE_API, LANGUAGE_EN


class SourceTests(APITestCase):
    def setUp(self) -> None:
        user = models.User.objects.create(
            username="apitest", password="blah", is_superuser=True
        )
        self.client.force_authenticate(user=user)

    def test_create_source(self):
        """Create a new source"""
        url = reverse("source-list")
        data = {
            "tags": ["tag1", "tag2"],
            "interface": "website",
            "source": "@Blah",
            "headline": "",
            "text": "Щось трапилося",
            "language": "ua",
            "timestamp": "2022-04-01T20:25:00Z",
            "pinned": "true",
            "translations": [],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Source.objects.count(), 1)
        self.assertEqual(Tag.objects.count(), 2)
        actual = Source.objects.get()
        for key in ["interface", "source", "headline", "text", "language"]:
            actual_value = getattr(actual, key)
            self.assertEqual(data[key], actual_value)
        self.assertCountEqual(data["tags"], list(actual.tags.names()))

    def test_list_sources(self):
        """Retrieve sources"""
        tz = zoneinfo.ZoneInfo("UTC")
        source = Source.objects.create(
            interface=INTERFACE_API,
            source="www.example.com",
            headline="Test headline",
            text="Text from website",
            language=LANGUAGE_EN,
            timestamp=dt.datetime(2022, 4, 1, 20, 55, tzinfo=tz),
            pinned=True,
        )
        source.tags.add("tag1", "tag2")
        url = reverse("source-list")
        response = self.client.get(url, format="json")
        expected = {
            "tags": ["tag1", "tag2"],
            "interface": "api",
            "source": "www.example.com",
            "headline": "Test headline",
            "text": "Text from website",
            "language": "en",
            "timestamp": "2022-04-01T20:55:00Z",
            "pinned": True,
            "translations": [],
        }
        sources = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(sources), 1)
        actual = sources[0]
        self.assertCountEqual(expected.keys(), actual.keys())
        for key in ["interface", "source", "headline", "text", "language", "pinned"]:
            self.assertEqual(expected[key], actual[key])
        self.assertCountEqual(expected["tags"], actual["tags"])

    def test_delete_source(self):
        """Delete a source"""
        source = Source(
            interface=INTERFACE_API,
            source="www.example.com",
            headline="Test headline",
            text="Text from website",
            language=LANGUAGE_EN,
            tags=["tag1", "tag2"],
            timestamp=timezone.now(),
            pinned=True,
        )
        source.save()
        url = reverse("source-detail", kwargs={"pk": source.id})
        response = self.client.delete(url, pk=1, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Source.objects.count(), 0)
        self.assertEqual(Tag.objects.count(), 0)
