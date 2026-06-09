#!/bin/bash
set -e

echo "=== Openmailer Startup ==="
echo "Environment: ${ENVIRONMENT:-production}"

cd /app/backend
alembic upgrade head
echo "Migrations complete"

python -m scripts.seed_data
echo "Seed data complete"

if [ "${ENABLE_CELERY:-true}" = "true" ]; then
    echo "Starting Celery worker..."
    celery -A app.workers.celery_app worker --loglevel=info --concurrency=2 &
    echo "Starting Celery beat..."
    celery -A app.workers.celery_app beat --loglevel=info &
fi

echo "Starting API server..."
cd /app/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers ${WORKERS:-2} &

sleep 3

echo "Starting frontend on port ${PORT:-3000}..."
cd /app/frontend
exec node server.js
