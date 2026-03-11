"""
Tests para GET /tasks/ — Listar tareas (con filtros, paginación y ordenamiento).
"""

import pytest

from apps.tasks.models import Task

from .conftest import TaskFactory

TASKS_URL = "/tasks/"


@pytest.mark.django_db
class TestListTasks:
    """Tests del endpoint de listado de tareas."""

    def test_list_tasks_returns_200(self, auth_client):
        response = auth_client.get(TASKS_URL)
        assert response.status_code == 200

    def test_list_tasks_without_auth_returns_401(self, api_client):
        response = api_client.get(TASKS_URL)
        assert response.status_code == 401

    def test_list_tasks_returns_paginated_response(self, auth_client, user):
        TaskFactory.create_batch(3, created_by=user)
        response = auth_client.get(TASKS_URL)
        assert "pagination" in response.data
        assert "results" in response.data
        assert response.data["pagination"]["count"] >= 3

    def test_list_tasks_filter_by_status(self, auth_client, user):
        TaskFactory(created_by=user, status=Task.Status.PENDING)
        TaskFactory(created_by=user, status=Task.Status.DONE)
        response = auth_client.get(TASKS_URL, {"status": "pending"})
        assert response.status_code == 200
        for task in response.data["results"]:
            assert task["status"] == "pending"

    def test_list_tasks_filter_by_priority(self, auth_client, user):
        TaskFactory(created_by=user, priority=Task.Priority.HIGH)
        TaskFactory(created_by=user, priority=Task.Priority.LOW)
        response = auth_client.get(TASKS_URL, {"priority": "high"})
        assert response.status_code == 200
        for task in response.data["results"]:
            assert task["priority"] == "high"

    def test_list_tasks_search_by_title(self, auth_client, user):
        TaskFactory(created_by=user, title="Unique Search Term XYZ")
        TaskFactory(created_by=user, title="Other Task")
        response = auth_client.get(TASKS_URL, {"search": "Unique Search Term"})
        assert response.status_code == 200
        assert any("Unique Search Term" in t["title"] for t in response.data["results"])

    def test_list_tasks_ordering_by_created_at_desc(self, auth_client, user):
        TaskFactory.create_batch(3, created_by=user)
        response = auth_client.get(TASKS_URL, {"ordering": "-created_at"})
        assert response.status_code == 200
        dates = [t["created_at"] for t in response.data["results"]]
        assert dates == sorted(dates, reverse=True)

    def test_list_tasks_pagination_page_size(self, auth_client, user):
        TaskFactory.create_batch(15, created_by=user)
        response = auth_client.get(TASKS_URL, {"page_size": 5})
        assert response.status_code == 200
        assert len(response.data["results"]) <= 5

    def test_list_tasks_excludes_soft_deleted(self, auth_client, user):
        task = TaskFactory(created_by=user, title="To Be Deleted")
        task.soft_delete()
        response = auth_client.get(TASKS_URL)
        titles = [t["title"] for t in response.data["results"]]
        assert "To Be Deleted" not in titles

    def test_list_tasks_mine_filter(self, auth_client, user, another_user):
        TaskFactory(created_by=user, title="My Task")
        TaskFactory(created_by=another_user, title="Other's Task")
        response = auth_client.get(TASKS_URL, {"mine": "true"})
        assert response.status_code == 200
        titles = [t["title"] for t in response.data["results"]]
        assert "My Task" in titles
