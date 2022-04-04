import datetime as dt

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from taggit.models import Tag, TaggedItem
from api.models import Source
import pytest
from . import factories

pytestmark = pytest.mark.integration


class SourceTests(APITestCase):
    def setUp(self) -> None:
        user = factories.UserFactory()
        self.client.force_authenticate(user=user)

    def test_create_source(self):
        """Create a new source"""
        url = reverse("source-list")
        tz = zoneinfo.ZoneInfo("UTC")
        data = {
            "tags": ["tag1", "tag2"],
            "interface": "website",
            "source": "@Blah",
            "headline": "",
            "text": "Щось трапилося",
            "language": "ua",
            "timestamp": dt.datetime(2022, 4, 1, 20, 55, tzinfo=tz),
            "pinned": True,
            "translations": [],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Source.objects.count(), 1)
        self.assertEqual(Tag.objects.count(), 2)
        self.assertEqual(TaggedItem.objects.count(), 2)
        actual = Source.objects.get()
        for key in data.keys():
            actual_value = getattr(actual, key)
            if key == "tags":
                self.assertCountEqual(data[key], list(actual.tags.names()))
            elif key == "translations":
                continue
            else:
                self.assertEqual(data[key], actual_value)

    def test_update_source(self):
        url = reverse("source-list")
        tz = zoneinfo.ZoneInfo("UTC")
        data = {
            "tags": ["tag1", "tag2"],
            "interface": "website",
            "source": "@Blah",
            "headline": "",
            "text": "Щось трапилося",
            "language": "ua",
            "timestamp": dt.datetime(2022, 4, 1, 20, 55, tzinfo=tz),
            "pinned": True,
            "translations": [],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Source.objects.count(), 1)
        self.assertEqual(Tag.objects.count(), 2)
        self.assertEqual(TaggedItem.objects.count(), 2)
        actual = Source.objects.get()
        for key in data.keys():
            actual_value = getattr(actual, key)
            if key == "tags":
                self.assertCountEqual(data[key], list(actual.tags.names()))
            elif key == "translations":
                continue
            else:
                self.assertEqual(data[key], actual_value)

    def test_list_sources(self):
        """Retrieve sources"""
        tz = zoneinfo.ZoneInfo("UTC")
        factories.SourceFactory(
            timestamp=dt.datetime(2022, 4, 1, 20, 55, tzinfo=tz),
            pinned=True,
        )
        url = reverse("source-list")
        response = self.client.get(url, format="json")
        expected = {
            "tags": ["tag1", "tag2"],
            "interface": "api",
            "source": "http://www.example.com",
            "headline": "Test headline",
            "text": "Something happened",
            "language": "en",
            "timestamp": "2022-04-01T20:55:00Z",
            "pinned": True,
            "translations": [],
        }
        sources = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(sources), 1)
        actual = sources[0]
        for key in expected.keys():
            if key == "tags":
                self.assertCountEqual(expected[key], actual[key])
            else:
                self.assertEqual(expected[key], actual[key])

    def test_delete_source(self):
        """Delete a source"""
        source = factories.SourceFactory(
            timestamp=timezone.now(),
            pinned=True,
        )
        url = reverse("source-detail", kwargs={"pk": source.id})
        response = self.client.delete(url, pk=1, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Source.objects.count(), 0)
        self.assertEqual(Tag.objects.count(), 2)
        self.assertEqual(TaggedItem.objects.count(), 0)
