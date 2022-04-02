import datetime as dt
import zoneinfo
from django.urls import reverse
from django.contrib.auth import models
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Source, INTERFACE_API, LANGUAGE_EN


class SourceTests(APITestCase):
    def setUp(self) -> None:
        self.user = models.User(username="apitest", password="blah", is_superuser=True)
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_create_source(self):
        """Create a new source"""
        url = reverse("source-list")
        data = {
            "tags": [],
            "interface": "website",
            "source": "@Blah",
            "headline": "",
            "text": "Щось трапилося",
            "language": "ua",
            "timestamp": "2022-04-01T20:25:00Z",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Source.objects.count(), 1)
        self.assertEqual(Source.objects.get().text, "Щось трапилося")

    def test_list_sources(self):
        """Retrieve sources"""
        tz = zoneinfo.ZoneInfo("UTC")
        source = Source(
            interface=INTERFACE_API,
            source="www.example.com",
            headline="Test headline",
            text="Text from website",
            language=LANGUAGE_EN,
            timestamp=dt.datetime(2022, 4, 1, 20, 55, tzinfo=tz),
        )
        source.save()
        url = reverse("source-list")
        response = self.client.get(url, format="json")
        expected = {
            "url": "http://testserver/api/sources/1",
            "tags": [],
            "interface": "api",
            "source": "www.example.com",
            "headline": "Test headline",
            "text": "Text from website",
            "language": "en",
            "timestamp": "2022-04-01T20:55:00Z",
        }
        actual = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(actual), 1)
        self.assertDictEqual(expected, actual[0])

    def test_delete_source(self):
        """Delete a source"""
        source = Source(
            interface=INTERFACE_API,
            source="www.example.com",
            headline="Test headline",
            text="Text from website",
            language=LANGUAGE_EN,
            timestamp=timezone.now(),
        )
        source.save()
        url = reverse("source-detail", kwargs={"pk": source.id})
        response = self.client.delete(url, pk=1, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Source.objects.count(), 0)
