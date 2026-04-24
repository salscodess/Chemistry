#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${PROJECT_ROOT}/build"
DIST_DIR="${PROJECT_ROOT}/dist"
APP_NAME="chemistry-desktop"
APPDIR="${BUILD_DIR}/${APP_NAME}.AppDir"
VENV_DIR="${PROJECT_ROOT}/.venv"
APPIMAGETOOL="${BUILD_DIR}/appimagetool-x86_64.AppImage"
APPIMAGE_OUTPUT="${DIST_DIR}/Chemistry-Desktop-x86_64.AppImage"
VENV_PYTHON=""

mkdir -p "${BUILD_DIR}" "${DIST_DIR}"

if ! python3 - <<'PY'
import tkinter
PY
then
  echo "Missing Tkinter runtime for the system Python used to package this app." >&2
  echo "Install it and retry:" >&2
  echo "  sudo apt update && sudo apt install -y python3-tk tk-dev" >&2
  exit 1
fi

if [[ ! -x "${VENV_DIR}/bin/python" && ! -x "${VENV_DIR}/bin/python3" ]]; then
  rm -rf "${VENV_DIR}"
  if python3 -m venv "${VENV_DIR}" 2>/dev/null; then
    :
  else
    # Fallback for minimal environments where ensurepip/python3-venv is unavailable.
    python3 -m pip install --user virtualenv
    python3 -m virtualenv "${VENV_DIR}"
  fi
fi

if [[ -x "${VENV_DIR}/bin/python" ]]; then
  VENV_PYTHON="${VENV_DIR}/bin/python"
elif [[ -x "${VENV_DIR}/bin/python3" ]]; then
  VENV_PYTHON="${VENV_DIR}/bin/python3"
else
  echo "Virtual environment was created but no python executable was found." >&2
  exit 1
fi

# Ensure pip exists in the venv even in stripped-down Python environments.
if ! "${VENV_PYTHON}" -m pip --version >/dev/null 2>&1; then
  if ! "${VENV_PYTHON}" -m ensurepip --upgrade >/dev/null 2>&1; then
    # Recreate with virtualenv when stdlib venv/ensurepip is not available.
    rm -rf "${VENV_DIR}"
    python3 -m pip install --user virtualenv
    python3 -m virtualenv "${VENV_DIR}"
    if [[ -x "${VENV_DIR}/bin/python" ]]; then
      VENV_PYTHON="${VENV_DIR}/bin/python"
    else
      VENV_PYTHON="${VENV_DIR}/bin/python3"
    fi
  fi
fi

"${VENV_PYTHON}" -m pip install --upgrade pip
"${VENV_PYTHON}" -m pip install -r "${PROJECT_ROOT}/requirements.txt" pyinstaller

# Build the bundled Linux executable first.
"${VENV_PYTHON}" -m PyInstaller \
  --noconfirm \
  --clean \
  --name "${APP_NAME}" \
  --onefile \
  --windowed \
  "${PROJECT_ROOT}/desktop_client.py"

rm -rf "${APPDIR}"
mkdir -p "${APPDIR}/usr/bin"
mkdir -p "${APPDIR}/usr/share/applications"
mkdir -p "${APPDIR}/usr/share/icons/hicolor/scalable/apps"

cp "${DIST_DIR}/${APP_NAME}" "${APPDIR}/usr/bin/${APP_NAME}"
cp "${PROJECT_ROOT}/scripts/chemistry-desktop.desktop" "${APPDIR}/usr/share/applications/${APP_NAME}.desktop"
cp "${PROJECT_ROOT}/assets/chemistry-desktop.svg" "${APPDIR}/usr/share/icons/hicolor/scalable/apps/${APP_NAME}.svg"

cat > "${APPDIR}/AppRun" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${HERE}/usr/bin/chemistry-desktop" "$@"
EOF
chmod +x "${APPDIR}/AppRun"

# AppImage tooling expects these convenience links/files at AppDir root.
cp "${APPDIR}/usr/share/applications/${APP_NAME}.desktop" "${APPDIR}/${APP_NAME}.desktop"
cp "${APPDIR}/usr/share/icons/hicolor/scalable/apps/${APP_NAME}.svg" "${APPDIR}/${APP_NAME}.svg"

if [[ ! -x "${APPIMAGETOOL}" ]]; then
  curl -L "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" -o "${APPIMAGETOOL}"
  chmod +x "${APPIMAGETOOL}"
fi

APPIMAGE_EXTRACT_AND_RUN=1 ARCH=x86_64 "${APPIMAGETOOL}" "${APPDIR}" "${APPIMAGE_OUTPUT}"
chmod +x "${APPIMAGE_OUTPUT}"

echo "AppImage created at: ${APPIMAGE_OUTPUT}"
