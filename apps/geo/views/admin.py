import logging

from django.contrib.auth import get_user_model
from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from apps.geo.schemas.admin import TestUserCreateSerializer, TestUserResponseSerializer

User = get_user_model()
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

        request_serializer = self.get_serializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        created_user = User.objects.create_user(
            username=request_serializer.validated_data["username"],
            password=request_serializer.validated_data["password"],
        )
        logger.info("test_user_created id=%s username=%s", created_user.id, created_user.username)

        response_payload = {"id": created_user.id, "username": created_user.username}
        response_data = TestUserResponseSerializer(response_payload).data
        return Response(data=response_data, status=201)
