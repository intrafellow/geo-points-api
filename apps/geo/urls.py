from django.urls import path
from rest_framework.routers import SimpleRouter

from apps.geo.views.admin import TestUsersCreateAPIView
from apps.geo.views.auth import RegisterAPIView
from apps.geo.views.messages import MessagesViewSet
from apps.geo.views.points import PointsViewSet

router = SimpleRouter()
router.register("points", PointsViewSet, basename="points")
router.register("points/messages", MessagesViewSet, basename="messages")

urlpatterns = [
    path("auth/register/", RegisterAPIView.as_view(), name="auth-register"),
    path("admin/test-users/", TestUsersCreateAPIView.as_view(), name="admin-test-users-create"),
    *router.urls,
]
