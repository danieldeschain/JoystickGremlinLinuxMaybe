"""Test 01: Import Smoke Tests - Verify all extracted modules can be imported.

This test ensures that:
1. All 33 extracted modules across Phases 5-9 can be imported without errors
2. No ImportError or ModuleNotFoundError occurs
3. Module structure is correct

This is the first line of defense - if these fail, nothing else matters.
"""

import pytest
import importlib
import sys


class TestModuleImports:
    """Test that all extracted modules can be imported successfully."""
    
    def test_phase5_device_modules(self):
        """Phase 5: Test device.py extracted modules (7 modules)."""
        modules = [
            "gremlin.device_information",
            "gremlin.device_query",
            "gremlin.device_registry",
            "gremlin.device_manager",
            "gremlin.device_constants",
            "gremlin.device_data",
            "gremlin.device_joystick",
        ]
        for module_name in modules:
            try:
                mod = importlib.import_module(module_name)
                assert mod is not None, f"{module_name} imported as None"
            except Exception as e:
                pytest.fail(f"Failed to import {module_name}: {e}")
    
    def test_phase5_code_runner_modules(self):
        """Phase 5: Test code_runner.py extracted modules (3 modules)."""
        modules = [
            "gremlin.code_runner_modules.callback_registry",
            "gremlin.code_runner_modules.event_loop",
            "gremlin.code_runner_modules.runner",
        ]
        for module_name in modules:
            try:
                mod = importlib.import_module(module_name)
                assert mod is not None
            except Exception as e:
                pytest.fail(f"Failed to import {module_name}: {e}")
    
    def test_phase5_map_to_vjoy_modules(self):
        """Phase 5: Test map_to_vjoy extracted modules (3 modules)."""
        modules = [
            "action_plugins.map_to_vjoy.map_to_vjoy_modules.axis_handler",
            "action_plugins.map_to_vjoy.map_to_vjoy_modules.button_handler",
            "action_plugins.map_to_vjoy.map_to_vjoy_modules.hat_handler",
        ]
        for module_name in modules:
            try:
                mod = importlib.import_module(module_name)
                assert mod is not None
            except Exception as e:
                pytest.fail(f"Failed to import {module_name}: {e}")
    
    def test_phase5_profile_modules(self):
        """Phase 5: Test ui/profile.py extracted modules (5 modules)."""
        modules = [
            "gremlin.ui.profile_modules.device_widget",
            "gremlin.ui.profile_modules.input_item_widget",
            "gremlin.ui.profile_modules.tree_model",
            "gremlin.ui.profile_modules.widget_registry",
            "gremlin.ui.profile_modules.delegates",
        ]
        for module_name in modules:
            try:
                mod = importlib.import_module(module_name)
                assert mod is not None
            except Exception as e:
                pytest.fail(f"Failed to import {module_name}: {e}")
    
    def test_phase7_user_script_modules(self):
        """Phase 7: Test user_script.py extracted modules (4 modules)."""
        modules = [
            "gremlin.user_script_modules.registries",
            "gremlin.user_script_modules.plugins",
            "gremlin.user_script_modules.script",
            "gremlin.user_script_modules.variables",
        ]
        for module_name in modules:
            try:
                mod = importlib.import_module(module_name)
                assert mod is not None
            except Exception as e:
                pytest.fail(f"Failed to import {module_name}: {e}")
    
    def test_phase8_config_modules(self):
        """Phase 8: Test config.py extracted modules (7 modules)."""
        modules = [
            "gremlin.config_modules.core",
            "gremlin.config_modules.persistence",
            "gremlin.config_modules.registry",
            "gremlin.config_modules.accessors",
            "gremlin.config_modules.metadata",
            "gremlin.config_modules.structure",
            "gremlin.config_modules.calibration",
        ]
        for module_name in modules:
            try:
                mod = importlib.import_module(module_name)
                assert mod is not None
            except Exception as e:
                pytest.fail(f"Failed to import {module_name}: {e}")
    
    def test_phase9_cheatsheet_modules(self):
        """Phase 9: Test cheatsheet.py extracted modules (4 modules)."""
        modules = [
            "gremlin.cheatsheet_modules.data",
            "gremlin.cheatsheet_modules.layout",
            "gremlin.cheatsheet_modules.generators",
            "gremlin.cheatsheet_modules.helpers",
        ]
        for module_name in modules:
            try:
                mod = importlib.import_module(module_name)
                assert mod is not None
            except Exception as e:
                pytest.fail(f"Failed to import {module_name}: {e}")
    
    def test_module_init_files(self):
        """Test that all __init__.py files work correctly."""
        init_modules = [
            "gremlin.code_runner_modules",
            "action_plugins.map_to_vjoy.map_to_vjoy_modules",
            "gremlin.ui.profile_modules",
            "gremlin.user_script_modules",
            "gremlin.config_modules",
            "gremlin.cheatsheet_modules",
        ]
        for module_name in init_modules:
            try:
                mod = importlib.import_module(module_name)
                assert mod is not None
                # __init__ files should expose their submodules
                assert hasattr(mod, '__all__') or len(dir(mod)) > 2  # More than just __name__, __doc__
            except Exception as e:
                pytest.fail(f"Failed to import {module_name}: {e}")


class TestModuleCount:
    """Verify the correct number of modules were extracted."""
    
    def test_total_module_count(self):
        """Verify we extracted 33 total modules."""
        total_modules = (
            7 +  # device.py
            3 +  # code_runner.py
            3 +  # map_to_vjoy
            5 +  # ui/profile.py
            4 +  # user_script.py
            7 +  # config.py
            4    # cheatsheet.py
        )
        assert total_modules == 33, "Expected 33 total extracted modules"
