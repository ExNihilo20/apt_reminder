from datetime import datetime
from pymongo.collection import Collection

class ContactRepository:
    def __init__(self, collection: Collection):
        self.collection = collection
    

    def create_contact(self, contact_data: dict) -> dict:
        contact_data["created_at"] = datetime.now()
        self.collection.insert_one(contact_data)
        return contact_data
    
    def get_all_contacts(self) ->list[dict]:
        contacts = list(
            self.collection.find(
                {},
                {"_id": 0} # exclude the Mongo internal ID
            )
        )
        return contacts