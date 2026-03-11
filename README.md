# Wizz Life — Task Manager API

API RESTful para gestión de tareas de equipo, desarrollada como prueba técnica fullstack junior de Wizz Life.

> **Stack:** Django 5.1 · Django REST Framework 3.15 · PostgreSQL 16 · JWT · Docker · Render

---

## Navegación

| Documento | Contenido |
|-----------|-----------|
| [⭐ Valor extra](docs/VALOR_EXTRA.md) | 16 funcionalidades adicionales implementadas más allá del mínimo |
| [🚀 Instalación local](docs/INSTALACION.md) | Prerequisitos, pasos, variables de entorno, datos de ejemplo |
| [🐳 Docker](docs/DOCKER.md) | docker-compose, imagen standalone, variables para contenedores |
| [🧪 Tests](docs/TESTS.md) | Comandos pytest, estructura de tests, cobertura |
| [☁️ Deploy en Render](docs/DEPLOY.md) | Blueprint automático y configuración manual |
| [🏗️ Arquitectura](docs/ARQUITECTURA.md) | Modelo ER, estructura de carpetas, decisiones técnicas |
| [📋 Endpoints (referencia completa)](ENDPOINTS.md) | Body, auth, respuestas y errores de cada endpoint |

---

## Inicio rápido

```bash
# 1. Clonar
git clone https://github.com/tu-usuario/wizzlife-technicaltest.git
cd wizzlife-technicaltest

# 2. Levantar DB con Docker
docker-compose up db -d

# 3. Entorno virtual e instalar dependencias
python -m venv .venv
.\.venv\Scripts\Activate.ps1         # Windows
# source .venv/bin/activate          # Linux/Mac
pip install -r requirements/local.txt

# 4. Configurar .env
cp .env.example .env

# 5. Migraciones y datos de ejemplo
python manage.py migrate
python manage.py seed_data

# 6. Servidor
python manage.py runserver
```

Accesos:

| URL | Descripción |
|-----|-------------|
| `http://localhost:8000/api/docs/` | Swagger UI interactivo |
| `http://localhost:8000/api/redoc/` | ReDoc |
| `http://localhost:8000/admin/` | Admin Django |

---

## Credenciales de demo

| Email | Password | Rol |
|-------|----------|-----|
| `admin@wizzlife.com` | `Admin12345!` | Superusuario |
| `alice@wizzlife.com` | `Demo12345!` | Usuario demo |
| `bob@wizzlife.com` | `Demo12345!` | Usuario demo |
| `carol@wizzlife.com` | `Demo12345!` | Usuario demo |
| `david@wizzlife.com` | `Demo12345!` | Usuario demo |

---

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Framework | Django 5.1 + Django REST Framework 3.15 |
| Autenticación | JWT con `djangorestframework-simplejwt` |
| Base de datos | PostgreSQL 16 |
| Documentación | drf-spectacular (Swagger UI + ReDoc) |
| Tests | pytest + factory-boy + pytest-cov |
| Rate limiting | DRF Throttling |
| Contenedores | Docker + docker-compose |
| Deploy | Render |

---

## Endpoints — resumen

Base URL: `http://localhost:8000`

### Autenticación
| Método | Ruta | Auth |
|--------|------|------|
| `POST` | `/signup/` | No |
| `POST` | `/signin/` | No |
| `POST` | `/token/refresh/` | No |
| `GET`  | `/users/me/` | Sí |

### Tareas
| Método | Ruta | Auth |
|--------|------|------|
| `GET`  | `/tasks/` | Sí |
| `POST` | `/tasks/` | Sí |
| `GET`  | `/tasks/{id}/` | Sí |
| `PATCH`| `/tasks/{id}/` | Sí |
| `DELETE`| `/tasks/{id}/` | Sí |

### Comentarios
| Método | Ruta | Auth |
|--------|------|------|
| `GET`  | `/tasks/{id}/comments/` | Sí |
| `POST` | `/tasks/{id}/comments/` | Sí |
| `DELETE` | `/tasks/{id}/comments/{id}/` | Sí |

→ [Ver referencia completa de endpoints con body, respuestas y errores](ENDPOINTS.md)

---

## Tests

```bash
# Activar virtualenv y correr tests
pytest --cov=apps --cov-report=term-missing
```

→ [Guía completa de tests](docs/TESTS.md)

---

## Deploy

El repositorio incluye `render.yaml` para deploy con un solo click en Render.

→ [Instrucciones de deploy](docs/DEPLOY.md)
