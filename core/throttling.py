"""
Throttling (rate limiting) personalizado para endpoints sensibles.
"""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class SignUpRateThrottle(AnonRateThrottle):
    """
    Throttle más restrictivo para el endpoint de registro.
    Limita a 5 intentos por minuto por IP anónima.
    """

    scope = "signup"


class SignInRateThrottle(AnonRateThrottle):
    """
    Throttle para el endpoint de inicio de sesión.
    Limita a 10 intentos por minuto por IP (previene fuerza bruta).
    """

    scope = "signin"


class AuthenticatedUserThrottle(UserRateThrottle):
    """
    Throttle estándar para usuarios autenticados.
    """

    scope = "user"
