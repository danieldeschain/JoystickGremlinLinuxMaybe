#!/bin/bash
# Simplified WSL Test Runner - Direct installation without venv
# For testing Linux dependencies in JoystickGremlin

set -e

echo "========================================="
echo "JoystickGremlin WSL Test Runner (Simple)"
echo "========================================="
echo ""

# Check Python
python3 --version || { echo "Python3 not found!"; exit 1; }
echo ""

# Install pytest if not present
echo "Checking pytest..."
python3 -m pip --version || { echo "pip not found!"; exit 1; }
python3 -c "import pytest" 2>/dev/null || python3 -m pip install --user pytest pytest-cov

# Try to install Linux dependencies (may need sudo)
echo ""
echo "Installing Linux dependencies..."
echo "NOTE: Some dependencies may require sudo password"
python3 -m pip install --user evdev pyudev || echo "Warning: Could not install evdev/pyudev (may need system packages)"
python3 -m pip install --user PySide6 reportlab dill || echo "Warning: Some optional dependencies failed"

echo ""
echo "Installed packages:"
python3 -m pip list --user | grep -E "(pytest|evdev|pyudev|PySide6|reportlab)" || echo "No packages found"

echo ""
echo "========================================="
echo "Running Tests"
echo "========================================="
echo ""

# Run tests
python3 -m pytest tests/refactoring/ -v --tb=short --color=yes 2>&1

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "✓ All tests passed!"
else
    echo "✗ Some tests failed (exit code: $exit_code)"
fi

exit $exit_code
