#!/usr/bin/env python3
"""
Test to check what key codes arrow keys actually produce
"""

import time

def test_arrow_key_codes():
    print("ARROW KEY CODE DETECTION TEST")
    print("="*40)
    print("Press arrow keys to see their codes...")
    print("Press 'q' to quit")
    
    try:
        import linput
        
        linput.initialize()
        km_manager = linput.get_keyboard_mouse_manager()
        
        quit_requested = False
        
        def key_callback(event):
            nonlocal quit_requested
            if event.input_type.name == 'Key':
                key_code = event.code
                is_pressed = event.value
                
                if key_code == 113 and is_pressed:  # 'q' key
                    quit_requested = True
                    return
                    
                if is_pressed:  # Only show key presses, not releases
                    print(f"Key code: {key_code}")
                    
                    # Check if it's an arrow key
                    arrow_names = {
                        65361: "Left Arrow",
                        65362: "Up Arrow", 
                        65363: "Right Arrow",
                        65364: "Down Arrow"
                    }
                    
                    if key_code in arrow_names:
                        print(f"  -> {arrow_names[key_code]}")
                    elif 97 <= key_code <= 122:  # lowercase letters
                        print(f"  -> Letter '{chr(key_code)}'")
                    else:
                        print(f"  -> Unknown/Special key")
        
        km_manager.register_input_callback(key_callback)
        km_manager.start()
        
        print("Monitoring started... press arrow keys and other keys")
        
        # Monitor for 30 seconds or until 'q' is pressed
        start_time = time.time()
        while time.time() - start_time < 30 and not quit_requested:
            time.sleep(0.1)
        
        km_manager.stop()
        linput.shutdown()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_arrow_key_codes()
