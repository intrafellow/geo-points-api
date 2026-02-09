from django.urls import path

from apps.geo.views.admin import TestUsersCreateAPIView
from apps.geo.views.auth import RegisterAPIView
from apps.geo.views.messages import MessagesViewSet
from apps.geo.views.points import PointsViewSet

urlpatterns = [
    path("auth/register/", RegisterAPIView.as_view(), name="auth-register"),
    path("points/", PointsViewSet.as_view({"post": "create"}), name="points-create"),
    path("points/search/", PointsViewSet.as_view({"get": "search"}), name="points-search"),
    path("points/messages/", MessagesViewSet.as_view({"post": "create"}), name="messages-create"),
    path(
        "points/messages/search/",
        MessagesViewSet.as_view({"get": "search"}),
        name="messages-search",
    ),
    path("admin/test-users/", TestUsersCreateAPIView.as_view(), name="admin-test-users-create"),
]
