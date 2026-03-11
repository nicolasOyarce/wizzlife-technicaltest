# Referencia de Endpoints — Uso Personal

Base URL local: `http://localhost:8000`  
Base URL producción: `https://{tu-app}.onrender.com`

> **Autenticación:** Los endpoints protegidos requieren el header:  
> `Authorization: Bearer {access_token}`  
> El token se obtiene en `/signup/` o `/signin/`.

---

## AUTH

---

### `POST /signup/` — Registro de usuario

**Autenticación:** No requerida

**Body (JSON):**
```json
{
    "email": "john@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
}
```

**Campos obligatorios:** `email`, `username`, `first_name`, `password`, `password_confirm`  
**Campos opcionales:** `last_name`

**Respuesta exitosa `201 Created`:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "created_at": "2026-03-11T10:00:00Z",
    "tokens": {
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}
```

**Errores posibles:**
```json
// 400 — Email ya registrado
{ "email": ["Ya existe una cuenta con este correo electrónico."] }

// 400 — Contraseñas no coinciden
{ "password_confirm": ["Las contraseñas no coinciden."] }

// 400 — Contraseña débil
{ "password": ["Esta contraseña es demasiado corta."] }

// 400 — Username duplicado
{ "username": ["Este nombre de usuario ya está en uso."] }
```

---

### `POST /signin/` — Inicio de sesión

**Autenticación:** No requerida

**Body (JSON):**
```json
{
    "email": "john@example.com",
    "password": "SecurePass123!"
}
```

**Respuesta exitosa `200 OK`:**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "john@example.com",
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "created_at": "2026-03-11T10:00:00Z"
    }
}
```

**Errores posibles:**
```json
// 401 — Credenciales incorrectas
{ "detail": "No active account found with the given credentials" }

// 400 — Falta email o password
{ "email": ["Este campo es requerido."] }
```

---

### `POST /token/refresh/` — Renovar access token

**Autenticación:** No requerida

**Body (JSON):**
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Respuesta exitosa `200 OK`:**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

> **Nota:** El refresh token anterior queda invalidado (blacklisted). Siempre guarda el nuevo.

**Errores posibles:**
```json
// 401 — Token inválido o expirado
{ "detail": "Token is invalid or expired", "code": "token_not_valid" }
```

---

### `GET /users/me/` — Perfil del usuario autenticado

**Autenticación:** ✅ Requerida

**Body:** No aplica

