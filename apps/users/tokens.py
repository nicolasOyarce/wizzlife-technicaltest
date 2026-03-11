"""
Serializer JWT personalizado para usar email como campo de login
y retornar datos del usuario junto con los tokens.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .serializers import UserSerializer

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extiende TokenObtainPairSerializer para:
    1. Usar 'email' en lugar de 'username' como campo de autenticación.
    2. Incluir los datos del usuario en la respuesta.
    """

    username_field = User.USERNAME_FIELD  # 'email'

    def validate(self, attrs):
        data = super().validate(attrs)
        # Agregar info del usuario a la respuesta del token
        data["user"] = UserSerializer(self.user).data
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Claims adicionales en el token JWT
        token["email"] = user.email
        token["full_name"] = user.get_full_name()
        return token
