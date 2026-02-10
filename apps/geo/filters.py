from __future__ import annotations

from typing import Any

from rest_framework.filters import BaseFilterBackend

from apps.geo.schemas.search import RadiusSearchQuerySerializer


class RadiusSearchFilterBackend(BaseFilterBackend):
    """
    Валидация query params для geo-поиска + применение `within_radius(...)`.
    """

    def filter_queryset(self, request, queryset, view):
        if getattr(view, "action", None) != "search":
            return queryset

        serializer = RadiusSearchQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        params: dict[str, Any] = serializer.validated_data
        request.radius_search_params = params

        within_radius = getattr(queryset, "within_radius", None)
        if callable(within_radius):
            return within_radius(
                latitude=params["latitude"],
                longitude=params["longitude"],
                radius_km=params["radius"],
            )
        return queryset