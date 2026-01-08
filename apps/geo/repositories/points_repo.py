from __future__ import annotations

from django.contrib.gis.geos import Point as GeoPoint
from django.contrib.gis.measure import D
from django.db.models import QuerySet

from apps.geo.models import Point


class PointsRepository:
    def create_point(self, *, title: str | None, latitude: float, longitude: float) -> Point:
        location = GeoPoint(longitude, latitude, srid=4326)
        return Point.objects.create(title=title, location=location)

    def get_point_by_id(self, *, point_id: int) -> Point | None:
        return Point.objects.filter(id=point_id).first()

    def search_points_within_radius(
        self, *, latitude: float, longitude: float, radius_km: float
    ) -> QuerySet[Point]:
        center = GeoPoint(longitude, latitude, srid=4326)
        return Point.objects.filter(location__dwithin=(center, D(km=radius_km))).order_by("id")



