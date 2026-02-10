import logging

from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema, inline_serializer
from rest_framework import mixins, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.geo.filters import RadiusSearchFilterBackend
from apps.geo.mixins import PaginatedListMixin
from apps.geo.models.point import Point
from apps.geo.schemas.messages import MessageCreateSerializer, MessageResponseSerializer

logger = logging.getLogger("apps.geo")


class MessagesViewSet(PaginatedListMixin, mixins.CreateModelMixin, GenericViewSet):
    serializer_class = MessageCreateSerializer
    filter_backends = [RadiusSearchFilterBackend]

    def get_queryset(self):
        from apps.geo.models.message import Message

        return Message.objects.all()

    @extend_schema(
        tags=["points"],
        request=MessageCreateSerializer,
        responses={201: MessageResponseSerializer},
        summary="Создание сообщения к точке",
    )
    def create(self, request: Request, *args, **kwargs) -> Response:
        request_serializer = self.get_serializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        created_message = self.perform_create(request_serializer)
        response_data = MessageResponseSerializer(created_message).data
        return Response(data=response_data, status=201)

    def perform_create(self, serializer: MessageCreateSerializer):
        point_id = serializer.validated_data["point_id"]
        point = Point.objects.only("id").filter(id=point_id).first()
        if point is None:
            raise NotFound(f"Point with id={point_id} not found")
        from apps.geo.models.message import Message

        created_message = Message.objects.create(
            point=point, author=self.request.user, text=serializer.validated_data["text"]
        )
        logger.info(
            "message_created id=%s point_id=%s author_id=%s text_len=%s",
            created_message.id,
            point.id,
            getattr(self.request.user, "id", None),
            len(created_message.text),
        )
        return created_message

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
    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(self.get_queryset())
        params = getattr(request, "radius_search_params", None)
        if params:
            logger.info(
                "messages_search lat=%s lon=%s radius_km=%s",
                params["latitude"],
                params["longitude"],
                params["radius"],
            )

        return self.respond_paginated(queryset, MessageResponseSerializer)
