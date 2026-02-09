from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from apps.geo.schemas.points import PointResponseSerializer
from apps.geo.schemas.search import RadiusSearchQuerySerializer
from apps.geo.services.search_service import SearchService


class PointsSearchAPIView(GenericAPIView):
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
            OpenApiParameter(
                "page", OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False
            ),
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
    def get(self, request: Request) -> Response:
        request_serializer = RadiusSearchQuerySerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)

        search_params = request_serializer.validated_data
        queryset = SearchService().search_points(
            latitude=search_params["latitude"],
            longitude=search_params["longitude"],
            radius_km=search_params["radius"],
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            paginated_data = PointResponseSerializer(page, many=True).data
            return self.get_paginated_response(paginated_data)

        response_data = PointResponseSerializer(queryset, many=True).data
        return Response(data=response_data, status=200)
