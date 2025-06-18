#!/usr/bin/env python3
"""
Test and monitor virtual joystick devices - create devices and show system visibility.
"""

import time
import subprocess
import threading

def monitor_input_devices():
    """Monitor and display input devices in the background."""
    while True:
        try:
            result = subprocess.run(['ls', '-la', '/dev/input/'], 
                                  capture_output=True, text=True, timeout=5)
            print(f"\n📁 /dev/input/ contents:")
            for line in result.stdout.split('\n'):
                if 'event' in line or 'js' in line:
                    print(f"  {line}")
            
            # Check for virtual joysticks specifically
            try:
                result = subprocess.run(['ls', '/dev/input/'], 
                                      capture_output=True, text=True, timeout=5)
                js_devices = [dev for dev in result.stdout.split() if dev.startswith('js')]
                event_devices = [dev for dev in result.stdout.split() if dev.startswith('event')]
                print(f"🎮 Found {len(js_devices)} joystick devices: {js_devices}")
                print(f"⚡ Found {len(event_devices)} event devices: {event_devices[:10]}...")  # Limit output
            except:
                pass
                
        except Exception as e:
            print(f"❌ Monitor error: {e}")
        
        time.sleep(3)

def main():
    print("🎮 VIRTUAL JOYSTICK SYSTEM VISIBILITY TEST")
    print("=" * 60)
    
    # Start monitoring thread
    monitor_thread = threading.Thread(target=monitor_input_devices, daemon=True)
    monitor_thread.start()
    
    try:
        import linput
        from gremlin.virtual_joystick_manager import get_virtual_joystick_manager
        
        print("Initializing backend...")
        linput.initialize()
        
        manager = get_virtual_joystick_manager()
        
        print("\n🚀 Creating virtual devices...")
        device_ids = []
        
        # Create test devices
        for i, (name, axes, buttons, hats) in enumerate([
            ("SystemTest1", 4, 8, 1),
            ("SystemTest2", 6, 12, 0),
        ]):
            device_id = manager.create_virtual_joystick(name, axes, buttons, hats)
            device_ids.append(device_id)
            print(f"✅ Created {name} (ID: {device_id})")
            time.sleep(1)  # Give system time to register device
        
        print(f"\n⏰ Devices created! Monitoring for 10 seconds...")
        print("   (Watch for new js* and event* devices)")
        
        # Monitor for 10 seconds
        for i in range(10):
            print(f"⏱ {10-i} seconds remaining...")
            time.sleep(1)
        
        print("\n🧪 Testing device control while monitoring...")
        if device_ids:
            test_device_id = device_ids[0]
            
            # Test controls
            for axis in range(2):
                for value in [-1.0, 0.0, 1.0]:
                    manager.set_axis(test_device_id, axis, value)
                    print(f"  📊 Set axis {axis} to {value}")
                    time.sleep(0.5)
            
            for button in range(4):
                manager.set_button(test_device_id, button, True)
                print(f"  🔴 Pressed button {button}")
                time.sleep(0.3)
                manager.set_button(test_device_id, button, False)
                print(f"  ⚪ Released button {button}")
                time.sleep(0.3)
        
        print("\n🧹 Cleaning up devices...")
        for device_id in device_ids:
            manager.destroy_virtual_joystick(device_id)
            print(f"✅ Destroyed device {device_id}")
            time.sleep(1)
        
        print("\n✅ Test completed successfully!")
        
        linput.shutdown()
        
    except KeyboardInterrupt:
        print("\n⚠ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
