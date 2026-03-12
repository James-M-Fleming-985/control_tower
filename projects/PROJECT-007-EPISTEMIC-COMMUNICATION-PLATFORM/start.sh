#!/bin/bash

echo "Running database migrations..."
alembic upgrade head || echo "WARNING: Alembic migration failed — app startup will create tables as fallback"

echo "Starting application..."
exec uvicorn epistemic_platform.main:app --host 0.0.0.0 --port "${PORT:-8000}"
