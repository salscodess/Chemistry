# Chemistry Desktop Client Setup

This directory now contains the desktop client for Chemistry.

## Features

- Desktop GUI for API interaction (Tkinter)
- Route selection (`cloud`, `hybrid`, `local`)
- ALT+0 shortcut to send routed request
- JSON request data editor and formatted response output
- Linux launcher and `.desktop` integration scripts
- Build scripts for Windows and Linux binaries via PyInstaller

## Quick Run (Development)

From repo root:

```bash
cd frontend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python desktop_client.py
```

Default API URL is `http://localhost:8000`.

## Linux Native Launcher

Run with:

```bash
./scripts/launch_linux.sh
```

This script creates/uses `frontend/.venv`, installs dependencies, and launches the app.

## Install Linux Desktop Entry

To install a desktop-menu shortcut:

```bash
./scripts/install_linux_desktop_entry.sh
```

This writes:
- `~/.local/share/applications/chemistry-desktop.desktop`
- `~/.local/bin/chemistry-desktop`

You can then run `chemistry-desktop` from your app launcher or terminal.

## Build Standalone Binaries

### Linux

```bash
cd frontend
./build/build_linux.sh
```

Output binary:
- `frontend/dist/chemistry-desktop`

### Windows

On Windows PowerShell:

```powershell
cd frontend
./build/build_windows.ps1
```

Output executable:
- `frontend/dist/ChemistryDesktop.exe`
