#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
LAUNCHER="${FRONTEND_DIR}/scripts/launch_linux.sh"
ICON_PATH="${FRONTEND_DIR}/assets/chemistry.png"

DESKTOP_DIR="${HOME}/.local/share/applications"
BIN_DIR="${HOME}/.local/bin"
BIN_LINK="${BIN_DIR}/chemistry-desktop"
DESKTOP_FILE="${DESKTOP_DIR}/chemistry-desktop.desktop"

mkdir -p "${DESKTOP_DIR}"
mkdir -p "${BIN_DIR}"
ln -sf "${LAUNCHER}" "${BIN_LINK}"

cat > "${DESKTOP_FILE}" <<EOF
[Desktop Entry]
Type=Application
Name=Chemistry Desktop Client
Comment=Route Chemistry tasks to cloud, hybrid, or local APIs
Exec=${BIN_LINK}
Icon=${ICON_PATH}
Terminal=false
Categories=Utility;Development;
StartupNotify=true
EOF

chmod 644 "${DESKTOP_FILE}"
chmod +x "${BIN_LINK}"

echo "Installed desktop entry: ${DESKTOP_FILE}"
echo "Installed launcher link: ${BIN_LINK}"
echo "If icon is missing, place one at: ${ICON_PATH}"
