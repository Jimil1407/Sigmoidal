#!/usr/bin/env bash
set -euo pipefail

# Wait for Postgres
if [[ -n "${DIRECT_URL:-}" ]]; then
  echo "Waiting for database..."
  python - <<'PY'
import os, time
import psycopg

url = os.environ.get('DIRECT_URL')
for i in range(60):
    try:
        with psycopg.connect(url, connect_timeout=3) as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT 1;')
                print('Database is ready')
                raise SystemExit(0)
    except Exception as e:
        print('DB not ready yet...', e)
        time.sleep(2)
raise SystemExit(1)
PY
fi

# Generate Prisma client (safe to repeat)
prisma generate

# Apply migrations (safe if already applied)
prisma migrate deploy

# Start API
exec uvicorn src.main:app --host 0.0.0.0 --port 8080 --proxy-headers
