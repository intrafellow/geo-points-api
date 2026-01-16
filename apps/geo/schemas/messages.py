from rest_framework import serializers

from apps.geo.models.message import Message


class MessageCreateSerializer(serializers.Serializer):
    point_id = serializers.IntegerField(min_value=1)
    text = serializers.CharField(allow_blank=False)


class MessageResponseSerializer(serializers.ModelSerializer):
    point_id = serializers.IntegerField(read_only=True)
    author = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Message
        fields = ("id", "point_id", "text", "author", "created_at")
