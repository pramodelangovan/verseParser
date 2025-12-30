@echo off
REM Batch wrapper for the Verse Parser setup script
REM This script sets up the project, installs dependencies, and builds the executable

setlocal enabledelayedexpansion

cd /d %~dp0..
python setup\setup.py
if errorlevel 1 (
    echo.
    echo Error: Setup failed. Please check the output above.
    pause
    exit /b 1
)

pause
