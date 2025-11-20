# Build a redistributable ZIP containing the exe and required files
# Requires that you already ran build_windows.ps1 and produced dist\run_app.exe

$here = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $here

$distExe = Join-Path $here 'dist\run_app.exe'
if (-not (Test-Path $distExe)) {
  Write-Error "Executable not found at $distExe. Run build_windows.ps1 first."
  exit 1
}

$outDir = Join-Path $here 'package'
Remove-Item -Recurse -Force $outDir -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $outDir | Out-Null

# copy exe
Copy-Item $distExe -Destination $outDir
# copy static files and templates for reference
Copy-Item "templates" -Destination $outDir -Recurse -Force
Copy-Item "static" -Destination $outDir -Recurse -Force
Copy-Item "README_ANDROID.md" -Destination $outDir -Force
Copy-Item "README.md" -Destination $outDir -Force

# create a simple launcher script for users (PowerShell)
$launcher = @"
# Lance o servidor local
.\run_app.exe
"@
Set-Content -Path (Join-Path $outDir 'run.bat') -Value ".\run_app.exe`r`n" -Encoding ASCII

# zip
$zipName = Join-Path $here "Fingest_windows_package.zip"
if (Test-Path $zipName) { Remove-Item $zipName -Force }
Add-Type -AssemblyName System.IO.Compression.FileSystem
[IO.Compression.ZipFile]::CreateFromDirectory($outDir, $zipName)
Write-Output "Package created: $zipName"

# cleanup
Remove-Item -Recurse -Force $outDir
Write-Output "Done. Distribute $zipName to users (contains run_app.exe and assets)."
