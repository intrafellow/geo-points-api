import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture()
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture()
def user(db):
    User = get_user_model()
    return User.objects.create_user(username="user", password="pass")


@pytest.fixture()
def admin_user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="admin",
        password="admin",
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture()
def auth_client(api_client: APIClient, user) -> APIClient:
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


@pytest.fixture()
def admin_client(api_client: APIClient, admin_user) -> APIClient:
    token = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client
