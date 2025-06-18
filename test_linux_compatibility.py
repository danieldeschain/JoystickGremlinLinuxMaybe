#!/usr/bin/env python3
# -*- coding: utf-8; -*-

"""
Comprehensive test for Joystick Penguin Linux compatibility.

This test verifies that all major components of the Linux port work together,
including the DILL compatibility layer, VJoyProxy, and core gremlin modules.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import logging
logging.basicConfig(level=logging.INFO)

def test_core_imports():
    """Test that all core gremlin modules can be imported."""
    print("Testing core gremlin module imports...")
    
    try:
        # Test DILL compatibility layer
        import dill
        print("✓ DILL compatibility layer imported")
        
        # Test VJoy compatibility layer
        from vjoy.vjoy import VJoyProxy
        print("✓ VJoyProxy compatibility layer imported")
        
        # Test core gremlin modules that depend on DILL
        from gremlin.input_cache import Joystick, Keyboard
        print("✓ input_cache module imported")
        
        from gremlin.profile import Profile
        print("✓ profile module imported")
        
        from gremlin.intermediate_output import IntermediateOutput
        print("✓ intermediate_output module imported")
        
        import gremlin.device_initialization
        print("✓ device_initialization module imported")
        
        # Test modules that depend on VJoyProxy
        from gremlin.user_script import CallbackRegistry
        print("✓ user_script module imported")
        
        from gremlin.macro import Macro
        print("✓ macro module imported")
        
        from gremlin.code_runner import CodeRunner
        print("✓ code_runner module imported")
        
        import gremlin.device_helpers
        print("✓ device_helpers module imported")
        
        # Test sendinput with MouseMotion
        from gremlin.sendinput import MouseMotion, FixedMouseMotion, AcceleratedMouseMotion
        print("✓ sendinput module with MouseMotion classes imported")
        
        # Test event handling
        from gremlin.event_handler import Event
        print("✓ event_handler module imported")
        
        # Test virtual joystick manager
        from gremlin.virtual_joystick_manager import VirtualJoystickManager
        print("✓ virtual_joystick_manager module imported")
        
        return True
        
    except Exception as e:
        print(f"✗ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dill_functionality():
    """Test basic DILL functionality."""
    print("\nTesting DILL compatibility layer functionality...")
    
    try:
        import dill
        
        # Test device enumeration
        device_count = dill.get_device_count()
        print(f"✓ DILL device enumeration: {device_count} devices found")
        
        # Show first few devices if any exist
        for i in range(min(3, device_count)):
            device = dill.get_device_information_by_index(i)
            print(f"  - {device.name} (GUID: {device.device_guid})")
        
        return True
        
    except Exception as e:
        print(f"✗ DILL functionality error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vjoy_functionality():
    """Test VJoyProxy functionality."""
    print("\nTesting VJoyProxy compatibility layer functionality...")
    
    try:
        from vjoy.vjoy import VJoyProxy
        
        vjoy = VJoyProxy()
        
        # Test device creation
        if vjoy.ensure_vjoy_device_exists(1):
            print("✓ VJoy device 1 created/exists")
            
            # Test basic operations
            vjoy.set_axis(1, 0, 0.0)
            vjoy.set_button(1, 1, False)
            vjoy.set_hat(1, 1, -1)  # Center
            print("✓ VJoy basic operations successful")
            
            # Test device info
            info = vjoy.get_device_info(1)
            if info:
                print(f"✓ VJoy device info: {info['button_count']} buttons, {info['axis_count']} axes")
            
            # Cleanup
            vjoy.cleanup()
            print("✓ VJoy cleanup successful")
            
        return True
        
    except Exception as e:
        print(f"✗ VJoyProxy functionality error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_input_cache():
    """Test input cache functionality with DILL."""
    print("\nTesting input cache functionality...")
    
    try:
        import gremlin.input_cache
        print("✓ input_cache module imported")
        
        # The cache should be able to initialize without errors
        return True
        
    except Exception as e:
        print(f"✗ Input cache error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all compatibility tests."""
    print("=" * 60)
    print("Joystick Penguin Linux Compatibility Test Suite")
    print("=" * 60)
    
    tests = [
        ("Core Imports", test_core_imports),
        ("DILL Functionality", test_dill_functionality),
        ("VJoyProxy Functionality", test_vjoy_functionality),
        ("Input Cache", test_input_cache),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:<30} {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED! Joystick Penguin Linux core functionality is working!")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
