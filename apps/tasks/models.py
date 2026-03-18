"""
Modelos de la app de tareas.

- Task:     Tarea principal con soft delete, prioridad y estados.
- Comment:  Comentario de un usuario sobre una tarea con soft delete.
"""

import uuid

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from core.models import SoftDeleteModel, TimeStampedModel

User = get_user_model()


class Task(SoftDeleteModel):
    """
    Tarea del sistema con soporte de soft delete.

    Campos destacados:
    - status:       Estado de avance (PENDING → IN_PROGRESS → REVIEW → DONE)
    - priority:     Prioridad de urgencia (LOW, MEDIUM, HIGH, URGENT)
    - due_date:     Fecha límite opcional
    - assigned_to:  Usuario asignado (puede ser distinto al creador)
    - created_by:   Usuario que creó la tarea (inmutable)
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        IN_PROGRESS = "in_progress", "En progreso"
        REVIEW = "review", "En revisión"
        DONE = "done", "Completada"

    class Priority(models.TextChoices):
        LOW = "low", "Baja"
        MEDIUM = "medium", "Media"
        HIGH = "high", "Alta"
        URGENT = "urgent", "Urgente"

    # Transiciones de estado válidas: {estado_actual: [estados_permitidos]}
    VALID_STATUS_TRANSITIONS = {
        Status.PENDING: [Status.IN_PROGRESS],
        Status.IN_PROGRESS: [Status.REVIEW, Status.PENDING],
        Status.REVIEW: [Status.DONE, Status.IN_PROGRESS],
        Status.DONE: [Status.IN_PROGRESS],  # Permite reabrir
    }

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Título",
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Descripción",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Estado",
        db_index=True,
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name="Prioridad",
        db_index=True,
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha límite",
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_tasks",
        verbose_name="Creado por",
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
        verbose_name="Asignado a",
    )

    class Meta:
        verbose_name = "Tarea"
        verbose_name_plural = "Tareas"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["created_by", "status"]),
            models.Index(fields=["assigned_to", "status"]),
            models.Index(fields=["due_date"]),
        ]

    def __str__(self):
        return f"[{self.get_priority_display()}] {self.title} — {self.get_status_display()}"

    @classmethod
    def allowed_transitions_from(cls, current_status: str) -> list[str]:
        return [str(status) for status in cls.VALID_STATUS_TRANSITIONS.get(current_status, [])]

    @classmethod
    def is_transition_allowed(cls, current_status: str, new_status: str) -> bool:
        if current_status == new_status:
            return True
        return new_status in cls.VALID_STATUS_TRANSITIONS.get(current_status, [])

    def can_transition_to(self, new_status: str) -> bool:
        """Verifica si la transición de estado es válida."""
        return self.is_transition_allowed(self.status, new_status)

    def save(self, *args, **kwargs):
        """Aplica reglas de transición de estado también fuera del serializer."""
        update_fields = kwargs.get("update_fields")
        should_validate_status = update_fields is None or "status" in update_fields

        if self.pk and should_validate_status:
            previous_status = (
                Task.all_objects.filter(pk=self.pk).values_list("status", flat=True).first()
            )
            if previous_status and not self.is_transition_allowed(previous_status, self.status):
                raise ValidationError(
                    {
                        "status": [
                            (
                                f"No se puede cambiar el estado de "
                                f"'{dict(Task.Status.choices).get(previous_status, previous_status)}' "
                                f"a '{self.get_status_display()}'. "
                                f"Transiciones válidas: "
                                f"{self.allowed_transitions_from(previous_status) or 'ninguna'}."
                            )
                        ]
                    }
                )

        return super().save(*args, **kwargs)


class Comment(SoftDeleteModel):
    """
    Comentario de un usuario sobre una tarea.

    Agrega una segunda relación al modelo User y soporte
    de borrado lógico para mantener trazabilidad.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Tarea",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="task_comments",
        verbose_name="Autor",
    )
    content = models.TextField(verbose_name="Contenido")

    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ["created_at"]

    def __str__(self):
        return f"Comentario de {self.author} en '{self.task.title}'"
