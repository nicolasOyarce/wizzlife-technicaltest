"""
Management command para poblar la base de datos con datos de ejemplo.

Uso:
    python manage.py seed_data
    python manage.py seed_data --users 5 --tasks 20
    python manage.py seed_data --clear  (borra todos los datos antes de crear)
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.tasks.models import Comment, Task

User = get_user_model()

SAMPLE_USERS = [
    {"email": "alice@wizzlife.com", "username": "alice", "first_name": "Alice", "last_name": "Johnson", "password": "Demo12345!"},
    {"email": "bob@wizzlife.com", "username": "bob", "first_name": "Bob", "last_name": "Smith", "password": "Demo12345!"},
    {"email": "carol@wizzlife.com", "username": "carol", "first_name": "Carol", "last_name": "Williams", "password": "Demo12345!"},
    {"email": "david@wizzlife.com", "username": "david", "first_name": "David", "last_name": "Brown", "password": "Demo12345!"},
]

SAMPLE_TASKS = [
    {
        "title": "Configurar infraestructura de CI/CD",
        "description": "Implementar pipeline con GitHub Actions para correr tests y deploy automático en cada PR.",
        "status": Task.Status.DONE,
        "priority": Task.Priority.HIGH,
    },
    {
        "title": "Diseño de base de datos",
        "description": "Definir el esquema ER, índices y relaciones del proyecto.",
        "status": Task.Status.DONE,
        "priority": Task.Priority.URGENT,
    },
    {
        "title": "Implementar autenticación JWT",
        "description": "Configurar djangorestframework-simplejwt con refresh token rotation y blacklisting.",
        "status": Task.Status.IN_PROGRESS,
        "priority": Task.Priority.HIGH,
    },
    {
        "title": "Desarrollar endpoints de tareas",
        "description": "CRUD completo con filtros, paginación y soft delete.",
        "status": Task.Status.IN_PROGRESS,
        "priority": Task.Priority.HIGH,
    },
    {
        "title": "Agregar documentación Swagger",
        "description": "Configurar drf-spectacular y documentar todos los endpoints con exemplos.",
        "status": Task.Status.REVIEW,
        "priority": Task.Priority.MEDIUM,
    },
    {
        "title": "Escribir tests unitarios",
        "description": "Cobertura mínima del 90% con pytest, factory-boy y pytest-cov.",
        "status": Task.Status.IN_PROGRESS,
        "priority": Task.Priority.HIGH,
    },
    {
        "title": "Dockerizar el proyecto",
        "description": "Crear Dockerfile multi-stage y docker-compose con PostgreSQL.",
        "status": Task.Status.PENDING,
        "priority": Task.Priority.MEDIUM,
    },
    {
        "title": "Deploy en Render",
        "description": "Configurar render.yaml con servicio web y base de datos PostgreSQL.",
        "status": Task.Status.PENDING,
        "priority": Task.Priority.MEDIUM,
    },
    {
        "title": "Optimizar consultas N+1",
        "description": "Revisar queryset con select_related y prefetch_related.",
        "status": Task.Status.PENDING,
        "priority": Task.Priority.LOW,
    },
    {
        "title": "Implementar rate limiting",
        "description": "Configurar throttling diferenciado por endpoint sensible (signup, signin).",
        "status": Task.Status.DONE,
        "priority": Task.Priority.MEDIUM,
    },
]

SAMPLE_COMMENTS = [
    "Listo para revisión, por favor verificar en staging.",
    "Encontré un edge case, abrí un issue.",
    "Necesito más contexto sobre los requisitos de seguridad.",
    "Actualizaré el README con las instrucciones.",
    "Esto bloquea el sprint, hay que priorizarlo.",
]


class Command(BaseCommand):
    help = "Pobla la base de datos con datos de ejemplo para testing/demo."

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Eliminar datos existentes antes de crear nuevos.")
        parser.add_argument("--admin-email", default="admin@wizzlife.com", help="Email del superusuario admin.")
        parser.add_argument("--admin-password", default="Admin12345!", help="Contraseña del superusuario admin.")

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write(self.style.WARNING("Eliminando datos existentes..."))
            Comment.all_objects.all().delete()
            Task.all_objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS("Datos eliminados."))

        self.stdout.write("Creando superusuario admin...")
        admin, created = User.objects.get_or_create(
            email=options["admin_email"],
            defaults={
                "username": "admin",
                "first_name": "Admin",
                "last_name": "Wizz Life",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password(options["admin_password"])
            admin.save()
            self.stdout.write(self.style.SUCCESS(f"  Admin creado: {admin.email} / {options['admin_password']}"))
        else:
            self.stdout.write(f"  Admin ya existe: {admin.email}")

        self.stdout.write("Creando usuarios de ejemplo...")
        users = [admin]
        for user_data in SAMPLE_USERS:
            password = user_data.pop("password")
            user, created = User.objects.get_or_create(email=user_data["email"], defaults=user_data)
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"  Usuario creado: {user.email} / {password}"))
            else:
                self.stdout.write(f"  Usuario ya existe: {user.email}")
            users.append(user)
            user_data["password"] = password  # restaurar para posibles re-usos

        self.stdout.write("Creando tareas de ejemplo...")
        for i, task_data in enumerate(SAMPLE_TASKS):
            creator = users[i % len(users)]
            assignee = users[(i + 1) % len(users)]
            task, created = Task.objects.get_or_create(
                title=task_data["title"],
                defaults={
                    **task_data,
                    "created_by": creator,
                    "assigned_to": assignee,
                },
            )
            if created:
                # Agregar comentario de ejemplo
                Comment.objects.create(
                    task=task,
                    author=assignee,
                    content=SAMPLE_COMMENTS[i % len(SAMPLE_COMMENTS)],
                )
                self.stdout.write(self.style.SUCCESS(f"  Tarea creada: {task.title}"))
            else:
                self.stdout.write(f"  Tarea ya existe: {task.title}")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("✓ Datos de ejemplo creados exitosamente."))
        self.stdout.write(self.style.SUCCESS(f"  Admin: {options['admin_email']} / {options['admin_password']}"))
        self.stdout.write(self.style.SUCCESS("  Usuarios demo: alice, bob, carol, david@wizzlife.com / Demo12345!"))
        self.stdout.write(self.style.SUCCESS(f"  Tareas creadas: {len(SAMPLE_TASKS)}"))
