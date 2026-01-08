from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point as GeoPoint
from django.contrib.gis.measure import D
from django.db.models import QuerySet

from apps.geo.models import Message, Point

User = get_user_model()


class MessagesRepository:
    def create_message(self, *, point: Point, author: User, text: str) -> Message:
        return Message.objects.create(point=point, author=author, text=text)

    def search_messages_within_radius(
        self, *, latitude: float, longitude: float, radius_km: float
    ) -> QuerySet[Message]:
        center = GeoPoint(longitude, latitude, srid=4326)
        return (
            Message.objects.select_related("point", "author")
            .filter(point__location__dwithin=(center, D(km=radius_km)))
            .order_by("id")
        )



