#!/bin/bash
# Start API + frontend in the Codespace (background, logs in /tmp).
# In Codespaces the browser talks to the forwarded API URL, not localhost:8000,
# so NEXT_PUBLIC_API_URL is set from CODESPACE_NAME before Next starts.
cd /workspaces/blood-bank

if [ -n "$CODESPACE_NAME" ]; then
  DOMAIN="${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}"
  export NEXT_PUBLIC_API_URL="https://${CODESPACE_NAME}-8000.${DOMAIN}"
  echo "API URL for browser: $NEXT_PUBLIC_API_URL"
else
  export NEXT_PUBLIC_API_URL="http://localhost:8000"
fi

pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "next dev" 2>/dev/null || true
sleep 1

cd apps/api
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/api.log 2>&1 &
cd ../web
nohup npm run dev > /tmp/web.log 2>&1 &
cd ../..

sleep 3
echo "API:  http://localhost:8000/docs  (log: /tmp/api.log)"
echo "Web:  http://localhost:3000       (log: /tmp/web.log)"
echo "Login: admin@bloodbank.local / Admin@123456"
