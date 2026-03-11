"""
Modelo de Usuario personalizado.

Usa email como campo principal de autenticación (USERNAME_FIELD).
Incluye UUIDs como PK para mayor seguridad.
"""

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    """
    Usuario personalizado con UUID como PK y email como identificador principal.

    Extiende AbstractUser para conservar el sistema de permisos de Django
    mientras se agrega el email como campo de login.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Correo electrónico",
        help_text="Usado para iniciar sesión.",
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name="Nombre",
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Apellido",
    )

    USERNAME_FIELD = "email"
    # username sigue siendo requerido por AbstractUser pero no se usa para login
    REQUIRED_FIELDS = ["username", "first_name"]

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_full_name()} <{self.email}>"

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.email
