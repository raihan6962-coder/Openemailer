#!/bin/bash
set -e

echo "=== Openmailer Startup ==="
cd /app/backend

alembic upgrade head &>/dev/null &

exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --log-level info
