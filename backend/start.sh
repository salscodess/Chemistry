#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="${ROOT_DIR}/api"
DASH_DIR="${ROOT_DIR}/dash"

if [[ ! -f "${API_DIR}/main.py" || ! -f "${DASH_DIR}/dashboard_api.py" ]]; then
  echo "Backend structure is missing expected files under backend/api or backend/dash." >&2
  exit 1
fi

if [[ ! -x "${ROOT_DIR}/.venv/bin/python" ]]; then
  echo "No backend virtualenv found. Run ./build.sh first." >&2
  exit 1
fi

source "${ROOT_DIR}/.venv/bin/activate"

echo "Starting Chemistry backend services..."
echo "Dashboard: http://localhost:8001"
echo "API docs:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both services."

uvicorn dashboard_api:app --host 0.0.0.0 --port 8001 --reload --app-dir "${DASH_DIR}" &
DASH_PID=$!

uvicorn main:app --host 0.0.0.0 --port 8000 --reload --app-dir "${API_DIR}" &
API_PID=$!

cleanup() {
  echo ""
  echo "Stopping services..."
  kill "${DASH_PID}" "${API_PID}" 2>/dev/null || true
}

trap cleanup EXIT INT TERM
wait