**Respuesta exitosa `200 OK`:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "created_at": "2026-03-11T10:00:00Z"
}
```

**Errores posibles:**
```json
// 401 — Sin token o token inválido
{ "detail": "Las credenciales de autenticación no se proveyeron." }
```

---

## TASKS

---

### `GET /tasks/` — Listar tareas

**Autenticación:** ✅ Requerida

**Body:** No aplica

**Query params disponibles:**

| Parámetro | Tipo | Ejemplo | Descripción |
|-----------|------|---------|-------------|
| `status` | string | `?status=pending` | Filtrar por estado |
| `status__in` | string | `?status__in=pending,in_progress` | Múltiples estados |
| `priority` | string | `?priority=high` | Filtrar por prioridad |
| `assigned_to` | UUID | `?assigned_to=550e8400-...` | Por usuario asignado |
| `created_by` | UUID | `?created_by=550e8400-...` | Por usuario creador |
| `due_date__gte` | date | `?due_date__gte=2026-01-01` | Fecha límite desde |
| `due_date__lte` | date | `?due_date__lte=2026-12-31` | Fecha límite hasta |
| `mine` | bool | `?mine=true` | Solo mis tareas |
| `search` | string | `?search=diseño` | Búsqueda en título/descripción |
| `ordering` | string | `?ordering=-due_date` | Ordenamiento (`-` = desc) |
| `page` | int | `?page=2` | Número de página |
| `page_size` | int | `?page_size=20` | Tamaño de página (max 100) |

**Valores válidos para `status`:** `pending` `in_progress` `review` `done`  
**Valores válidos para `priority`:** `low` `medium` `high` `urgent`  
**Campos ordenables:** `created_at` `updated_at` `due_date` `priority` `status` `title`

**Respuesta exitosa `200 OK`:**
```json
{
    "pagination": {
        "count": 25,
        "total_pages": 3,
        "current_page": 1,
        "page_size": 10,
        "next": "http://localhost:8000/tasks/?page=2",
        "previous": null
    },
    "results": [
        {
            "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
            "title": "Implementar autenticación JWT",
            "status": "in_progress",
            "status_display": "En progreso",
            "priority": "high",
            "priority_display": "Alta",
            "due_date": "2026-04-15",
            "created_by": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "john@example.com",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "created_at": "2026-03-11T10:00:00Z"
            },
            "assigned_to": null,
            "comments_count": 2,
            "created_at": "2026-03-11T10:00:00Z",
            "updated_at": "2026-03-11T10:30:00Z"
        }
    ]
}
```

---

### `POST /tasks/` — Crear tarea

**Autenticación:** ✅ Requerida

**Body (JSON):**
```json
{
    "title": "Diseñar base de datos",
    "description": "Definir esquema ER con todas las relaciones.",
    "status": "pending",
    "priority": "high",
    "due_date": "2026-04-30",
    "assigned_to_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Campos obligatorios:** `title`  
**Campos opcionales:** `description` `status` `priority` `due_date` `assigned_to_id`  
**Defaults:** `status=pending`, `priority=medium`

> **Nota:** `created_by` se asigna automáticamente al usuario autenticado.  
> `assigned_to_id` debe ser el UUID de un usuario existente.

**Respuesta exitosa `201 Created`:**
```json
{
    "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "title": "Diseñar base de datos",
    "description": "Definir esquema ER con todas las relaciones.",
    "status": "pending",
    "status_display": "Pendiente",
    "priority": "high",
    "priority_display": "Alta",
    "due_date": "2026-04-30",
    "created_by": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "john@example.com",
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "created_at": "2026-03-11T10:00:00Z"
    },
    "assigned_to": null,
    "valid_next_statuses": ["in_progress"],
    "comments": [],
    "created_at": "2026-03-11T10:00:00Z",
    "updated_at": "2026-03-11T10:00:00Z"
}
```

**Errores posibles:**
```json
// 400 — Falta el título
{ "title": ["Este campo es requerido."] }

// 400 — UUID de assigned_to inválido o inexistente
{ "assigned_to_id": ["El usuario asignado no existe."] }

// 401 — Sin autenticación
{ "detail": "Las credenciales de autenticación no se proveyeron." }
```

---

### `GET /tasks/{id}/` — Detalle de tarea

**Autenticación:** ✅ Requerida

**Body:** No aplica

**URL param:** `id` = UUID de la tarea (ej: `7c9e6679-7425-40de-944b-e07fc1f90ae7`)

**Respuesta exitosa `200 OK`:**
```json
{
    "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "title": "Diseñar base de datos",
    "description": "Definir esquema ER con todas las relaciones.",
    "status": "pending",
    "status_display": "Pendiente",
    "priority": "high",
    "priority_display": "Alta",
    "due_date": "2026-04-30",
    "created_by": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "john@example.com",
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "created_at": "2026-03-11T10:00:00Z"
    },
    "assigned_to": null,
    "valid_next_statuses": ["in_progress"],
    "comments": [
        {
            "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "author": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "john@example.com",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "created_at": "2026-03-11T10:00:00Z"
            },
            "content": "Revisar con el equipo antes de proceder.",
            "created_at": "2026-03-11T10:15:00Z",
            "updated_at": "2026-03-11T10:15:00Z"
        }
    ],
    "created_at": "2026-03-11T10:00:00Z",
    "updated_at": "2026-03-11T10:00:00Z"
}
```

**Errores posibles:**
```json
// 404 — Tarea no existe o fue eliminada
{ "detail": "No encontrado." }

// 401 — Sin autenticación
{ "detail": "Las credenciales de autenticación no se proveyeron." }
```

---

### `PATCH /tasks/{id}/` — Actualizar tarea

**Autenticación:** ✅ Requerida  
**Permisos:** Solo el creador o el usuario asignado a la tarea

**Body (JSON) — todos los campos son opcionales:**
```json
{
    "title": "Nuevo título",
    "description": "Descripción actualizada",
    "status": "in_progress",
    "priority": "urgent",
    "due_date": "2026-05-01",
    "assigned_to_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

> **Desasignar usuario:** enviar `"assigned_to_id": null`

**Transiciones de estado válidas:**

| Estado actual | Puede pasar a |
|--------------|---------------|
| `pending` | `in_progress` |
| `in_progress` | `review`, `pending` |
| `review` | `done`, `in_progress` |
| `done` | `in_progress` |

**Respuesta exitosa `200 OK`:** (misma estructura que detalle de tarea)

**Errores posibles:**
```json
// 400 — Transición de estado inválida
{
    "status": [
        "No se puede cambiar el estado de 'Pendiente' a 'Completada'. Transiciones válidas: ['in_progress']."
    ]
}

// 403 — No eres el creador ni el asignado
{ "detail": "Solo el creador o el usuario asignado pueden realizar esta acción." }

// 404 — Tarea no existe
{ "detail": "No encontrado." }
```

---

### `DELETE /tasks/{id}/` — Eliminar tarea (soft delete)

**Autenticación:** ✅ Requerida  
**Permisos:** Solo el creador o el usuario asignado

**Body:** No aplica

**Respuesta exitosa `204 No Content`:** (sin body)

> **Nota:** La tarea NO se borra físicamente. Se marca como eliminada y deja de aparecer en el listado y detalle. El admin Django puede ver y restaurar tareas eliminadas.

**Errores posibles:**
```json
// 403 — No eres el creador ni el asignado
{ "detail": "Solo el creador o el usuario asignado pueden realizar esta acción." }

// 404 — Tarea no existe o ya fue eliminada
{ "detail": "No encontrado." }
```

---

## COMMENTS (Extra)

---

### `GET /tasks/{task_id}/comments/` — Listar comentarios

**Autenticación:** ✅ Requerida

**Body:** No aplica

**Respuesta exitosa `200 OK`:**
```json
[
    {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "author": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "john@example.com",
            "username": "johndoe",
            "first_name": "John",
            "last_name": "Doe",
            "created_at": "2026-03-11T10:00:00Z"
        },
        "content": "Revisar con el equipo antes de proceder.",
        "created_at": "2026-03-11T10:15:00Z",
        "updated_at": "2026-03-11T10:15:00Z"
    }
]
```

---

### `POST /tasks/{task_id}/comments/` — Agregar comentario

**Autenticación:** ✅ Requerida

**Body (JSON):**
```json
{
    "content": "Necesitamos revisar los requisitos antes de avanzar."
}
```

> El `author` se asigna automáticamente al usuario autenticado.

**Respuesta exitosa `201 Created`:**
```json
{
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "content": "Necesitamos revisar los requisitos antes de avanzar.",
    "created_at": "2026-03-11T10:15:00Z"
}
```

---

### `DELETE /tasks/{task_id}/comments/{id}/` — Eliminar comentario

**Autenticación:** ✅ Requerida  
**Permisos:** Solo el autor del comentario

**Body:** No aplica

**Respuesta exitosa `204 No Content`:** (sin body)

---

## Usuarios de demo (seed_data)

| Email | Password | Rol |
|-------|----------|-----|
| `admin@wizzlife.com` | `Admin12345!` | Superusuario |
| `alice@wizzlife.com` | `Demo12345!` | Usuario demo |
| `bob@wizzlife.com` | `Demo12345!` | Usuario demo |
| `carol@wizzlife.com` | `Demo12345!` | Usuario demo |
| `david@wizzlife.com` | `Demo12345!` | Usuario demo |

Admin Django: `http://localhost:8000/admin/`  
Swagger UI: `http://localhost:8000/api/docs/`

---

## Flujo rápido de prueba

```bash
# 1. Registrar usuario
POST /signup/
body: { email, username, first_name, password, password_confirm }
→ Guardar tokens.access y tokens.refresh

# 2. Crear tarea
POST /tasks/
header: Authorization: Bearer {access}
body: { title, priority, due_date }
→ Guardar id de la tarea

# 3. Ver mis tareas
GET /tasks/?mine=true&ordering=-created_at
header: Authorization: Bearer {access}

# 4. Cambiar estado
PATCH /tasks/{id}/
header: Authorization: Bearer {access}
body: { status: "in_progress" }

# 5. Agregar comentario
POST /tasks/{id}/comments/
header: Authorization: Bearer {access}
body: { content: "En proceso..." }

# 6. Eliminar tarea
DELETE /tasks/{id}/
header: Authorization: Bearer {access}
→ 204, la tarea desaparece del listado

# 7. Refrescar token cuando expira
POST /token/refresh/
body: { refresh: "{refresh_token}" }
→ Nuevo access + nuevo refresh
```
