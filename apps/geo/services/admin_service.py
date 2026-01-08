from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from apps.geo.services.exceptions import UsernameAlreadyExistsError

User = get_user_model()


class AdminService:
    def create_test_user(self, *, username: str, password: str) -> User:
        normalized_username = self._normalize_username(username)
        if User.objects.filter(username=normalized_username).exists():
            raise UsernameAlreadyExistsError(username=normalized_username)

        validate_password(password)
        return User.objects.create_user(username=normalized_username, password=password)

    @staticmethod
    def _normalize_username(username: str) -> str:
        return username.strip()



