#!/bin/bash
# Shell wrapper for the Verse Parser setup script
# Usage:
#   ./setup.sh          Run both setup and build
#   ./setup.sh setup    Only setup (venv + dependencies)
#   ./setup.sh build    Only build (PyInstaller)

set -e

OPTION="${1:-}"

echo ""

# Validate option
if [ -n "$OPTION" ] && [ "$OPTION" != "setup" ] && [ "$OPTION" != "build" ]; then
    echo "Error: Unknown option '$OPTION'"
    echo ""
    echo "Usage:"
    echo "  ./setup.sh          Run both setup and build"
    echo "  ./setup.sh setup    Only setup (venv + dependencies)"
    echo "  ./setup.sh build    Only build (PyInstaller)"
    echo ""
    exit 1
fi

if [ -z "$OPTION" ]; then
    echo "Starting Verse Parser setup and build..."
else
    echo "Starting Verse Parser $OPTION..."
fi
echo ""

# Navigate to parent directory
cd "$(dirname "$0")"..

# Run the Python setup script
if [ -z "$OPTION" ]; then
    python3 setup/setup.py
else
    python3 setup/setup.py "$OPTION"
fi

if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Operation failed. Please check the output above."
    echo ""
    exit 1
fi

echo ""
echo "Operation completed successfully!"
echo ""
