import os

from django.conf import settings
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.geo.schemas import TestUserCreateSerializer, TestUserResponseSerializer
from apps.geo.services import AdminService
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
        if not settings.DEBUG and "PYTEST_CURRENT_TEST" not in os.environ:
            return Response(status=404)

        serializer = TestUserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = AdminService().create_test_user(**serializer.validated_data)
        except UsernameAlreadyExistsError:
            raise ValidationError({"username": ["Пользователь с таким username уже существует."]})

        data = TestUserResponseSerializer({"id": user.id, "username": user.username}).data
        return Response(data=data, status=201)



