import logging

from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema, inline_serializer
from rest_framework import mixins, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.geo.models.point import Point
from apps.geo.schemas.messages import MessageCreateSerializer, MessageResponseSerializer
from apps.geo.schemas.search import RadiusSearchQuerySerializer

logger = logging.getLogger("apps.geo")


class MessagesViewSet(mixins.CreateModelMixin, GenericViewSet):
    serializer_class = MessageCreateSerializer

    @extend_schema(
        tags=["points"],
        request=MessageCreateSerializer,
        responses={201: MessageResponseSerializer},
        summary="Создание сообщения к точке",
    )
    def perform_create(self, serializer: MessageCreateSerializer) -> None:
        point_id = serializer.validated_data["point_id"]
        point = Point.objects.only("id").filter(id=point_id).first()
        if point is None:
            raise NotFound(f"Point with id={point_id} not found")
        created_message = serializer.save(point=point, author=self.request.user)
        logger.info(
            "message_created id=%s point_id=%s author_id=%s text_len=%s",
            created_message.id,
            point.id,
            getattr(self.request.user, "id", None),
            len(created_message.text),
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
        request_serializer = RadiusSearchQuerySerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)

        params = request_serializer.validated_data
        logger.info(
            "messages_search lat=%s lon=%s radius_km=%s",
            params["latitude"],
            params["longitude"],
            params["radius"],
        )
        from apps.geo.models.message import Message

        queryset = Message.objects.all().within_radius(
            latitude=params["latitude"],
            longitude=params["longitude"],
            radius_km=params["radius"],
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = MessageResponseSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MessageResponseSerializer(queryset, many=True)
        return Response(serializer.data)
