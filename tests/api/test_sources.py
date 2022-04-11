import datetime as dt

try:
    import zoneinfo
except (ImportError, ModuleNotFoundError):
    from backports import zoneinfo
import json
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from taggit.models import Tag, TaggedItem
from api.models import Source, Translation, Location
from tests.api import factories
import pytest


pytestmark = [pytest.mark.integration, pytest.mark.django_db]
TZ_UTC = zoneinfo.ZoneInfo("UTC")


@pytest.fixture
def source():
    return factories.SourceFactory(
        timestamp=timezone.now(),
    )


def create_source_set():
    """Helper method to create multiple sources"""
    source1 = factories.SourceFactory(
        interface="website",
        source="http://www.msnbc.com",
        headline="Terrible events in Bucha",
        text="Russian soldiers killed peaceful civilians in Bucha",
        timestamp=dt.datetime(2022, 4, 1, 1, 55, tzinfo=TZ_UTC),
    )
    source1.tags.add("bucha", "killing")

    source2 = factories.SourceFactory(
        interface="twitter",
        source="@Blah",
        headline="Kramatorsk train station attack",
        text="In Kramatorsk, dozens killed when trying to evacuate",
        timestamp=dt.datetime(2022, 4, 2, 2, 55, tzinfo=TZ_UTC),
    )
    source2.tags.add("kramatorsk", "killing", "train station")

    source3 = factories.SourceFactory(
        interface="api",
        source="http://factal.com",
        headline="Russians retreating from Kharkiv",
        text="Russian troops are dropping attempts to take Kharkiv",
        timestamp=dt.datetime(2022, 4, 3, 3, 55, tzinfo=TZ_UTC),
    )
    source3.tags.add("kharkiv", "free")

    return source1, source2, source3


def compare_children(expected_children, actual_children):
    for i, actual_child in enumerate(actual_children):
        expected_child = expected_children[i]
        for field_name in expected_child:
            expected_value = expected_child[field_name]
            if hasattr(actual_child[field_name], "json"):
                actual_value = json.loads(actual_child[field_name].json)
            else:
                actual_value = actual_child[field_name]
            assert expected_value == actual_value


