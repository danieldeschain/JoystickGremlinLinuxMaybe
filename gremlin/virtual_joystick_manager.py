#!/usr/bin/env python3
# -*- coding: utf-8; -*-

"""
Enhanced Virtual Joystick Manager for Linux Output Backend

This module provides advanced virtual joystick management capabilities,
including permission handling, multiple device support, and robust
device lifecycle management.
"""

import logging
import os
import subprocess
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import linput
import linput.virtual_output
from linput.types import DeviceSummary


class VirtualJoystickPermissionError(Exception):
    """Raised when there are permission issues with virtual device creation."""
    pass


class VirtualJoystickManager:
    """Enhanced virtual joystick manager with permission handling and multi-device support."""
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._devices: Dict[int, linput.virtual_output.LinuxVirtualDevice] = {}
        self._device_summaries: Dict[int, DeviceSummary] = {}
        self._next_device_id = 1
        
        # Check permissions on initialization
        self._permission_status = self._check_permissions()
        
    def _check_permissions(self) -> Dict[str, bool]:
        """Check current permission status for virtual device creation."""
        status = {
            'uinput_accessible': False,
            'user_in_input_group': False,
            'uinput_module_loaded': False,
            'can_create_devices': False
        }
        
        try:
            # Check if /dev/uinput exists and is accessible
            uinput_path = Path('/dev/uinput')
            if uinput_path.exists():
                try:
                    # Try to open for reading (doesn't require write for test)
                    with open(uinput_path, 'rb'):
                        status['uinput_accessible'] = True
                except PermissionError:
                    self._logger.debug("/dev/uinput exists but not accessible")
            else:
                self._logger.debug("/dev/uinput does not exist")
                
            # Check if user is in input group
            try:
                import grp
                import os
                user_groups = [grp.getgrgid(gid).gr_name for gid in os.getgroups()]
                status['user_in_input_group'] = 'input' in user_groups
            except Exception as e:
                self._logger.debug(f"Could not check user groups: {e}")
                
            # Check if uinput module is loaded
            try:
                with open('/proc/modules', 'r') as f:
                    modules = f.read()
                    status['uinput_module_loaded'] = 'uinput' in modules
            except Exception as e:
                self._logger.debug(f"Could not check loaded modules: {e}")
                
            # Test actual device creation capability
            status['can_create_devices'] = self._test_device_creation()
                
        except Exception as e:
            self._logger.warning(f"Permission check failed: {e}")
            
        return status
    
    def _test_device_creation(self) -> bool:
        """Test if we can actually create a virtual device."""
        try:
            # Try to create a minimal test device directly
            test_device = linput.virtual_output.LinuxVirtualDevice(
                device_id=9999,  # Use high ID to avoid conflicts
                name="PermissionTest",
                axis_count=1,
                button_count=1,
                hat_count=0
            )
            test_device.create()
            test_device.destroy()
            return True
        except Exception as e:
            self._logger.debug(f"Test device creation failed: {e}")
            return False
    
    def get_permission_status(self) -> Dict[str, bool]:
        """Get current permission status."""
        return self._permission_status.copy()
    
    def get_permission_recommendations(self) -> List[str]:
        """Get recommendations for fixing permission issues."""
        recommendations = []
        
        if not self._permission_status['uinput_module_loaded']:
            recommendations.append("Load uinput module: sudo modprobe uinput")
            
        if not self._permission_status['user_in_input_group']:
            recommendations.append(f"Add user to input group: sudo usermod -a -G input {os.getenv('USER', 'username')}")
            recommendations.append("Then logout and login again for group changes to take effect")
            
        if not self._permission_status['uinput_accessible']:
            recommendations.append("Set uinput permissions: sudo chmod 666 /dev/uinput")
            recommendations.append("Or run application with sudo (not recommended for security)")
            
        if not recommendations:
            recommendations.append("Permissions appear correct - try running a test")
            
        return recommendations
    
    def create_virtual_joystick(self, 
                              name: str,
                              axis_count: int = 4,
                              button_count: int = 8, 
                              hat_count: int = 1) -> int:
        """Create a new virtual joystick device.
        
        Args:
            name: Name for the virtual device
            axis_count: Number of axes (default 4 for dual-stick)
            button_count: Number of buttons (default 8)
            hat_count: Number of hat switches (default 1)
            
        Returns:
            Device ID for the created device
            
        Raises:
            VirtualJoystickPermissionError: If permissions are insufficient
            RuntimeError: If device creation fails
        """
        if not self._permission_status['can_create_devices']:
            raise VirtualJoystickPermissionError(
                "Cannot create virtual devices. Check permissions with get_permission_recommendations()"
            )
        
        device_id = self._next_device_id
        self._next_device_id += 1
        
        try:
            # Create device directly (LinuxVirtualDevice, not via manager to avoid double-creation)
            device = linput.virtual_output.LinuxVirtualDevice(
                device_id=device_id,
                name=f"JoystickGremlin_{name}",
                axis_count=axis_count,
                button_count=button_count,
                hat_count=hat_count
            )
            
            # Actually create the device
            device.create()
            
            # Store device and create summary
            self._devices[device_id] = device
            device_summary = device.get_device_summary()
            self._device_summaries[device_id] = device_summary
            
            self._logger.info(f"Created virtual joystick: {name} (ID: {device_id})")
            return device_id
            
        except Exception as e:
            self._logger.error(f"Failed to create virtual joystick: {e}")
            raise RuntimeError(f"Virtual joystick creation failed: {e}")
    
    def destroy_virtual_joystick(self, device_id: int) -> bool:
        """Destroy a virtual joystick device.
        
        Args:
            device_id: ID of device to destroy
            
        Returns:
            True if destroyed successfully, False otherwise
        """
        if device_id not in self._devices:
            self._logger.warning(f"Device ID {device_id} not found")
            return False
            
        try:
            device = self._devices[device_id]
            device.destroy()
            
            del self._devices[device_id]
            del self._device_summaries[device_id]
            
            self._logger.info(f"Destroyed virtual joystick ID: {device_id}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to destroy device {device_id}: {e}")
            return False
    
    def get_virtual_joystick(self, device_id: int) -> Optional[linput.virtual_output.LinuxVirtualDevice]:
        """Get virtual joystick device by ID."""
        return self._devices.get(device_id)
    
    def list_virtual_joysticks(self) -> List[Tuple[int, DeviceSummary]]:
        """List all created virtual joysticks.
        
        Returns:
            List of (device_id, device_summary) tuples
        """
        return [(device_id, summary) for device_id, summary in self._device_summaries.items()]
    
    def set_axis(self, device_id: int, axis_id: int, value: float) -> bool:
        """Set axis value on virtual joystick.
        
        Args:
            device_id: Virtual device ID
            axis_id: Axis ID (0-based)
            value: Axis value (-1.0 to 1.0)
            
        Returns:
            True if successful, False otherwise
        """
        device = self._devices.get(device_id)
        if not device:
            return False
            
        try:
            device.set_axis(axis_id, value)
            return True
        except Exception as e:
            self._logger.error(f"Failed to set axis {axis_id} on device {device_id}: {e}")
            return False
    
    def set_button(self, device_id: int, button_id: int, pressed: bool) -> bool:
        """Set button state on virtual joystick.
        
        Args:
            device_id: Virtual device ID
            button_id: Button ID (0-based)
            pressed: Button state
            
        Returns:
            True if successful, False otherwise
        """
        device = self._devices.get(device_id)
        if not device:
            return False
            
        try:
            device.set_button(button_id, pressed)
            return True
        except Exception as e:
            self._logger.error(f"Failed to set button {button_id} on device {device_id}: {e}")
            return False
    
    def set_hat(self, device_id: int, hat_id: int, direction: Tuple[int, int]) -> bool:
        """Set hat switch direction on virtual joystick.
        
        Args:
            device_id: Virtual device ID
            hat_id: Hat ID (0-based)
            direction: Hat direction as (x, y) tuple (-1, 0, 1)
            
        Returns:
            True if successful, False otherwise
        """
        device = self._devices.get(device_id)
        if not device:
            return False
            
        try:
            device.set_hat(hat_id, direction)
            return True
        except Exception as e:
            self._logger.error(f"Failed to set hat {hat_id} on device {device_id}: {e}")
            return False
    
    def reset_device(self, device_id: int) -> bool:
        """Reset all controls on virtual joystick to neutral state.
        
        Args:
            device_id: Virtual device ID
            
        Returns:
            True if successful, False otherwise
        """
        device = self._devices.get(device_id)
        if not device:
            return False
            
        try:
            device.reset()
            return True
        except Exception as e:
            self._logger.error(f"Failed to reset device {device_id}: {e}")
            return False
    
    def destroy_all(self) -> int:
        """Destroy all virtual joysticks.
        
        Returns:
            Number of devices destroyed
        """
        destroyed_count = 0
        device_ids = list(self._devices.keys())
        
        for device_id in device_ids:
            if self.destroy_virtual_joystick(device_id):
                destroyed_count += 1
                
        return destroyed_count
    
    def get_device_count(self) -> int:
        """Get number of created virtual devices."""
        return len(self._devices)


# Global instance
_virtual_joystick_manager = None


def get_virtual_joystick_manager() -> VirtualJoystickManager:
    """Get the global virtual joystick manager instance."""
    global _virtual_joystick_manager
    if _virtual_joystick_manager is None:
        _virtual_joystick_manager = VirtualJoystickManager()
    return _virtual_joystick_manager
