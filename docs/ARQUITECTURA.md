# Arquitectura del proyecto

← [Volver al README principal](../README.md)

---

## Modelo de datos (ER)

```
User (users_user)
├── id          UUID  PK
├── email       unique — USERNAME_FIELD (usado para login)
├── username    CharField
├── first_name  CharField
├── last_name   CharField
├── created_at  DateTimeField (auto)
└── updated_at  DateTimeField (auto)

Task (tasks_task)
├── id           UUID  PK
├── title        CharField(255)
├── description  TextField (opcional)
├── status       choices: pending | in_progress | review | done
├── priority     choices: low | medium | high | urgent
├── due_date     DateField (opcional)
├── created_by   FK → User  (CASCADE)
├── assigned_to  FK → User  (SET_NULL, opcional)
├── is_deleted   BooleanField — soft delete
├── deleted_at   DateTimeField (opcional)
├── created_at   DateTimeField (auto)
└── updated_at   DateTimeField (auto)

Comment (tasks_comment)
├── id        UUID  PK
├── task      FK → Task  (CASCADE)
├── author    FK → User  (CASCADE)
├── content   TextField
├── created_at DateTimeField (auto)
└── updated_at DateTimeField (auto)
```

**Relaciones:**
- Un `User` puede crear muchas `Task` (1:N via `created_by`)
- Un `User` puede tener muchas `Task` asignadas (1:N via `assigned_to`)
- Una `Task` puede tener muchos `Comment` (1:N)
- Un `User` puede escribir muchos `Comment` (1:N via `author`)

---

## Estructura de carpetas

```
wizzlife-technicaltest/
├── apps/
│   ├── users/                  # App de usuarios y autenticación
│   │   ├── models.py           # Modelo User personalizado (UUID PK, email como login)
│   │   ├── serializers.py      # SignUpSerializer, UserSerializer
│   │   ├── views.py            # SignUpView, SignInView, UserMeView
│   │   ├── tokens.py           # JWT personalizado — login con email
│   │   ├── urls.py             # /signup/ /signin/ /token/refresh/ /users/me/
│   │   ├── admin.py
│   │   └── tests/
│   │       ├── conftest.py     # UserFactory, fixtures de auth
│   │       ├── test_signup.py  # 12 tests
│   │       └── test_signin.py  # 10 tests
│   └── tasks/                  # App de tareas y comentarios
│       ├── models.py           # Task (soft delete) + Comment
│       ├── serializers.py      # List, Detail, Create, Update serializers
│       ├── views.py            # TaskViewSet + CommentViewSet
│       ├── filters.py          # Filtros con django-filter
│       ├── permissions.py      # IsTaskOwnerOrAssigned, IsCommentAuthor
│       ├── urls.py             # Router tasks + nested router comments
│       ├── admin.py            # Admin con badges de color
│       ├── management/
│       │   └── commands/
│       │       └── seed_data.py
│       └── tests/
│           ├── conftest.py     # TaskFactory, fixtures
│           ├── test_create_task.py  # 9 tests
│           └── test_tasks.py        # ~20 tests
├── config/
│   ├── settings/
│   │   ├── base.py             # Settings compartidos
│   │   ├── local.py            # Desarrollo local
│   │   └── production.py       # Producción (Render)
│   ├── urls.py                 # Rutas raíz + /api/docs/ + /api/schema/
│   ├── wsgi.py
│   └── asgi.py
├── core/
│   ├── models.py               # TimeStampedModel, SoftDeleteModel
│   ├── pagination.py           # CustomPageNumberPagination
│   └── throttling.py           # SignUpRateThrottle, SignInRateThrottle
├── requirements/
│   ├── base.txt                # Django, DRF, psycopg, simplejwt...
│   ├── local.txt               # + pytest, factory-boy, flake8
│   └── production.txt          # + dj-database-url, gunicorn
├── docs/                       # Documentación detallada
│   ├── VALOR_EXTRA.md
│   ├── INSTALACION.md
│   ├── DOCKER.md
│   ├── TESTS.md
│   ├── DEPLOY.md
│   └── ARQUITECTURA.md
├── ENDPOINTS.md                # Referencia completa de endpoints
├── Dockerfile                  # Multi-stage build
├── docker-compose.yml          # PostgreSQL + Django local
├── .dockerignore
├── render.yaml                 # Infraestructura como código
├── build.sh                    # Script de build para Render
├── setup.cfg                   # pytest + coverage + flake8 config
├── .env.example
└── .env                        # No incluido en Git
```

---

## Decisiones técnicas

### UUID como Primary Key
Los IDs enteros secuenciales exponen el volumen de datos del sistema y son previsibles (vulnerables a IDOR attacks). Los UUIDs eliminan ambos problemas y son ideales para sistemas distribuidos.

### Soft Delete
Las tareas eliminadas no se borran físicamente. El manager por defecto (`SoftDeleteManager`) las excluye automáticamente de todas las queries. `all_objects` permite verlas en admin para auditoría y recuperación.

### Settings divididos por entorno
`base.py` tiene la configuración compartida. `local.py` y `production.py` solo sobreescriben lo necesario para cada entorno. Elimina el anti-patrón `if DEBUG:` y es la práctica estándar en proyectos Django escalables (Two Scoops of Django).

### Modelos abstractos reutilizables en `core/`
`TimeStampedModel` y `SoftDeleteModel` implementan el principio DRY. Cualquier modelo nuevo hereda timestamps y soft delete con solo añadirlo como clase base.

### Validación de transiciones de estado
El diccionario `VALID_STATUS_TRANSITIONS` en el modelo `Task` es la única fuente de verdad. El serializer consulta ese diccionario y rechaza transiciones inválidas con un mensaje descriptivo. El campo `valid_next_statuses` en el detalle guía al frontend.

### `select_related` y `prefetch_related`
El ViewSet de tareas usa:
```python
Task.objects.select_related("created_by", "assigned_to")
            .prefetch_related("comments__author")
```
Esto resuelve el problema N+1: el listado completo generaría 30+ queries SQL sin esta optimización. Con ella, siempre son 3 queries fijas.

### JWT con Refresh Token Rotation
Cada uso del refresh token invalida el anterior (blacklist). Si un token es interceptado, solo puede usarse una vez. `signup` y `signin` retornan tokens + datos de usuario en una sola respuesta para evitar llamadas adicionales.

### drf-nested-routers para comentarios
Los comentarios están anidados bajo tareas:  
`/tasks/{task_pk}/comments/` y `/tasks/{task_pk}/comments/{id}/`  
Esto refleja la relación natural de los datos y es la convención REST estándar para recursos anidados.

---

← [Volver al README principal](../README.md)
