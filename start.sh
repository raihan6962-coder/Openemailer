#!/bin/bash
set -e

echo "=== Openmailer Startup ==="
cd /app/backend

alembic upgrade head &
python -m scripts.seed_data &

exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WORKERS:-2}
