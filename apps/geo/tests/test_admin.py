from uuid import uuid4


def test_admin_test_user_endpoint_requires_authentication(api_client):
    username = f"u_{uuid4().hex}"
    password = "S0mething-Longer_123"
    resp = api_client.post(
        "/api/admin/test-users/",
        data={"username": username, "password": password},
        format="json",
    )
    assert resp.status_code == 401


def test_admin_test_user_endpoint_forbids_non_admin(auth_client):
    username = f"u_{uuid4().hex}"
    password = "S0mething-Longer_123"
    resp = auth_client.post(
        "/api/admin/test-users/",
        data={"username": username, "password": password},
        format="json",
    )
    assert resp.status_code == 403


def test_admin_test_user_endpoint_creates_user(admin_client):
    username = f"u_{uuid4().hex}"
    password = "S0mething-Longer_123"
    resp = admin_client.post(
        "/api/admin/test-users/",
        data={"username": username, "password": password},
        format="json",
    )
    assert resp.status_code == 201
    assert resp.data["id"] > 0
    assert resp.data["username"] == username
