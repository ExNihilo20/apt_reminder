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

@pytest.mark.asyncio
async def test_duplicate_phone_returns_409(client):
    # create a new payload
    payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "phone_number": "5559990000",
        "email_address": "jane@example.com"
    }

    # first create succeeds
    res1 = await client.post("/contacts", json=payload)
    assert res1.status_code == 201

    # second create with same phone fails
    res2 = await client.post("/contacts", json=payload)
    assert res2.status_code == 409

@pytest.mark.asyncio
async def test_get_contacts_returns_list(client):
    """
    Tests the following:
    - return is in list format
    - return is 
    
    :param client: the pytest client object
    :return: None
    :rtype: Any
    """
    payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "phone_number": "5551112222",
        "email": "alice@example.com",
    }

    await client.post("/contacts", json=payload)

    response = await client.get("/contacts")
    assert response.status_code == 200

    contacts = response.json()
    assert isinstance(contacts, list)
    assert contacts[0]["firstname"] == "Alice"


@pytest.mark.asyncio
async def test_get_contact_not_found(client):
    """
    Malformed URL should return a 404
    
    :param client: the pytest client object
    """
    response = await client.get("/contacts/does-not-exist")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_contact(client):
    payload = {
        "firstname": "Bob",
        "lastname": "Jones",
        "phone_number": "5553334444",
        "email": "bob@example.com",
    }

    create_res = await client.post("/contacts", json=payload)
    contact_id = create_res.json()["id"]

    update_payload = {
        "firstname": "Robert",
        "lastname": "Jones",
        "phone_number": "5553334444",
        "email": "robert@example.com",
    }

    update_res = await client.put(f"/contacts/{contact_id}", json=update_payload)
    assert update_res.status_code == 200

    updated = update_res.json()
    assert updated["firstname"] == "Robert"
    assert updated["email_address"] == "robert@example.com"

@pytest.mark.asyncio
async def test_soft_delete_contact(client):
    payload = {
        "firstname": "Tom",
        "lastname": "Hardy",
        "phone_number": "5557778888",
        "email": "tom@example.com",
    }

    res = await client.post("/contacts", json=payload)
    contact_id = res.json()["id"]

    delete_res = await client.delete(f"/contacts/{contact_id}")
    assert delete_res.status_code == 204

    # should now be gone
    get_res = await client.get(f"/contacts/{contact_id}")
    assert get_res.status_code == 404

@pytest.mark.asyncio
async def test_update_contact(client):
    payload = {
        "firstname": "Bob",
        "lastname": "Jones",
        "phone_number": "5553334444",
        "email": "bob@example.com",
    }

    create_res = await client.post("/contacts", json=payload)
    assert create_res.status_code == 201

    contact_id = create_res.json()["id"]

    update_payload = {
        "firstname": "Robert",
        "lastname": "Jones",
        "phone_number": "5553334444",
        "email": "robert@example.com",
    }

    update_res = await client.put(f"/contacts/{contact_id}", json=update_payload)
    assert update_res.status_code == 200

    updated = update_res.json()
    assert updated["firstname"] == "Robert"
    assert updated["email_address"] == "robert@example.com"

@pytest.mark.asyncio
async def test_soft_delete_contact(client):
    payload = {
        "firstname": "Tom",
        "lastname": "Hardy",
        "phone_number": "5557778888",
        "email": "tom@example.com",
    }

    res = await client.post("/contacts", json=payload)
    contact_id = res.json()["id"]

    delete_res = await client.delete(f"/contacts/{contact_id}")
    assert delete_res.status_code == 204

    # Should now be hidden
    get_res = await client.get(f"/contacts/{contact_id}")
    assert get_res.status_code == 404
