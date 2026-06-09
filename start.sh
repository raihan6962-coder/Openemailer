#!/bin/bash
set -e

echo "=== Openmailer Startup ==="

cd /app/backend

# Start API server FIRST so healthcheck passes immediately
echo "Starting API server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 &

sleep 2

# Run migrations in background
echo "Running migrations..."
alembic upgrade head &
python -m scripts.seed_data &

# Start Celery in background
if [ "${ENABLE_CELERY:-true}" = "true" ]; then
    echo "Starting Celery..."
    celery -A app.workers.celery_app worker --loglevel=info --concurrency=2 &
    celery -A app.workers.celery_app beat --loglevel=info &
fi

# Start frontend (proxies /api/* and /health to backend)
echo "Starting frontend..."
cd /app/frontend
exec node server.js
