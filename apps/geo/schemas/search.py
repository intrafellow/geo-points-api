from rest_framework import serializers


class RadiusSearchQuerySerializer(serializers.Serializer):
    latitude = serializers.FloatField(min_value=-90.0, max_value=90.0)
    longitude = serializers.FloatField(min_value=-180.0, max_value=180.0)
    radius = serializers.FloatField(min_value=0.0)
