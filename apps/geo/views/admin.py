import logging

from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from apps.geo.schemas.admin import TestUserCreateSerializer, TestUserResponseSerializer

logger = logging.getLogger("apps.geo")


class TestUsersCreateAPIView(CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = TestUserCreateSerializer

    @extend_schema(
        tags=["admin"],
        request=TestUserCreateSerializer,
        responses={201: TestUserResponseSerializer},
        summary="Создание тестового пользователя (только для dev/test)",
    )
    def create(self, request, *args, **kwargs) -> Response:
        if not settings.ENABLE_TEST_USER_ENDPOINT:
            return Response(status=404)

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer: TestUserCreateSerializer) -> None:
        created_user = serializer.save()
        logger.info("test_user_created id=%s username=%s", created_user.id, created_user.username)
