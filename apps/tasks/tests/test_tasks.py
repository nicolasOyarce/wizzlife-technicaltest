"""
Tests para GET /tasks/{id}/, PATCH /tasks/{id}/, DELETE /tasks/{id}/
"""

import pytest

from apps.tasks.models import Task

from .conftest import TaskFactory

TASKS_URL = "/tasks/"


@pytest.mark.django_db
class TestRetrieveTask:
    """Tests del endpoint de detalle de tarea."""

    def test_retrieve_task_returns_200(self, auth_client, task):
        response = auth_client.get(f"{TASKS_URL}{task.id}/")
        assert response.status_code == 200

    def test_retrieve_task_returns_full_data(self, auth_client, task):
        response = auth_client.get(f"{TASKS_URL}{task.id}/")
        assert "description" in response.data
        assert "comments" in response.data
        assert "valid_next_statuses" in response.data

    def test_retrieve_task_without_auth_returns_401(self, api_client, task):
        response = api_client.get(f"{TASKS_URL}{task.id}/")
        assert response.status_code == 401

    def test_retrieve_nonexistent_task_returns_404(self, auth_client):
        response = auth_client.get(f"{TASKS_URL}00000000-0000-0000-0000-000000000000/")
        assert response.status_code == 404

    def test_retrieve_soft_deleted_task_returns_404(self, auth_client, task):
        task.soft_delete()
        response = auth_client.get(f"{TASKS_URL}{task.id}/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestUpdateTask:
    """Tests del endpoint de actualización parcial (PATCH)."""

    def test_update_task_returns_200(self, auth_client, task):
        response = auth_client.patch(f"{TASKS_URL}{task.id}/", {"title": "Nuevo título"}, format="json")
        assert response.status_code == 200

    def test_update_task_title(self, auth_client, task):
        auth_client.patch(f"{TASKS_URL}{task.id}/", {"title": "Título actualizado"}, format="json")
        task.refresh_from_db()
        assert task.title == "Título actualizado"

    def test_update_task_status_valid_transition(self, auth_client, task):
        # PENDING → IN_PROGRESS es válido
        response = auth_client.patch(
            f"{TASKS_URL}{task.id}/",
            {"status": Task.Status.IN_PROGRESS},
            format="json",
        )
        assert response.status_code == 200
        task.refresh_from_db()
        assert task.status == Task.Status.IN_PROGRESS

    def test_update_task_status_invalid_transition_returns_400(self, auth_client, task):
        # PENDING → DONE no está permitido
        response = auth_client.patch(
            f"{TASKS_URL}{task.id}/",
            {"status": Task.Status.DONE},
            format="json",
        )
        assert response.status_code == 400

    def test_update_task_without_auth_returns_401(self, api_client, task):
        response = api_client.patch(f"{TASKS_URL}{task.id}/", {"title": "x"}, format="json")
        assert response.status_code == 401

    def test_update_task_by_non_owner_returns_403(self, another_auth_client, task):
        response = another_auth_client.patch(
            f"{TASKS_URL}{task.id}/",
            {"title": "Intento no autorizado"},
            format="json",
        )
        assert response.status_code == 403

    def test_update_task_as_assigned_user_allowed(self, user, another_user, another_auth_client):
        task = TaskFactory(created_by=user, assigned_to=another_user)
        response = another_auth_client.patch(
            f"{TASKS_URL}{task.id}/",
            {"title": "Permitido porque estoy asignado"},
            format="json",
        )
        assert response.status_code == 200


@pytest.mark.django_db
class TestDeleteTask:
    """Tests del endpoint de eliminación (soft delete)."""

    def test_delete_task_returns_204(self, auth_client, task):
        response = auth_client.delete(f"{TASKS_URL}{task.id}/")
        assert response.status_code == 204

    def test_delete_task_soft_deletes(self, auth_client, task):
        auth_client.delete(f"{TASKS_URL}{task.id}/")
        task.refresh_from_db()
        assert task.is_deleted is True
        assert task.deleted_at is not None

    def test_deleted_task_not_in_list(self, auth_client, task):
        auth_client.delete(f"{TASKS_URL}{task.id}/")
        response = auth_client.get(TASKS_URL)
        ids = [t["id"] for t in response.data["results"]]
        assert str(task.id) not in ids

    def test_deleted_task_not_retrievable(self, auth_client, task):
        auth_client.delete(f"{TASKS_URL}{task.id}/")
        response = auth_client.get(f"{TASKS_URL}{task.id}/")
        assert response.status_code == 404

    def test_delete_task_without_auth_returns_401(self, api_client, task):
        response = api_client.delete(f"{TASKS_URL}{task.id}/")
        assert response.status_code == 401

    def test_delete_task_by_non_owner_returns_403(self, another_auth_client, task):
        response = another_auth_client.delete(f"{TASKS_URL}{task.id}/")
        assert response.status_code == 403

    def test_delete_nonexistent_task_returns_404(self, auth_client):
        response = auth_client.delete(f"{TASKS_URL}00000000-0000-0000-0000-000000000000/")
        assert response.status_code == 404
