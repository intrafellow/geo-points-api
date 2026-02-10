from __future__ import annotations

from rest_framework.response import Response


class PaginatedListMixin:
    def respond_paginated(self, queryset, serializer_cls) -> Response:
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializer_cls(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializer_cls(queryset, many=True)
        return Response(serializer.data)

