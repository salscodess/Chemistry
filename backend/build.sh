#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DIR="${ROOT_DIR}/backend/api"
DASH_DIR="${ROOT_DIR}/backend/dash"

echo "Installing backend dependencies..."

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "Python is required but not found in PATH." >&2
  exit 1
fi

if [[ ! -d "${API_DIR}" || ! -d "${DASH_DIR}" ]]; then
  echo "Run this script from inside the Chemistry repository." >&2
  exit 1
fi

"${PYTHON_BIN}" -m pip install -r "${API_DIR}/requirements.txt"
"${PYTHON_BIN}" -m pip install -r "${DASH_DIR}/requirements.txt"

echo "Backend dependency install completed."
