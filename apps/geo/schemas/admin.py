from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class TestUserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=1, max_length=150)
    password = serializers.CharField(min_length=8, max_length=128, write_only=True)

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value


class TestUserResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()



