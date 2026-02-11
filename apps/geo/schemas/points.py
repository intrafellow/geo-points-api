from rest_framework import serializers

from apps.geo.models.point import Point


class PointCreateSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    latitude = serializers.FloatField(min_value=-90.0, max_value=90.0)
    longitude = serializers.FloatField(min_value=-180.0, max_value=180.0)

    def validate_title(self, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class PointSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(read_only=True)
    longitude = serializers.FloatField(read_only=True)

    class Meta:
        model = Point
        fields = ("id", "title", "latitude", "longitude", "created_at")
