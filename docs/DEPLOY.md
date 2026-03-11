# Deploy — Producción en Render

← [Volver al README principal](../README.md)

---

## URL de producción

> **https://wizzlife-technicaltest.onrender.com**

La API está desplegada y operativa en Render. Todos los endpoints están disponibles desde esa URL base.

---

## Accesos de producción

| URL | Descripción |
|-----|-------------|
| `https://wizzlife-technicaltest.onrender.com/api/docs/` | Swagger UI interactivo |
| `https://wizzlife-technicaltest.onrender.com/api/redoc/` | ReDoc |
| `https://wizzlife-technicaltest.onrender.com/api/schema/` | Schema OpenAPI YAML |
| `https://wizzlife-technicaltest.onrender.com/admin/` | Panel de administración Django |

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

## Stack de producción

| Componente | Detalle |
|------------|---------|
| Plataforma | Render |
| Servidor WSGI | Gunicorn |
| Base de datos | PostgreSQL 16 (Render managed) |
| Settings | `config.settings.production` |
| Build | `./build.sh` (instala deps, collectstatic, migrate) |

---

## Infraestructura como código

El repositorio incluye `render.yaml` con toda la infraestructura declarada en código: el web service, la base de datos PostgreSQL, las variables de entorno y el health check. Esto permite reproducir el entorno completo con un solo click desde el dashboard de Render.

---

## Nota sobre el plan Free

El plan Free de Render hace spin-down después de 15 min de inactividad. La primera request tras el reposo puede tardar ~30 seg (cold start). Es completamente normal en este tier.

---

← [Volver al README principal](../README.md)