import json
import logging

from psqlextra.query import ConflictAction

from api.models import Location, Source

logger = logging.getLogger(__name__)


def add_response_error(x: Exception, errors: list):
    """Append error to list"""
    errors.append(
        {
            "exception_class": x.__class__.__name__,
            "exception_message": str(x),
        }
    )


def _normalize_location(loc_data):
    """Prepare to insert location, it should be a string representation of Point or Polygon."""
    loc_data["polygon"] = loc_data.get("polygon", None)
    loc_data["point"] = loc_data.get("point", None)
    if isinstance(loc_data["point"], dict):
        loc_data["point"] = json.dumps(loc_data["point"])
    if isinstance(loc_data["polygon"], dict):
        loc_data["polygon"] = json.dumps(loc_data["polygon"])
    return loc_data


def _source_fields(row):
    """Remove child objects from the record. They should be inserted separately"""
    return {k: v for k, v in row.items() if k not in ("locations", "translations")}


def bulk_insert_sources(chunk, conflict_action, errors):
    """Insert chunk of data. If fails, append exception to errors."""
    logger.info("Inserting %s records", len(chunk))
    source_results = []
    location_results = []
    try:
        source_results = Source.objects.on_conflict(
            ["external_id"], conflict_action
        ).bulk_insert([_source_fields(row) for row in chunk], return_model=False)
        location_data = []
        location_source_ids = []
        for i, data in enumerate(source_results):
            if chunk[i].get("locations", None):
                location_source_ids.append(data["id"])
                for loc_data in chunk[i]["locations"]:
                    loc_data["source_id"] = data["id"]
                    loc_data = _normalize_location(loc_data)
                    location_data.append(loc_data)

        # remove old locations, if any
        Location.objects.filter(source_id__in=location_source_ids).delete()

        if location_data:
            logger.info("Inserting %s location records", len(location_data))
            # bulk insert locations
            location_results = Location.objects.on_conflict(
                ["id"], ConflictAction.NOTHING
            ).bulk_insert(location_data, return_model=False)

    except Exception as x:
        # log exception, do not raise
        add_response_error(x, errors)
        logger.exception("Failed inserting data.")
        for value in chunk:
            logger.debug(str(value))

    results = {
        "sources": source_results,
        "locations": location_results,
    }
    return results, errors
