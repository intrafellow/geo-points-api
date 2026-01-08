from django.conf import settings
from rest_framework import serializers


class RadiusSearchQuerySerializer(serializers.Serializer):
    latitude = serializers.FloatField(min_value=-90.0, max_value=90.0)
    longitude = serializers.FloatField(min_value=-180.0, max_value=180.0)
    radius = serializers.FloatField(min_value=0.0)

    def validate_radius(self, value: float) -> float:
        max_radius_km = getattr(settings, "MAX_SEARCH_RADIUS_KM", None)
        if max_radius_km is not None and value > float(max_radius_km):
            raise serializers.ValidationError(f"radius не должен превышать {float(max_radius_km)} км.")
        return value



