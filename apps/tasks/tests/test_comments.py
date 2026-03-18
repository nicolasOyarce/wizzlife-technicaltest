"""
Tests para endpoints de comentarios anidados en tareas.
"""

import pytest

from apps.tasks.models import Comment

TASKS_URL = "/tasks/"


@pytest.mark.django_db
class TestCommentDeleteSoftDelete:
    """Tests del endpoint DELETE /tasks/{task_id}/comments/{id}/ con soft delete."""

    def test_delete_comment_returns_204(self, auth_client, task, user):
        comment = Comment.objects.create(task=task, author=user, content="Comentario")

        response = auth_client.delete(f"{TASKS_URL}{task.id}/comments/{comment.id}/")

        assert response.status_code == 204

    def test_delete_comment_soft_deletes(self, auth_client, task, user):
        comment = Comment.objects.create(task=task, author=user, content="Comentario")

        auth_client.delete(f"{TASKS_URL}{task.id}/comments/{comment.id}/")
        comment.refresh_from_db()

        assert comment.is_deleted is True
        assert comment.deleted_at is not None

    def test_deleted_comment_not_in_comment_list(self, auth_client, task, user):
        comment = Comment.objects.create(task=task, author=user, content="Comentario")

        auth_client.delete(f"{TASKS_URL}{task.id}/comments/{comment.id}/")
        response = auth_client.get(f"{TASKS_URL}{task.id}/comments/")

        ids = [item["id"] for item in response.data["results"]]
        assert str(comment.id) not in ids

    def test_deleted_comment_not_in_task_detail(self, auth_client, task, user):
        comment = Comment.objects.create(task=task, author=user, content="Comentario")

        auth_client.delete(f"{TASKS_URL}{task.id}/comments/{comment.id}/")
        response = auth_client.get(f"{TASKS_URL}{task.id}/")

        ids = [item["id"] for item in response.data["comments"]]
        assert str(comment.id) not in ids

    def test_delete_comment_without_auth_returns_401(self, api_client, task, user):
        comment = Comment.objects.create(task=task, author=user, content="Comentario")

        response = api_client.delete(f"{TASKS_URL}{task.id}/comments/{comment.id}/")

        assert response.status_code == 401

    def test_delete_comment_by_non_author_returns_403(self, another_auth_client, task, user):
        comment = Comment.objects.create(task=task, author=user, content="Comentario")

        response = another_auth_client.delete(f"{TASKS_URL}{task.id}/comments/{comment.id}/")

        assert response.status_code == 403

    def test_redelete_comment_returns_404(self, auth_client, task, user):
        comment = Comment.objects.create(task=task, author=user, content="Comentario")

        first_response = auth_client.delete(f"{TASKS_URL}{task.id}/comments/{comment.id}/")
        second_response = auth_client.delete(f"{TASKS_URL}{task.id}/comments/{comment.id}/")

        assert first_response.status_code == 204
        assert second_response.status_code == 404

    def test_comment_default_manager_excludes_soft_deleted(self, task, user):
        comment = Comment.objects.create(task=task, author=user, content="Comentario")
        comment.soft_delete()

        assert not Comment.objects.filter(id=comment.id).exists()
        assert Comment.all_objects.filter(id=comment.id).exists()
