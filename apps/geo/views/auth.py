import logging

from drf_spectacular.utils import extend_schema
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from apps.geo.schemas.auth import RegisterRequestSerializer, RegisterResponseSerializer

logger = logging.getLogger("apps.geo")


class RegisterAPIView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterRequestSerializer

    @extend_schema(
        tags=["auth"],
        request=RegisterRequestSerializer,
        responses={201: RegisterResponseSerializer},
        summary="Регистрация пользователя (служебный эндпоинт для тестового задания)",
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer: RegisterRequestSerializer) -> None:
        created_user = serializer.save()
        logger.info("user_registered id=%s username=%s", created_user.id, created_user.username)
