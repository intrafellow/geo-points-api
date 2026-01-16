from django.contrib.gis.geos import Point as GeoPoint

from apps.geo.models.message import Message
from apps.geo.models.point import Point


def _create_point(*, title: str, latitude: float, longitude: float) -> Point:
    location = GeoPoint(longitude, latitude, srid=4326)
    return Point.objects.create(title=title, location=location)


def test_search_points_requires_authentication(api_client):
    # Act
    resp = api_client.get("/api/points/search/?latitude=55&longitude=37&radius=1")
    # Assert
    assert resp.status_code == 401


def test_search_points_uses_radius_in_kilometers(auth_client, db):
    # 0.01 градуса широты ~ 1.11 км
    center = _create_point(title="center", latitude=55.751244, longitude=37.618423)
    near_1_1km = _create_point(title="near", latitude=55.761244, longitude=37.618423)
    far_3_3km = _create_point(title="far", latitude=55.781244, longitude=37.618423)

    resp_1km = auth_client.get(
        "/api/points/search/?latitude=55.751244&longitude=37.618423&radius=1"
    )
    assert resp_1km.status_code == 200
    ids_1km = {p["id"] for p in resp_1km.data["results"]}
    assert center.id in ids_1km
    assert near_1_1km.id not in ids_1km
    assert far_3_3km.id not in ids_1km

    resp_2km = auth_client.get(
        "/api/points/search/?latitude=55.751244&longitude=37.618423&radius=2"
    )
    assert resp_2km.status_code == 200
    ids_2km = {p["id"] for p in resp_2km.data["results"]}
    assert center.id in ids_2km
    assert near_1_1km.id in ids_2km
    assert far_3_3km.id not in ids_2km


def test_search_messages_returns_messages_linked_to_points_in_radius(auth_client, user, db):
    center = _create_point(title="center", latitude=55.751244, longitude=37.618423)
    near = _create_point(title="near", latitude=55.761244, longitude=37.618423)

    msg_center = Message.objects.create(point=center, author=user, text="c")
    Message.objects.create(point=near, author=user, text="n")

    resp = auth_client.get(
        "/api/points/messages/search/?latitude=55.751244&longitude=37.618423&radius=1"
    )
    assert resp.status_code == 200
    ids = {m["id"] for m in resp.data["results"]}
    assert msg_center.id in ids


def test_search_radius_over_limit_returns_400(auth_client, settings):
    settings.MAX_SEARCH_RADIUS_KM = 1
    resp = auth_client.get("/api/points/search/?latitude=55&longitude=37&radius=2")
    assert resp.status_code == 400
