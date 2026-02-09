from __future__ import annotations

import logging

from django.contrib.auth import get_user_model

from apps.geo.services.exceptions import UsernameAlreadyExistsError

User = get_user_model()
logger = logging.getLogger("apps.geo")


class AuthService:
    def register_user(self, *, username: str, password: str) -> User:
        normalized_username = self._normalize_username(username)
        if User.objects.filter(username=normalized_username).exists():
            raise UsernameAlreadyExistsError(username=normalized_username)
        created_user = User.objects.create_user(username=normalized_username, password=password)
        logger.info("user_registered id=%s username=%s", created_user.id, created_user.username)
        return created_user

    @staticmethod
    def _normalize_username(username: str) -> str:
        return username.strip()
