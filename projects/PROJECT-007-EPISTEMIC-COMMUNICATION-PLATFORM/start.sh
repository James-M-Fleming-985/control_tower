#!/bin/bash
set -o pipefail

# Diagnostic: show masked DATABASE_URL so we can debug connection issues
if [ -n "$DATABASE_URL" ]; then
  echo "DATABASE_URL scheme: $(echo "$DATABASE_URL" | grep -oP '^[^:]+')://***@$(echo "$DATABASE_URL" | grep -oP '@\K[^?]+')"
else
  echo "WARNING: DATABASE_URL is not set"
fi

# Auto-stamp: if tables exist but Alembic doesn't know about them,
# stamp the initial migration so subsequent migrations can run.
echo "Checking if Alembic auto-stamp is needed..."
python3 -c "
import sys
try:
    from epistemic_platform.config import get_settings
    settings = get_settings()
    # Use synchronous psycopg2 / raw connection for this one-off check
    db_url = settings.database_url.replace('postgresql+asyncpg://', 'postgresql://')
    import sqlalchemy
    engine = sqlalchemy.create_engine(db_url)
    insp = sqlalchemy.inspect(engine)
    tables = insp.get_table_names()
    has_app_tables = 'user_profiles' in tables
    has_alembic = 'alembic_version' in tables
    if has_app_tables and not has_alembic:
        print('Tables exist without Alembic tracking - stamping d842c1e0030d')
        import subprocess
        result = subprocess.run(['alembic', 'stamp', 'd842c1e0030d'], capture_output=True, text=True)
        print(f'Stamp stdout: {result.stdout}')
        print(f'Stamp stderr: {result.stderr}')
        print(f'Stamp exit code: {result.returncode}')
    elif has_app_tables and has_alembic:
        with engine.connect() as conn:
            row = conn.execute(sqlalchemy.text('SELECT version_num FROM alembic_version')).fetchone()
            ver = row[0] if row else 'no version'
            print(f'Alembic already tracking: {ver}')
    else:
        print('Fresh database - no stamp needed')
    engine.dispose()
except Exception as e:
    print(f'Auto-stamp check failed (non-fatal): {e}')
    sys.exit(0)
" || echo "WARNING: Auto-stamp script failed (non-fatal)"

echo "Running database migrations..."
ALEMBIC_OUTPUT=$(timeout 60 alembic upgrade head 2>&1) || {
  ALEMBIC_EXIT=$?
  echo "ERROR: Alembic migration failed (exit code $ALEMBIC_EXIT)"
  echo "Alembic output: $ALEMBIC_OUTPUT"
  echo "Attempting to continue anyway..."
}
echo "Alembic output: $ALEMBIC_OUTPUT"

echo "Verifying app import..."
python -c "from epistemic_platform.main import app; print(f'App loaded: {len(app.routes)} routes')" || echo "WARNING: App import check failed"

echo "Starting application..."
exec uvicorn epistemic_platform.main:app --host 0.0.0.0 --port "${PORT:-8000}"
