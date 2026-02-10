import logging

from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.geo.schemas.auth import RegisterRequestSerializer, RegisterResponseSerializer

User = get_user_model()
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
    def create(self, request, *args, **kwargs) -> Response:
        request_serializer = self.get_serializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        created_user = User.objects.create_user(
            username=request_serializer.validated_data["username"],
            password=request_serializer.validated_data["password"],
        )
        logger.info("user_registered id=%s username=%s", created_user.id, created_user.username)

        response_payload = {"id": created_user.id, "username": created_user.username}
        response_data = RegisterResponseSerializer(response_payload).data
        return Response(data=response_data, status=201)
