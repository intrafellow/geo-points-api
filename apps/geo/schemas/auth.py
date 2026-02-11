from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegisterRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
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

    def create(self, validated_data: dict):
        return User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )


class RegisterResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
