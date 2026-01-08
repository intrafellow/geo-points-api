def test_admin_create_test_user_401(api_client):
    resp = api_client.post(
        "/api/admin/test-users/",
        data={"username": "t1", "password": "S0mething-Longer_123"},
        format="json",
    )
    assert resp.status_code == 401


def test_admin_create_test_user_403(auth_client):
    resp = auth_client.post(
        "/api/admin/test-users/",
        data={"username": "t1", "password": "S0mething-Longer_123"},
        format="json",
    )
    assert resp.status_code == 403


def test_admin_create_test_user_201(admin_client):
    resp = admin_client.post(
        "/api/admin/test-users/",
        data={"username": "t1", "password": "S0mething-Longer_123"},
        format="json",
    )
    assert resp.status_code == 201
    assert resp.data["id"] > 0
    assert resp.data["username"] == "t1"



