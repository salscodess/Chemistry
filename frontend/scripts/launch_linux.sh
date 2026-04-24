#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${FRONTEND_DIR}/.venv"
PYTHON_BIN=""

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "Python is required but was not found in PATH." >&2
  exit 1
fi

cd "${FRONTEND_DIR}"

if ! "${PYTHON_BIN}" -c "import tkinter" >/dev/null 2>&1; then
  echo "Tkinter is required but not installed on this system." >&2
  echo "Install it, then re-run:" >&2
  echo "  sudo apt update && sudo apt install -y python3-tk" >&2
  exit 1
fi

if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
  "${VENV_DIR}/bin/pip" install -r requirements.txt
fi

exec "${VENV_DIR}/bin/python" desktop_client.py "$@"
