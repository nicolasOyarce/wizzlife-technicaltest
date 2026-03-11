"""
Serializers para la app de tareas.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.users.serializers import UserSerializer

from .models import Comment, Task

User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    """Serializer para comentarios de tareas."""

    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "author", "content", "created_at", "updated_at"]
        read_only_fields = ["id", "author", "created_at", "updated_at"]


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear comentarios."""

    class Meta:
        model = Comment
        fields = ["id", "content", "created_at"]
        read_only_fields = ["id", "created_at"]


class TaskListSerializer(serializers.ModelSerializer):
    """
    Vista resumida de una tarea para el listado.
    Incluye los campos más relevantes sin la descripción completa.
    """

    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "status",
            "status_display",
            "priority",
            "priority_display",
            "due_date",
            "created_by",
            "assigned_to",
            "comments_count",
            "created_at",
            "updated_at",
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()


class TaskDetailSerializer(serializers.ModelSerializer):
    """Vista completa de una tarea individual (detalle)."""

    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    valid_next_statuses = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "status_display",
            "priority",
            "priority_display",
            "due_date",
            "created_by",
            "assigned_to",
            "valid_next_statuses",
            "comments",
            "created_at",
            "updated_at",
        ]

    def get_valid_next_statuses(self, obj):
        """Retorna los estados a los que se puede transicionar desde el estado actual."""
        return Task.VALID_STATUS_TRANSITIONS.get(obj.status, [])


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear nuevas tareas."""

    assigned_to_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        write_only=True,
        help_text="UUID del usuario a asignar (opcional).",
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "assigned_to_id",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_assigned_to_id(self, value):
        if value is None:
            return value
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("El usuario asignado no existe.")
        return value

    def create(self, validated_data):
        assigned_to_id = validated_data.pop("assigned_to_id", None)
        user = self.context["request"].user
        task = Task.objects.create(
            created_by=user,
            assigned_to_id=assigned_to_id,
            **validated_data,
        )
        return task

    def to_representation(self, instance):
        """Retornar la representación detallada tras la creación."""
        return TaskDetailSerializer(instance, context=self.context).data


class TaskUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualización parcial de tareas (PATCH).

    Valida transiciones de estado y permite actualizar
    cualquier campo de la tarea.
    """

    assigned_to_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        write_only=True,
        help_text="UUID del usuario a asignar (null para desasignar).",
    )

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "assigned_to_id",
        ]

    def validate_assigned_to_id(self, value):
        if value is None:
            return value
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("El usuario asignado no existe.")
        return value

    def validate_status(self, new_status):
        """Valida que la transición de estado sea permitida."""
        instance = self.instance
        if instance and instance.status != new_status:
            if not instance.can_transition_to(new_status):
                allowed = Task.VALID_STATUS_TRANSITIONS.get(instance.status, [])
                raise serializers.ValidationError(
                    f"No se puede cambiar el estado de '{instance.get_status_display()}' "
                    f"a '{dict(Task.Status.choices).get(new_status, new_status)}'. "
                    f"Transiciones válidas: {allowed or 'ninguna'}."
                )
        return new_status

    def update(self, instance, validated_data):
        assigned_to_id = validated_data.pop("assigned_to_id", ...)
        if assigned_to_id is not ...:
            instance.assigned_to_id = assigned_to_id
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        return TaskDetailSerializer(instance, context=self.context).data
