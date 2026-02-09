from django.urls import path

from .admin import TestUsersCreateAPIView
from .auth import RegisterAPIView
from .messages import MessagesCreateAPIView, MessagesSearchAPIView
from .points import PointsCreateAPIView
from .search import PointsSearchAPIView

urlpatterns = [
    path("auth/register/", RegisterAPIView.as_view(), name="auth-register"),
    path("points/", PointsCreateAPIView.as_view(), name="points-create"),
    path("points/messages/", MessagesCreateAPIView.as_view(), name="messages-create"),
    path("points/search/", PointsSearchAPIView.as_view(), name="points-search"),
    path("points/messages/search/", MessagesSearchAPIView.as_view(), name="messages-search"),
    path("admin/test-users/", TestUsersCreateAPIView.as_view(), name="admin-test-users-create"),
]
