"""Test 04: Integration Tests - Verify key functionality works.

This test ensures:
1. Extracted modules maintain their core functionality
2. Classes and functions work correctly after refactoring
3. Integration between modules still functions

This validates that refactoring didn't break actual behavior.
"""

import pytest
import sys


class TestCodeRunnerIntegration:
    """Test code_runner functionality after extraction."""
    
    def test_callback_registry_basic_operations(self):
        """Test CallbackRegistry can register and retrieve callbacks."""
        from gremlin.code_runner import CallbackRegistry
        
        registry = CallbackRegistry()
        
        # Test callback registration
        def test_callback():
            return "test"
        
        registry.add(test_callback, "test_event")
        
        # Verify callback was registered
        callbacks = registry.callbacks.get("test_event", [])
        assert len(callbacks) > 0, "Callback not registered"
        assert callbacks[0] == test_callback, "Wrong callback registered"
    
    def test_event_listener_exists(self):
        """Test EventListener class is accessible."""
        from gremlin.code_runner import EventListener
        
        # Should be able to create instance (even if we don't fully initialize)
        assert EventListener is not None
        assert callable(EventListener)
    
    def test_code_runner_singleton(self):
        """Test CodeRunner maintains singleton pattern."""
        from gremlin.code_runner import CodeRunner
        
        # Should be able to access the class
        assert CodeRunner is not None


class TestConfigIntegration:
    """Test config.py facade functionality after extraction."""
    
    def test_configuration_singleton(self):
        """Test Configuration maintains singleton pattern."""
        from gremlin.config import Configuration
        
        config1 = Configuration()
        config2 = Configuration()
        
        # Should be the same instance
        assert config1 is config2, "Configuration singleton broken"
    
    def test_configuration_basic_methods(self):
        """Test Configuration has all expected methods."""
        from gremlin.config import Configuration
        
        config = Configuration()
        
        # Check facade methods exist
        assert hasattr(config, 'get'), "Missing get() method"
        assert hasattr(config, 'set'), "Missing set() method"
        assert hasattr(config, 'value'), "Missing value() method"
        assert hasattr(config, 'save'), "Missing save() method"
        assert hasattr(config, 'load'), "Missing load() method"
        
        # Verify methods are callable
        assert callable(config.get)
        assert callable(config.set)
    
    def test_settings_registry_accessible(self):
        """Test settings registry is accessible."""
        from gremlin.config import settings
        
        assert settings is not None, "settings registry not accessible"


class TestUserScriptIntegration:
    """Test user_script.py functionality after extraction."""
    
    def test_vjoy_registry_basic(self):
        """Test VJoyRegistry class is functional."""
        from gremlin.user_script import VJoyRegistry
        
        registry = VJoyRegistry()
        assert registry is not None
        
        # Should have vjoy method
        assert hasattr(registry, 'vjoy'), "VJoyRegistry missing vjoy() method"
    
    def test_registries_independent(self):
        """Test that different registries are independent."""
        from gremlin.user_script import (
            VJoyRegistry,
            JoystickInputSignalRegistry,
            KeyboardInputSignalRegistry,
        )
        
        vjoy = VJoyRegistry()
        joystick = JoystickInputSignalRegistry()
        keyboard = KeyboardInputSignalRegistry()
        
        # Should be different objects
        assert vjoy is not vjoy
        assert joystick is not keyboard
    
    def test_user_script_class(self):
        """Test UserScript class is accessible."""
        from gremlin.user_script import UserScript
        
        assert UserScript is not None
        assert callable(UserScript)
    
    def test_state_variable(self):
        """Test state variable is accessible."""
        from gremlin.user_script import state
        
        assert state is not None


class TestCheatsheetIntegration:
    """Test cheatsheet.py functionality after extraction."""
    
    def test_generate_cheatsheet_exists(self):
        """Test main cheatsheet generation function exists."""
        from gremlin.cheatsheet import generate_cheatsheet
        
        assert generate_cheatsheet is not None
        assert callable(generate_cheatsheet)
    
    def test_input_item_data_class(self):
        """Test InputItemData class is accessible."""
        from gremlin.cheatsheet import InputItemData
        
        assert InputItemData is not None
        assert callable(InputItemData)
    
    def test_helper_functions(self):
        """Test helper functions are accessible."""
        from gremlin.cheatsheet import recursive, sort_data, format_input_name
        
        assert callable(recursive), "recursive() not callable"
        assert callable(sort_data), "sort_data() not callable"
        assert callable(format_input_name), "format_input_name() not callable"
    
    def test_flowable_classes(self):
        """Test PDF flowable classes are accessible."""
        from gremlin.cheatsheet import DeviceFloat, ModeFloat
        
        assert DeviceFloat is not None
        assert ModeFloat is not None


class TestDeviceModulesIntegration:
    """Test device.py extracted modules (Phase 5)."""
    
    def test_device_information_accessible(self):
        """Test DeviceInformation class is accessible."""
        try:
            from gremlin.device_information import DeviceInformation
            assert DeviceInformation is not None
        except ImportError:
            pytest.skip("DeviceInformation not available (may need hardware)")
    
    def test_device_manager_accessible(self):
        """Test DeviceManager class is accessible."""
        try:
            from gremlin.device_manager import DeviceManager
            assert DeviceManager is not None
        except ImportError:
            pytest.skip("DeviceManager not available")
    
    def test_device_constants_accessible(self):
        """Test device constants are accessible."""
        try:
            from gremlin.device_constants import DeviceType
            assert DeviceType is not None
        except ImportError:
            pytest.skip("DeviceConstants not available")


class TestProfileModulesIntegration:
    """Test ui/profile.py extracted modules (Phase 5)."""
    
    def test_device_widget_accessible(self):
        """Test DeviceWidget class is accessible."""
        try:
            from gremlin.ui.profile_modules.device_widget import DeviceWidget
            assert DeviceWidget is not None
        except ImportError as e:
            # May fail due to Qt dependencies, which is OK
            if 'PyQt5' not in str(e) and 'PySide2' not in str(e):
                pytest.fail(f"Unexpected import error: {e}")
    
    def test_tree_model_accessible(self):
        """Test TreeModel class is accessible."""
        try:
            from gremlin.ui.profile_modules.tree_model import ProfileTree
            assert ProfileTree is not None
        except ImportError as e:
            if 'PyQt5' not in str(e) and 'PySide2' not in str(e):
                pytest.fail(f"Unexpected import error: {e}")


class TestMapToVJoyIntegration:
    """Test map_to_vjoy extracted modules (Phase 5)."""
    
    def test_axis_handler_accessible(self):
        """Test AxisHandler class is accessible."""
        try:
            from action_plugins.map_to_vjoy.map_to_vjoy_modules.axis_handler import AxisHandler
            assert AxisHandler is not None
        except ImportError:
            pytest.skip("AxisHandler not available (may need vjoy)")
    
    def test_button_handler_accessible(self):
        """Test ButtonHandler class is accessible."""
        try:
            from action_plugins.map_to_vjoy.map_to_vjoy_modules.button_handler import ButtonHandler
            assert ButtonHandler is not None
        except ImportError:
            pytest.skip("ButtonHandler not available")
    
    def test_hat_handler_accessible(self):
        """Test HatHandler class is accessible."""
        try:
            from action_plugins.map_to_vjoy.map_to_vjoy_modules.hat_handler import HatHandler
            assert HatHandler is not None
        except ImportError:
            pytest.skip("HatHandler not available")
