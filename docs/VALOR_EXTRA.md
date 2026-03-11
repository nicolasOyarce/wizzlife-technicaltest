# ⭐ Valor extra implementado

← [Volver al README principal](../README.md)

Esta prueba técnica incluye decisiones y funcionalidades que van **más allá de los requerimientos mínimos**, pensadas para demostrar criterio de diseño, buenas prácticas de producción y madurez técnica.

---

## 1. Modelo de datos enriquecido

**Requerido:** Crear tareas con estado.  
**Implementado:**

- **Campo `priority`** (`low / medium / high / urgent`): permite ordenar y filtrar por urgencia.
- **Campo `due_date`**: fecha límite opcional por tarea, fundamental en gestión de equipos.
- **Relación `assigned_to`**: una tarea puede asignarse a un usuario distinto al creador.
- **Modelo `Comment`**: segunda entidad con múltiples FKs hacia `User`, demostrando modelamiento relacional avanzado.
- **Índices de BD** en campos de búsqueda frecuente (`status`, `priority`, `created_by`, `assigned_to`, `due_date`).

---

## 2. Soft Delete (borrado lógico)

**Requerido:** Eliminar una tarea.  
**Implementado:** Las tareas eliminadas **no se borran físicamente** de la base de datos.

- Se marcan con `is_deleted=True` y `deleted_at=timestamp`.
- El **manager por defecto** (`SoftDeleteManager`) excluye registros eliminados automáticamente de todas las queries.
- Un manager adicional `all_objects` permite ver registros eliminados (para auditoría y admin).
- Método `restore()` para recuperar tareas eliminadas accidentalmente.

Esta práctica permite auditoría, recuperación de datos y análisis histórico sin pérdida de información.

---

## 3. Validación de transiciones de estado

**Requerido:** Actualizar el estado de una tarea.  
**Implementado:** Las transiciones siguen un flujo lógico:

```
PENDING → IN_PROGRESS
IN_PROGRESS → REVIEW | PENDING
REVIEW → DONE | IN_PROGRESS
DONE → IN_PROGRESS  (permite reabrir)
```

Si se intenta una transición inválida (ej: `PENDING → DONE`), la API retorna un error descriptivo indicando exactamente qué transiciones son válidas.

El detalle de tarea incluye el campo `valid_next_statuses` para orientar al frontend.

---

## 4. Settings divididos por entorno

**Requerido:** Un solo archivo de configuración.  
**Implementado:**

| Archivo | Propósito |
|---------|-----------|
| `config/settings/base.py` | Configuración compartida |
| `config/settings/local.py` | Desarrollo (`DEBUG=True`, CORS abierto) |
| `config/settings/production.py` | Producción (HTTPS, HSTS, `DATABASE_URL`) |

Elimina el anti-patrón `if DEBUG:` dentro de settings (práctica de Two Scoops of Django).

---

## 5. Modelos abstractos reutilizables en `core/`

**Requerido:** Modelos con timestamps.  
**Implementado:**

- `TimeStampedModel`: agrega `created_at` / `updated_at` a cualquier modelo (principio DRY).
- `SoftDeleteModel`: extiende `TimeStampedModel` con todo el mecanismo de borrado lógico.
- `SoftDeleteQuerySet`: operaciones en masa respetan el soft delete automáticamente.

---

## 6. UUIDs como Primary Key

**Requerido:** IDs para identificar recursos.  
**Implementado:** Todos los modelos usan `UUIDField` como PK en lugar de enteros secuenciales.

- **Seguridad**: los enteros exponen el volumen de datos y son vulnerables a IDOR attacks.
- **Escalabilidad**: los UUIDs son seguros para sistemas distribuidos y microservicios.

---

## 7. JWT con Refresh Token Rotation y Blacklisting

**Requerido:** Token de autenticación.  
**Implementado:**

- **Access token** (60 min) + **Refresh token** (7 días).
- **Refresh Token Rotation**: el token anterior queda en blacklist (`token_blacklist` de simplejwt). Si es interceptado, solo funciona una vez.
- `POST /signup/` y `POST /signin/` retornan tokens + datos de usuario en una sola respuesta.
- `POST /token/refresh/` para renovar tokens desde el frontend.
- Claims personalizados en el JWT (`email`, `full_name`) para decodificar sin llamadas adicionales.

---

## 8. Filtros avanzados, paginación y ordenamiento

**Requerido:** Listar tareas (+3 puntos por filtros, paginación y ordenamiento).  
**Implementado:**

```
?status=pending                     # Filtro por estado
?status__in=pending,in_progress     # Múltiples estados a la vez
?priority=high                      # Filtro por prioridad
?assigned_to={uuid}                 # Por usuario asignado
?created_by={uuid}                  # Por creador
?due_date__gte=2026-01-01           # Rango de fechas
?mine=true                          # Solo mis tareas
?search=keyword                     # Búsqueda en título Y descripción
?ordering=-due_date                 # Ordenamiento (- = descendente)
?page=2&page_size=20                # Paginación configurable
```

