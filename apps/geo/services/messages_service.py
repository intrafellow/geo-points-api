from __future__ import annotations

from django.contrib.auth import get_user_model

from apps.geo.models import Message, Point
from apps.geo.repositories import MessagesRepository, PointsRepository
from apps.geo.services.exceptions import PointNotFoundError

User = get_user_model()


class MessagesService:
    def __init__(
        self,
        *,
        messages_repo: MessagesRepository | None = None,
        points_repo: PointsRepository | None = None,
    ) -> None:
        self._messages_repo = messages_repo or MessagesRepository()
        self._points_repo = points_repo or PointsRepository()

    def create_message(self, *, point_id: int, author: User, text: str) -> Message:
        point = self._get_point(point_id)
        normalized_text = self._normalize_text(text)
        return self._messages_repo.create_message(point=point, author=author, text=normalized_text)

    def _get_point(self, point_id: int) -> Point:
        point = self._points_repo.get_point_by_id(point_id=point_id)
        if point is None:
            raise PointNotFoundError(point_id=point_id)
        return point

    @staticmethod
    def _normalize_text(text: str) -> str:
        return text.strip()



