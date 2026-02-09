from __future__ import annotations

from django.conf import settings
from django.contrib.gis.geos import Point as GeoPoint
from django.contrib.gis.measure import D
from django.db import models

from .point import Point


class MessageQuerySet(models.QuerySet["Message"]):
    def within_radius(
        self, *, latitude: float, longitude: float, radius_km: float
    ) -> MessageQuerySet:
        center = GeoPoint(longitude, latitude, srid=4326)
        return (
            self.select_related("author")
            .only("id", "point_id", "author_id", "text", "created_at", "author__username")
            .filter(point__location__dwithin=(center, D(km=radius_km)))
            .order_by("id")
        )


class Message(models.Model):
    point = models.ForeignKey(Point, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="geo_messages"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects: MessageQuerySet = MessageQuerySet.as_manager()

    class Meta:
        db_table = "geo_messages"
        indexes = [models.Index(fields=["point", "created_at"])]
