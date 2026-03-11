"""
Tests para POST /tasks/ — Crear tarea.
"""

import pytest

from apps.tasks.models import Task

TASKS_URL = "/tasks/"


@pytest.mark.django_db
class TestCreateTask:
    """Tests del endpoint de creación de tareas."""

    def test_create_task_returns_201(self, auth_client):
        response = auth_client.post(
            TASKS_URL,
            {"title": "Nueva tarea", "description": "Descripción de prueba"},
            format="json",
        )
        assert response.status_code == 201

    def test_create_task_saves_to_db(self, auth_client):
        auth_client.post(TASKS_URL, {"title": "Tarea en DB"}, format="json")
        assert Task.objects.filter(title="Tarea en DB").exists()

    def test_create_task_assigns_created_by(self, auth_client, user):
        auth_client.post(TASKS_URL, {"title": "Tarea con autor"}, format="json")
        task = Task.objects.get(title="Tarea con autor")
        assert task.created_by == user

    def test_create_task_default_status_is_pending(self, auth_client):
        response = auth_client.post(TASKS_URL, {"title": "Tarea default"}, format="json")
        assert response.data["status"] == Task.Status.PENDING

    def test_create_task_default_priority_is_medium(self, auth_client):
        response = auth_client.post(TASKS_URL, {"title": "Tarea prioridad"}, format="json")
        assert response.data["priority"] == Task.Priority.MEDIUM

    def test_create_task_with_all_fields(self, auth_client, another_user):
        payload = {
            "title": "Tarea completa",
            "description": "Descripción completa",
            "status": Task.Status.IN_PROGRESS,
            "priority": Task.Priority.HIGH,
            "due_date": "2026-12-31",
            "assigned_to_id": str(another_user.id),
        }
        response = auth_client.post(TASKS_URL, payload, format="json")
        assert response.status_code == 201
        assert response.data["title"] == "Tarea completa"
        assert response.data["priority"] == "high"

    def test_create_task_without_auth_returns_401(self, api_client):
        response = api_client.post(TASKS_URL, {"title": "Sin auth"}, format="json")
        assert response.status_code == 401

    def test_create_task_missing_title_returns_400(self, auth_client):
        response = auth_client.post(TASKS_URL, {"description": "Sin título"}, format="json")
        assert response.status_code == 400

    def test_create_task_invalid_assigned_to_returns_400(self, auth_client):
        response = auth_client.post(
            TASKS_URL,
            {"title": "Tarea", "assigned_to_id": "00000000-0000-0000-0000-000000000000"},
            format="json",
        )
        assert response.status_code == 400
