from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema, inline_serializer
from rest_framework import serializers

from apps.geo.schemas import (
    MessageCreateSerializer,
    MessageResponseSerializer,
    RadiusSearchQuerySerializer,
)
from apps.geo.services import MessagesService, SearchService
from apps.geo.services.exceptions import PointNotFoundError


class MessagesCreateAPIView(APIView):
    @extend_schema(
        tags=["points"],
        request=MessageCreateSerializer,
        responses={201: MessageResponseSerializer},
        summary="Создание сообщения к точке",
    )
    def post(self, request: Request) -> Response:
        serializer = MessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            message = MessagesService().create_message(author=request.user, **serializer.validated_data)
        except PointNotFoundError as exc:
            raise NotFound(f"Point with id={exc.point_id} not found")

        data = MessageResponseSerializer(message).data
        return Response(data=data, status=201)


class MessagesSearchAPIView(GenericAPIView):
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
                name="PaginatedMessageResponse",
                fields={
                    "count": serializers.IntegerField(),
                    "next": serializers.URLField(allow_null=True),
                    "previous": serializers.URLField(allow_null=True),
                    "results": MessageResponseSerializer(many=True),
                },
            )
        },
        summary="Поиск сообщений в радиусе",
    )
    def get(self, request: Request) -> Response:
        serializer = RadiusSearchQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        query = serializer.validated_data
        qs = SearchService().search_messages(
            latitude=query["latitude"],
            longitude=query["longitude"],
            radius_km=query["radius"],
        )
        page = self.paginate_queryset(qs)
        if page is not None:
            data = MessageResponseSerializer(page, many=True).data
            return self.get_paginated_response(data)

        data = MessageResponseSerializer(qs, many=True).data
        return Response(data=data, status=200)



