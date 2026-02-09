from rest_framework import serializers

from apps.geo.models.message import Message


class MessageCreateSerializer(serializers.Serializer):
    point_id = serializers.IntegerField(min_value=1)
    text = serializers.CharField(allow_blank=False)

    def validate_text(self, value: str) -> str:
        return value.strip()

    def create(self, validated_data: dict) -> Message:
        validated_data.pop("point_id", None)
        return Message.objects.create(**validated_data)

    def to_representation(self, instance: Message) -> dict:
        return MessageResponseSerializer(instance).data


class MessageResponseSerializer(serializers.ModelSerializer):
    point_id = serializers.IntegerField(read_only=True)
    author = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Message
        fields = ("id", "point_id", "text", "author", "created_at")
