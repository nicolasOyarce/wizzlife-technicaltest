"""
Vistas de autenticación.

- SignUpView:   POST /signup/  — Registro de usuario + retorna tokens JWT
- SignInView:   POST /signin/  — Login con email/password + retorna tokens JWT
- UserMeView:   GET /users/me/ — Perfil del usuario autenticado
- TokenRefreshView: POST /token/refresh/ — Refrescar access token (simplejwt)
"""

from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from core.throttling import SignInRateThrottle, SignUpRateThrottle

from .serializers import SignInResponseSerializer, SignUpSerializer, UserSerializer
from .tokens import CustomTokenObtainPairSerializer

User = get_user_model()


@extend_schema(
    tags=["Auth"],
    summary="Registro de usuario",
    description=(
        "Crea un nuevo usuario y retorna sus tokens JWT de acceso y refresco. "
        "El usuario queda autenticado inmediatamente tras el registro."
    ),
    responses={
        201: OpenApiResponse(response=SignUpSerializer, description="Usuario creado exitosamente."),
        400: OpenApiResponse(description="Datos inválidos (email duplicado, contraseñas no coinciden, etc.)."),
    },
    examples=[
        OpenApiExample(
            "Ejemplo registro",
            value={
                "email": "john@example.com",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
            },
            request_only=True,
        )
    ],
)
class SignUpView(generics.CreateAPIView):
    """Registro de nuevos usuarios con retorno automático de tokens JWT."""

    serializer_class = SignUpSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [SignUpRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["Auth"],
    summary="Inicio de sesión",
    description=(
        "Autentica un usuario con email y contraseña. "
        "Retorna tokens JWT de acceso (60 min) y refresco (7 días), "
        "junto con la información del usuario."
    ),
    responses={
        200: OpenApiResponse(response=SignInResponseSerializer, description="Login exitoso."),
        401: OpenApiResponse(description="Credenciales incorrectas."),
    },
    examples=[
        OpenApiExample(
            "Ejemplo login",
            value={"email": "john@example.com", "password": "SecurePass123!"},
            request_only=True,
        )
    ],
)
class SignInView(TokenObtainPairView):
    """Login con email/password. Retorna access + refresh tokens y datos del usuario."""

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [SignInRateThrottle]


@extend_schema(
    tags=["Users"],
    summary="Perfil del usuario autenticado",
    description="Retorna la información del usuario actualmente autenticado.",
    responses={200: UserSerializer},
)
class UserMeView(APIView):
    """Devuelve el perfil del usuario autenticado (GET /users/me/)."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
