# -*- coding: utf-8; -*-

"""
Linux VJoyProxy Compatibility Layer

This module provides a Linux-compatible replacement for the Windows VJoyProxy
class from vjoy.vjoy. It wraps our Linux virtual joystick manager to provide
the same interface that the rest of Joystick Gremlin expects.
"""

import logging
import uuid
from typing import Dict, List, Optional, Tuple

from gremlin.virtual_joystick_manager import VirtualJoystickManager
from linput.types import DeviceSummary
import linput.virtual_output


class VJoyProxy:
    """Linux-compatible VJoyProxy replacement using virtual joystick manager."""
    
    def __init__(self):
        """Initialize the VJoy proxy with Linux virtual joystick manager."""
        self._logger = logging.getLogger(__name__)
        self._manager = VirtualJoystickManager()
        self._vjoy_to_device_id: Dict[int, int] = {}  # VJoy ID -> Linux device ID mapping
        
        # Legacy VJoy device numbering (1-based indexing)
        self._next_vjoy_id = 1
        
    def ensure_vjoy_device_exists(self, vjoy_id: int) -> bool:
        """Ensure a virtual joystick device exists with the given VJoy ID.
        
        Args:
            vjoy_id: VJoy device ID (1-based, compatible with Windows VJoy)
            
        Returns:
            True if device exists or was created successfully, False otherwise
        """
        try:
            if vjoy_id not in self._vjoy_to_device_id:
                # Create device with reasonable defaults
                device_id = self._manager.create_virtual_joystick(
                    name=f"VJoy_{vjoy_id}",
                    axis_count=8,  # Standard VJoy default
                    button_count=32,  # Standard VJoy default
                    hat_count=4   # Standard VJoy default
                )
                if device_id is not None:
                    self._vjoy_to_device_id[vjoy_id] = device_id
                    self._logger.info(f"Created virtual joystick device {vjoy_id} -> Linux ID {device_id}")
                    return True
                else:
                    self._logger.error(f"Failed to create virtual joystick device {vjoy_id}")
                    return False
            return True
            
        except Exception as e:
            self._logger.error(f"Error ensuring VJoy device {vjoy_id} exists: {e}")
            return False
    
    def get_device(self, vjoy_id: int) -> Optional[linput.virtual_output.LinuxVirtualDevice]:
        """Get the virtual joystick device with the given VJoy ID.
        
        Args:
            vjoy_id: VJoy device ID
            
        Returns:
            Virtual joystick device if it exists, None otherwise
        """
        if self.ensure_vjoy_device_exists(vjoy_id):
            device_id = self._vjoy_to_device_id.get(vjoy_id)
            if device_id is not None:
                return self._manager.get_virtual_joystick(device_id)
        return None
    
    def set_axis(self, vjoy_id: int, axis_id: int, value: float) -> bool:
        """Set axis value on a virtual joystick device.
        
        Args:
            vjoy_id: VJoy device ID
            axis_id: Axis ID (0-based)
            value: Axis value (-1.0 to 1.0)
            
        Returns:
            True if successful, False otherwise
        """
        if self.ensure_vjoy_device_exists(vjoy_id):
            device_id = self._vjoy_to_device_id.get(vjoy_id)
            if device_id is not None:
                return self._manager.set_axis(device_id, axis_id, value)
        return False
    
    def set_button(self, vjoy_id: int, button_id: int, pressed: bool) -> bool:
        """Set button state on a virtual joystick device.
        
        Args:
            vjoy_id: VJoy device ID
            button_id: Button ID (1-based, compatible with VJoy)
            pressed: True if button is pressed, False if released
            
        Returns:
            True if successful, False otherwise
        """
        if self.ensure_vjoy_device_exists(vjoy_id):
            device_id = self._vjoy_to_device_id.get(vjoy_id)
            if device_id is not None:
                # Convert to 0-based indexing for Linux
                return self._manager.set_button(device_id, button_id - 1, pressed)
        return False
    
    def set_hat(self, vjoy_id: int, hat_id: int, direction: int) -> bool:
        """Set hat (POV) direction on a virtual joystick device.
        
        Args:
            vjoy_id: VJoy device ID
            hat_id: Hat ID (1-based, compatible with VJoy)
            direction: Hat direction (0-7 for 8-way hat, -1 for center)
            
        Returns:
            True if successful, False otherwise
        """
        if self.ensure_vjoy_device_exists(vjoy_id):
            device_id = self._vjoy_to_device_id.get(vjoy_id)
            if device_id is not None:
                # Convert VJoy direction to (x, y) tuple
                if direction == -1:  # Center
                    direction_tuple = (0, 0)
                elif direction == 0:  # North
                    direction_tuple = (0, 1)
                elif direction == 1:  # NorthEast
                    direction_tuple = (1, 1)
                elif direction == 2:  # East
                    direction_tuple = (1, 0)
                elif direction == 3:  # SouthEast
                    direction_tuple = (1, -1)
                elif direction == 4:  # South
                    direction_tuple = (0, -1)
                elif direction == 5:  # SouthWest
                    direction_tuple = (-1, -1)
                elif direction == 6:  # West
                    direction_tuple = (-1, 0)
                elif direction == 7:  # NorthWest
                    direction_tuple = (-1, 1)
                else:
                    direction_tuple = (0, 0)  # Invalid direction, center
                
                # Convert to 0-based indexing for Linux
                return self._manager.set_hat(device_id, hat_id - 1, direction_tuple)
        return False
    
    def reset_device(self, vjoy_id: int) -> bool:
        """Reset all controls on a virtual joystick device to neutral state.
        
        Args:
            vjoy_id: VJoy device ID
            
        Returns:
            True if successful, False otherwise
        """
        if self.ensure_vjoy_device_exists(vjoy_id):
            device_id = self._vjoy_to_device_id.get(vjoy_id)
            if device_id is not None:
                return self._manager.reset_device(device_id)
        return False
    
    def get_device_count(self) -> int:
        """Get the number of available virtual joystick devices.
        
        Returns:
            Number of virtual joystick devices
        """
        return len(self._vjoy_to_device_id)
    
    def is_device_available(self, vjoy_id: int) -> bool:
        """Check if a virtual joystick device is available.
        
        Args:
            vjoy_id: VJoy device ID
            
        Returns:
            True if device is available, False otherwise
        """
        return vjoy_id in self._vjoy_to_device_id or self.ensure_vjoy_device_exists(vjoy_id)
    
    def get_device_info(self, vjoy_id: int) -> Optional[Dict]:
        """Get information about a virtual joystick device.
        
        Args:
            vjoy_id: VJoy device ID
            
        Returns:
            Dictionary with device information, None if device doesn't exist
        """
        device = self.get_device(vjoy_id)
        if device:
            # Get device summary from manager
            device_list = self._manager.list_virtual_joysticks()
            device_id = self._vjoy_to_device_id.get(vjoy_id)
            for did, summary in device_list:
                if did == device_id:
                    return {
                        'axis_count': summary.axis_count,
                        'button_count': summary.button_count,
                        'hat_count': summary.hat_count,
                        'name': summary.name,
                        'device_guid': summary.device_guid
                    }
        return None
    
    def cleanup(self):
        """Clean up all virtual joystick devices."""
        try:
            for vjoy_id in list(self._vjoy_to_device_id.keys()):
                device_id = self._vjoy_to_device_id[vjoy_id]
                self._manager.destroy_virtual_joystick(device_id)
                self._logger.info(f"Destroyed virtual joystick device {vjoy_id}")
            self._vjoy_to_device_id.clear()
        except Exception as e:
            self._logger.error(f"Error during VJoy cleanup: {e}")
    
    @staticmethod
    def reset():
        """Reset all VJoy devices (static method for compatibility)."""
        global _vjoy_proxy_instance
        if _vjoy_proxy_instance:
            _vjoy_proxy_instance.cleanup()
            _vjoy_proxy_instance = None


# Create a singleton instance for compatibility with Windows VJoy usage
_vjoy_proxy_instance = None

def vjoy_proxy() -> VJoyProxy:
    """Get the singleton VJoyProxy instance."""
    global _vjoy_proxy_instance
    if _vjoy_proxy_instance is None:
        _vjoy_proxy_instance = VJoyProxy()
    return _vjoy_proxy_instance
