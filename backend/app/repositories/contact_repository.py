from datetime import datetime
from pymongo.collection import Collection

class ContactRepository:
    def __init__(self, collection: Collection):
        self.collection = collection
    

    def create_contact(self, contact_data: dict) -> dict:
        result = self.collection.insert_one(contact_data)
        return self.collection.find_one({"_id": result.inserted_id})
    
    def get_all_contacts(self) ->list[dict]:
        contacts = list(
            self.collection.find(
                {},
                {"_id": 0} # exclude the Mongo internal ID
            )
        )
        return contacts
    
    def get_by_phone_number(self, phone_number: str) -> dict | None:
        return self.collection.find_one(
            {"phone_number": phone_number},
            {"_id": 0}
        )
    
    def get_by_name(self, firstname: str, lastname:str) -> list[dict]:
        return list(
            self.collection.find(
                {
                    "firstname": firstname,
                    "lastname": lastname
                },
                {"_id": 0}
            )
        )