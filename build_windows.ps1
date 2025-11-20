# PowerShell script to build a Windows executable using PyInstaller
# Requirements: install PyInstaller in your Python environment: pip install pyinstaller

$here = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $here

# ensure pyinstaller is available
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
  Write-Error "pyinstaller not found in PATH. Install it with: pip install pyinstaller"
  exit 1
}

# Prepare add-data entries
$addDataArgs = "--add-data `"templates;templates`" --add-data `"static;static`"`

# include icon if present
$iconArg = ""
if (Test-Path "icon.ico") {
  Write-Output "Found icon.ico, will include it in the bundle and use as exe icon."
  $addDataArgs += " --add-data `"icon.ico;.`"`
  $iconArg = "--icon icon.ico"
} else {
  Write-Output "icon.ico not found in project root. To include a custom icon, place an icon.ico file in the project root."
}

# Build single-file exe, include templates and static folders
pyinstaller --onefile $addDataArgs --hidden-import sklearn --hidden-import pandas $iconArg run_app.py

Write-Output "Build finished. Dist folder contains the executable (run_app.exe). If you included an icon it will be embedded." 
