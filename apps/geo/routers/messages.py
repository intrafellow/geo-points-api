from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.geo.schemas.messages import MessageCreateSerializer, MessageResponseSerializer
from apps.geo.schemas.search import RadiusSearchQuerySerializer
from apps.geo.services.exceptions import PointNotFoundError
from apps.geo.services.messages_service import MessagesService
from apps.geo.services.search_service import SearchService


class MessagesCreateAPIView(APIView):
    @extend_schema(
        tags=["points"],
        request=MessageCreateSerializer,
        responses={201: MessageResponseSerializer},
        summary="Создание сообщения к точке",
    )
    def post(self, request: Request) -> Response:
        request_serializer = MessageCreateSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        try:
            payload = request_serializer.validated_data
            created_message = MessagesService().create_message(author=request.user, **payload)
        except PointNotFoundError as exc:
            raise NotFound(f"Point with id={exc.point_id} not found") from exc

        response_data = MessageResponseSerializer(created_message).data
        return Response(data=response_data, status=201)


class MessagesSearchAPIView(GenericAPIView):
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
        request_serializer = RadiusSearchQuerySerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)

        search_params = request_serializer.validated_data
        queryset = SearchService().search_messages(
            latitude=search_params["latitude"],
            longitude=search_params["longitude"],
            radius_km=search_params["radius"],
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            paginated_data = MessageResponseSerializer(page, many=True).data
            return self.get_paginated_response(paginated_data)

        response_data = MessageResponseSerializer(queryset, many=True).data
        return Response(data=response_data, status=200)
