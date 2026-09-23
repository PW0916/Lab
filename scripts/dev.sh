#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT"
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!
trap 'kill $API_PID' EXIT
cd frontend
if [ ! -d node_modules ]; then
  npm install
fi
npm run dev -- --host 0.0.0.0 --port 5173
