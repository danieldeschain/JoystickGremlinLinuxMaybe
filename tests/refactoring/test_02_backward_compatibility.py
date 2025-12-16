"""Test 02: Backward Compatibility - Verify old import paths still work.

This test ensures:
1. All old import paths continue to work via re-exports
2. Classes, functions, and constants are accessible from original locations
3. 100% backward compatibility maintained

This is critical for ensuring existing code doesn't break.
"""

import pytest
import importlib


class TestLegacyImports:
    """Test that legacy import paths still work via re-exports."""
    
    def test_code_runner_legacy_imports(self):
        """Test code_runner.py re-exports all extracted classes."""
        import gremlin.code_runner as cr
        
        # From callback_registry module
        assert hasattr(cr, 'CallbackRegistry')
        assert hasattr(cr, 'callback_registry')
        
        # From event_loop module  
        assert hasattr(cr, 'EventListener')
        
        # From runner module
        assert hasattr(cr, 'CodeRunner')
        
        # Verify they're actual classes, not None
        assert cr.CallbackRegistry is not None
        assert cr.EventListener is not None
        assert cr.CodeRunner is not None
    
    def test_user_script_legacy_imports(self):
        """Test user_script.py re-exports all extracted classes."""
        import gremlin.user_script as us
        
        # From registries module
        assert hasattr(us, 'VJoyRegistry')
        assert hasattr(us, 'JoystickInputSignalRegistry')
        assert hasattr(us, 'KeyboardInputSignalRegistry')
        assert hasattr(us, 'MergeAxisRegistry')
        assert hasattr(us, 'ResponseCurveRegistry')
        
        # From plugins module
        assert hasattr(us, 'PeriodicRegistry')
        assert hasattr(us, 'SquashedAxis')
        
        # From script module
        assert hasattr(us, 'UserScript')
        
        # From variables module
        assert hasattr(us, 'state')
        assert hasattr(us, 'Variable')
        
        # Verify classes are real
        assert us.UserScript is not None
        assert us.VJoyRegistry is not None
    
    def test_config_facade_legacy_imports(self):
        """Test config.py facade maintains all legacy access patterns."""
        import gremlin.config as cfg
        
        # Singleton instance
        assert hasattr(cfg, 'Configuration')
        config = cfg.Configuration()
        assert config is not None
        
        # Verify facade methods exist (from accessors)
        assert hasattr(config, 'get')
        assert hasattr(config, 'set')
        assert hasattr(config, 'value')
        
        # Verify persistence methods exist
        assert hasattr(config, 'save')
        assert hasattr(config, 'load')
        
        # Verify registry is accessible
        assert hasattr(cfg, 'settings')
    
    def test_cheatsheet_legacy_imports(self):
        """Test cheatsheet.py re-exports all functionality."""
        import gremlin.cheatsheet as cs
        
        # From data module
        assert hasattr(cs, 'InputItemData')
        
        # From layout module
        assert hasattr(cs, 'DeviceFloat')
        assert hasattr(cs, 'ModeFloat')
        
        # From generators module
        assert hasattr(cs, 'generate_cheatsheet')
        
        # From helpers module
        assert hasattr(cs, 'recursive')
        assert hasattr(cs, 'sort_data')
        assert hasattr(cs, 'format_input_name')
        
        # Verify main function exists
        assert cs.generate_cheatsheet is not None
        assert callable(cs.generate_cheatsheet)


class TestWrapperIntegrity:
    """Test that wrapper files maintain correct structure."""
    
    def test_code_runner_wrapper(self):
        """Verify code_runner.py is a thin wrapper."""
        import gremlin.code_runner as cr
        import inspect
        
        # Check file is small (should be < 100 lines)
        source_file = inspect.getfile(cr)
        with open(source_file, 'r') as f:
            lines = len(f.readlines())
        assert lines < 100, f"code_runner.py wrapper too large: {lines} lines"
    
    def test_user_script_wrapper(self):
        """Verify user_script.py is a thin wrapper."""
        import gremlin.user_script as us
        import inspect
        
        source_file = inspect.getfile(us)
        with open(source_file, 'r') as f:
            lines = len(f.readlines())
        assert lines < 200, f"user_script.py wrapper too large: {lines} lines"
    
    def test_config_facade(self):
        """Verify config.py is a lightweight facade."""
        import gremlin.config as cfg
        import inspect
        
        source_file = inspect.getfile(cfg)
        with open(source_file, 'r') as f:
            lines = len(f.readlines())
        assert lines < 250, f"config.py facade too large: {lines} lines"
    
    def test_cheatsheet_wrapper(self):
        """Verify cheatsheet.py is a thin wrapper."""
        import gremlin.cheatsheet as cs
        import inspect
        
        source_file = inspect.getfile(cs)
        with open(source_file, 'r') as f:
            lines = len(f.readlines())
        assert lines < 100, f"cheatsheet.py wrapper too large: {lines} lines"


class TestClassIdentity:
    """Test that re-exported classes maintain identity."""
    
    def test_code_runner_class_identity(self):
        """Verify re-exported classes are the same objects."""
        from gremlin.code_runner import CodeRunner as CR1
        from gremlin.code_runner_modules.runner import CodeRunner as CR2
        
        assert CR1 is CR2, "CodeRunner class identity broken by re-export"
    
    def test_user_script_class_identity(self):
        """Verify re-exported classes are the same objects."""
        from gremlin.user_script import UserScript as US1
        from gremlin.user_script_modules.script import UserScript as US2
        
        assert US1 is US2, "UserScript class identity broken by re-export"
    
    def test_config_singleton_identity(self):
        """Verify Configuration singleton is preserved."""
        from gremlin.config import Configuration
        
        instance1 = Configuration()
        instance2 = Configuration()
        
        assert instance1 is instance2, "Configuration singleton broken"
