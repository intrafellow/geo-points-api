from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.geo.schemas import PointCreateSerializer, PointResponseSerializer
from apps.geo.services import PointsService


class PointsCreateAPIView(APIView):
    @extend_schema(
        tags=["points"],
        request=PointCreateSerializer,
        responses={201: PointResponseSerializer},
        summary="Создание точки",
    )
    def post(self, request: Request) -> Response:
        serializer = PointCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        point = PointsService().create_point(**serializer.validated_data)
        data = PointResponseSerializer(point).data
        return Response(data=data, status=201)






