import datetime as dt

try:
    import zoneinfo
except (ImportError, ModuleNotFoundError):
    from backports import zoneinfo

import pytest
from django.urls import reverse

from api.models import Source

pytestmark = [pytest.mark.integration, pytest.mark.django_db]
TZ_UTC = zoneinfo.ZoneInfo("UTC")


ITEMS = [
    {
        "external_id": "1",
        "headline": "Explosions reported in Sumy",
        "interface": "website",
        "language": "en",
        "origin": "LiveUA Map",
        "text": "Explosions reported in Sumy",
        "timestamp": dt.datetime(2022, 4, 15, 14, 21, tzinfo=TZ_UTC),
        "url": "https://liveuamap.com/en/2022/15-april-explosions-reported-in-sumy",
    },
    {
        "external_id": "2",
        "headline": (
            "Several ships are visible off the west coast of Crimea on SAR "
            "imagery from today. These ships are near the Southern Naval "
            "Base in Donuzlav Lake"
        ),
        "interface": "website",
        "language": "en",
        "origin": "LiveUA Map",
        "text": (
            "Several ships are visible off the west coast of Crimea on SAR "
            "imagery from today. These ships are near the Southern Naval Base in "
            "Donuzlav Lake"
        ),
        "timestamp": dt.datetime(2022, 4, 15, 14, 21, tzinfo=TZ_UTC),
        "url": "https://liveuamap.com/en/2022/15-april-several-ships-are-visible-off-the-west-coast-of",
    },
    {
        "external_id": "3",
        "headline": "Explosion reported in Kirovohrad region ",
        "interface": "website",
        "language": "en",
        "origin": "LiveUA Map",
        "text": "Explosion reported in Kirovohrad region ",
        "timestamp": dt.datetime(2022, 4, 15, 13, 21, tzinfo=TZ_UTC),
        "url": "https://liveuamap.com/en/2022/15-april-explosion-reported-in-kirovohrad-region-",
    },
]


@pytest.mark.parametrize(
    ("query", "expected_overwrite"),
    [
        ({}, False),
        ({"overwrite": "true"}, True),
        ({"overwrite": "false"}, False),
    ],
)
def test_refresh(apiclient, admin_user, mocker, query, expected_overwrite):
    """Test refresh sources"""
    apiclient.force_authenticate(user=admin_user)
    url = reverse("source-refresh")

    # provide liveuamap site key only
    import api.views

    mocker.patch.object(api.views.settings, "WEBSCRAPER_SITE_KEYS", ["liveuamap"])
    # don't call real API
    mocker.patch("infotools.webscraping.webscraper.get_latest", return_value=ITEMS)
    mocker.patch("infotools.twitter.twitter.search_recent_tweets", return_value=[])
    mocker.patch(
        "infotools.telegram.telegram.search_recent_telegram_messages", return_value=[]
    )

    response = apiclient.get(url, data=query, format="json")
    data = response.json()

    assert "meta" in data
    assert "sites" in data
    assert data["meta"]["overwrite"] == expected_overwrite
    assert data["sites"] == {
        "liveuamap": {
            "detail": "Refresh completed",
            "errors": {"exceptions": [], "total": 0},
            "processed": 3,
        },
        "twitter": {
            "detail": "Refresh completed",
            "errors": {"exceptions": [], "total": 0},
            "processed": 0,
        },
        "telegram": {
            "detail": "Refresh completed",
            "errors": {"exceptions": [], "total": 0},
            "processed": 0,
        },
    }
    assert Source.objects.count() == 3


@pytest.mark.parametrize(
    ("query", "expected_overwrite"),
    [
        ({"overwrite": "true"}, True),
        ({"overwrite": "false"}, False),
    ],
)
def test_refresh_twice(apiclient, admin_user, mocker, query, expected_overwrite):
    """Test refresh sources"""
    apiclient.force_authenticate(user=admin_user)
    url = reverse("source-refresh")

    # provide liveuamap site key only
    import api.views

    mocker.patch.object(api.views.settings, "WEBSCRAPER_SITE_KEYS", ["liveuamap"])

    # don't call real API
    mocker.patch("infotools.webscraping.webscraper.get_latest", return_value=ITEMS)
    mocker.patch("infotools.twitter.twitter.search_recent_tweets", return_value=[])
    mocker.patch(
        "infotools.telegram.telegram.search_recent_telegram_messages", return_value=[]
    )

    # refresh twice. We should still have the same number of sources.
    expected_response = {
        "liveuamap": {
            "detail": "Refresh completed",
            "errors": {"exceptions": [], "total": 0},
            "processed": 3,
        },
        "twitter": {
            "detail": "Refresh completed",
            "errors": {"exceptions": [], "total": 0},
            "processed": 0,
        },
        "telegram": {
            "detail": "Refresh completed",
            "errors": {"exceptions": [], "total": 0},
            "processed": 0,
        },
    }

    # first refresh
    response = apiclient.get(url, data=query, format="json")
    data = response.json()
    assert "meta" in data
    assert "sites" in data
    assert data["meta"]["overwrite"] == expected_overwrite
    assert data["sites"] == expected_response
    assert Source.objects.count() == 3

    # second refresh
    response = apiclient.get(url, data=query, format="json")
    data = response.json()
    assert data["sites"] == expected_response
    assert Source.objects.count() == 3
