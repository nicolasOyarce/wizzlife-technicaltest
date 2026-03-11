"""
Permisos personalizados para la app de tareas.
"""

from rest_framework import permissions


class IsTaskOwnerOrAssigned(permissions.BasePermission):
    """
    Permiso para modificar o eliminar una tarea.

    Permite la acción si el usuario autenticado es:
    - El creador de la tarea, O
    - El usuario asignado a la tarea.

    Los superusuarios y staff siempre tienen acceso.
    """

    message = "Solo el creador o el usuario asignado pueden realizar esta acción."

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        return obj.created_by == request.user or obj.assigned_to == request.user


class IsCommentAuthor(permissions.BasePermission):
    """
    Permiso para modificar o eliminar un comentario.

    Solo el autor del comentario puede editarlo o eliminarlo.
    """

    message = "Solo el autor puede modificar o eliminar este comentario."

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
