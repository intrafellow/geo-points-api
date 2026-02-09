from __future__ import annotations

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point as GeoPoint
from django.contrib.gis.measure import D
from django.contrib.postgres.indexes import GistIndex


class PointQuerySet(models.QuerySet["Point"]):
    def within_radius(
        self, *, latitude: float, longitude: float, radius_km: float
    ) -> PointQuerySet:
        center = GeoPoint(longitude, latitude, srid=4326)
        return (
            self.only("id", "title", "location", "created_at")
            .filter(location__dwithin=(center, D(km=radius_km)))
            .order_by("id")
        )


class Point(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    location = models.PointField(srid=4326, geography=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects: PointQuerySet = PointQuerySet.as_manager()

    class Meta:
        db_table = "geo_points"
        indexes = [GistIndex(fields=["location"])]

    @property
    def latitude(self) -> float:
        return float(self.location.y)

    @property
    def longitude(self) -> float:
        return float(self.location.x)
