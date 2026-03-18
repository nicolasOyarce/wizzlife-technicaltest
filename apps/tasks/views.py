"""
Vistas de la app de tareas.

TaskViewSet implementa los 5 endpoints requeridos por la prueba:
    GET    /tasks/       — Listado con filtros, paginación y ordenamiento
    POST   /tasks/       — Crear tarea
    GET    /tasks/{id}/  — Detalle de tarea
    PATCH  /tasks/{id}/  — Actualizar tarea (parcial)
    DELETE /tasks/{id}/  — Eliminar tarea (soft delete)

CommentViewSet agrega endpoints de comentarios como valor extra:
    GET    /tasks/{task_id}/comments/      — Listar comentarios
    POST   /tasks/{task_id}/comments/      — Agregar comentario
    DELETE /tasks/{task_id}/comments/{id}/ — Eliminar comentario
"""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from .filters import TaskFilter
from .models import Comment, Task
from .permissions import IsCommentAuthor, IsTaskOwnerOrAssigned
from .serializers import (
    CommentCreateSerializer,
    CommentSerializer,
    TaskCreateSerializer,
    TaskDetailSerializer,
    TaskListSerializer,
    TaskUpdateSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=["Tasks"],
        summary="Listar tareas",
        description=(
            "Retorna el listado paginado de tareas. "
            "Soporta filtros por estado, prioridad, usuario asignado/creador y fechas. "
            "Ordenamiento disponible en: created_at, due_date, priority, status, title."
        ),
        parameters=[
            OpenApiParameter("status", OpenApiTypes.STR, description="Filtrar por estado (pending, in_progress, review, done)"),
            OpenApiParameter("priority", OpenApiTypes.STR, description="Filtrar por prioridad (low, medium, high, urgent)"),
            OpenApiParameter("assigned_to", OpenApiTypes.UUID, description="UUID del usuario asignado"),
            OpenApiParameter("created_by", OpenApiTypes.UUID, description="UUID del usuario creador"),
            OpenApiParameter("due_date__gte", OpenApiTypes.DATE, description="Fecha límite desde (YYYY-MM-DD)"),
            OpenApiParameter("due_date__lte", OpenApiTypes.DATE, description="Fecha límite hasta (YYYY-MM-DD)"),
            OpenApiParameter("mine", OpenApiTypes.BOOL, description="Solo mis tareas (creadas o asignadas a mí)"),
            OpenApiParameter("search", OpenApiTypes.STR, description="Búsqueda en título y descripción"),
            OpenApiParameter("ordering", OpenApiTypes.STR, description="Campo de ordenamiento (ej: -due_date, priority)"),
            OpenApiParameter("page", OpenApiTypes.INT, description="Número de página"),
            OpenApiParameter("page_size", OpenApiTypes.INT, description="Tamaño de página (max: 100)"),
        ],
    ),
    create=extend_schema(
        tags=["Tasks"],
        summary="Crear tarea",
        description="Crea una nueva tarea. El campo 'created_by' se asigna automáticamente al usuario autenticado.",
    ),
    retrieve=extend_schema(
        tags=["Tasks"],
        summary="Detalle de tarea",
        description="Retorna la información completa de una tarea, incluyendo comentarios y transiciones de estado válidas.",
    ),
    partial_update=extend_schema(
        tags=["Tasks"],
        summary="Actualizar tarea",
        description=(
            "Actualiza parcialmente una tarea. "
            "Para cambios de estado, valida que la transición sea permitida "
            "(PENDING → IN_PROGRESS → REVIEW → DONE)."
        ),
    ),
    destroy=extend_schema(
        tags=["Tasks"],
        summary="Eliminar tarea",
        description=(
            "Elimina una tarea mediante soft delete (no se borra físicamente de la BD). "
            "La tarea deja de aparecer en el listado pero puede ser restaurada."
        ),
        responses={204: OpenApiResponse(description="Tarea eliminada exitosamente.")},
    ),
)
class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para gestión de tareas.

    Todos los endpoints requieren autenticación JWT (Bearer token).
    """

    permission_classes = [permissions.IsAuthenticated]
    filterset_class = TaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "due_date", "priority", "status", "title"]
    ordering = ["-created_at"]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        return (
            Task.objects.select_related("created_by", "assigned_to")
            .prefetch_related("comments__author")
            .all()
        )

    def get_serializer_class(self):
        if self.action == "create":
            return TaskCreateSerializer
        if self.action == "partial_update":
            return TaskUpdateSerializer
        if self.action == "retrieve":
            return TaskDetailSerializer
        return TaskListSerializer

    def get_permissions(self):
        if self.action in ["partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsTaskOwnerOrAssigned()]
        return [permissions.IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        """Soft delete: marca la tarea como eliminada sin borrarla físicamente."""
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para comentarios de una tarea específica.

    Endpoints:
        GET    /tasks/{task_id}/comments/
        POST   /tasks/{task_id}/comments/
        DELETE /tasks/{task_id}/comments/{id}/
    """

    http_method_names = ["get", "post", "delete", "head", "options"]
    permission_classes = [permissions.IsAuthenticated]

    def get_task(self):
        return get_object_or_404(Task, pk=self.kwargs["task_pk"])

    def get_queryset(self):
        task = self.get_task()
        return Comment.objects.filter(task=task).select_related("author")

    def get_serializer_class(self):
        if self.action == "create":
            return CommentCreateSerializer
        return CommentSerializer

    def get_permissions(self):
        if self.action == "destroy":
            return [permissions.IsAuthenticated(), IsCommentAuthor()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        task = self.get_task()
        serializer.save(author=self.request.user, task=task)

    @extend_schema(tags=["Comments"], summary="Listar comentarios de una tarea")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=["Comments"], summary="Agregar comentario a una tarea")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(tags=["Comments"], summary="Eliminar comentario")
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
