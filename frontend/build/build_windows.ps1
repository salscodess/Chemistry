param(
    [string]$Python = "python",
    [switch]$OneFile
)

$ErrorActionPreference = "Stop"

Push-Location "$PSScriptRoot\.."
try {
    & $Python -m pip install --upgrade pip
    & $Python -m pip install -r requirements.txt pyinstaller

    $target = if ($OneFile) { "--onefile" } else { "--onedir" }

    & $Python -m PyInstaller `
        --noconfirm `
        --windowed `
        $target `
        --name chemistry-desktop `
        desktop_client.py

    Write-Host "Windows build complete."
    if ($OneFile) {
        Write-Host "Output: frontend/dist/chemistry-desktop.exe"
    } else {
        Write-Host "Output: frontend/dist/chemistry-desktop/"
    }
}
finally {
    Pop-Location
}
