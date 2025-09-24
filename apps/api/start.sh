#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8080}"
: "${API_INTERNAL_BASE_URL:="http://localhost:${PORT}"}"
export API_INTERNAL_BASE_URL

DB_WAIT_ENABLED="${DB_WAIT_ENABLED:-true}"
DB_WAIT_MAX_SECONDS="${DB_WAIT_MAX_SECONDS:-60}"

# Best-effort DB readiness check (non-fatal)
if [[ "${DB_WAIT_ENABLED}" == "true" && -n "${DIRECT_URL:-}" ]]; then
  echo "Waiting for database (up to ${DB_WAIT_MAX_SECONDS}s)..."
  python - <<PY || echo "DB not ready after wait; continuing startup"
import os, time, socket, sys
import psycopg

def host_from_url(url: str) -> str:
    try:
        # naive parse: postgresql://user:pass@host:port/db
        hostpart = url.split('@', 1)[1]
        host = hostpart.split('/', 1)[0].split(':', 1)[0]
        return host
    except Exception:
        return ''

url = os.environ.get('DIRECT_URL', '')
max_seconds = int(os.environ.get('DB_WAIT_MAX_SECONDS', '60'))
start = time.time()
while time.time() - start < max_seconds:
    try:
        with psycopg.connect(url, connect_timeout=3) as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT 1;')
                print('Database is ready')
                sys.exit(0)
    except Exception as e:
        # DNS errors or connection errors: print once per loop
        print('DB not ready yet...', repr(e))
        time.sleep(2)
# timeout: return non-zero to trigger || handler in shell
sys.exit(1)
PY
fi

# Generate Prisma client (safe to repeat)
prisma generate || true

# Apply migrations (non-fatal; app can run read-only even if fails)
prisma migrate deploy || echo "Prisma migrate deploy failed; continuing startup"

# Start API
exec uvicorn src.main:app --host 0.0.0.0 --port "${PORT}" --proxy-headers
