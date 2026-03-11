# Docker

← [Volver al README principal](../README.md)

---

## Requisitos

- Docker
- Docker Compose

---

## Con docker-compose (recomendado)

docker-compose levanta automáticamente el servicio web y la base de datos PostgreSQL juntos.

```bash
# Build y arrancar todos los servicios
docker-compose up --build

# En segundo plano (modo detached)
docker-compose up --build -d

# Ver logs en tiempo real
docker-compose logs -f web

# Ejecutar migraciones manualmente (si fuera necesario)
docker-compose exec web python manage.py migrate

# Poblar con datos de ejemplo
docker-compose exec web python manage.py seed_data

# Abrir shell de Django
docker-compose exec web python manage.py shell

# Detener los servicios
docker-compose down

# Detener y eliminar volúmenes (borra la BD por completo)
docker-compose down -v
```

La API quedará disponible en `http://localhost:8000`.

---

## Solo con el Dockerfile (sin compose)

Útil para construir y probar la imagen de producción de forma aislada.

```bash
# Construir la imagen
docker build -t wizzlife-api .

# Correr el contenedor
docker run -p 8000:8000 \
  -e SECRET_KEY=cambia-esta-clave-secreta \
  -e DATABASE_URL=postgres://user:pass@host:5432/dbname \
  -e DJANGO_SETTINGS_MODULE=config.settings.production \
  wizzlife-api
```

> Asegúrate de que el `DATABASE_URL` apunte a una PostgreSQL accesible desde el contenedor.

---

## Notas sobre el Dockerfile

El Dockerfile usa **multi-stage build** con dos etapas:

| Etapa | Imagen base | Propósito |
|-------|-------------|-----------|
| `builder` | `python:3.12-slim` | Instala todas las dependencias |
| `runtime` | `python:3.12-slim` | Copia solo lo necesario, imagen final más liviana |

Características extras:
- **Usuario no-root** (`appuser`): evita escalada de privilegios si hay una vulnerabilidad en la app.
- **Health check** incluido: los orquestadores (Kubernetes, Docker Swarm) pueden detectar si el servicio está saludable.
- **Gunicorn** como servidor WSGI para producción (no el servidor de desarrollo de Django).
- **Migración automática** al arrancar el contenedor (`python manage.py migrate` en el entrypoint).

---

## Variables de entorno para Docker

| Variable | Descripción |
|----------|-------------|
| `SECRET_KEY` | Clave secreta de Django |
| `DATABASE_URL` | URL de conexión a PostgreSQL |
| `DJANGO_SETTINGS_MODULE` | Usar `config.settings.production` |
| `ALLOWED_HOSTS` | Hosts permitidos (ej: `tu-app.onrender.com`) |

---

← [Volver al README principal](../README.md)
