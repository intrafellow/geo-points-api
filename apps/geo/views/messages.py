import logging

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.geo.filters import MessagesRadiusSearchFilterSet
from apps.geo.models.message import Message
from apps.geo.models.point import Point
from apps.geo.schemas.messages import MessageCreateSerializer, MessageSerializer

logger = logging.getLogger("apps.geo")


class MessagesViewSet(mixins.CreateModelMixin, GenericViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessagesRadiusSearchFilterSet

    def get_serializer_class(self):
        if self.action == "search":
            return MessageSerializer
        return MessageCreateSerializer

    def get_queryset(self):
        return Message.objects.all()

    @extend_schema(
        tags=["points"],
        request=MessageCreateSerializer,
        responses={201: MessageSerializer},
        summary="Создание сообщения к точке",
    )
    def create(self, request: Request, *args, **kwargs) -> Response:
        request_serializer = self.get_serializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        created_message = self.perform_create(request_serializer)
        response_data = MessageSerializer(created_message).data
        return Response(data=response_data, status=201)

    def perform_create(self, serializer: MessageCreateSerializer):
        point_id = serializer.validated_data["point_id"]
        point = Point.objects.only("id").filter(id=point_id).first()
        if point is None:
            raise NotFound(f"Point with id={point_id} not found")
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
        summary="Поиск сообщений в радиусе",
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
