# Deploy en Render

← [Volver al README principal](../README.md)

---

## Opción A — Blueprint (recomendado)

El repositorio incluye `render.yaml`, que es un Blueprint de infraestructura como código. Con él puedes desplegar el servicio web **y** la base de datos PostgreSQL con un solo click.

### Pasos

1. Sube el repositorio a GitHub (debe ser público o privado con acceso de Render).

2. Entra a [dashboard.render.com](https://dashboard.render.com) y haz click en **New → Blueprint**.

3. Conecta tu repositorio de GitHub.

4. Render detectará automáticamente el archivo `render.yaml` y mostrará los servicios que va a crear:
   - `wizzlife-api` — Web Service (Django + Gunicorn)
   - `wizzlife-db` — PostgreSQL 16

5. Haz click en **Apply** y espera el build (~3-5 min).

6. Una vez desplegado, la URL del servicio aparece en el dashboard (ej: `https://wizzlife-api.onrender.com`).

---

## Opción B — Manual

Si prefieres configurarlo manualmente sin el blueprint:

### Crear la base de datos

1. **New → PostgreSQL**
2. Nombre: `wizzlife-db`
3. Plan: Free
4. Guarda el **Internal Database URL** que Render genera.

### Crear el Web Service

1. **New → Web Service**
2. Conecta tu repositorio GitHub
3. Configura:

| Campo | Valor |
|-------|-------|
| Runtime | Python 3 |
| Build Command | `./build.sh` |
| Start Command | `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT` |
| Plan | Free |

4. En **Environment Variables**, agrega:

| Variable | Valor |
|----------|-------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `DATABASE_URL` | El Internal Database URL de tu PostgreSQL |
| `SECRET_KEY` | Genera uno en [djecrety.ir](https://djecrety.ir) |
| `ALLOWED_HOSTS` | `tu-app.onrender.com` |

5. Haz click en **Create Web Service**.

---

## Variables de entorno en producción

Las siguientes variables se configuran automáticamente via `render.yaml`:

| Variable | Origen |
|----------|--------|
| `SECRET_KEY` | Auto-generada por Render |
| `DATABASE_URL` | Desde la base de datos de Render |
| `DJANGO_SETTINGS_MODULE` | Fijo: `config.settings.production` |

---

## Script `build.sh`

El archivo `build.sh` se ejecuta durante cada deploy en Render:

```bash
#!/usr/bin/env bash
set -o errexit

pip install -r requirements/production.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

---

## Notas

- El plan **Free** de Render hace spin-down después de 15 min de inactividad. La primera request tarda ~30 seg en responder (cold start). Esto es normal.
- Para evitar el cold start, considera upgrade al plan Starter.
- El `render.yaml` configura un health check en `/api/schema/` para que Render sepa que el servicio está saludable.

---

← [Volver al README principal](../README.md)
