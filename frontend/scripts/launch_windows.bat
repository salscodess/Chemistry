@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%\.."
cd /d "%PROJECT_ROOT%"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" desktop_client.py
) else (
    python desktop_client.py
)
