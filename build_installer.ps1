# Build Inno Setup installer if Inno's ISCC is installed (Inno Setup compiler)
# Download Inno Setup: https://jrsoftware.org/isdl.php

$here = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $here

$iss = Join-Path $here 'installer.iss'
if (-not (Test-Path $iss)) { Write-Error 'installer.iss not found'; exit 1 }

# find ISCC
$found = Get-Command iscc.exe -ErrorAction SilentlyContinue
if (-not $found) {
  Write-Error "ISCC (Inno Setup Compiler) not found in PATH. Install Inno Setup and ensure iscc.exe is on PATH."
  exit 1
}

# ensure dist/run_app.exe exists
if (-not (Test-Path (Join-Path $here 'dist\run_app.exe'))) {
  Write-Error "dist\run_app.exe not found. Run build_windows.ps1 first."
  exit 1
}

# run compiler
Write-Output "Running ISCC to build installer..."
& iscc.exe $iss
Write-Output "If successful, installer will be in the project root as defined by installer.iss (Fingest_Installer.exe)."
