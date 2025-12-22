#!/bin/bash

# Pre-release checks for RhamaaCLI
set -e

echo "🔍 Running pre-release checks..."

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "❌ setup.py not found. Run this script from the project root."
    exit 1
fi

# Check version consistency
echo "📋 Checking version consistency..."
SETUP_VERSION=$(python -c "import setup; print(setup.setup().get_version())" 2>/dev/null || echo "unknown")
PYPROJECT_VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)

if [ "$SETUP_VERSION" != "unknown" ] && [ "$SETUP_VERSION" != "$PYPROJECT_VERSION" ]; then
    echo "❌ Version mismatch between setup.py and pyproject.toml"
    echo "   setup.py: $SETUP_VERSION"
    echo "   pyproject.toml: $PYPROJECT_VERSION"
    exit 1
fi

# Test CLI functionality
echo "🧪 Testing CLI functionality..."
python -m rhamaa --help > /dev/null
echo "✅ CLI help works"

python -c "from rhamaa.cli import main; print('CLI import successful')"
echo "✅ CLI import works"

# Check required files
echo "📁 Checking required files..."
REQUIRED_FILES=("README.md" "LICENSE" "setup.py" "pyproject.toml")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required file missing: $file"
        exit 1
    fi
    echo "✅ $file exists"
done

# Check package structure
echo "📦 Checking package structure..."
if [ ! -d "rhamaa" ]; then
    echo "❌ rhamaa package directory not found"
    exit 1
fi

if [ ! -f "rhamaa/__init__.py" ]; then
    echo "❌ rhamaa/__init__.py not found"
    exit 1
fi

if [ ! -f "rhamaa/cli.py" ]; then
    echo "❌ rhamaa/cli.py not found"
    exit 1
fi

echo "✅ Package structure looks good"

# Test import
echo "🐍 Testing Python imports..."
python -c "import rhamaa; print('✅ rhamaa package imports successfully')"
python -c "from rhamaa.cli import main; print('✅ CLI main function imports successfully')"
python -c "from rhamaa.commands.cms.startapp import startapp; print('✅ startapp command imports successfully')"

echo ""
echo "🎉 All pre-release checks passed!"
echo "📋 Summary:"
echo "   Version: $PYPROJECT_VERSION"
echo "   Package: rhamaa"
echo "   CLI: rhamaa"
echo ""
echo "Ready for release! 🚀"