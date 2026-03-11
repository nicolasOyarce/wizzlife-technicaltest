"""
Modelos abstractos reutilizables.

- TimeStampedModel: agrega created_at / updated_at a cualquier modelo.
- SoftDeleteModel:  extiende TimeStampedModel con borrado lógico (is_deleted).
"""

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """Agrega timestamps de creación y actualización."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado el")

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet con soporte de soft delete."""

    def delete(self):
        """Soft delete en masa."""
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        """Eliminación física real."""
        return super().delete()

    def alive(self):
        """Solo registros no eliminados."""
        return self.filter(is_deleted=False)

    def dead(self):
        """Solo registros eliminados."""
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    """Manager que excluye registros eliminados por defecto."""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()


class AllObjectsManager(models.Manager):
    """Manager que incluye todos los registros, incluyendo eliminados."""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)


class SoftDeleteModel(TimeStampedModel):
    """
    Extiende TimeStampedModel con borrado lógico.

    En lugar de eliminar físicamente el registro, marca is_deleted=True.
    El manager por defecto excluye registros eliminados.
    """

    is_deleted = models.BooleanField(default=False, verbose_name="Eliminado")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Eliminado el")

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def soft_delete(self):
        """Marca el registro como eliminado sin eliminarlo físicamente."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self):
        """Restaura un registro previamente eliminado."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])

    def delete(self, using=None, keep_parents=False):
        """Override de delete para usar soft delete por defecto."""
        self.soft_delete()
