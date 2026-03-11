"""
URLs de autenticación y perfil de usuario.

Rutas (especificación exacta de la prueba técnica):
    POST /signup/         — Registro
    POST /signin/         — Login (obtener tokens)
    POST /token/refresh/  — Refrescar access token
    GET  /users/me/       — Perfil del usuario autenticado
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import SignInView, SignUpView, UserMeView

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("signin/", SignInView.as_view(), name="signin"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("users/me/", UserMeView.as_view(), name="user-me"),
]
