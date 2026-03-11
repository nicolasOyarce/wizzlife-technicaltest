"""
Serializers para la app de usuarios.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Representación pública de un usuario (sin datos sensibles)."""

    class Meta:
        model = User
        fields = ["id", "email", "username", "first_name", "last_name", "created_at"]
        read_only_fields = fields


class SignUpSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de nuevos usuarios.

    Valida:
    - Email único
    - Contraseña segura (validators de Django)
    - Confirmación de contraseña coincidente
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        validators=[validate_password],
        help_text="Mínimo 8 caracteres. No puede ser solo números ni demasiado común.",
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        help_text="Repite la contraseña.",
    )
    tokens = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
            "tokens",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "tokens"]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Ya existe una cuenta con este correo electrónico.")
        return value.lower()

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está en uso.")
        return value

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Las contraseñas no coinciden."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def get_tokens(self, obj):
        """Genera tokens JWT para el usuario recién registrado."""
        refresh = RefreshToken.for_user(obj)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class SignInResponseSerializer(serializers.Serializer):
    """Serializer de respuesta del endpoint de login (solo para documentación Swagger)."""

    access = serializers.CharField(help_text="Token de acceso JWT (expira en 60 min por defecto).")
    refresh = serializers.CharField(help_text="Token de refresco JWT (expira en 7 días por defecto).")
    user = UserSerializer()
