import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()
logger = logging.getLogger("apps.geo")


class RegisterRequestSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=1, max_length=150)
    password = serializers.CharField(
        min_length=8,
        max_length=128,
        write_only=True,
        validators=[validate_password],
    )

    def validate_username(self, value: str) -> str:
        return value.strip()

    def validate(self, attrs: dict) -> dict:
        username = attrs["username"]
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {"username": ["Пользователь с таким username уже существует."]}
            )
        return attrs

    def create(self, validated_data: dict) -> User:
        created_user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )
        logger.info("user_registered id=%s username=%s", created_user.id, created_user.username)
        return created_user

    def to_representation(self, instance: User) -> dict:
        payload = {"id": instance.id, "username": instance.username}
        return RegisterResponseSerializer(payload).data


class RegisterResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
