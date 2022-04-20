import datetime as dt

try:
    import zoneinfo
except (ImportError, ModuleNotFoundError):
    from backports import zoneinfo

import json

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from taggit.models import Tag, TaggedItem

from api.models import Location, Source, Translation
from tests.api import factories

pytestmark = [pytest.mark.integration, pytest.mark.django_db]
TZ_UTC = zoneinfo.ZoneInfo("UTC")


@pytest.fixture
def source():
    return factories.SourceFactory(
        timestamp=timezone.now(),
    )


@pytest.fixture
def source_set():
    """Helper method to create multiple sources"""
    source1 = factories.SourceFactory(
        interface="website",
        origin="http://www.msnbc.com",
        headline="Terrible events in Bucha",
        text="Russian soldiers killed peaceful civilians in Bucha",
        timestamp=dt.datetime(2022, 4, 1, 1, 55, tzinfo=TZ_UTC),
    )
    source1.tags.add("bucha", "killing")

    source2 = factories.SourceFactory(
        interface="twitter",
        origin="@Blah",
        headline="Kramatorsk train station attack",
        text="In Kramatorsk, dozens killed when trying to evacuate",
        timestamp=dt.datetime(2022, 4, 2, 2, 55, tzinfo=TZ_UTC),
    )
    source2.tags.add("kramatorsk", "killing", "train station")

    source3 = factories.SourceFactory(
        interface="api",
        origin="http://factal.com",
        headline="Russians retreating from Kharkiv",
        text="Russian troops are dropping attempts to take Kharkiv",
        timestamp=dt.datetime(2022, 4, 3, 3, 55, tzinfo=TZ_UTC),
    )
    source3.tags.add("kharkiv", "free")

    return source1, source2, source3


@pytest.fixture
def bool_source_set():
    sources = []
    sources.append(factories.SourceFactory(pinned=True, deleted=False))
    sources.append(factories.SourceFactory(pinned=False, deleted=False))
    sources.append(factories.SourceFactory(pinned=False, deleted=True))
    return sources


@pytest.fixture
def multi_search_source_set():
    """Helper method to create multiple sources"""

    sources = []

    for kw in ["Bucha", "Kramatorsk", "Kharkiv"]:
        # keyword in headline only
        source1 = factories.SourceFactory(
            interface="website",
            origin="http://www.msnbc.com",
            headline=f"Terrible events in {kw}",
            text="Russian soldiers killed peaceful civilians",
            timestamp=dt.datetime(2022, 4, 1, 1, 55, tzinfo=TZ_UTC),
        )
        sources.append(source1)

        # keyword in text only
        source2 = factories.SourceFactory(
            interface="website",
            origin="http://www.msnbc.com",
            headline="Terrible events in Ukraine",
            text=f"Russian soldiers killed peaceful civilians in {kw}",
            timestamp=dt.datetime(2022, 4, 1, 1, 55, tzinfo=TZ_UTC),
        )
        sources.append(source2)

        # keyword in tags only
        source3 = factories.SourceFactory(
            interface="website",
            origin="http://www.msnbc.com",
            headline="Terrible events in Ukraine",
            text="Russian soldiers killed peaceful civilians",
            timestamp=dt.datetime(2022, 4, 1, 1, 55, tzinfo=TZ_UTC),
        )
        source3.tags.add(kw)
        sources.append(source3)

    return sources


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
        "language": "uk",
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
        "language": "uk",
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
    source.translations.set([Translation(**td) for td in translation_data], bulk=False)
    source.locations.set([Location(**ld) for ld in create_location_data], bulk=False)

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
        ({"timestamp__range": "2022-04-01T01:55:00Z,2022-04-02T02:55:00Z"}, 2),
    ],
)
def test_filter_by_timestamp(apiclient, admin_user, source_set, query, expected_count):
    """Filter by timestamp"""
    apiclient.force_authenticate(user=admin_user)
    url = reverse("source-list")

    response = apiclient.get(url, data=query, format="json")
    data = response.json()
    results = data["results"]
    assert expected_count == len(results)


