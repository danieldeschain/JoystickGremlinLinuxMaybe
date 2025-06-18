#!/usr/bin/env python3
"""
Isolated test of the Linux input backend without problematic Windows imports.
"""

import sys
import time

def test_linput_backend():
    """Test the Linux input backend in complete isolation."""
    print("Testing Linux Input Backend (Isolated)")
    print("=" * 50)
    
    try:
        # Test linput imports
        print("1. Testing linput imports...")
        import linput
        print("   ✓ linput imported successfully")
        
        # Initialize the backend
        print("2. Initializing Linux backend...")
        linput.initialize()
        print("   ✓ Linux backend initialized")
        
        # Test device enumeration
        print("3. Testing device enumeration...")
        device_count = linput.get_device_count()
        print(f"   ✓ Found {device_count} input devices")
        
        devices = linput.get_joystick_devices()
        for i, device in enumerate(devices):
            print(f"   Device {i}: {device.name} (GUID: {device.device_guid})")
            print(f"     Axes: {device.axis_count}, Buttons: {device.button_count}, Hats: {device.hat_count}")
        
        # Test device manager
        print("4. Testing device manager...")
        device_manager = linput.get_device_manager()
        print(f"   ✓ Device manager active with {device_manager.get_device_count()} devices")
        
        # Test keyboard/mouse manager
        print("5. Testing keyboard/mouse manager...")
        km_manager = linput.get_keyboard_mouse_manager()
        print("   ✓ Keyboard/mouse manager initialized")
        
        print("\n6. Testing for 5 seconds - move joystick if available...")
        
        # Set up event callback
        def event_callback(event):
            print(f"   Input event: {event.input_type.name} code={event.code} value={event.value}")
        
        device_manager.set_input_event_callback(event_callback)
        
        # Listen for events for 5 seconds
        start_time = time.time()
        while time.time() - start_time < 5:
            time.sleep(0.1)
        
        print("\n7. Shutting down...")
        linput.shutdown()
        print("   ✓ Linux backend shutdown complete")
        
        print("\n" + "=" * 50)
        print("✓ ALL TESTS PASSED - Linux backend is working!")
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_linput_backend()
    sys.exit(0 if success else 1)
