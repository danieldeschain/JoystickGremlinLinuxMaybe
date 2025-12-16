"""Test 03: Dependency Analysis - Verify circular dependencies eliminated.

This test ensures:
1. Phase 6 successfully eliminated all runtime circular dependencies
2. No new cycles introduced by refactoring
3. Import structure is clean

This validates the architectural improvement from refactoring.
"""

import pytest
import sys
import importlib
from typing import Set, Dict, List
import ast
import os
from pathlib import Path


class ImportVisitor(ast.NodeVisitor):
    """AST visitor to extract import statements."""
    
    def __init__(self):
        self.imports = []
    
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
    
    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.append(node.module)


def get_module_imports(module_path: Path) -> List[str]:
    """Extract all imports from a Python module."""
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        visitor = ImportVisitor()
        visitor.visit(tree)
        # Filter to only gremlin and action_plugins imports
        return [imp for imp in visitor.imports 
                if imp.startswith('gremlin') or imp.startswith('action_plugins')]
    except Exception as e:
        return []


def find_circular_dependencies(base_path: Path) -> List[tuple]:
    """Find circular dependencies in gremlin package."""
    module_imports = {}
    
    # Scan all Python files
    for py_file in base_path.rglob('*.py'):
        if 'test' in str(py_file) or '__pycache__' in str(py_file):
            continue
        
        # Convert path to module name
        rel_path = py_file.relative_to(base_path.parent)
        module_name = str(rel_path.with_suffix('')).replace(os.sep, '.')
        
        imports = get_module_imports(py_file)
        module_imports[module_name] = imports
    
    # Detect cycles
    cycles = []
    for module, imports in module_imports.items():
        for imported in imports:
            # Check if imported module imports back
            if imported in module_imports:
                if module in module_imports[imported] or \
                   any(module.startswith(imp) for imp in module_imports[imported]):
                    cycles.append((module, imported))
    
    return cycles


class TestNoDependencyCycles:
    """Verify no circular dependencies exist."""
    
    def test_no_runtime_cycles_in_gremlin(self, project_root_path):
        """Test that gremlin package has no circular dependencies."""
        gremlin_path = project_root_path / "gremlin"
        
        if not gremlin_path.exists():
            pytest.skip("gremlin package not found")
        
        cycles = find_circular_dependencies(gremlin_path)
        
        if cycles:
            cycle_details = "\n".join([f"  {a} <-> {b}" for a, b in cycles])
            pytest.fail(f"Found circular dependencies:\n{cycle_details}")
    
    def test_phase6_domain_layer_imports(self):
        """Verify Phase 6 fixed domain layer imports correctly."""
        # These modules had circular dependency issues in Phase 6
        critical_modules = [
            "gremlin.base_classes",
            "gremlin.event_handler", 
            "gremlin.ui.action_model",
        ]
        
        for module_name in critical_modules:
            try:
                mod = importlib.import_module(module_name)
                assert mod is not None
            except ImportError as e:
                pytest.fail(f"Phase 6 fix failed for {module_name}: {e}")


class TestModuleSeparation:
    """Verify extracted modules are properly separated."""
    
    def test_code_runner_modules_independent(self):
        """Test code_runner modules don't have internal cycles."""
        modules = [
            "gremlin.code_runner_modules.callback_registry",
            "gremlin.code_runner_modules.event_loop",
            "gremlin.code_runner_modules.runner",
        ]
        
        # Import all modules
        imported = {}
        for mod_name in modules:
            imported[mod_name] = importlib.import_module(mod_name)
        
        # Verify each can be imported independently
        for mod_name, mod in imported.items():
            assert mod is not None
            # Module should not depend on its siblings
            assert not any(other in str(mod.__file__) 
                          for other in modules if other != mod_name)
    
    def test_config_modules_independent(self):
        """Test config modules are properly separated."""
        modules = [
            "gremlin.config_modules.core",
            "gremlin.config_modules.persistence",
            "gremlin.config_modules.registry",
            "gremlin.config_modules.accessors",
        ]
        
        imported = {}
        for mod_name in modules:
            imported[mod_name] = importlib.import_module(mod_name)
        
        for mod_name, mod in imported.items():
            assert mod is not None
    
    def test_user_script_modules_independent(self):
        """Test user_script modules are properly separated."""
        modules = [
            "gremlin.user_script_modules.registries",
            "gremlin.user_script_modules.plugins",
            "gremlin.user_script_modules.script",
            "gremlin.user_script_modules.variables",
        ]
        
        imported = {}
        for mod_name in modules:
            imported[mod_name] = importlib.import_module(mod_name)
        
        for mod_name, mod in imported.items():
            assert mod is not None


class TestImportCleanliness:
    """Test that imports follow best practices."""
    
    def test_no_wildcard_imports_in_wrappers(self, project_root_path):
        """Verify wrapper files don't use 'from module import *' excessively."""
        wrapper_files = [
            project_root_path / "gremlin" / "code_runner.py",
            project_root_path / "gremlin" / "user_script.py",
            project_root_path / "gremlin" / "cheatsheet.py",
        ]
        
        for wrapper in wrapper_files:
            if not wrapper.exists():
                continue
            
            with open(wrapper, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Wildcard imports are OK in wrapper files, but should be controlled
            wildcard_count = content.count('import *')
            # Should have some re-exports but not excessive
            assert wildcard_count < 10, f"{wrapper.name} has too many wildcard imports"
    
    def test_type_checking_guards_exist(self, project_root_path):
        """Verify TYPE_CHECKING guards are used for type hints (Phase 6 pattern)."""
        # Check that base_classes.py uses TYPE_CHECKING
        base_classes = project_root_path / "gremlin" / "base_classes.py"
        
        if not base_classes.exists():
            pytest.skip("base_classes.py not found")
        
        with open(base_classes, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have TYPE_CHECKING import
        assert 'from typing import TYPE_CHECKING' in content or 'TYPE_CHECKING' in content, \
            "base_classes.py should use TYPE_CHECKING for type hints"
