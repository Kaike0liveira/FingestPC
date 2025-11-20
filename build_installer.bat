@echo off
REM Execute build_installer.ps1 with an ExecutionPolicy bypass for this run only
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0build_installer.ps1" %*
pause
