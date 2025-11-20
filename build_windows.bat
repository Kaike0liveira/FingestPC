@echo off
REM Execute build_windows.ps1 with an ExecutionPolicy bypass for this run only
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0build_windows.ps1" %*
REM wrapper completes without interactive pause to support CI/automation
