@echo off
REM Batch wrapper for the Verse Parser setup script
REM Usage:
REM   setup.bat              Run both setup and build
REM   setup.bat setup        Only setup (venv + dependencies)
REM   setup.bat build        Only build (PyInstaller)

setlocal enabledelayedexpansion

if "%1"=="" (
    echo.
    echo Starting Verse Parser setup and build...
) else if "%1"=="setup" (
    echo.
    echo Starting Verse Parser setup...
) else if "%1"=="build" (
    echo.
    echo Starting Verse Parser build...
) else (
    echo.
    echo Error: Unknown option '%1'
    echo.
    echo Usage:
    echo   setup.bat        Run both setup and build
    echo   setup.bat setup  Only setup (venv + dependencies)
    echo   setup.bat build  Only build (PyInstaller)
    echo.
    pause
    exit /b 1
)

cd /d %~dp0..
python setup\setup.py %1
if errorlevel 1 (
    echo.
    echo Error: Operation failed. Please check the output above.
    pause
    exit /b 1
)

echo.
echo Operation completed successfully!
echo.
pause
