import logging

from django.conf import settings
from rest_framework import serializers

logger = logging.getLogger("apps.geo")


class RadiusSearchQuerySerializer(serializers.Serializer):
    latitude = serializers.FloatField(min_value=-90.0, max_value=90.0)
    longitude = serializers.FloatField(min_value=-180.0, max_value=180.0)
    radius = serializers.FloatField(min_value=0.0)

    def validate_radius(self, value: float) -> float:
        max_radius = getattr(settings, "MAX_SEARCH_RADIUS_KM", None)
        if max_radius is None:
            return value

        if value > max_radius:
            logger.warning("radius_limit_exceeded radius_km=%s max_radius_km=%s", value, max_radius)
            raise serializers.ValidationError(f"radius не должен превышать {float(max_radius)} км.")

        return value
