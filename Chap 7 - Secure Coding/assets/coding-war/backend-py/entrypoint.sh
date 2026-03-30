#!/bin/sh
set -e

echo "Running database migrations..."
cd /app
PYTHONPATH=/app alembic upgrade head
echo "Migrations complete. Starting server..."

exec uvicorn app.main:top_app --host 0.0.0.0 --port 3000 --workers 4
