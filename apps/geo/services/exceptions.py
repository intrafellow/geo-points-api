from __future__ import annotations


class GeoServiceError(Exception):
    """Базовое доменное исключение сервисного слоя."""


class PointNotFoundError(GeoServiceError):
    def __init__(self, *, point_id: int) -> None:
        super().__init__(f"Point not found: {point_id}")
        self.point_id = point_id


class UsernameAlreadyExistsError(GeoServiceError):
    def __init__(self, *, username: str) -> None:
        super().__init__(f"Username already exists: {username}")
        self.username = username
