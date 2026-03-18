#!/bin/bash
set -o pipefail

# Diagnostic: show masked DATABASE_URL so we can debug connection issues
if [ -n "$DATABASE_URL" ]; then
  echo "DATABASE_URL scheme: $(echo "$DATABASE_URL" | grep -oP '^[^:]+')://***@$(echo "$DATABASE_URL" | grep -oP '@\K[^?]+')"
else
  echo "WARNING: DATABASE_URL is not set"
fi

echo "Running database migrations..."
timeout 30 alembic upgrade head || echo "WARNING: Alembic migration failed or timed out — app startup will create tables as fallback"

echo "Verifying app import..."
python -c "from epistemic_platform.main import app; print(f'App loaded: {len(app.routes)} routes')" || echo "WARNING: App import check failed"

echo "Starting application..."
exec uvicorn epistemic_platform.main:app --host 0.0.0.0 --port "${PORT:-8000}"
