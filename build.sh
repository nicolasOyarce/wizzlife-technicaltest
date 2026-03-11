#!/usr/bin/env bash
# build.sh — Script de build para Render
# Se ejecuta antes de iniciar el servicio web.

set -o errexit  # Salir si algún comando falla

pip install -r requirements/production.txt

python manage.py collectstatic --no-input
python manage.py migrate
