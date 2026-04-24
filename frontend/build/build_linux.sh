#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$PROJECT_ROOT"
python3 -m pip install -r requirements.txt
python3 -m pip install pyinstaller

pyinstaller \
  --name chemistry-desktop \
  --onefile \
  --windowed \
  desktop_client.py

echo "Linux binary created at: $PROJECT_ROOT/dist/chemistry-desktop"
