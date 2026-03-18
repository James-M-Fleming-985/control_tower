#!/bin/bash

echo "Running database migrations..."
timeout 30 alembic upgrade head || echo "WARNING: Alembic migration failed or timed out — app startup will create tables as fallback"

echo "Starting application..."
exec uvicorn epistemic_platform.main:app --host 0.0.0.0 --port "${PORT:-8000}"