@pytest.mark.parametrize(
    ("query", "expected_count"),
    [
        ({"interface": "website"}, 1),
        ({"interface": "twitter"}, 1),
        ({"interface": "api"}, 1),
    ],
)
def test_filter_by_interface(apiclient, admin_user, source_set, query, expected_count):
    """Filter by interface"""
    apiclient.force_authenticate(user=admin_user)
    url = reverse("source-list")

    response = apiclient.get(url, data=query, format="json")
    results = response.json()["results"]
    assert expected_count == len(results)


@pytest.mark.parametrize(
    ("query", "expected_count"),
    [
        ({"origin": "http://www.msnbc.com"}, 1),
        ({"origin": "@Blah"}, 1),
        ({"origin": "http://factal.com"}, 1),
    ],
)
def test_filter_by_source(apiclient, admin_user, source_set, query, expected_count):
    """Filter by source"""
    apiclient.force_authenticate(user=admin_user)
    url = reverse("source-list")

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
def test_filter_by_headline(apiclient, admin_user, source_set, query, expected_count):
    """Filter by headline"""
    apiclient.force_authenticate(user=admin_user)
    url = reverse("source-list")

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
def test_filter_by_text(apiclient, admin_user, source_set, query, expected_count):
    """Filter by text"""
    apiclient.force_authenticate(user=admin_user)
    url = reverse("source-list")

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
def test_filter_by_tags(apiclient, admin_user, source_set, query, expected_count):
    """Filter by text"""
    apiclient.force_authenticate(user=admin_user)
    url = reverse("source-list")

    response = apiclient.get(url, data=query, format="json")
    results = response.json()["results"]
    assert expected_count == len(results)


@pytest.mark.parametrize(
    ("query", "expected_count"),
    [
        ({"q": "bucha"}, 3),
        ({"q": "kramatorsk"}, 3),
        ({"q": "kharkiv"}, 3),
    ],
)
def test_multi_search_q(
    apiclient, admin_user, multi_search_source_set, query, expected_count
):
    """Filter by text, keyword or tag"""
    apiclient.force_authenticate(user=admin_user)
    url = reverse("source-list")

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
def test_paginate(
    apiclient, admin_user, query, source_set, expected_count, has_next, has_prev
):
    """Test pagination"""
    apiclient.force_authenticate(user=admin_user)
    url = reverse("source-list")

    response = apiclient.get(url, data=query, format="json")
    data = response.json()
    next = data["next"]
    prev = data["previous"]
    results = ["results"]
    assert has_next == (next is not None)
    assert has_prev == (prev is not None)
    assert expected_count == len(results)


def test_sort(apiclient, admin_user, source_set):
    """Test default sort order"""
    apiclient.force_authenticate(user=admin_user)
    url = reverse("source-list")

    response = apiclient.get(url, data={"limit": 3}, format="json")
    data = response.json()
    results = data["results"]
    timestamps = [r["timestamp"] for r in results]
    assert sorted(timestamps, reverse=True) == timestamps


@pytest.mark.parametrize(
    ("query", "expected_count"),
    [
        ({"pinned": "true"}, 1),
        ({"pinned": "false"}, 1),
        ({"deleted": "true"}, 1),
        ({"deleted": "false"}, 2),
    ],
)
def test_boolean_filters(apiclient, admin_user, bool_source_set, query, expected_count):
    """Filter by boolean field (pinned/deleted)"""
    apiclient.force_authenticate(user=admin_user)
    url = reverse("source-list")

    response = apiclient.get(url, data=query, format="json")
    results = response.json()["results"]
    assert expected_count == len(results)


@pytest.mark.parametrize(
    ("query", "expected_count"),
    [
        ({}, 2),  # if not specifically requested, exclude deleted
        ({"deleted": "any"}, 3),
    ],
)
def test_deleted_filters(apiclient, admin_user, bool_source_set, query, expected_count):
    """Filter by deleted"""
    apiclient.force_authenticate(user=admin_user)
    url = reverse("source-list")

    response = apiclient.get(url, data=query, format="json")
    results = response.json()["results"]
    assert expected_count == len(results)
