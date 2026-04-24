#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$PROJECT_ROOT"

if ! python3 -c "import tkinter" >/dev/null 2>&1; then
  echo "Tkinter is missing from your Python installation." >&2
  echo "Install it first, then rebuild:" >&2
  echo "  sudo apt update && sudo apt install -y python3-tk" >&2
  exit 1
fi

python3 -m pip install -r requirements.txt
python3 -m pip install pyinstaller

pyinstaller \
  --name chemistry-desktop \
  --onefile \
  --windowed \
  desktop_client.py

echo "Linux binary created at: $PROJECT_ROOT/dist/chemistry-desktop"
