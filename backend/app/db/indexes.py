import logging
from pymongo.collection import Collection
from pymongo.errors import OperationFailure

logger = logging.getLogger(__name__)


def ensure_contact_indexes(collection: Collection) -> None:
    """
    Enforces rule that indexes exist on the contacts collection.

    Creates a unique index on the 'phone_number' field to enforce data integrity.
    This operation is idempotent — running it multiple times has no side effects,
    as MongoDB will not recreate an index if it already exists with the same specification.

    Args:
        collection (Collection): The PyMongo collection on which to create the index.

    Raises:
        OperationFailure: If the index creation fails due to a server-side error,
                         such as permission issues or conflicting index options.
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

def ensure_message_template_indexes(collection):
    collection.create_index("name", unique=True)
    collection.create_index("is_active")
    
def ensure_message_indexes(collection):
    collection.create_index("contact_id")
    collection.create_index("status")
    collection.create_index("provider_message_sid")
    collection.create_index("created_at")