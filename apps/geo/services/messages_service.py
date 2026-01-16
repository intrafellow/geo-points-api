from __future__ import annotations

import logging

from django.contrib.auth import get_user_model

from apps.geo.models.message import Message
from apps.geo.models.point import Point
from apps.geo.repositories.messages_repo import MessagesRepository
from apps.geo.repositories.points_repo import PointsRepository
from apps.geo.services.exceptions import PointNotFoundError

User = get_user_model()
logger = logging.getLogger("apps.geo")


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
        created_message = self._messages_repo.create_message(
            point=point, author=author, text=normalized_text
        )
        logger.info(
            "message_created id=%s point_id=%s author_id=%s text_len=%s",
            created_message.id,
            point.id,
            getattr(author, "id", None),
            len(normalized_text),
        )
        return created_message

    def _get_point(self, point_id: int) -> Point:
        point = self._points_repo.get_point_by_id(point_id=point_id)
        if point is None:
            raise PointNotFoundError(point_id=point_id)
        return point

    @staticmethod
    def _normalize_text(text: str) -> str:
        return text.strip()