Paginación enriquecida con `total_pages`, `current_page` y `page_size` además del estándar.

---

## 9. Rate Limiting diferenciado

**Requerido:** No requerido.  
**Implementado:**

| Throttle | Tasa | Aplicado en |
|----------|------|-------------|
| `SignUpRateThrottle` | 5/min | `POST /signup/` |
| `SignInRateThrottle` | 10/min | `POST /signin/` |
| `UserRateThrottle` | 60/min | Endpoints autenticados |
| `AnonRateThrottle` | 20/min | Endpoints anónimos |

Previene ataques de fuerza bruta en los endpoints más sensibles.

---

## 10. Permisos a nivel de objeto

**Requerido:** Endpoints protegidos con token.  
**Implementado:** Permiso personalizado `IsTaskOwnerOrAssigned`:

- Solo el **creador** o el **usuario asignado** pueden modificar o eliminar una tarea.
- Otros usuarios autenticados reciben `403 Forbidden`.
- Staff y superusuarios tienen acceso completo.
- Mismo patrón aplicado a comentarios con `IsCommentAuthor`.

---

## 11. Documentación interactiva con Swagger UI

**Requerido:** No requerido.  
**Implementado:**

- `GET /api/docs/` → Swagger UI interactivo con autenticación Bearer integrada.
- `GET /api/redoc/` → Documentación en formato ReDoc.
- `GET /api/schema/` → Schema OpenAPI 3.0 en YAML.
- El revisor puede **probar la API directamente desde el navegador** sin Postman.

---

## 12. Optimización de queries (N+1)

**Requerido:** No requerido.  
**Implementado:**

```python
Task.objects.select_related("created_by", "assigned_to")
            .prefetch_related("comments__author")
```

Sin esta optimización, listar 10 tareas generaría **30+ queries SQL**. Con `select_related` y `prefetch_related` se resuelve en **3 queries fijas** independientemente del volumen.

---

## 13. Django Admin mejorado

**Requerido:** No requerido.  
**Implementado:**

- Badges de color en el admin para `status` y `priority`.
- Filtros laterales, búsqueda por email, campos de solo lectura.
- Inline de comentarios dentro del detalle de cada tarea.
- Muestra **todas las tareas** incluyendo eliminadas (soft delete) via `all_objects` manager.

---

## 14. Management command `seed_data`

**Requerido:** No requerido.  
**Implementado:** `python manage.py seed_data`

- Crea un superusuario admin (`admin@wizzlife.com`).
- Crea 4 usuarios de demo con datos realistas.
- Crea 10 tareas en distintos estados y prioridades con comentarios.
- Opciones: `--clear`, `--admin-email`, `--admin-password`.
- Facilita enormemente la evaluación de la prueba por el revisor.

---

## 15. Dockerfile multi-stage + docker-compose production-ready

**Requerido:** Dockerfile funcional.  
**Implementado:**

- **Multi-stage build**: imagen resultante ~60% más liviana.
- **Usuario no-root** (`appuser`): evita escalada de privilegios.
- **Health check** en el Dockerfile para orquestadores.
- **docker-compose** con health check en PostgreSQL: el web no arranca hasta que la BD está lista.
- Migration automática al arrancar el contenedor.

---

## 16. `render.yaml` — Infraestructura como código

**Requerido:** Deploy en Render.  
**Implementado:**

- Blueprint que crea servicio web + PostgreSQL con **un solo click** en Render.
- Variables de entorno, región, plan y healthcheck declarados en código.
- `SECRET_KEY` generada automáticamente por Render.
- Reproducible: cualquier persona puede hacer fork y deployar en minutos.

---

## Resumen

| # | Extra | Impacto |
|---|-------|---------|
| 1 | Modelo enriquecido (priority, due_date, assigned_to, Comment) | Modelamiento BD |
| 2 | Soft delete con manager personalizado | Buenas prácticas |
| 3 | Validación de transiciones de estado | Diseño de negocio |
| 4 | Settings divididos por entorno | Organización |
| 5 | Modelos abstractos reutilizables | DRY / separación |
| 6 | UUID como PK | Seguridad |
| 7 | JWT con refresh rotation + blacklisting | Auth completo |
| 8 | Filtros/paginación/ordenamiento avanzados | +3 pts explícitos |
| 9 | Rate limiting diferenciado | Seguridad |
| 10 | Permisos a nivel de objeto | Reglas de negocio |
| 11 | Swagger UI + ReDoc + OpenAPI schema | Experiencia de API |
| 12 | Optimización N+1 con select_related | Rendimiento |
| 13 | Django Admin mejorado con badges | Dominio del framework |
| 14 | Management command seed_data | Experiencia del revisor |
| 15 | Dockerfile multi-stage + usuario no-root | Docker production-ready |
| 16 | render.yaml Infrastructure as Code | Deploy reproducible |

---

← [Volver al README principal](../README.md)
