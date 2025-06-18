#!/usr/bin/env python3
# -*- coding: utf-8; -*-

"""
Test Enhanced Virtual Joystick Manager for Linux Output Backend

This test verifies the enhanced virtual joystick management capabilities,
including permission checking, multi-device support, and error handling.
"""

import sys
import time
from typing import List

def test_permission_checking():
    """Test permission detection and recommendations."""
    print("=" * 60)
    print("PERMISSION CHECKING TEST")
    print("=" * 60)
    
    try:
        from gremlin.virtual_joystick_manager import get_virtual_joystick_manager
        
        manager = get_virtual_joystick_manager()
        
        # Get permission status
        status = manager.get_permission_status()
        print("Permission Status:")
        for permission, granted in status.items():
            indicator = "✅" if granted else "❌"
            print(f"  {indicator} {permission}: {granted}")
        
        # Get recommendations if needed
        recommendations = manager.get_permission_recommendations()
        if recommendations:
            print("\nRecommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        else:
            print("\n✅ All permissions are correctly configured!")
        
        can_create = status.get('can_create_devices', False)
        return can_create
        
    except Exception as e:
        print(f"❌ Permission check failed: {e}")
        return False

def test_virtual_device_creation():
    """Test creating and managing virtual devices."""
    print("\n" + "=" * 60)
    print("VIRTUAL DEVICE CREATION TEST")
    print("=" * 60)
    
    try:
        from gremlin.virtual_joystick_manager import get_virtual_joystick_manager
        
        manager = get_virtual_joystick_manager()
        device_ids = []
        
        print("Creating multiple virtual joysticks...")
        
        # Create test devices
        test_configs = [
            ("TestGamepad", 4, 8, 1),      # Standard gamepad
            ("FlightStick", 6, 12, 0),     # Flight stick
            ("RacingWheel", 2, 16, 1),     # Racing wheel
        ]
        
        for name, axes, buttons, hats in test_configs:
            try:
                device_id = manager.create_virtual_joystick(
                    name=name,
                    axis_count=axes,
                    button_count=buttons,
                    hat_count=hats
                )
                device_ids.append(device_id)
                print(f"✅ Created {name}: ID={device_id}, Axes={axes}, Buttons={buttons}, Hats={hats}")
                
            except Exception as e:
                print(f"❌ Failed to create {name}: {e}")
        
        # List all devices
        print(f"\nCreated {len(device_ids)} virtual devices")
        devices = manager.list_virtual_joysticks()
        for device_id, summary in devices:
            print(f"  ID {device_id}: {summary.name} ({summary.axis_count}a, {summary.button_count}b, {summary.hat_count}h)")
        
        return device_ids
        
    except Exception as e:
        print(f"❌ Device creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_device_control(device_ids: List[int]):
    """Test controlling virtual devices."""
    if not device_ids:
        print("\n⚠ No devices to test control on")
        return False
        
    print("\n" + "=" * 60)
    print("DEVICE CONTROL TEST")
    print("=" * 60)
    
    try:
        from gremlin.virtual_joystick_manager import get_virtual_joystick_manager
        
        manager = get_virtual_joystick_manager()
        test_device_id = device_ids[0]  # Use first device
        
        print(f"Testing control on device ID {test_device_id}...")
        
        # Test axis control
        print("Testing axes...")
        test_values = [-1.0, -0.5, 0.0, 0.5, 1.0]
        for axis in range(4):  # Test first 4 axes
            for value in test_values:
                success = manager.set_axis(test_device_id, axis, value)
                if success:
                    print(f"  ✅ Axis {axis}: {value:+.1f}")
                else:
                    print(f"  ❌ Axis {axis}: {value:+.1f} FAILED")
                time.sleep(0.1)
        
        # Test button control  
        print("Testing buttons...")
        for button in range(8):  # Test first 8 buttons
            # Press button
            success_press = manager.set_button(test_device_id, button, True)
            time.sleep(0.1)
            # Release button
            success_release = manager.set_button(test_device_id, button, False)
            
            if success_press and success_release:
                print(f"  ✅ Button {button}: press/release")
            else:
                print(f"  ❌ Button {button}: FAILED")
            time.sleep(0.1)
        
        # Test hat control
        print("Testing hat switches...")
        hat_directions = [
            (0, 0),    # Center
            (0, 1),    # Up
            (1, 1),    # Up-Right
            (1, 0),    # Right
            (1, -1),   # Down-Right
            (0, -1),   # Down
            (-1, -1),  # Down-Left
            (-1, 0),   # Left
            (-1, 1),   # Up-Left
            (0, 0),    # Center
        ]
        
        for direction in hat_directions:
            success = manager.set_hat(test_device_id, 0, direction)
            if success:
                print(f"  ✅ Hat 0: {direction}")
            else:
                print(f"  ❌ Hat 0: {direction} FAILED")
            time.sleep(0.2)
        
        # Test reset
        print("Testing device reset...")
        success = manager.reset_device(test_device_id)
        if success:
            print("  ✅ Device reset successful")
        else:
            print("  ❌ Device reset failed")
            
        return True
        
    except Exception as e:
        print(f"❌ Device control test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_device_cleanup(device_ids: List[int]):
    """Test device cleanup and destruction."""
    print("\n" + "=" * 60)
    print("DEVICE CLEANUP TEST")
    print("=" * 60)
    
    try:
        from gremlin.virtual_joystick_manager import get_virtual_joystick_manager
        
        manager = get_virtual_joystick_manager()
        
        print(f"Cleaning up {len(device_ids)} devices...")
        
        # Destroy individual devices
        destroyed_count = 0
        for device_id in device_ids[:-1]:  # Leave one for destroy_all test
            success = manager.destroy_virtual_joystick(device_id)
            if success:
                print(f"  ✅ Destroyed device ID {device_id}")
                destroyed_count += 1
            else:
                print(f"  ❌ Failed to destroy device ID {device_id}")
        
        # Test destroy_all for remaining devices
        remaining = manager.destroy_all()
        print(f"  ✅ Destroyed {remaining} remaining devices with destroy_all()")
        
        # Verify cleanup
        final_count = manager.get_device_count()
        if final_count == 0:
            print(f"✅ All devices cleaned up successfully")
            return True
        else:
            print(f"⚠ {final_count} devices still remain")
            return False
            
    except Exception as e:
        print(f"❌ Cleanup test failed: {e}")
        return False

def main():
    """Run all enhanced virtual joystick manager tests."""
    print("ENHANCED VIRTUAL JOYSTICK MANAGER TEST")
    print("Date:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    # Check if we need to initialize linput backend
    try:
        import linput
        print("Initializing linput backend...")
        linput.initialize()
        print("✅ Backend initialized")
    except Exception as e:
        print(f"❌ Backend initialization failed: {e}")
        return 1
    
    tests = [
        ("Permission Checking", test_permission_checking),
        ("Virtual Device Creation", test_virtual_device_creation),
    ]
    
    results = []
    device_ids = []
    
    # Run initial tests
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"RUNNING: {test_name}")
        print(f"{'='*60}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            # Special handling for device creation test
            if test_name == "Virtual Device Creation" and isinstance(result, list):
                device_ids = result
                results[-1] = (test_name, len(result) > 0)  # Convert to boolean
                
        except KeyboardInterrupt:
            print(f"\n⚠ {test_name} interrupted by user")
            results.append((test_name, False))
            break
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Run control and cleanup tests if we have devices
    if device_ids:
        control_tests = [
            ("Device Control", lambda: test_device_control(device_ids)),
            ("Device Cleanup", lambda: test_device_cleanup(device_ids)),
        ]
        
        for test_name, test_func in control_tests:
            print(f"\n{'='*60}")
            print(f"RUNNING: {test_name}")
            print(f"{'='*60}")
            
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")
                results.append((test_name, False))
    
    # Cleanup linput
    try:
        linput.shutdown()
        print("\n✅ Backend shutdown complete")
    except:
        pass
    
    # Final summary
    print(f"\n{'='*60}")
    print("FINAL TEST RESULTS")
    print(f"{'='*60}")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Enhanced virtual joystick manager is working!")
        return 0
    else:
        print("⚠ Some tests failed. Check output for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
