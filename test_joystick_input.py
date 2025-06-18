#!/usr/bin/env python3
"""
Test joystick/gamepad input detection with the Linux backend.
"""

import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_joystick_detection():
    """Test joystick device detection and input monitoring."""
    print("=" * 60)
    print("JOYSTICK/GAMEPAD DETECTION TEST")
    print("=" * 60)
    
    try:
        import linput
        
        print("Initializing Linux backend...")
        linput.initialize()
        
        # Test device detection
        print("\n🎮 DEVICE DETECTION:")
        device_count = linput.get_device_count()
        print(f"Found {device_count} joystick/gamepad devices")
        
        if device_count == 0:
            print("⚠️  No joystick devices detected.")
            print("   - Make sure a joystick/gamepad is connected")
            print("   - Check if user is in 'input' group: groups")
            print("   - Check device permissions: ls -la /dev/input/")
            return False
        
        # List all devices
        devices = linput.get_joystick_devices()
        for i, device in enumerate(devices):
            print(f"\n📱 Device {i}: {device.name}")
            print(f"   GUID: {device.device_guid}")
            print(f"   Vendor/Product ID: {device.vendor_id:04x}:{device.product_id:04x}")
            print(f"   Capabilities: {device.axis_count} axes, {device.button_count} buttons, {device.hat_count} hats")
            print(f"   Device path: {device.device_path}")
            print(f"   Virtual: {device.is_virtual}")
        
        # Test input monitoring
        print(f"\n🎯 INPUT MONITORING TEST")
        print("Move joystick axes, press buttons, or move D-pad...")
        print("Test will run for 10 seconds...")
        
        events_received = []
        
        def joystick_callback(event):
            events_received.append(event)
            # Show different event types
            if hasattr(event, 'input_type'):
                if str(event.input_type) == 'InputType.Axis':
                    print(f"🕹️  Axis {event.code}: {event.value}")
                elif str(event.input_type) == 'InputType.Button':
                    state = "PRESSED" if event.value else "RELEASED"
                    print(f"🔘 Button {event.code}: {state}")
                elif str(event.input_type) == 'InputType.Hat':
                    print(f"🎯 Hat {event.code}: {event.value}")
                else:
                    print(f"❓ {event.input_type} {event.code}: {event.value}")
        
        # Set up monitoring
        device_manager = linput.get_device_manager()
        device_manager.set_input_event_callback(joystick_callback)
        
        # Monitor for 10 seconds
        start_time = time.time()
        print("\n" + "="*50)
        while time.time() - start_time < 10.0:
            time.sleep(0.1)
            elapsed = int(time.time() - start_time)
            if elapsed % 3 == 0 and elapsed > 0:
                print(f"⏱️  {elapsed}s - Events received: {len(events_received)}")
        
        print(f"\n📊 RESULTS:")
        print(f"Total joystick events: {len(events_received)}")
        
        if len(events_received) > 0:
            print("Sample events:")
            for i, event in enumerate(events_received[:5]):
                print(f"  {i+1}. Type:{event.input_type} Code:{event.code} Value:{event.value}")
            print("✅ Joystick input monitoring is working!")
        else:
            print("⚠️  No joystick events received - try moving controls")
        
        linput.shutdown()
        return len(events_received) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_joystick_detection()
    if success:
        print("\n🎉 Joystick detection test PASSED!")
    else:
        print("\n⚠️  Joystick detection needs attention")
