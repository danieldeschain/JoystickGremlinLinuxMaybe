#!/usr/bin/env python3
# -*- coding: utf-8; -*-

"""
Simple test to verify keyboard/mouse input monitoring with correct API.
"""

import time
import sys

def test_input_monitoring():
    """Test input monitoring with the correct API."""
    print("=" * 60)
    print("KEYBOARD/MOUSE INPUT MONITORING TEST")
    print("=" * 60)
    
    try:
        import linput
        
        print("Initializing backend...")
        linput.initialize()
        
        # Get keyboard/mouse manager
        km_manager = linput.get_keyboard_mouse_manager()
        print(f"✓ Got manager: {type(km_manager)}")
        
        # Set up callback
        events_received = []
        
        def input_callback(event):
            events_received.append(event)
            print(f"📥 Input Event: {event.input_type} code={event.code} value={event.value}")
        
        # Register the callback
        km_manager.register_input_callback(input_callback)
        print("✓ Input callback registered")
        
        # Start monitoring
        km_manager.start()
        print("✓ Monitoring started")
        
        print("\n" + "="*50)
        print("🎯 MONITORING ACTIVE - Press keys and move mouse!")
        print("Test will run for 15 seconds...")
        print("="*50)
        
        # Monitor for 15 seconds
        start_time = time.time()
        try:
            while time.time() - start_time < 15.0:
                time.sleep(0.5)
                elapsed = int(time.time() - start_time)
                if elapsed % 3 == 0 and elapsed > 0:
                    print(f"⏱️  {elapsed}s - Events received: {len(events_received)}")
                    
        except KeyboardInterrupt:
            print("\n⚠ Interrupted by user")
        
        # Stop monitoring
        km_manager.stop()
        print(f"\n✓ Monitoring stopped")
        
        # Results
        print(f"\n📊 RESULTS:")
        print(f"Total events received: {len(events_received)}")
        
        if len(events_received) > 0:
            print("Sample events:")
            for i, event in enumerate(events_received[:5]):
                print(f"  {i+1}. Type:{event.input_type} Code:{event.code} Value:{event.value}")
        
        # Test output capabilities
        print(f"\n🔧 Testing output capabilities...")
        
        print("Testing text output...")
        km_manager.send_text("test")
        
        print("✓ Keyboard output test complete")
        
        # Cleanup
        linput.shutdown()
        print("✓ Backend shutdown")
        
        success = len(events_received) > 0
        if success:
            print("\n🎉 SUCCESS: Input monitoring is working!")
        else:
            print("\n⚠ No events detected - try moving mouse or pressing keys during test")
        
        return success
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_input_monitoring()
    sys.exit(0 if success else 1)
