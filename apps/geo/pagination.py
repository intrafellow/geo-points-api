from rest_framework.pagination import PageNumberPagination


class StandardPageNumberPagination(PageNumberPagination):
    """
    Базовая пагинация для API.
    """

    page_size_query_param = "page_size"
    max_page_size = 200






