# Windows Test Runner for JoystickGremlin
# This script runs tests that don't require Linux-specific dependencies

Write-Host "=========================================" -ForegroundColor Yellow
Write-Host "JoystickGremlin Windows Test Runner" -ForegroundColor Yellow
Write-Host "Testing Windows-compatible modules only" -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Yellow
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Cyan
python --version
Write-Host ""

# Install test dependencies (skip Linux-only packages)
Write-Host "Installing Windows-compatible dependencies..." -ForegroundColor Cyan
pip install pytest pytest-cov PySide6 reportlab dill
Write-Host ""

# Run syntax checks
Write-Host "Checking for syntax errors..." -ForegroundColor Cyan
python -m py_compile gremlin/user_script_modules/registries.py
python -m py_compile gremlin/user_script_modules/plugins.py
Write-Host ""

# Run tests (excluding Linux-specific tests)
Write-Host "=========================================" -ForegroundColor Yellow
Write-Host "Running Test Suite (Windows subset)" -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Yellow
Write-Host ""

python -m pytest tests/refactoring/ `
    -v `
    --tb=short `
    --color=yes `
    -k "not linux" `
    --cov=gremlin `
    --cov=action_plugins `
    --cov-report=term-missing `
    --cov-report=html:htmlcov_windows

$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "=========================================" -ForegroundColor Yellow
Write-Host "Test Results Summary" -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Yellow
Write-Host ""

if ($exitCode -eq 0) {
    Write-Host "✓ All Windows tests passed!" -ForegroundColor Green
} else {
    Write-Host "✗ Some tests failed (exit code: $exitCode)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Coverage report: htmlcov_windows/index.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "NOTE: For full Linux compatibility testing, run: wsl bash run_tests_wsl.sh" -ForegroundColor Yellow
Write-Host ""

exit $exitCode
