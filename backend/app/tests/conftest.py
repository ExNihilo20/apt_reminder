import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.repositories.dependencies import get_contact_repository
from app.repositories.contact_repository import ContactRepository


class FakeContactRepository:
    def __init__(self):
        self._data = {}
        self._counter = 1

    def create_contact(self, contact: dict):
        # simulate unique phone constraint
        for existing in self._data.values():
            if existing["phone_number"] == contact["phone_number"]:
                raise Exception("DuplicateKeyError")

        contact_id = str(self._counter)
        self._counter += 1

        contact["_id"] = contact_id
        contact["id"] = contact_id
        self._data[contact_id] = contact
        return contact

    def get_all_contacts(self):
        return list(self._data.values())

    def get_by_id(self, contact_id: str):
        return self._data.get(contact_id)
    
    def update_contact(self, contact_id: str, updates: dict):
        if contact_id not in self._data:
            return None

        self._data[contact_id].update(updates)
        return self._data[contact_id]
    
    def update_contact(self, contact_id: str, updates: dict):
        contact = self._data.get(contact_id)
        if not contact or not contact.get("is_active", True):
            return None

        contact.update(updates)
        return contact


    def soft_delete_contact(self, contact_id: str) -> bool:
        contact = self._data.get(contact_id)
        if not contact or not contact.get("is_active", True):
            return False

        contact["is_active"] = False
        return True




@pytest.fixture
def fake_repo():
    return FakeContactRepository()

@pytest_asyncio.fixture
async def client(fake_repo):
    app.dependency_overrides[get_contact_repository] = lambda: fake_repo

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
