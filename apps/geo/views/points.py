import logging

from django.contrib.gis.geos import Point as GeoPoint
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.geo.filters import PointsRadiusSearchFilterSet
from apps.geo.models.point import Point
from apps.geo.schemas.points import PointCreateSerializer, PointSerializer

logger = logging.getLogger("apps.geo")


class PointsViewSet(mixins.CreateModelMixin, GenericViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_class = PointsRadiusSearchFilterSet

    def get_serializer_class(self):
        if self.action == "search":
            return PointSerializer
        return PointCreateSerializer

    def get_queryset(self):
        return Point.objects.all()

    @extend_schema(
        tags=["points"],
        request=PointCreateSerializer,
        responses={201: PointSerializer},
        summary="Создание точки",
    )
    def create(self, request: Request, *args, **kwargs) -> Response:
        request_serializer = self.get_serializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        created_point = self.perform_create(request_serializer)
        response_data = PointSerializer(created_point).data
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
        summary="Поиск точек в радиусе",
        filters=True,
    )
    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
