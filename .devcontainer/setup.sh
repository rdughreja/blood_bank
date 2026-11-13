#!/bin/bash
# Codespaces setup — runs once when the Codespace is created.
# Installs deps, waits for Postgres, runs migrations + seed.
# Safe to re-run: pip/npm are idempotent, seed is idempotent, alembic is a no-op at head.
set -e
cd /workspaces/blood-bank

echo "=== Waiting for Postgres (db:5432) ==="
until pg_isready -h db -U bloodbank -q; do sleep 2; done
echo "Postgres is up."

echo "=== API .env ==="
if [ ! -f .env ]; then cp .env.example .env; fi
# In Codespaces the DB host is the `db` service, not localhost.
sed -i 's|DATABASE_URL=.*|DATABASE_URL=postgresql+psycopg://bloodbank:bloodbank_dev@db:5432/bloodbank|' .env
sed -i 's|REDIS_URL=.*|REDIS_URL=redis://redis:6379/0|' .env
# Random SECRET_KEY if still the placeholder.
if grep -q "change-me-to-a-long-random-string" .env; then
  python3 -c "import secrets; print(secrets.token_urlsafe(48))" > /tmp/secret_key.txt
  KEY=$(cat /tmp/secret_key.txt)
  sed -i "s|SECRET_KEY=.*|SECRET_KEY=$KEY|" .env
  rm /tmp/secret_key.txt
fi
# CORS must allow the forwarded Codespaces web URL as well as localhost.
if [ -n "$CODESPACE_NAME" ]; then
  DOMAIN="${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}"
  WEB_URL="https://${CODESPACE_NAME}-3000.${DOMAIN}"
  sed -i "s|CORS_ORIGINS=.*|CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,${WEB_URL}|" .env
else
  sed -i "s|CORS_ORIGINS=.*|CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000|" .env
fi
cp .env apps/api/.env

echo "=== Installing Python deps ==="
pip install -r requirements.txt

echo "=== Migrations + seed ==="
cd apps/api
python -m alembic upgrade head
python -m alembic current
python seed.py
cd ../..

echo "=== Installing frontend deps ==="
cd apps/web
npm install
cd ../..

echo "=== Setup done ==="
echo "Start everything with: bash .devcontainer/start.sh"
echo "Then open the forwarded port 3000 and log in as admin@bloodbank.local / Admin@123456"
