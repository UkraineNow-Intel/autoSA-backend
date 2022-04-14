import datetime as dt

try:
    import zoneinfo
except (ImportError, ModuleNotFoundError):
    from backports import zoneinfo
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from taggit.models import Tag, TaggedItem
from api.models import Source, Translation, Location
import pytest
import json
from . import factories

pytestmark = pytest.mark.integration
TZ_UTC = zoneinfo.ZoneInfo("UTC")


class SourceTests(APITestCase):
    def setUp(self) -> None:
        user = factories.UserFactory()
        self.client.force_authenticate(user=user)

    def compare_children(self, expected_children, actual_children):
        for i, actual_child in enumerate(actual_children):
            expected_child = expected_children[i]
            for field_name in expected_child:
                expected_value = expected_child[field_name]
                if hasattr(actual_child[field_name], "json"):
                    actual_value = json.loads(actual_child[field_name].json)
                else:
                    actual_value = actual_child[field_name]
                self.assertEqual(expected_value, actual_value)

    def test_create_source(self):
        """Create a new source"""
        url = reverse("source-list")
        data = {
            "tags": ["tag1", "tag2"],
            "interface": "website",
            "origin": "example.com",
            "url": "http://example.com/page1.html",
            "headline": "Важливи новини",
            "text": "Щось трапилося",
            "language": "ua",
            "timestamp": dt.datetime(2022, 4, 1, 20, 55, tzinfo=TZ_UTC),
            "pinned": True,
            "translations": [{"language": "en", "text": "Something happened"}],
            "locations": [
                {
                    "name": "Somewhere",
                    "point": {"type": "Point", "coordinates": [30.7233095, 46.482526]},
                }
            ],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Source.objects.count(), 1)
        self.assertEqual(Tag.objects.count(), 2)
        self.assertEqual(TaggedItem.objects.count(), 2)
        self.assertEqual(Translation.objects.count(), 1)
        self.assertEqual(Location.objects.count(), 1)
        actual = Source.objects.get()
        for key in data.keys():
            actual_value = getattr(actual, key)
            if key == "tags":
                self.assertCountEqual(data[key], list(actual.tags.names()))
            elif key in ("translations", "locations"):
                actual_children = list(getattr(actual, key).values())
                self.compare_children(data[key], actual_children)
            else:
                self.assertEqual(data[key], actual_value)

    def test_update_source(self):
        source = factories.SourceFactory(
            timestamp=timezone.now(),
            pinned=True,
        )
        url = reverse("source-detail", kwargs={"pk": source.id})
        data = {
            "tags": ["tag1"],
            "interface": "website",
            "origin": "example.com",
            "url": "http://example.com/page1.html",
            "headline": "Важливи новини",
            "text": "Щось трапилося",
            "language": "ua",
            "timestamp": dt.datetime(2022, 4, 1, 20, 55, tzinfo=TZ_UTC),
            "pinned": True,
            "translations": [{"language": "en", "text": "Something happened"}],
            "locations": [
                {
                    "name": "Somewhere",
                    "point": {"type": "Point", "coordinates": [30.7233095, 46.482526]},
                }
            ],
        }
        response = self.client.put(url, data, pk=1, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Source.objects.count(), 1)
        self.assertEqual(Translation.objects.count(), 1)
        self.assertEqual(Location.objects.count(), 1)
        actual = Source.objects.first()
        for key, value in data.items():
            if key == "tags":
                actual_value = list(actual.tags.names())
                self.assertCountEqual(value, actual_value)
            elif key in ("translations", "locations"):
                actual_children = list(getattr(actual, key).values())
                self.compare_children(data[key], actual_children)
            else:
                actual_value = getattr(actual, key)
                self.assertEqual(value, actual_value)

    def test_partial_update_source(self):
        source = factories.SourceFactory(
            timestamp=timezone.now(),
            pinned=True,
        )
        url = reverse("source-detail", kwargs={"pk": source.id})
        data = {
            "text": "Что-то случилось",
            "language": "ru",
            "translations": [{"language": "en", "text": "Something happened"}],
            "locations": [
                {
                    "name": "Somewhere",
                    "point": {"type": "Point", "coordinates": [30.7233095, 46.482526]},
                }
            ],
        }
        response = self.client.patch(url, data, pk=1, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Source.objects.count(), 1)
        actual = Source.objects.first()
        # these should change
        for key, value in data.items():
            if key in ("translations", "locations"):
                actual_children = list(getattr(actual, key).values())
                self.compare_children(data[key], actual_children)
            else:
                actual_value = getattr(actual, key)
                self.assertEqual(value, actual_value)
        # these should be preserved
        preserve_fields = [
            "id",
            "interface",
            "origin",
            "external_id",
            "url",
            "headline",
            "pinned",
        ]
        for key in preserve_fields:
            self.assertEqual(getattr(source, key), getattr(actual, key))
        self.assertEqual(list(source.tags.names()), list(actual.tags.names()))

    def test_list_sources(self):
        """Retrieve sources"""
        source = factories.SourceFactory(
            origin="example.com",
            url="http://example.com/page1.html",
            headline="Важливи новини",
            timestamp=dt.datetime(2022, 4, 1, 20, 55, tzinfo=TZ_UTC),
            pinned=True,
        )
        translation_data = [{"language": "en", "text": "Something happened"}]
        create_location_data = [
            {
                "name": "Somewhere",
                "point": "POINT(30.7233095 46.482526)",
            }
        ]
        expected_location_data = [
            {
                "name": "Somewhere",
                "point": {"type": "Point", "coordinates": [30.7233095, 46.482526]},
            }
        ]
        source.translations.set(
            [Translation(**td) for td in translation_data], bulk=False
        )
        source.locations.set(
            [Location(**ld) for ld in create_location_data], bulk=False
        )
        url = reverse("source-list")
        response = self.client.get(url, format="json")
        expected = {
            "tags": ["tag1", "tag2"],
            "interface": "api",
            "origin": "example.com",
            "url": "http://example.com/page1.html",
            "headline": "Важливи новини",
            "text": "Something happened",
            "language": "en",
            "timestamp": "2022-04-01T20:55:00Z",
            "pinned": True,
            "translations": translation_data,
            "locations": expected_location_data,
        }
        sources = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(sources), 1)
        actual = sources[0]
        for key in expected.keys():
            if key == "tags":
                self.assertCountEqual(expected[key], actual[key])
            elif key in ("translations", "locations"):
                self.compare_children(expected[key], actual[key])
            else:
                self.assertEqual(expected[key], actual[key])

    def test_delete_source(self):
        """Delete a source"""
        source = factories.SourceFactory(
            timestamp=timezone.now(),
            pinned=True,
        )
        source.translations.add(
            Translation(source=source, language="en", text="Something happened"),
            bulk=False,
        )
        source.locations.add(
            Location(source=source, name="Somewhere"),
            bulk=False,
        )
        url = reverse("source-detail", kwargs={"pk": source.id})
        response = self.client.delete(url, pk=1, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Source.objects.count(), 0)
        self.assertEqual(Translation.objects.count(), 0)
        self.assertEqual(Location.objects.count(), 0)
        self.assertEqual(Tag.objects.count(), 2)
        self.assertEqual(TaggedItem.objects.count(), 0)
