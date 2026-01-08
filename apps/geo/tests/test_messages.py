from django.contrib.gis.geos import Point as GeoPoint

from apps.geo.models import Message, Point


def _create_point(*, title: str, latitude: float, longitude: float) -> Point:
    location = GeoPoint(longitude, latitude, srid=4326)
    return Point.objects.create(title=title, location=location)


def test_create_message_401(api_client, db):
    point = _create_point(title="A", latitude=55.0, longitude=37.0)
    resp = api_client.post(
        "/api/points/messages/",
        data={"point_id": point.id, "text": "hello"},
        format="json",
    )
    assert resp.status_code == 401


def test_create_message_404_point_not_found(auth_client):
    resp = auth_client.post(
        "/api/points/messages/",
        data={"point_id": 999999, "text": "hello"},
        format="json",
    )
    assert resp.status_code == 404


def test_create_message_success(auth_client, user, db):
    point = _create_point(title="A", latitude=55.0, longitude=37.0)
    resp = auth_client.post(
        "/api/points/messages/",
        data={"point_id": point.id, "text": " hello "},
        format="json",
    )
    assert resp.status_code == 201
    assert resp.data["point_id"] == point.id
    assert resp.data["text"] == "hello"
    assert resp.data["author"] == user.username
    assert "created_at" in resp.data

    msg = Message.objects.get(id=resp.data["id"])
    assert msg.point_id == point.id
    assert msg.author_id == user.id
    assert msg.text == "hello"
