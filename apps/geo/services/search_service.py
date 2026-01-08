from __future__ import annotations

from django.db.models import QuerySet

from apps.geo.models import Message, Point
from apps.geo.repositories import MessagesRepository, PointsRepository


class SearchService:
    def __init__(
        self,
        *,
        points_repo: PointsRepository | None = None,
        messages_repo: MessagesRepository | None = None,
    ) -> None:
        self._points_repo = points_repo or PointsRepository()
        self._messages_repo = messages_repo or MessagesRepository()

    def search_points(
        self, *, latitude: float, longitude: float, radius_km: float
    ) -> QuerySet[Point]:
        return self._points_repo.search_points_within_radius(
            latitude=latitude, longitude=longitude, radius_km=radius_km
        )

    def search_messages(
        self, *, latitude: float, longitude: float, radius_km: float
    ) -> QuerySet[Message]:
        return self._messages_repo.search_messages_within_radius(
            latitude=latitude, longitude=longitude, radius_km=radius_km
        )



