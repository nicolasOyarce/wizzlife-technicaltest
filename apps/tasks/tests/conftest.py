"""
Factories y fixtures para los tests de tareas.
"""

import factory
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.tasks.models import Task
from apps.users.tests.conftest import UserFactory

User = get_user_model()


class TaskFactory(factory.django.DjangoModelFactory):
    """Factory para crear tareas de test."""

    class Meta:
        model = Task

    title = factory.Sequence(lambda n: f"Test Task {n}")
    description = factory.Faker("paragraph")
    status = Task.Status.PENDING
    priority = Task.Priority.MEDIUM
    created_by = factory.SubFactory(UserFactory)
    assigned_to = None


@pytest.fixture
def task_factory():
    return TaskFactory


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def another_user(db):
    return UserFactory()


@pytest.fixture
def task(user):
    return TaskFactory(created_by=user)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(user):
    """Cliente API autenticado con JWT."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def another_auth_client(another_user):
    client = APIClient()
    refresh = RefreshToken.for_user(another_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client
