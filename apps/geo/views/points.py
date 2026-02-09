import logging

from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema, inline_serializer
from rest_framework import mixins, serializers
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.geo.models.point import Point
from apps.geo.schemas.points import PointCreateSerializer, PointResponseSerializer
from apps.geo.schemas.search import RadiusSearchQuerySerializer

logger = logging.getLogger("apps.geo")


class PointsViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = Point.objects.all()
    serializer_class = PointCreateSerializer

    @extend_schema(
        tags=["points"],
        request=PointCreateSerializer,
        responses={201: PointResponseSerializer},
        summary="Создание точки",
    )
    def perform_create(self, serializer: PointCreateSerializer) -> None:
        created_point = serializer.save()
        logger.info(
            "point_created id=%s lat=%s lon=%s has_title=%s",
            created_point.id,
            serializer.validated_data["latitude"],
            serializer.validated_data["longitude"],
            bool(created_point.title),
        )

    @extend_schema(
        tags=["points"],
        parameters=[
            OpenApiParameter(
                "latitude", OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY, required=True
            ),
            OpenApiParameter(
                "longitude", OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY, required=True
            ),
            OpenApiParameter(
                "radius", OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY, required=True
            ),
            OpenApiParameter("page", OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
            OpenApiParameter(
                "page_size", OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={
            200: inline_serializer(
                name="PaginatedPointResponse",
                fields={
                    "count": serializers.IntegerField(),
                    "next": serializers.URLField(allow_null=True),
                    "previous": serializers.URLField(allow_null=True),
                    "results": PointResponseSerializer(many=True),
                },
            )
        },
        summary="Поиск точек в радиусе",
    )
    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request: Request, *args, **kwargs) -> Response:
        request_serializer = RadiusSearchQuerySerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)
        params = request_serializer.validated_data

        logger.info(
            "points_search lat=%s lon=%s radius_km=%s",
            params["latitude"],
            params["longitude"],
            params["radius"],
        )
        queryset = Point.objects.within_radius(
            latitude=params["latitude"],
            longitude=params["longitude"],
            radius_km=params["radius"],
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PointResponseSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PointResponseSerializer(queryset, many=True)
        return Response(serializer.data)
