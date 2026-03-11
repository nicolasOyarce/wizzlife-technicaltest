# Instalación y ejecución local

← [Volver al README principal](../README.md)

---

## Prerrequisitos

- Python 3.12+
- PostgreSQL 16
- Git

---

## Pasos

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/wizzlife-technicaltest.git
cd wizzlife-technicaltest
```

---

### 2. Crear y activar el entorno virtual

```bash
python -m venv .venv
```

**Windows:**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux / Mac:**
```bash
source .venv/bin/activate
```

---

### 3. Instalar dependencias

```bash
pip install -r requirements/local.txt
```

---

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` con los datos de tu base de datos:

```env
SECRET_KEY=django-insecure-cambia-esto-en-produccion
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://wizzlife:wizzlife_secret@localhost:5432/wizzlife_db
DJANGO_SETTINGS_MODULE=config.settings.local
```

---

### 5. Crear la base de datos en PostgreSQL

```sql
CREATE DATABASE wizzlife_db;
CREATE USER wizzlife WITH PASSWORD 'wizzlife_secret';
GRANT ALL PRIVILEGES ON DATABASE wizzlife_db TO wizzlife;
```

O desde la CLI de PostgreSQL:

```bash
psql -U postgres -c "CREATE DATABASE wizzlife_db;"
psql -U postgres -c "CREATE USER wizzlife WITH PASSWORD 'wizzlife_secret';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE wizzlife_db TO wizzlife;"
```

---

### 6. Ejecutar migraciones

```bash
python manage.py migrate
```

---

### 7. (Opcional) Poblar con datos de ejemplo

```bash
python manage.py seed_data
```

Esto crea:
- Superusuario: `admin@wizzlife.com` / `Admin12345!`
- 4 usuarios demo: `alice/bob/carol/david@wizzlife.com` / `Demo12345!`
- 10 tareas con comentarios en distintos estados

Opciones del comando:
```bash
python manage.py seed_data --clear                       # Borra y re-crea todo
python manage.py seed_data --admin-email otro@email.com  # Otro email para admin
python manage.py seed_data --admin-password OtraPass123! # Otra contraseña
```

---

### 8. Iniciar el servidor de desarrollo

```bash
python manage.py runserver
```

Accesos disponibles:

| URL | Descripción |
|-----|-------------|
| `http://localhost:8000/api/docs/` | Swagger UI interactivo |
| `http://localhost:8000/api/redoc/` | Documentación ReDoc |
| `http://localhost:8000/admin/` | Panel de administración Django |
| `http://localhost:8000/api/schema/` | Schema OpenAPI YAML |

---

## Variables de entorno — referencia

| Variable | Requerida | Descripción |
|----------|-----------|-------------|
| `SECRET_KEY` | Sí | Clave secreta de Django |
| `DEBUG` | No | `True` en local, `False` en producción |
| `ALLOWED_HOSTS` | Sí | Hosts permitidos separados por coma |
| `DATABASE_URL` | Sí | URL de conexión a PostgreSQL |
| `DJANGO_SETTINGS_MODULE` | No | Default: `config.settings.local` |

---

← [Volver al README principal](../README.md)