def test_create_source(apiclient, admin_user):
    """Create a new source"""
    apiclient.force_authenticate(user=admin_user)
    url = reverse("source-list")
    data = {
        "tags": ["tag1", "tag2"],
        "interface": "website",
        "origin": "example.com",
        "url": "http://example.com/page1.html",
        "media_url": "http://example.com/image1.jpg",
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
    response = apiclient.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert Source.objects.count() == 1
    assert Tag.objects.count() == 2
    assert TaggedItem.objects.count() == 2
    assert Translation.objects.count() == 1
    assert Location.objects.count() == 1
    actual = Source.objects.get()
    for key in data.keys():
        actual_value = getattr(actual, key)
        if key == "tags":
            assert sorted(data[key]) == sorted(list(actual.tags.names()))
        elif key in ("translations", "locations"):
            actual_children = list(getattr(actual, key).values())
            compare_children(data[key], actual_children)
        else:
            assert data[key] == actual_value


def test_update_source(apiclient, admin_user, source):
    apiclient.force_authenticate(user=admin_user)
    url = reverse("source-detail", kwargs={"pk": source.id})

    data = {
        "tags": ["tag1"],
        "interface": "website",
        "origin": "example.com",
        "url": "http://example.com/page1.html",
        "media_url": "http://example.com/image1.jpg",
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
    response = apiclient.put(url, data, pk=1, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert Source.objects.count() == 1
    assert Translation.objects.count() == 1
    assert Location.objects.count() == 1
    actual = Source.objects.first()
    for key, value in data.items():
        if key == "tags":
            actual_value = list(actual.tags.names())
            assert sorted(value) == sorted(actual_value)
        elif key in ("translations", "locations"):
            actual_children = list(getattr(actual, key).values())
            compare_children(data[key], actual_children)
        else:
            actual_value = getattr(actual, key)
            assert value == actual_value


def test_partial_update_source(apiclient, admin_user, source):
    apiclient.force_authenticate(user=admin_user)
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
    response = apiclient.patch(url, data, pk=1, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert Source.objects.count() == 1
    actual = Source.objects.first()
    # these should change
    for key, value in data.items():
        if key in ("translations", "locations"):
            actual_children = list(getattr(actual, key).values())
            compare_children(data[key], actual_children)
        else:
            actual_value = getattr(actual, key)
            assert value == actual_value
    # these should be preserved
    preserve_fields = [
        "id",
        "interface",
        "origin",
        "external_id",
        "url",
        "media_url",
        "headline",
        "pinned",
    ]
    for key in preserve_fields:
        assert getattr(source, key) == getattr(actual, key)
    assert sorted(list(source.tags.names())) == sorted(list(actual.tags.names()))


def test_list_sources(apiclient, admin_user):
    """Retrieve sources"""
    apiclient.force_authenticate(user=admin_user)

    source = factories.SourceFactory(
        origin="example.com",
        url="http://example.com/page1.html",
        media_url="http://example.com/image1.jpg",
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
    response = apiclient.get(url, format="json")
    expected = {
        "tags": ["tag1", "tag2"],
        "interface": "api",
        "origin": "example.com",
        "url": "http://example.com/page1.html",
        "media_url": "http://example.com/image1.jpg",
        "headline": "Важливи новини",
        "text": "Something happened",
        "language": "en",
        "timestamp": "2022-04-01T20:55:00Z",
        "pinned": True,
        "translations": translation_data,
        "locations": expected_location_data,
    }
    sources = response.json()["results"]
    assert response.status_code == status.HTTP_200_OK
    assert len(sources) == 1
    actual = sources[0]
    for key in expected.keys():
        if key == "tags":
            assert sorted(expected[key]) == sorted(actual[key])
        elif key in ("translations", "locations"):
            compare_children(expected[key], actual[key])
        else:
            assert expected[key] == actual[key]


def test_delete_source(apiclient, admin_user, source):
    """Delete a source"""
    apiclient.force_authenticate(user=admin_user)

    source.translations.add(
        Translation(source=source, language="en", text="Something happened"),
        bulk=False,
    )
    source.locations.add(
        Location(source=source, name="Somewhere"),
        bulk=False,
    )

    url = reverse("source-detail", kwargs={"pk": source.id})
    response = apiclient.delete(url, pk=1, format="json")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Source.objects.count() == 0
    assert Translation.objects.count() == 0
    assert Location.objects.count() == 0
    assert Tag.objects.count() == 2
    assert TaggedItem.objects.count() == 0


@pytest.mark.parametrize(
    ("query", "expected_count"),
    [
        ({"timestamp": "2022-04-01T01:55:00Z"}, 1),
        ({"timestamp__lt": "2022-04-03T03:55:00Z"}, 2),
        ({"timestamp__lte": "2022-04-03T03:55:00Z"}, 3),
        ({"timestamp__gt": "2022-04-01T01:55:00Z"}, 2),
        ({"timestamp__gte": "2022-04-01T01:55:00Z"}, 3),
    ],
)
def test_filter_by_timestamp(apiclient, admin_user, query, expected_count):
    """Filter by timestamp"""
    apiclient.force_authenticate(user=admin_user)
    url = reverse("source-list")
    create_source_set()

    response = apiclient.get(url, data=query, format="json")
    results = response.json()["results"]
    assert expected_count == len(results)


@pytest.mark.parametrize(
    ("query", "expected_count"),
    [
        ({"interface": "website"}, 1),
        ({"interface": "twitter"}, 1),
        ({"interface": "api"}, 1),
    ],
)
def test_filter_by_interface(apiclient, admin_user, query, expected_count):
    """Filter by interface"""
    apiclient.force_authenticate(user=admin_user)
    url = reverse("source-list")
    create_source_set()

    response = apiclient.get(url, data=query, format="json")
    results = response.json()["results"]
    assert expected_count == len(results)


@pytest.mark.parametrize(
    ("query", "expected_count"),
    [
        ({"source": "http://www.msnbc.com"}, 1),
        ({"source": "@Blah"}, 1),
        ({"source": "http://factal.com"}, 1),
    ],
)
def test_filter_by_source(apiclient, admin_user, query, expected_count):
    """Filter by source"""
    apiclient.force_authenticate(user=admin_user)
    url = reverse("source-list")
    create_source_set()

    response = apiclient.get(url, data=query, format="json")
    results = response.json()["results"]
    assert expected_count == len(results)


@pytest.mark.parametrize(
    ("query", "expected_count"),
    [
        # exact match
        ({"headline": "Terrible events in Bucha"}, 1),
        ({"headline": "Kramatorsk train station attack"}, 1),
        ({"headline": "Russians retreating from Kharkiv"}, 1),
        # contains
        ({"headline__contains": "Bucha"}, 1),
        ({"headline__contains": "Kramatorsk"}, 1),
        ({"headline__contains": "Kharkiv"}, 1),
        # contains, case insensitive
        ({"headline__icontains": "bucha"}, 1),
        ({"headline__icontains": "kramatorsk"}, 1),
        ({"headline__icontains": "kharkiv"}, 1),
    ],
)
def test_filter_by_headline(apiclient, admin_user, query, expected_count):
    """Filter by headline"""
    apiclient.force_authenticate(user=admin_user)
    url = reverse("source-list")
    create_source_set()

    response = apiclient.get(url, data=query, format="json")
    results = response.json()["results"]
    assert expected_count == len(results)


@pytest.mark.parametrize(
    ("query", "expected_count"),
    [
        # exact match
        ({"text": "Russian soldiers killed peaceful civilians in Bucha"}, 1),
        ({"text": "In Kramatorsk, dozens killed when trying to evacuate"}, 1),
        ({"text": "Russian troops are dropping attempts to take Kharkiv"}, 1),
        # contains
        ({"text__contains": "Bucha"}, 1),
        ({"text__contains": "Kramatorsk"}, 1),
        ({"text__contains": "Kharkiv"}, 1),
        # contains, case insensitive
        ({"text__icontains": "bucha"}, 1),
        ({"text__icontains": "kramatorsk"}, 1),
        ({"text__icontains": "kharkiv"}, 1),
    ],
)
def test_filter_by_text(apiclient, admin_user, query, expected_count):
    """Filter by text"""
    apiclient.force_authenticate(user=admin_user)
    url = reverse("source-list")
    create_source_set()

    response = apiclient.get(url, data=query, format="json")
    results = response.json()["results"]
    assert expected_count == len(results)


@pytest.mark.parametrize(
    ("query", "expected_count"),
    [
        # one tag
        ({"tags": "bucha"}, 1),
        ({"tags": "kramatorsk"}, 1),
        ({"tags": "kharkiv"}, 1),
        # multiple tags: OR
        ({"tags": "bucha,kramatorsk"}, 2),
        ({"tags": "kramatorsk,killing"}, 2),
        ({"tags": "kharkiv,killing"}, 3),
    ],
)
def test_filter_by_tags(apiclient, admin_user, query, expected_count):
    """Filter by text"""
    apiclient.force_authenticate(user=admin_user)
    url = reverse("source-list")
    create_source_set()

    response = apiclient.get(url, data=query, format="json")
    results = response.json()["results"]
    assert expected_count == len(results)


@pytest.mark.parametrize(
    ("query", "expected_count", "has_next", "has_prev"),
    [
        ({"limit": 1, "offset": 0}, 1, True, False),
        ({"limit": 1, "offset": 1}, 1, True, True),
        ({"limit": 1, "offset": 2}, 1, False, True),
    ],
)
def test_paginate(apiclient, admin_user, query, expected_count, has_next, has_prev):
    """Test pagination"""
    apiclient.force_authenticate(user=admin_user)
    url = reverse("source-list")
    create_source_set()

    response = apiclient.get(url, data=query, format="json")
    data = response.json()
    next = data["next"]
    prev = data["previous"]
    results = ["results"]
    assert has_next == (next is not None)
    assert has_prev == (prev is not None)
    assert expected_count == len(results)
