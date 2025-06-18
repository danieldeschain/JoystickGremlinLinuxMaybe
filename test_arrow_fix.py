#!/usr/bin/env python3

"""
Quick test of corrected arrow key mapping.
"""

import time

def quick_arrow_test():
    print("QUICK ARROW KEY TEST")
    print("=" * 40)
    
    try:
        import linput
        linput.initialize()
        
        km_manager = linput.get_keyboard_mouse_manager()
        
        # Virtual joystick state
        state = {
            'left_x': 0.0, 'left_y': 0.0,
            'right_x': 0.0, 'right_y': 0.0,
            'buttons': [False, False]
        }
        
        # Corrected key mappings
        mappings = {
            # WASD = Left stick
            97: ('left_x', -1.0),   # A
            100: ('left_x', 1.0),   # D
            119: ('left_y', 1.0),   # W
            115: ('left_y', -1.0),  # S
            
            # Arrow keys = Right stick
            37: ('right_x', -1.0),  # Left arrow
            39: ('right_x', 1.0),   # Right arrow
            38: ('right_y', 1.0),   # Up arrow
            40: ('right_y', -1.0),  # Down arrow
            
            # Buttons
            32: ('button', 0),      # Space
            13: ('button', 1),      # Enter
        }
        
        def handle_input(event):
            if event.input_type.name != 'Key':
                return
                
            code = event.code
            pressed = event.value
            
            if code == 113:  # Q to quit
                print("🛑 Quit key pressed")
                return
                
            if code in mappings:
                mapping = mappings[code]
                
                if mapping[0] == 'button':
                    button_idx = mapping[1]
                    state['buttons'][button_idx] = pressed
                    print(f"🎮 Button {button_idx + 1}: {'ON' if pressed else 'OFF'}")
                else:
                    axis = mapping[0]
                    value = mapping[1] if pressed else 0.0
                    state[axis] = value
                    
                    # Show current state
                    print(f"🕹️  Left: X={state['left_x']:+.1f} Y={state['left_y']:+.1f}")
                    print(f"🕹️  Right: X={state['right_x']:+.1f} Y={state['right_y']:+.1f}")
                    print("-" * 30)
        
        km_manager.register_input_callback(handle_input)
        km_manager.start()
        
        print("Controls:")
        print("  WASD = Left stick")
        print("  Arrow keys = Right stick")
        print("  Space/Enter = Buttons")
        print("  Q = Quit")
        print()
        print("Testing for 20 seconds...")
        print("=" * 40)
        
        time.sleep(20)
        
        km_manager.stop()
        linput.shutdown()
        
        print("\n✅ Test complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_arrow_test()
