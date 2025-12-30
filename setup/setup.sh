#!/bin/bash
# Shell wrapper for the Verse Parser setup script
# This script sets up the project, installs dependencies, and builds the executable

set -e

echo ""
echo "Starting Verse Parser setup..."
echo ""

# Navigate to parent directory
cd "$(dirname "$0")"..

# Run the Python setup script
python3 setup/setup.py

if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Setup failed. Please check the output above."
    echo ""
    exit 1
fi

echo ""
echo "Setup completed successfully!"
echo ""
