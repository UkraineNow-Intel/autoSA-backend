import pytest
from psqlextra.query import ConflictAction

from api import helpers
from api.models import Location, Source

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

LOCATION_POINT = {
    "name": "Los Angeles, CA",
    "point": {
        "type": "point",
        "coordinates": [-40.5, 30.1],
    },
}


LOCATION_POLYGON = {
    "name": "Manhattan, NY",
    "polygon": {
        "type": "polygon",
        "coordinates": [
            [
                [100.0, 0.0],
                [101.0, 0.0],
                [101.0, 1.0],
                [100.0, 1.0],
                [100.0, 0.0],
            ]
        ],
    },
}


def source_data(
    interface="web",
    origin="example.com",
    external_id="aaa",
    text="blah",
    locations=None,
):
    return dict(
        interface=interface,
        origin=origin,
        external_id=external_id,
        text=text,
        locations=locations,
    )


def test_upsert():
    """Test upsert"""
    errors = []
    sources1 = [source_data(external_id="aaa"), source_data(external_id="bbb")]

    results, errors = helpers.bulk_insert_sources(
        sources1, ConflictAction.UPDATE, errors
    )
    assert len(errors) == 0
    assert Source.objects.count() == 2
    source_results = results["sources"]
    assert [x["external_id"] for x in source_results] == ["aaa", "bbb"]
    assert [x["text"] for x in source_results] == ["blah", "blah"]

    errors = []
    sources2 = [
        source_data(external_id="aaa", text="blah blah"),
        source_data(external_id="bbb", text="blah blah"),
    ]
    results, errors = helpers.bulk_insert_sources(
        sources2, ConflictAction.UPDATE, errors
    )
    # make sure records were updated
    assert len(errors) == 0
    assert Source.objects.count() == 2
    source_results = results["sources"]
    assert [x["external_id"] for x in source_results] == ["aaa", "bbb"]
    assert [x["text"] for x in source_results] == ["blah blah", "blah blah"]


def test_insert_with_locations():
    """Test inserting with locations"""
    errors = []
    sources = [
        source_data(external_id="aaa", locations=[LOCATION_POLYGON]),
        source_data(external_id="bbb", locations=[LOCATION_POINT]),
    ]

    results, errors = helpers.bulk_insert_sources(
        sources, ConflictAction.UPDATE, errors
    )
    assert len(errors) == 0
    assert Source.objects.count() == 2
    assert Location.objects.count() == 2

    source1 = Source.objects.get(external_id="aaa")
    source2 = Source.objects.get(external_id="bbb")

    loc1 = Location.objects.get(source_id=source1.id)
    loc2 = Location.objects.get(source_id=source2.id)

    assert loc1.point is None
    assert loc1.polygon is not None

    assert loc2.point is not None
    assert loc2.polygon is None


def test_update_with_locations():
    """Test updating with locations"""
    errors = []
    sources1 = [source_data(external_id="aaa", locations=[LOCATION_POLYGON])]

    results, errors = helpers.bulk_insert_sources(
        sources1, ConflictAction.UPDATE, errors
    )
    assert len(errors) == 0
    assert Source.objects.count() == 1
    assert Location.objects.count() == 1

    source = Source.objects.get(external_id="aaa")
    loc = Location.objects.get(source_id=source.id)
    assert loc.point is None
    assert loc.polygon is not None

    sources2 = [source_data(external_id="aaa", locations=[LOCATION_POINT])]

    results, errors = helpers.bulk_insert_sources(
        sources2, ConflictAction.UPDATE, errors
    )
    assert len(errors) == 0
    assert Source.objects.count() == 1
    assert Location.objects.count() == 1

    source = Source.objects.get(external_id="aaa")
    loc = Location.objects.get(source_id=source.id)
    assert loc.point is not None
    assert loc.polygon is None
