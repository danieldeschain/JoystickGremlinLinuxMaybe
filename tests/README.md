# JoystickGremlin Test Suite

Comprehensive test suite for Phases 5-9 refactoring validation.

## Test Structure

```
tests/
├── conftest.py                    # Pytest configuration & fixtures
├── refactoring/
│   ├── test_01_imports.py         # Import smoke tests (33 modules)
│   ├── test_02_backward_compatibility.py  # Legacy import paths
│   ├── test_03_dependency_analysis.py     # Circular dependency checks
│   └── test_04_integration.py     # Functionality integration tests
```

## Running Tests

### On Windows (Partial)

Windows can only test **Windows-compatible modules** (excludes Linux-specific dependencies like `evdev`, `pyudev`):

```powershell
# PowerShell
.\run_tests_windows.ps1
```

Or manually:
```powershell
python -m pytest tests/refactoring/ -v
```

### On Linux / WSL (Full Suite)

**Recommended** for complete validation including all Linux dependencies:

```bash
# In WSL/Linux
bash run_tests_wsl.sh
```

Or manually:
```bash
# Create venv
python3 -m venv venv_wsl
source venv_wsl/bin/activate

# Install all dependencies (including Linux-specific)
pip install -r requirements.txt
pip install pytest pytest-cov

# Run tests
pytest tests/refactoring/ -v --cov=gremlin --cov=action_plugins
```

### Quick Test (Single Command)

```bash
# From Windows, run in WSL
wsl bash run_tests_wsl.sh
```

## Test Coverage

### Phase 5 - Module Extraction (18 modules)
- ✅ device.py → 7 modules
- ✅ code_runner.py → 3 modules  
- ✅ map_to_vjoy → 3 modules
- ✅ ui/profile.py → 5 modules

### Phase 6 - Dependency Cleanup
- ✅ Circular dependency elimination
- ✅ TYPE_CHECKING guards
- ✅ Domain layer import fixes

### Phase 7 - user_script.py (4 modules)
- ✅ Registries, plugins, script, variables separation

### Phase 8 - config.py (7 modules + facade)
- ✅ Facade pattern implementation
- ✅ Singleton behavior preservation

### Phase 9 - cheatsheet.py (4 modules)
- ✅ Data, layout, generators, helpers separation

## What Tests Cover

1. **Import Smoke Tests** (`test_01_imports.py`)
   - All 33 modules can be imported
   - No ImportError or ModuleNotFoundError
   - Package structure integrity

2. **Backward Compatibility** (`test_02_backward_compatibility.py`)
   - Legacy import paths work via re-exports
   - Class identity preserved (singleton patterns)
   - 100% backward compatibility

3. **Dependency Analysis** (`test_03_dependency_analysis.py`)
   - Zero circular dependencies
   - Module independence verification
   - Import cleanliness (TYPE_CHECKING usage)

4. **Integration Tests** (`test_04_integration.py`)
   - Core functionality preserved
   - Singleton patterns work
   - Class methods accessible
   - Cross-module integration

## Dependencies

### Required for All Tests
- `pytest` >= 8.0
- `pytest-cov` (for coverage reports)

### Platform-Specific

**Linux/WSL Required:**
- `evdev` - Linux input device interface
- `pyudev` - udev device detection
- `python-uinput` - Virtual input device creation

**Optional (both platforms):**
- `PySide6` - Qt GUI framework (UI tests)
- `reportlab` - PDF generation (cheatsheet tests)

## Expected Results

### Full Suite (Linux/WSL)
```
tests/refactoring/test_01_imports.py .................... [ 50%]
tests/refactoring/test_02_backward_compatibility.py .... [ 75%]
tests/refactoring/test_03_dependency_analysis.py ....... [ 87%]
tests/refactoring/test_04_integration.py ............... [100%]

========== 60+ passed in X.XXs ==========
```

### Windows Subset
Some tests will be **skipped** due to missing Linux dependencies:
```
tests/refactoring/test_01_imports.py ..........sss...... [ 50%]
tests/refactoring/test_02_backward_compatibility.py .... [ 75%]
tests/refactoring/test_03_dependency_analysis.py ....... [ 87%]
tests/refactoring/test_04_integration.py .....sssss.... [100%]

========== XX passed, XX skipped in X.XXs ==========
```

## Continuous Integration

For CI/CD, use the WSL runner:
```yaml
# .github/workflows/test.yml example
- name: Run Tests in WSL
  run: wsl bash run_tests_wsl.sh
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'evdev'"
- **Solution**: Run tests in WSL/Linux environment
- Or: Install Linux system dependencies (see `run_tests_wsl.sh`)

### "No module named 'PySide6'"
- **Solution**: `pip install PySide6` (optional dependency)
- Or: Tests will skip GUI-related functionality

### WSL not found
- **Install WSL**: `wsl --install -d Ubuntu-24.04`
- **Enable WSL 2**: `wsl --set-version Ubuntu-24.04 2`

## Coverage Reports

After running tests, coverage reports are generated:

- **Linux/WSL**: `htmlcov_wsl/index.html`
- **Windows**: `htmlcov_windows/index.html`

Open in browser to view detailed line-by-line coverage.
