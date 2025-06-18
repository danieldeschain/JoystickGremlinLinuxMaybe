#!/usr/bin/env python3
# -*- coding: utf-8; -*-

"""
Test script to verify mouse and keyboard input detection in the Linux backend.

This script tests the keyboard_mouse module's ability to detect and process
keyboard and mouse events in real-time.
"""

import sys
import time
import threading
from typing import List

def test_keyboard_mouse_detection():
    """Test keyboard and mouse input detection."""
    print("=" * 60)
    print("LINUX BACKEND - KEYBOARD & MOUSE INPUT TEST")
    print("=" * 60)
    
    try:
        import linput
        
        print("Initializing Linux input backend...")
        linput.initialize()
        
        # Get the keyboard/mouse manager
        km_manager = linput.get_keyboard_mouse_manager()
        print(f"✓ Keyboard/Mouse manager: {type(km_manager)}")
        
        # Check available methods
        methods = [method for method in dir(km_manager) if not method.startswith('_')]
        print(f"✓ Available methods: {', '.join(methods)}")
        
        print("\n" + "=" * 60)
        print("LIVE INPUT MONITORING TEST")
        print("=" * 60)
        print("Instructions:")
        print("- Press keyboard keys to test keyboard input")
        print("- Move mouse to test mouse movement")
        print("- Click mouse buttons to test mouse clicks")
        print("- Press Ctrl+C to stop the test")
        print("- Test will run for 30 seconds")
        print()
        
        # Event counters
        keyboard_events = []
        mouse_events = []
        
        # Test if we can set up callbacks
        print("Setting up input monitoring...")
        
        # Try to access callback methods if they exist
        if hasattr(km_manager, 'set_keyboard_callback'):
            def keyboard_callback(event):
                keyboard_events.append(event)
                print(f"📋 KEYBOARD: {event}")
            
            km_manager.set_keyboard_callback(keyboard_callback)
            print("✓ Keyboard callback set")
        else:
            print("⚠ No keyboard callback method found")
            
        if hasattr(km_manager, 'set_mouse_callback'):
            def mouse_callback(event):
                mouse_events.append(event)
                print(f"🖱️  MOUSE: {event}")
            
            km_manager.set_mouse_callback(mouse_callback)
            print("✓ Mouse callback set")
        else:
            print("⚠ No mouse callback method found")
        
        # Alternative: Check if there are listener methods
        if hasattr(km_manager, 'start_monitoring'):
            print("✓ Starting input monitoring...")
            km_manager.start_monitoring()
        elif hasattr(km_manager, 'start_listeners'):
            print("✓ Starting input listeners...")
            km_manager.start_listeners()
        else:
            print("⚠ No monitoring start method found - checking for direct access...")
            
        print(f"\n🎯 Monitoring for 30 seconds... (Press keys/move mouse)")
        print("=" * 60)
        
        # Monitor for 30 seconds
        start_time = time.time()
        try:
            while time.time() - start_time < 30.0:
                time.sleep(0.1)
                
                # Show periodic status
                elapsed = int(time.time() - start_time)
                if elapsed % 5 == 0 and elapsed > 0:
                    print(f"⏱️  {elapsed}s elapsed - Keyboard events: {len(keyboard_events)}, Mouse events: {len(mouse_events)}")
                    
        except KeyboardInterrupt:
            print("\n⚠ Test interrupted by user")
        
        print(f"\n" + "=" * 60)
        print("TEST RESULTS")
        print("=" * 60)
        print(f"📋 Keyboard events detected: {len(keyboard_events)}")
        print(f"🖱️  Mouse events detected: {len(mouse_events)}")
        
        if len(keyboard_events) > 0:
            print("\nSample keyboard events:")
            for i, event in enumerate(keyboard_events[:5]):  # Show first 5
                print(f"  {i+1}. {event}")
                
        if len(mouse_events) > 0:
            print("\nSample mouse events:")
            for i, event in enumerate(mouse_events[:5]):  # Show first 5
                print(f"  {i+1}. {event}")
        
        # Test sending capabilities
        print(f"\n" + "=" * 60)
        print("TESTING OUTPUT CAPABILITIES")
        print("=" * 60)
        
        if hasattr(km_manager, 'send_key_press'):
            print("✓ Keyboard output available (send_key_press)")
        else:
            print("⚠ No keyboard output method found")
            
        if hasattr(km_manager, 'send_mouse_click'):
            print("✓ Mouse output available (send_mouse_click)")
        else:
            print("⚠ No mouse output method found")
            
        if hasattr(km_manager, 'send_mouse_move'):
            print("✓ Mouse movement available (send_mouse_move)")
        else:
            print("⚠ No mouse movement method found")
        
        # Clean up
        if hasattr(km_manager, 'stop_monitoring'):
            km_manager.stop_monitoring()
        elif hasattr(km_manager, 'stop_listeners'):
            km_manager.stop_listeners()
            
        linput.shutdown()
        print("\n✓ Backend shutdown complete")
        
        # Summary
        success = len(keyboard_events) > 0 or len(mouse_events) > 0
        
        print(f"\n" + "=" * 60)
        if success:
            print("🎉 SUCCESS: Input detection is working!")
        else:
            print("⚠ NOTICE: No input events detected (this may be normal)")
            print("   - Make sure you pressed keys and moved mouse during the test")
            print("   - Check that the user has permission to access input devices")
            print("   - Verify that pynput is working correctly")
        print("=" * 60)
        
        return success
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keyboard_mouse_static():
    """Test keyboard/mouse module without live monitoring."""
    print("\n" + "=" * 60)
    print("STATIC KEYBOARD/MOUSE MODULE TEST")
    print("=" * 60)
    
    try:
        import linput.keyboard_mouse
        
        # Check the module structure
        print("✓ linput.keyboard_mouse module imported")
        
        # Look for the main class
        if hasattr(linput.keyboard_mouse, 'KeyboardMouseManager'):
            manager_class = linput.keyboard_mouse.KeyboardMouseManager
            print(f"✓ KeyboardMouseManager class found")
            
            # Create instance
            manager = manager_class()
            print(f"✓ Manager instance created: {type(manager)}")
            
            # Check methods
            methods = [method for method in dir(manager) if not method.startswith('_')]
            print(f"✓ Available methods: {', '.join(methods)}")
            
            return True
        else:
            print("⚠ KeyboardMouseManager class not found")
            print("Available attributes:", [attr for attr in dir(linput.keyboard_mouse) if not attr.startswith('_')])
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pynput_directly():
    """Test pynput library directly to verify it's working."""
    print("\n" + "=" * 60)
    print("DIRECT PYNPUT TEST")
    print("=" * 60)
    
    try:
        from pynput import mouse, keyboard
        print("✓ pynput imported successfully")
        
        print("Testing keyboard listener for 10 seconds...")
        print("(Press some keys to test)")
        
        key_events = []
        
        def on_key_press(key):
            key_events.append(f"Press: {key}")
            print(f"Key pressed: {key}")
            
        def on_key_release(key):
            key_events.append(f"Release: {key}")
            print(f"Key released: {key}")
            if key == keyboard.Key.esc:
                return False  # Stop listener
        
        # Start keyboard listener
        listener = keyboard.Listener(
            on_press=on_key_press,
            on_release=on_key_release
        )
        listener.start()
        
        # Wait for events
        start_time = time.time()
        while time.time() - start_time < 10.0 and listener.running:
            time.sleep(0.1)
            
        listener.stop()
        
        print(f"✓ Detected {len(key_events)} keyboard events")
        
        if len(key_events) > 0:
            print("Sample events:")
            for event in key_events[:3]:
                print(f"  {event}")
        
        return len(key_events) > 0
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all keyboard/mouse tests."""
    print("JOYSTICK GREMLIN - LINUX KEYBOARD/MOUSE INPUT TEST")
    print("Date:", time.strftime("%Y-%m-%d %H:%M:%S"))
    
    # Check permissions
    import os
    if os.geteuid() != 0:
        print("\n⚠ WARNING: Not running as root")
        print("Some input monitoring may require elevated permissions")
        print("If tests fail, try running with: sudo python test_keyboard_mouse.py")
    
    tests = [
        ("Static Module Test", test_keyboard_mouse_static),
        ("Direct pynput Test", test_pynput_directly),
        ("Live Input Detection", test_keyboard_mouse_detection),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"RUNNING: {test_name}")
        print(f"{'='*60}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except KeyboardInterrupt:
            print(f"\n⚠ {test_name} interrupted by user")
            results.append((test_name, False))
            break
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
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
        print("🎉 All tests passed! Keyboard/mouse input is working correctly.")
        return 0
    else:
        print("⚠ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
