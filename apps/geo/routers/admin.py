from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.geo.schemas.admin import TestUserCreateSerializer, TestUserResponseSerializer
from apps.geo.services.admin_service import AdminService
from apps.geo.services.exceptions import UsernameAlreadyExistsError


class TestUsersCreateAPIView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=["admin"],
        request=TestUserCreateSerializer,
        responses={201: TestUserResponseSerializer},
        summary="Создание тестового пользователя (только для dev/test)",
    )
    def post(self, request: Request) -> Response:
        if not settings.ENABLE_TEST_USER_ENDPOINT:
            return Response(status=404)

        request_serializer = TestUserCreateSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        try:
            payload = request_serializer.validated_data
            created_user = AdminService().create_test_user(**payload)
        except UsernameAlreadyExistsError as exc:
            raise ValidationError(
                {"username": ["Пользователь с таким username уже существует."]}
            ) from exc

        response_payload = {"id": created_user.id, "username": created_user.username}
        response_data = TestUserResponseSerializer(response_payload).data
        return Response(data=response_data, status=201)
