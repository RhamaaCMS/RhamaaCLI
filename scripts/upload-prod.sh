#!/bin/bash

# Upload to Production PyPI
set -e

echo "🚀 Uploading RhamaaCLI to Production PyPI..."

# Check if dist directory exists
if [ ! -d "dist" ]; then
    echo "❌ No dist directory found. Run build.sh first."
    exit 1
fi

# Confirmation prompt
read -p "⚠️  Are you sure you want to upload to PRODUCTION PyPI? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Upload cancelled."
    exit 1
fi

# Upload to Production PyPI
echo "📤 Uploading to Production PyPI..."
python -m twine upload dist/*

echo "✅ Upload to Production PyPI completed!"
echo ""
echo "To install:"
echo "  pip install rhamaa"