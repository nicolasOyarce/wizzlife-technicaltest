"""
Factories y fixtures para los tests de usuarios.
"""

import factory
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory para crear usuarios de test."""

    class Meta:
        model = User
        skip_postgeneration_save = False

    email = factory.Sequence(lambda n: f"user{n}@test.com")
    username = factory.Sequence(lambda n: f"user{n}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.PostGenerationMethodCall("set_password", "TestPassword123!")
    is_active = True


@pytest.fixture
def user_factory():
    return UserFactory


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def another_user(db):
    return UserFactory()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(user):
    """Cliente API autenticado con JWT para el usuario dado."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def another_auth_client(another_user):
    """Cliente API autenticado para el segundo usuario."""
    client = APIClient()
    refresh = RefreshToken.for_user(another_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client
