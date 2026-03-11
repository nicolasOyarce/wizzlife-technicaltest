"""
Configuración global de pytest.
"""

import pytest
from django.core.cache import cache


@pytest.fixture(scope="session")
def django_db_setup():
    """Usar la DB de test configurada en settings."""
    pass


@pytest.fixture(autouse=True)
def clear_throttle_cache():
    """Limpia la caché de throttling antes de cada test para evitar 429 falsos."""
    cache.clear()
    yield
    cache.clear()
