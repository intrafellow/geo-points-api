import logging

from django.contrib.gis.geos import Point as GeoPoint
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema, inline_serializer
from rest_framework import mixins, serializers
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.geo.filters import RadiusSearchFilterBackend
from apps.geo.mixins import PaginatedListMixin
from apps.geo.models.point import Point
from apps.geo.schemas.points import PointCreateSerializer, PointResponseSerializer

logger = logging.getLogger("apps.geo")


class PointsViewSet(PaginatedListMixin, mixins.CreateModelMixin, GenericViewSet):
    serializer_class = PointCreateSerializer
    filter_backends = [RadiusSearchFilterBackend]

    def get_queryset(self):
        return Point.objects.all()

    @extend_schema(
        tags=["points"],
        request=PointCreateSerializer,
        responses={201: PointResponseSerializer},
        summary="Создание точки",
    )
    def create(self, request: Request, *args, **kwargs) -> Response:
        request_serializer = self.get_serializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        created_point = self.perform_create(request_serializer)
        response_data = PointResponseSerializer(created_point).data
        return Response(data=response_data, status=201)

    def perform_create(self, serializer: PointCreateSerializer) -> Point:
        title = serializer.validated_data.get("title")
        latitude = serializer.validated_data["latitude"]
        longitude = serializer.validated_data["longitude"]
        location = GeoPoint(longitude, latitude, srid=4326)
        created_point = Point.objects.create(title=title, location=location)
        logger.info(
            "point_created id=%s lat=%s lon=%s has_title=%s",
            created_point.id,
            serializer.validated_data["latitude"],
            serializer.validated_data["longitude"],
            bool(created_point.title),
        )
        return created_point

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
        queryset = self.filter_queryset(self.get_queryset())
        params = getattr(request, "radius_search_params", None)

        if params:
            logger.info(
                "points_search lat=%s lon=%s radius_km=%s",
                params["latitude"],
                params["longitude"],
                params["radius"],
            )

        return self.respond_paginated(queryset, PointResponseSerializer)
