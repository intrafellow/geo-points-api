from __future__ import annotations

import logging

from django.conf import settings
from django.db.models import QuerySet
from rest_framework.exceptions import ValidationError

from apps.geo.models.message import Message
from apps.geo.models.point import Point
from apps.geo.repositories.messages_repo import MessagesRepository
from apps.geo.repositories.points_repo import PointsRepository

logger = logging.getLogger("apps.geo")


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
        self._validate_radius(radius_km)
        logger.info("points_search lat=%s lon=%s radius_km=%s", latitude, longitude, radius_km)
        return self._points_repo.search_points_within_radius(
            latitude=latitude, longitude=longitude, radius_km=radius_km
        )

    def search_messages(
        self, *, latitude: float, longitude: float, radius_km: float
    ) -> QuerySet[Message]:
        self._validate_radius(radius_km)
        logger.info("messages_search lat=%s lon=%s radius_km=%s", latitude, longitude, radius_km)
        return self._messages_repo.search_messages_within_radius(
            latitude=latitude, longitude=longitude, radius_km=radius_km
        )

    @staticmethod
    def _validate_radius(radius_km: float) -> None:
        max_radius = getattr(settings, "MAX_SEARCH_RADIUS_KM", None)
        if max_radius is None:
            return
        if radius_km > max_radius:
            logger.warning(
                "radius_limit_exceeded radius_km=%s max_radius_km=%s", radius_km, max_radius
            )
            raise ValidationError(
                {"radius": [f"radius не должен превышать {float(max_radius)} км."]}
            )
