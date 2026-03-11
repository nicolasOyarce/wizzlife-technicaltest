"""
Filtros para el endpoint de listado de tareas.

Permite filtrar por status, priority, usuario asignado,
usuario creador y rango de fechas.
"""

import django_filters
from django.db import models

from .models import Task


class TaskFilter(django_filters.FilterSet):
    """
    Filtros disponibles en GET /tasks/.

    Parámetros de query:
        - status              : exact (ej: ?status=pending)
        - status__in          : múltiples valores (ej: ?status__in=pending,in_progress)
        - priority            : exact (ej: ?priority=high)
        - assigned_to         : UUID del usuario asignado
        - created_by          : UUID del usuario creador
        - due_date__gte       : fecha límite desde (YYYY-MM-DD)
        - due_date__lte       : fecha límite hasta (YYYY-MM-DD)
        - created_at__gte     : creada desde (YYYY-MM-DD)
        - created_at__lte     : creada hasta (YYYY-MM-DD)
        - search              : búsqueda en título y descripción (via SearchFilter)
    """

    status = django_filters.ChoiceFilter(choices=Task.Status.choices)
    status__in = django_filters.BaseInFilter(field_name="status", lookup_expr="in")
    priority = django_filters.ChoiceFilter(choices=Task.Priority.choices)
    assigned_to = django_filters.UUIDFilter(field_name="assigned_to__id")
    created_by = django_filters.UUIDFilter(field_name="created_by__id")
    due_date__gte = django_filters.DateFilter(field_name="due_date", lookup_expr="gte")
    due_date__lte = django_filters.DateFilter(field_name="due_date", lookup_expr="lte")
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    # Filtro booleano para ver solo tareas asignadas a mí
    mine = django_filters.BooleanFilter(method="filter_mine", label="Solo mis tareas")

    class Meta:
        model = Task
        fields = [
            "status",
            "priority",
            "assigned_to",
            "created_by",
        ]

    def filter_mine(self, queryset, name, value):
        """Filtra tareas creadas por o asignadas al usuario autenticado."""
        if value:
            user = self.request.user
            return queryset.filter(
                models.Q(created_by=user) | models.Q(assigned_to=user)
            )
        return queryset
