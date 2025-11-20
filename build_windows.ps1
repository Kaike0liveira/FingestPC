# PowerShell script to build a Windows executable using PyInstaller
# Requirements: install PyInstaller in your Python environment: pip install pyinstaller

$here = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $here

# ensure pyinstaller is available
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
  Write-Error "pyinstaller not found in PATH. Install it with: pip install pyinstaller"
  exit 1
}

# Build single-file exe, include templates and static folders
pyinstaller --onefile `
  --add-data "templates;templates" `
  --add-data "static;static" `
  --hidden-import sklearn `
  --hidden-import pandas `
  run_app.py

Write-Output "Build finished. Dist folder contains the executable (run_app.exe)."
