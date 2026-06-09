#!/bin/bash
set -e

echo "=== Running Database Migrations ==="

cd backend

echo "Generating new migration..."
alembic revision --autogenerate -m "$1"

echo "Applying migration..."
alembic upgrade head

echo "Migration complete!"
