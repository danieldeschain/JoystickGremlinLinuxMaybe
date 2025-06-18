#!/usr/bin/env python3
# -*- coding: utf-8; -*-

"""
Quick test to verify keyboard/mouse input monitoring works.
"""

import time
import sys

def quick_test():
    """Quick test with 5 second monitoring."""
    print("QUICK INPUT MONITORING TEST (5 seconds)")
    print("="*50)
    
    try:
        import linput
        
        print("1. Initializing...")
        linput.initialize()
        
        print("2. Getting manager...")
        km_manager = linput.get_keyboard_mouse_manager()
        
        print("3. Setting up callback...")
        events = []
        
        def callback(event):
            events.append(event)
            print(f"   📥 {event.input_type} code={event.code} value={event.value}")
        
        km_manager.register_input_callback(callback)
        
        print("4. Starting monitoring...")
        km_manager.start()
        
        print("5. 🎯 MONITORING (press keys now!) - 5 seconds...")
        time.sleep(5)
        
        print("6. Stopping...")
        km_manager.stop()
        
        print("7. Testing output...")
        km_manager.send_text("hello")
        
        print("8. Cleanup...")
        linput.shutdown()
        
        print(f"\n✅ RESULTS: {len(events)} events detected")
        
        if len(events) > 0:
            print("Sample events:")
            for i, e in enumerate(events[:3]):
                print(f"  {i+1}. {e.input_type} code={e.code}")
        
        return len(events) > 0
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = quick_test()
    print(f"\n{'✅ SUCCESS' if success else '⚠ NO EVENTS'}")
    sys.exit(0 if success else 1)
