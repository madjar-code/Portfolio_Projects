#!/bin/bash
set -e

echo "==> Running migrations"
python manage.py migrate --noinput

echo "==> Starting Gunicorn"
exec gunicorn config.asgi:application \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers "${GUNICORN_WORKERS:-2}" \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile - \
    --timeout 120