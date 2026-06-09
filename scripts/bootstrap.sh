#!/bin/bash
set -e

echo "=== Openmailer Bootstrap ==="

echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install -r backend/requirements.txt

echo "Running database migrations..."
cd backend
alembic upgrade head

echo "Seeding default data..."
python -m scripts.seed_data

echo "Starting development server..."
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
