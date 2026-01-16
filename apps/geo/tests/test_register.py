from uuid import uuid4


def test_register_creates_user(api_client, db):
    username = f"u_{uuid4().hex}"
    password = "S0mething-Longer_123"

    resp = api_client.post(
        "/api/auth/register/",
        data={"username": username, "password": password},
        format="json",
    )

    assert resp.status_code == 201
    assert resp.data["id"] > 0
    assert resp.data["username"] == username


def test_register_returns_400_for_duplicate_username(api_client, db):
    username = f"u_{uuid4().hex}"
    password = "S0mething-Longer_123"

    first = api_client.post(
        "/api/auth/register/",
        data={"username": username, "password": password},
        format="json",
    )
    assert first.status_code == 201

    second = api_client.post(
        "/api/auth/register/",
        data={"username": username, "password": password},
        format="json",
    )

    assert second.status_code == 400
