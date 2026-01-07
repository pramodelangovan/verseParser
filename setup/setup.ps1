# PowerShell wrapper for the Verse Parser setup script
# Usage:
#   .\setup.ps1              Run both setup and build
#   .\setup.ps1 -Option setup   Only setup (venv + dependencies)
#   .\setup.ps1 -Option build   Only build (PyInstaller)

param(
    [string]$Option = ""
)

$ErrorActionPreference = "Stop"

try {
    Write-Host ""

    # Validate option
    if ($Option -and $Option -notin @("setup", "build")) {
        Write-Host "Error: Unknown option '$Option'" -ForegroundColor Red
        Write-Host ""
        Write-Host "Usage:" -ForegroundColor Yellow
        Write-Host "  .\setup.ps1                  # Run both setup and build" -ForegroundColor Yellow
        Write-Host "  .\setup.ps1 -Option setup    # Only setup (venv + dependencies)" -ForegroundColor Yellow
        Write-Host "  .\setup.ps1 -Option build    # Only build (PyInstaller)" -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }

    if ($Option) {
        Write-Host "Starting Verse Parser $Option..." -ForegroundColor Green
    } else {
        Write-Host "Starting Verse Parser setup and build..." -ForegroundColor Green
    }
    Write-Host ""

    # Navigate to parent directory
    Push-Location (Split-Path -Parent $PSScriptRoot)

    # Run the Python setup script with optional argument
    if ($Option) {
        python setup\setup.py $Option
    } else {
        python setup\setup.py
    }

    if ($LASTEXITCODE -ne 0) {
        Pop-Location
        Write-Host ""
        Write-Host "Error: Operation failed. Please check the output above." -ForegroundColor Red
        Write-Host ""
        exit 1
    }

    Pop-Location

    Write-Host ""
    Write-Host "Operation completed successfully!" -ForegroundColor Green
    Write-Host ""
}
catch {
    Write-Host ""
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    exit 1
}
