#!/usr/bin/env bash
# Production-style: build the UI and serve it from FastAPI on :8000
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/frontend"
if [ ! -d node_modules ]; then
  npm install
fi
npm run build
cd "$ROOT"
export PYTHONPATH="$ROOT"
exec python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
