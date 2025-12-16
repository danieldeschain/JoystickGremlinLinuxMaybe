#!/bin/bash
# WSL Test Runner for JoystickGremlin Linux Integration
# This script runs the full test suite in a Linux environment

set -e  # Exit on error

echo "========================================="
echo "JoystickGremlin WSL Test Runner"
echo "Testing Linux integration & dependencies"
echo "========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the Windows path converted to WSL path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Working directory: $SCRIPT_DIR"
echo ""

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3 not found! Installing...${NC}"
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
fi

python3 --version
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv_wsl" ]; then
    echo -e "${YELLOW}Creating WSL virtual environment...${NC}"
    python3 -m venv venv_wsl
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv_wsl/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip
echo ""

# Install Linux-specific dependencies
echo -e "${YELLOW}Installing Linux dependencies...${NC}"
echo "This includes: evdev, pyudev, python-uinput"

# Install system dependencies first
sudo apt-get update
sudo apt-get install -y \
    libudev-dev \
    libevdev-dev \
    python3-dev \
    build-essential

# Install Python packages
pip install -r requirements.txt

# Install additional test dependencies
pip install pytest pytest-cov

echo ""
echo -e "${GREEN}Dependencies installed successfully!${NC}"
echo ""

# Show installed packages
echo -e "${YELLOW}Installed Python packages:${NC}"
pip list | grep -E "(evdev|pyudev|uinput|PySide6|reportlab|pytest)"
echo ""

# Run syntax error fixes first (commit these)
echo -e "${YELLOW}Checking for syntax errors in user_script modules...${NC}"
python3 -m py_compile gremlin/user_script_modules/registries.py || echo -e "${RED}Syntax error in registries.py${NC}"
python3 -m py_compile gremlin/user_script_modules/plugins.py || echo -e "${RED}Syntax error in plugins.py${NC}"
echo ""

# Run the test suite
echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}Running Test Suite${NC}"
echo -e "${YELLOW}=========================================${NC}"
echo ""

# Run tests with coverage
pytest tests/refactoring/ \
    -v \
    --tb=short \
    --color=yes \
    --cov=gremlin \
    --cov=action_plugins \
    --cov-report=term-missing \
    --cov-report=html:htmlcov_wsl

TEST_EXIT_CODE=$?

echo ""
echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}Test Results Summary${NC}"
echo -e "${YELLOW}=========================================${NC}"
echo ""

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${RED}✗ Some tests failed (exit code: $TEST_EXIT_CODE)${NC}"
fi

echo ""
echo -e "Coverage report: ${YELLOW}htmlcov_wsl/index.html${NC}"
echo ""

# Deactivate venv
deactivate

exit $TEST_EXIT_CODE
