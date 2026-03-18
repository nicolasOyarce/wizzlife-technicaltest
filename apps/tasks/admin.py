"""
Configuración del admin para los modelos de tareas.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import Comment, Task


class CommentInline(admin.TabularInline):
    """Comentarios inline dentro del detalle de una tarea."""

    model = Comment
    extra = 0
    readonly_fields = ["id", "author", "created_at"]
    fields = ["author", "content", "created_at"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin completo para tareas con filtros y búsqueda."""

    list_display = [
        "title",
        "status_badge",
        "priority_badge",
        "created_by",
        "assigned_to",
        "due_date",
        "is_deleted",
        "created_at",
    ]
    list_filter = ["status", "priority", "is_deleted", "created_at", "due_date"]
    search_fields = ["title", "description", "created_by__email", "assigned_to__email"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "created_at", "updated_at", "deleted_at"]
    raw_id_fields = ["created_by", "assigned_to"]
    inlines = [CommentInline]

    fieldsets = (
        ("Información general", {"fields": ("id", "title", "description")}),
        ("Estado y prioridad", {"fields": ("status", "priority", "due_date")}),
        ("Asignación", {"fields": ("created_by", "assigned_to")}),
        ("Soft delete", {"fields": ("is_deleted", "deleted_at"), "classes": ("collapse",)}),
        ("Fechas", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def status_badge(self, obj):
        colors = {
            "pending": "#6c757d",
            "in_progress": "#0d6efd",
            "review": "#fd7e14",
            "done": "#198754",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:10px;font-size:11px">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Estado"

    def priority_badge(self, obj):
        colors = {
            "low": "#20c997",
            "medium": "#0dcaf0",
            "high": "#ffc107",
            "urgent": "#dc3545",
        }
        color = colors.get(obj.priority, "#6c757d")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:10px;font-size:11px">{}</span>',
            color,
            obj.get_priority_display(),
        )

    priority_badge.short_description = "Prioridad"

    def get_queryset(self, request):
        """Mostrar todas las tareas en admin, incluyendo las eliminadas."""
        return Task.all_objects.all().select_related("created_by", "assigned_to")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["task", "author", "content_preview", "is_deleted", "created_at"]
    list_filter = ["created_at", "is_deleted"]
    search_fields = ["content", "author__email", "task__title"]
    readonly_fields = ["id", "created_at", "updated_at", "is_deleted", "deleted_at"]

    def get_queryset(self, request):
        """Mostrar todos los comentarios en admin, incluyendo los eliminados."""
        return Comment.all_objects.all().select_related("task", "author")

    def content_preview(self, obj):
        return obj.content[:80] + "..." if len(obj.content) > 80 else obj.content

    content_preview.short_description = "Contenido"
