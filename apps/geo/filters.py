from __future__ import annotations

import logging
from typing import Any

from django import forms
from django.conf import settings
from django.core.validators import MaxValueValidator
from django_filters import rest_framework as filters

from apps.geo.models.message import Message
from apps.geo.models.point import Point

logger = logging.getLogger("apps.geo")


def as_float(value: Any) -> float:
    return float(value)


class FloatNumberFilter(filters.NumberFilter):
    field_class = forms.FloatField


def make_required_float_filter(
    *,
    help_text: str,
    min_value: float | None = None,
    max_value: float | None = None,
) -> FloatNumberFilter:
    return FloatNumberFilter(
        required=True,
        method="noop",
        min_value=min_value,
        max_value=max_value,
        help_text=help_text,
    )


def latitude_filter() -> FloatNumberFilter:
    return make_required_float_filter(
        min_value=-90.0,
        max_value=90.0,
        help_text="Широта центра (от -90 до 90).",
    )


def longitude_filter() -> FloatNumberFilter:
    return make_required_float_filter(
        min_value=-180.0,
        max_value=180.0,
        help_text="Долгота центра (от -180 до 180).",
    )


def radius_filter() -> FloatNumberFilter:
    return make_required_float_filter(
        min_value=0.0,
        help_text="Радиус поиска (км).",
    )


class RadiusSearchBaseFilterSet(filters.FilterSet):
    log_prefix: str = "radius"

    latitude = latitude_filter()
    longitude = longitude_filter()
    radius = radius_filter()

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)

        max_radius = getattr(settings, "MAX_SEARCH_RADIUS_KM", None)
        if max_radius is not None:
            max_radius_f = as_float(max_radius)
            field = self.form.fields["radius"]

            field.max_value = max_radius_f
            field.validators = [v for v in field.validators if not isinstance(v, MaxValueValidator)]
            field.validators.append(MaxValueValidator(max_radius_f))
            field.error_messages["max_value"] = f"radius не должен превышать {max_radius_f} км."

    def noop(self, queryset, name, value):
        return queryset

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        lat = as_float(self.form.cleaned_data["latitude"])
        lon = as_float(self.form.cleaned_data["longitude"])
        radius_km = as_float(self.form.cleaned_data["radius"])

        logger.info("%s_search lat=%s lon=%s radius_km=%s", self.log_prefix, lat, lon, radius_km)

        within_radius = getattr(queryset, "within_radius", None)
        if callable(within_radius):
            return within_radius(latitude=lat, longitude=lon, radius_km=radius_km)
        return queryset


class PointsRadiusSearchFilterSet(RadiusSearchBaseFilterSet):
    log_prefix = "points"

    class Meta:
        model = Point
        fields: list[str] = []


class MessagesRadiusSearchFilterSet(RadiusSearchBaseFilterSet):
    log_prefix = "messages"

    class Meta:
        model = Message
        fields: list[str] = []
