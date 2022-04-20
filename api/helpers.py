import logging

from api.models import Source

logger = logging.getLogger(__name__)


def add_response_error(x: Exception, errors: list):
    """Append error to list"""
    errors.append(
        {
            "exception_class": x.__class__.__name__,
            "exception_message": str(x),
        }
    )


def bulk_insert_sources(chunk, conflict_action, errors):
    """Insert chunk of data. If fails, append exception to errors."""
    logger.info("Inserting %s records", len(chunk))
    try:
        results = Source.objects.on_conflict(
            ["external_id"], conflict_action
        ).bulk_insert(
            [{k: v for k, v in row.items if k != "locations"} for row in chunk]
        )
        locations_chunk = []

    except Exception as x:
        # log exception, do not raise
        add_response_error(x, errors)
        logger.exception("Failed inserting data.")
        for value in chunk:
            logger.debug(str(value))
    return errors
