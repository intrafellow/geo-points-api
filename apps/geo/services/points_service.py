from __future__ import annotations

from apps.geo.models import Point
from apps.geo.repositories import PointsRepository


class PointsService:
    def __init__(self, points_repo: PointsRepository | None = None) -> None:
        self._points_repo = points_repo or PointsRepository()

    def create_point(self, *, title: str | None, latitude: float, longitude: float) -> Point:
        normalized_title = self._normalize_title(title)
        return self._points_repo.create_point(
            title=normalized_title, latitude=latitude, longitude=longitude
        )

    @staticmethod
    def _normalize_title(title: str | None) -> str | None:
        if title is None:
            return None
        stripped = title.strip()
        return stripped or None







