"""
URLs de la app de tareas.

Rutas exactas según especificación de la prueba técnica:
    GET    /tasks/
    POST   /tasks/
    GET    /tasks/{id}/
    PATCH  /tasks/{id}/
    DELETE /tasks/{id}/

Rutas extra (valor adicional):
    GET    /tasks/{task_id}/comments/
    POST   /tasks/{task_id}/comments/
    DELETE /tasks/{task_id}/comments/{id}/
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .views import CommentViewSet, TaskViewSet

# Router principal para /tasks/
router = DefaultRouter()
router.register("tasks", TaskViewSet, basename="task")

# Router anidado para /tasks/{task_pk}/comments/
tasks_router = NestedDefaultRouter(router, "tasks", lookup="task")
tasks_router.register("comments", CommentViewSet, basename="task-comments")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(tasks_router.urls)),
]
