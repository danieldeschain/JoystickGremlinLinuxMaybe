#!/usr/bin/env python3
"""
Debug uinput device creation to find the root cause of the TypeError.
"""

import sys
import traceback

print("Testing uinput device creation...")

try:
    import uinput
    print("✅ uinput module imported successfully")
    
    # Test 1: Simple device creation
    print("\nTest 1: Creating minimal device...")
    try:
        events = [uinput.BTN_A]
        device = uinput.Device(events, name="TestDevice")
        print("✅ Minimal device created successfully")
        device.destroy()
        print("✅ Minimal device destroyed successfully")
    except Exception as e:
        print(f"❌ Minimal device creation failed: {e}")
        traceback.print_exc()
    
    # Test 2: Device with axes
    print("\nTest 2: Creating device with axes...")
    try:
        events = [
            (uinput.ABS_X, (-32768, 32767, 0, 0)),
            uinput.BTN_A
        ]
        device = uinput.Device(events, name="TestDeviceWithAxes")
        print("✅ Device with axes created successfully")
        device.destroy()
        print("✅ Device with axes destroyed successfully")
    except Exception as e:
        print(f"❌ Device with axes creation failed: {e}")
        traceback.print_exc()
    
    # Test 3: Our exact configuration
    print("\nTest 3: Creating device with our configuration...")
    try:
        events = []
        
        # Add axes
        axis_events = [
            uinput.ABS_X, uinput.ABS_Y,      # Left stick
            uinput.ABS_RX, uinput.ABS_RY,    # Right stick  
        ]
        
        for axis in axis_events:
            events.append((axis, (-32768, 32767, 0, 0)))
        
        # Add buttons
        button_events = [
            uinput.BTN_JOYSTICK, uinput.BTN_THUMB
        ]
        
        for button in button_events:
            events.append(button)
        
        print(f"Events list: {events}")
        
        device = uinput.Device(events, name="TestJoystick")
        print("✅ Our configuration device created successfully")
        device.destroy()
        print("✅ Our configuration device destroyed successfully")
        
    except Exception as e:
        print(f"❌ Our configuration device creation failed: {e}")
        traceback.print_exc()
        
    print("\n✅ All uinput tests completed successfully!")
    
except ImportError as e:
    print(f"❌ uinput module not available: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    traceback.print_exc()
    sys.exit(1)
