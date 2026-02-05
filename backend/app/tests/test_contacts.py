import pytest


@pytest.mark.asyncio
async def test_create_and_get_contact(client):
    # create contact
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "phone_number": "5551234567",
        "email_address": "john@example.com",
    }

    response = await client.post("/contacts", json=payload)
    assert response.status_code == 201

    created = response.json()
    assert created["firstname"] == "John"
    assert created["phone_number"] == "5551234567"
    assert "id" in created

    contact_id = created["id"]
    

    # get contact by id
    response = await client.get(f"/contacts/{contact_id}")
    assert response.status_code == 200

    fetched = response.json()
    assert fetched["email_address"] == "john@example.com"

