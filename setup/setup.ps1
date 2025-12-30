# PowerShell wrapper for the Verse Parser setup script
# This script sets up the project, installs dependencies, and builds the executable

$ErrorActionPreference = "Stop"

try {
    Write-Host ""
    Write-Host "Starting Verse Parser setup..." -ForegroundColor Green
    Write-Host ""

    # Navigate to parent directory
    Push-Location (Split-Path -Parent $PSScriptRoot)

    # Run the Python setup script
    python setup\setup.py

    if ($LASTEXITCODE -ne 0) {
        Pop-Location
        Write-Host ""
        Write-Host "Error: Setup failed. Please check the output above." -ForegroundColor Red
        Write-Host ""
        exit 1
    }

    Pop-Location

    Write-Host ""
    Write-Host "Setup completed successfully!" -ForegroundColor Green
    Write-Host ""
}
catch {
    Write-Host ""
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    exit 1
}
