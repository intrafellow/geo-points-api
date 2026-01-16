from apps.geo.models.point import Point


def test_create_point_requires_authentication(api_client):
    resp = api_client.post(
        "/api/points/",
        data={"title": "A", "latitude": 55.0, "longitude": 37.0},
        format="json",
    )
    assert resp.status_code == 401


def test_create_point_returns_400_for_invalid_latitude(auth_client):
    resp = auth_client.post(
        "/api/points/",
        data={"title": "A", "latitude": 999.0, "longitude": 37.0},
        format="json",
    )
    assert resp.status_code == 400


def test_create_point_creates_point(auth_client, db):
    resp = auth_client.post(
        "/api/points/",
        data={"title": " A ", "latitude": 55.751244, "longitude": 37.618423},
        format="json",
    )
    assert resp.status_code == 201
    assert resp.data["id"] > 0
    assert resp.data["title"] == "A"
    assert resp.data["latitude"] == 55.751244
    assert resp.data["longitude"] == 37.618423
    assert "created_at" in resp.data

    point = Point.objects.get(id=resp.data["id"])
    assert point.title == "A"
