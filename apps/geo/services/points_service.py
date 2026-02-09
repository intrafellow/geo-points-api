from __future__ import annotations

import logging

from apps.geo.models.point import Point
from apps.geo.repositories.points_repo import PointsRepository

logger = logging.getLogger("apps.geo")


class PointsService:
    def __init__(self, points_repo: PointsRepository | None = None) -> None:
        self._points_repo = points_repo or PointsRepository()

    def create_point(self, *, title: str | None, latitude: float, longitude: float) -> Point:
        normalized_title = self._normalize_title(title)
        created_point = self._points_repo.create_point(
            title=normalized_title, latitude=latitude, longitude=longitude
        )
        logger.info(
            "point_created id=%s lat=%s lon=%s has_title=%s",
            created_point.id,
            latitude,
            longitude,
            bool(normalized_title),
        )
        return created_point

    @staticmethod
    def _normalize_title(title: str | None) -> str | None:
        if title is None:
            return None
        stripped = title.strip()
        return stripped or None
