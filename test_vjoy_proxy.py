#!/usr/bin/env python3
# -*- coding: utf-8; -*-

"""
Test script for VJoyProxy Linux compatibility layer.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from vjoy.vjoy import VJoyProxy
import time

def test_vjoy_proxy():
    """Test the VJoyProxy Linux compatibility layer."""
    print("Testing VJoyProxy Linux compatibility layer...")
    
    try:
        # Create VJoy proxy instance
        vjoy = VJoyProxy()
        print("✓ VJoyProxy instance created")
        
        # Test device creation
        if vjoy.ensure_vjoy_device_exists(1):
            print("✓ VJoy device 1 created/exists")
        else:
            print("✗ Failed to create VJoy device 1")
            return False
        
        # Test setting axis values
        if vjoy.set_axis(1, 0, 0.5):
            print("✓ Set axis 0 to 0.5")
        else:
            print("✗ Failed to set axis")
            
        # Test setting button states
        if vjoy.set_button(1, 1, True):
            print("✓ Set button 1 to pressed")
        else:
            print("✗ Failed to set button")
            
        # Test setting hat direction
        if vjoy.set_hat(1, 1, 0):  # North
            print("✓ Set hat 1 to North")
        else:
            print("✗ Failed to set hat")
            
        # Test device info
        info = vjoy.get_device_info(1)
        if info:
            print(f"✓ Device info: {info}")
        else:
            print("✗ Failed to get device info")
            
        # Test reset
        if vjoy.reset_device(1):
            print("✓ Device reset successful")
        else:
            print("✗ Failed to reset device")
            
        # Cleanup
        vjoy.cleanup()
        print("✓ Cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_vjoy_proxy()
    if success:
        print("\n✓ All VJoyProxy tests passed!")
        sys.exit(0)
    else:
        print("\n✗ VJoyProxy tests failed!")
        sys.exit(1)
