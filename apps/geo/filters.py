from __future__ import annotations

import logging

from django import forms
from django.conf import settings
from django.core.validators import MaxValueValidator
from django_filters import rest_framework as filters

from apps.geo.models.message import Message
from apps.geo.models.point import Point

logger = logging.getLogger("apps.geo")


class _FloatNumberFilter(filters.NumberFilter):

    field_class = forms.FloatField


class _RadiusSearchBaseFilterSet(filters.FilterSet):
    log_prefix: str = "radius"

    latitude = _FloatNumberFilter(
        required=True,
        method="noop",
        min_value=-90.0,
        max_value=90.0,
        help_text="Широта центра (от -90 до 90).",
    )
    longitude = _FloatNumberFilter(
        required=True,
        method="noop",
        min_value=-180.0,
        max_value=180.0,
        help_text="Долгота центра (от -180 до 180).",
    )
    radius = _FloatNumberFilter(
        required=True,
        method="noop",
        min_value=0.0,
        help_text="Радиус поиска (км).",
    )

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)
        max_radius = getattr(settings, "MAX_SEARCH_RADIUS_KM", None)
        if max_radius is not None:
            field = self.form.fields["radius"]
            field.max_value = float(max_radius)
            field.validators = [v for v in field.validators if not isinstance(v, MaxValueValidator)]
            field.validators.append(MaxValueValidator(field.max_value))
            field.error_messages["max_value"] = (
                f"radius не должен превышать {float(max_radius)} км."
            )

    def noop(self, queryset, name, value):
        return queryset

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        lat = self.form.cleaned_data["latitude"]
        lon = self.form.cleaned_data["longitude"]
        radius_km = self.form.cleaned_data["radius"]

        logger.info(
            "%s_search lat=%s lon=%s radius_km=%s",
            self.log_prefix,
            lat,
            lon,
            radius_km,
        )

        within_radius = getattr(queryset, "within_radius", None)
        if callable(within_radius):
            return within_radius(latitude=lat, longitude=lon, radius_km=radius_km)
        return queryset


class PointsRadiusSearchFilterSet(_RadiusSearchBaseFilterSet):
    log_prefix = "points"

    class Meta:
        model = Point
        fields: list[str] = []


class MessagesRadiusSearchFilterSet(_RadiusSearchBaseFilterSet):
    log_prefix = "messages"

    class Meta:
        model = Message
        fields: list[str] = []
