from drf_spectacular.utils import extend_schema
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from apps.geo.schemas.auth import RegisterRequestSerializer, RegisterResponseSerializer


class RegisterAPIView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterRequestSerializer

    @extend_schema(
        tags=["auth"],
        request=RegisterRequestSerializer,
        responses={201: RegisterResponseSerializer},
        summary="Регистрация пользователя (служебный эндпоинт для тестового задания)",
    )
    pass
