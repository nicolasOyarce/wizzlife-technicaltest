# Tests

← [Volver al README principal](../README.md)

---

## Requisitos previos

Asegúrate de tener el virtualenv activo y la base de datos Docker corriendo:

```powershell
# Windows: activar virtualenv
.\.venv\Scripts\Activate.ps1

# Levantar la base de datos (si no está corriendo)
docker-compose up db -d
```

---

## Comandos

```bash
# Correr todos los tests
pytest

# Con reporte de cobertura en terminal
pytest --cov=apps --cov-report=term-missing

# Solo los tests de una app específica
pytest apps/users/tests/
pytest apps/tasks/tests/

# Un archivo de test específico
pytest apps/users/tests/test_signup.py

# Un test específico
pytest apps/users/tests/test_signup.py::TestSignUp::test_signup_success

# Reporte HTML de cobertura (se genera en htmlcov/index.html)
pytest --cov=apps --cov-report=html

# Modo verbose (muestra cada test individualmente)
pytest -v

# Detener en el primer fallo
pytest -x
```

---

## Estructura de tests

```
apps/
├── users/
│   └── tests/
│       ├── conftest.py         # UserFactory, fixtures de auth
│       ├── test_signup.py      # 12 tests — registro de usuario
│       └── test_signin.py      # 10 tests — inicio de sesión
└── tasks/
    └── tests/
        ├── conftest.py         # TaskFactory, fixtures de tareas
        ├── test_create_task.py # 9 tests — creación de tareas
        └── test_tasks.py       # ~20 tests — retrieve, update, delete
```

---

## Qué cubre cada archivo

### `test_signup.py`
- Registro exitoso retorna 201 y tokens JWT
- Registro sin email retorna 400
- Email duplicado retorna 400
- Contraseñas no coincidentes retorna 400
- Contraseña débil retorna 400
- Email se normaliza a minúsculas
- Username duplicado retorna 400
- Todos los campos requeridos
- Tokens válidos generados correctamente
- Rate limiting: superar 5 intentos/min retorna 429

### `test_signin.py`
- Login exitoso retorna 200 con access + refresh + user data
- Credenciales incorrectas retorna 401
- Email inexistente retorna 401
- Falta password retorna 400
- Falta email retorna 400
- Token devuelto es válido para endpoints protegidos
- Rate limiting: superar 10 intentos/min retorna 429

### `test_create_task.py`
- Crear tarea mínima (solo título) retorna 201
- Crear tarea completa retorna 201 con todos los campos
- Sin autenticación retorna 401
- Título vacío retorna 400
- Status default es `pending`
- Priority default es `medium`
- `created_by` se asigna automáticamente al usuario autenticado
- `assigned_to_id` con UUID válido asigna correctamente
- `assigned_to_id` con UUID inválido retorna 400

### `test_tasks.py`
- GET detalle de tarea existente retorna 200
- GET tarea inexistente retorna 404
- GET tarea eliminada retorna 404
- Listar tareas retorna paginación enriquecida
- PATCH título y descripción retorna 200
- PATCH transición de estado válida retorna 200
- PATCH transición de estado inválida retorna 400
- PATCH por usuario no propietario retorna 403
- DELETE por propietario retorna 204
- DELETE por usuario no propietario retorna 403
- Tarea eliminada no aparece en el listado

---

## Herramientas usadas

| Herramienta | Uso |
|-------------|-----|
| `pytest` | Runner de tests |
| `pytest-django` | Integración de Django con pytest |
| `factory-boy` | Generación de objetos de prueba (UserFactory, TaskFactory) |
| `faker` | Datos aleatorios realistas |
| `pytest-cov` | Reporte de cobertura de código |

---

← [Volver al README principal](../README.md)
