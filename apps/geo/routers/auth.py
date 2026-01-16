from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.geo.schemas.auth import RegisterRequestSerializer, RegisterResponseSerializer
from apps.geo.services.auth_service import AuthService
from apps.geo.services.exceptions import UsernameAlreadyExistsError


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["auth"],
        request=RegisterRequestSerializer,
        responses={201: RegisterResponseSerializer},
        summary="Регистрация пользователя (служебный эндпоинт для тестового задания)",
    )
    def post(self, request: Request) -> Response:
        request_serializer = RegisterRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        try:
            payload = request_serializer.validated_data
            created_user = AuthService().register_user(**payload)
        except UsernameAlreadyExistsError as exc:
            raise ValidationError(
                {"username": ["Пользователь с таким username уже существует."]}
            ) from exc

        response_payload = {"id": created_user.id, "username": created_user.username}
        response_data = RegisterResponseSerializer(response_payload).data
        return Response(data=response_data, status=201)
