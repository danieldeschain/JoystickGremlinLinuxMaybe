"""Test 05: Module Metrics - Verify refactoring metrics and code quality.

This test ensures:
1. Modules stay within size limits
2. Refactoring achieved its reduction goals
3. Code quality metrics are maintained

This validates the success of the refactoring effort.
"""

import pytest
from pathlib import Path
import ast


def count_lines(file_path: Path) -> int:
    """Count non-empty, non-comment lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        count = 0
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                count += 1
        return count
    except Exception:
        return 0


def count_classes(file_path: Path) -> int:
    """Count number of classes in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        return sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
    except Exception:
        return 0


def count_functions(file_path: Path) -> int:
    """Count number of top-level functions in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        return sum(1 for node in tree.body if isinstance(node, ast.FunctionDef))
    except Exception:
        return 0


class TestModuleSizeConstraints:
    """Verify extracted modules stay within reasonable size limits."""
    
    def test_extracted_modules_under_300_lines(self, project_root_path):
        """Test that extracted modules are focused (< 300 lines each)."""
        # Check a sample of extracted modules
        modules_to_check = [
            project_root_path / "gremlin" / "code_runner_modules" / "runner.py",
            project_root_path / "gremlin" / "user_script_modules" / "script.py",
            project_root_path / "gremlin" / "config_modules" / "core.py",
            project_root_path / "gremlin" / "cheatsheet_modules" / "generators.py",
        ]
        
        oversized = []
        for module in modules_to_check:
            if not module.exists():
                continue
            
            lines = count_lines(module)
            if lines > 300:
                oversized.append((module.name, lines))
        
        if oversized:
            details = "\n".join([f"  {name}: {lines} lines" for name, lines in oversized])
            pytest.fail(f"Modules exceeded 300 line limit:\n{details}")
    
    def test_wrapper_files_are_thin(self, project_root_path):
        """Test that wrapper files are < 250 lines."""
        wrappers = [
            project_root_path / "gremlin" / "code_runner.py",
            project_root_path / "gremlin" / "user_script.py",
            project_root_path / "gremlin" / "cheatsheet.py",
        ]
        
        too_large = []
        for wrapper in wrappers:
            if not wrapper.exists():
                continue
            
            lines = count_lines(wrapper)
            if lines > 250:
                too_large.append((wrapper.name, lines))
        
        if too_large:
            details = "\n".join([f"  {name}: {lines} lines" for name, lines in too_large])
            pytest.fail(f"Wrappers should be thin (< 250 lines):\n{details}")


class TestRefactoringGoals:
    """Verify refactoring achieved its stated goals."""
    
    def test_code_runner_reduction(self, project_root_path):
        """Test code_runner.py achieved ~90% reduction (578 → ~50 lines)."""
        code_runner = project_root_path / "gremlin" / "code_runner.py"
        
        if not code_runner.exists():
            pytest.skip("code_runner.py not found")
        
        lines = count_lines(code_runner)
        # Should be around 48 lines (91.7% reduction from 578)
        assert lines < 100, f"code_runner.py too large: {lines} lines (expected < 100)"
    
    def test_user_script_reduction(self, project_root_path):
        """Test user_script.py achieved ~90% reduction (1,208 → ~130 lines)."""
        user_script = project_root_path / "gremlin" / "user_script.py"
        
        if not user_script.exists():
            pytest.skip("user_script.py not found")
        
        lines = count_lines(user_script)
        # Should be around 128 lines (89.4% reduction from 1,208)
        assert lines < 200, f"user_script.py too large: {lines} lines (expected < 200)"
    
    def test_config_reduction(self, project_root_path):
        """Test config.py achieved ~78% reduction (953 → ~210 lines)."""
        config = project_root_path / "gremlin" / "config.py"
        
        if not config.exists():
            pytest.skip("config.py not found")
        
        lines = count_lines(config)
        # Should be around 210 lines (78% reduction from 953)
        assert lines < 300, f"config.py too large: {lines} lines (expected < 300)"
    
    def test_cheatsheet_reduction(self, project_root_path):
        """Test cheatsheet.py achieved ~86% reduction (525 → ~71 lines)."""
        cheatsheet = project_root_path / "gremlin" / "cheatsheet.py"
        
        if not cheatsheet.exists():
            pytest.skip("cheatsheet.py not found")
        
        lines = count_lines(cheatsheet)
        # Should be around 71 lines (86.5% reduction from 525)
        assert lines < 100, f"cheatsheet.py too large: {lines} lines (expected < 100)"


class TestModuleComplexity:
    """Test that modules maintain reasonable complexity."""
    
    def test_focused_modules_have_limited_classes(self, project_root_path):
        """Test extracted modules have ≤ 5 classes each (focused responsibility)."""
        modules_to_check = [
            project_root_path / "gremlin" / "code_runner_modules" / "callback_registry.py",
            project_root_path / "gremlin" / "user_script_modules" / "registries.py",
            project_root_path / "gremlin" / "config_modules" / "persistence.py",
            project_root_path / "gremlin" / "cheatsheet_modules" / "data.py",
        ]
        
        complex_modules = []
        for module in modules_to_check:
            if not module.exists():
                continue
            
            num_classes = count_classes(module)
            if num_classes > 5:
                complex_modules.append((module.name, num_classes))
        
        if complex_modules:
            details = "\n".join([f"  {name}: {count} classes" for name, count in complex_modules])
            pytest.fail(f"Modules too complex (> 5 classes):\n{details}")
    
    def test_init_files_are_simple(self, project_root_path):
        """Test __init__.py files are simple re-export only."""
        init_files = [
            project_root_path / "gremlin" / "code_runner_modules" / "__init__.py",
            project_root_path / "gremlin" / "user_script_modules" / "__init__.py",
            project_root_path / "gremlin" / "config_modules" / "__init__.py",
            project_root_path / "gremlin" / "cheatsheet_modules" / "__init__.py",
        ]
        
        complex_inits = []
        for init_file in init_files:
            if not init_file.exists():
                continue
            
            # __init__ files should be < 100 lines (just re-exports)
            lines = count_lines(init_file)
            if lines > 100:
                complex_inits.append((init_file.parent.name, lines))
        
        if complex_inits:
            details = "\n".join([f"  {name}: {lines} lines" for name, lines in complex_inits])
            pytest.fail(f"__init__.py files too complex:\n{details}")


class TestBackupFiles:
    """Verify backup files were created during refactoring."""
    
    def test_phase5_backup_exists(self, project_root_path):
        """Test Phase 5 backup file exists."""
        backup = project_root_path / "gremlin" / "code_runner_original_backup.py"
        assert backup.exists(), "Phase 5 backup missing"
    
    def test_phase7_backup_exists(self, project_root_path):
        """Test Phase 7 backup file exists."""
        backup = project_root_path / "gremlin" / "user_script.py.phase7_backup"
        assert backup.exists(), "Phase 7 backup missing"
    
    def test_phase8_backup_exists(self, project_root_path):
        """Test Phase 8 backup file exists."""
        backup = project_root_path / "gremlin" / "config.py.phase8_backup"
        assert backup.exists(), "Phase 8 backup missing"
    
    def test_phase9_backup_exists(self, project_root_path):
        """Test Phase 9 backup file exists."""
        backup = project_root_path / "gremlin" / "cheatsheet.py.phase9_backup"
        assert backup.exists(), "Phase 9 backup missing"


class TestDocumentation:
    """Verify refactoring documentation exists."""
    
    def test_phase5_summary_exists(self, project_root_path):
        """Test PHASE5_SUMMARY.md documentation exists."""
        doc = project_root_path / "PHASE5_SUMMARY.md"
        assert doc.exists(), "PHASE5_SUMMARY.md not found"
        
        # Should contain Phase 9 info
        with open(doc, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'Phase 9' in content, "Phase 9 not documented"
        assert 'cheatsheet.py' in content, "cheatsheet.py not mentioned"
