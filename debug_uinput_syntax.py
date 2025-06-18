#!/usr/bin/env python3
"""
Test correct uinput device creation syntax.
"""

import uinput

print("Testing correct uinput syntax...")

# Method 1: Use the constants directly
print("\nTest 1: Direct axis constants...")
try:
    events = [
        uinput.ABS_X + (-32768, 32767, 0, 0),
        uinput.BTN_A
    ]
    device = uinput.Device(events, name="TestMethod1")
    print("✅ Method 1 worked!")
    device.destroy()
except Exception as e:
    print(f"❌ Method 1 failed: {e}")

# Method 2: Define axes differently
print("\nTest 2: Axis tuple method...")
try:
    events = [
        uinput.ABS_X,
        uinput.BTN_A
    ]
    device = uinput.Device(events, name="TestMethod2")
    print("✅ Method 2 worked!")
    device.destroy()
except Exception as e:
    print(f"❌ Method 2 failed: {e}")

# Method 3: Check actual uinput constants
print("\nDebugging uinput constants...")
print(f"uinput.ABS_X = {uinput.ABS_X}")
print(f"uinput.BTN_A = {uinput.BTN_A}")
print(f"type(uinput.ABS_X) = {type(uinput.ABS_X)}")
print(f"type(uinput.BTN_A) = {type(uinput.BTN_A)}")

# Method 4: Research correct syntax
print("\nTest 4: Research uinput documentation...")
try:
    # Looking at python-uinput examples, axes need min/max/fuzz/flat values
    events = [
        uinput.ABS_X + (-32768, 32767, 0, 0),  # This should be the correct syntax
        uinput.ABS_Y + (-32768, 32767, 0, 0),
        uinput.BTN_A,
        uinput.BTN_B
    ]
    device = uinput.Device(events, name="TestCorrectSyntax")
    print("✅ Correct syntax worked!")
    device.destroy()
except Exception as e:
    print(f"❌ Correct syntax failed: {e}")
    import traceback
    traceback.print_exc()
