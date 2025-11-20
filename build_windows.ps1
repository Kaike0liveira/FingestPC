# PowerShell script to build a Windows executable using PyInstaller
# Requirements: install PyInstaller in your Python environment: pip install pyinstaller

$here = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $here

# ensure pyinstaller is available
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
  Write-Error "pyinstaller not found in PATH. Install it with: pip install pyinstaller"
  exit 1
}

# find pyinstaller executable (prefer venv)
$pyinstallerCmd = (Get-Command pyinstaller.exe -ErrorAction SilentlyContinue).Source
if (-not $pyinstallerCmd) {
  $possible = Join-Path $PSScriptRoot 'venv\Scripts\pyinstaller.exe'
  if (Test-Path $possible) { $pyinstallerCmd = $possible }
}
if (-not $pyinstallerCmd) {
  Write-Error "pyinstaller not found. Install it in the project's venv or ensure it's on PATH."
  exit 1
}

# build argument list
$args = @('--onefile')
$args += '--add-data'; $args += 'templates;templates'
$args += '--add-data'; $args += 'static;static'

if (Test-Path (Join-Path $PSScriptRoot 'icon.ico')) {
  Write-Output "Found icon.ico, will include it in the bundle and use as exe icon."
  $args += '--add-data'; $args += 'icon.ico;.'
  $args += '--icon'; $args += 'icon.ico'
} else {
  Write-Output "icon.ico not found in project root. To include a custom icon, place an icon.ico file in the project root."
}

$args += '--hidden-import'; $args += 'sklearn'
$args += '--hidden-import'; $args += 'pandas'
$args += 'run_app.py'

Write-Output "Running: $pyinstallerCmd $($args -join ' ')"
& $pyinstallerCmd @args

Write-Output "Build finished. Dist folder contains the executable (run_app.exe). If you included an icon it will be embedded." 
