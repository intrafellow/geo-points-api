from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.geo.schemas.points import PointCreateSerializer, PointResponseSerializer
from apps.geo.services.points_service import PointsService


class PointsCreateAPIView(APIView):
    @extend_schema(
        tags=["points"],
        request=PointCreateSerializer,
        responses={201: PointResponseSerializer},
        summary="Создание точки",
    )
    def post(self, request: Request) -> Response:
        request_serializer = PointCreateSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        payload = request_serializer.validated_data
        created_point = PointsService().create_point(**payload)
        response_data = PointResponseSerializer(created_point).data
        return Response(data=response_data, status=201)
