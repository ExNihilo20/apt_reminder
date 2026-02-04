import logging
from pymongo.collection import Collection
from pymongo.errors import OperationFailure

logger = logging.getLogger(__name__)


def ensure_contact_indexes(collection: Collection) -> None:
    """
    Be sure that required indexes exist for the contacts collection.
    This function is idempotent and safe to run on every startup.
    """
    try:
        collection.create_index(
            [("phone_number", 1)],
            unique=True,
            name="unique_phone_number"
        )
        logger.info("Ensured unique index on contacts.phone_number")
    except OperationFailure:
        logger.exception("Failed to create indexes for contacts collection")
        raise
