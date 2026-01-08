from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema, inline_serializer
from rest_framework import serializers

from apps.geo.schemas import PointResponseSerializer, RadiusSearchQuerySerializer
from apps.geo.services import SearchService


class PointsSearchAPIView(GenericAPIView):
    @extend_schema(
        tags=["points"],
        parameters=[
            OpenApiParameter("latitude", OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY, required=True),
            OpenApiParameter("longitude", OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY, required=True),
            OpenApiParameter("radius", OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY, required=True),
            OpenApiParameter("page", OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
            OpenApiParameter("page_size", OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
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
        serializer = RadiusSearchQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        query = serializer.validated_data
        qs = SearchService().search_points(
            latitude=query["latitude"],
            longitude=query["longitude"],
            radius_km=query["radius"],
        )
        page = self.paginate_queryset(qs)
        if page is not None:
            data = PointResponseSerializer(page, many=True).data
            return self.get_paginated_response(data)

        data = PointResponseSerializer(qs, many=True).data
        return Response(data=data, status=200)



