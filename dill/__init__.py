# -*- coding: utf-8; -*-

"""
Linux-compatible DILL module replacement for Joystick Penguin

This module provides a Linux-compatible replacement for the Windows-specific
DILL (Device Input Library) module. It bridges the gap between the Windows 
DILL interface and our Linux linput module, enabling the full Joystick Gremlin
mapping engine to work on Linux.
"""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Any, Callable, List, Optional

# Import our Linux input types
try:
    from linput.types import (
        DeviceSummary as LinputDeviceSummary, 
        InputEvent as LinputInputEvent,
        InputType as LinputInputType, 
        DeviceActionType as LinputDeviceActionType,
        UUID_Keyboard, UUID_Virtual, UUID_Invalid
    )
    import linput
    LINPUT_AVAILABLE = True
except ImportError:
    LINPUT_AVAILABLE = False
    # Fallback UUIDs if linput not available
    UUID_Keyboard = uuid.uuid5(uuid.NAMESPACE_OID, "Keyboard")
    UUID_Virtual = uuid.uuid5(uuid.NAMESPACE_OID, "Virtual")
    UUID_Invalid = uuid.UUID("00000000-0000-0000-0000-000000000000")


class DILLError(Exception):
    """Exception raised when an error occurs within the DILL module."""
    
    def __init__(self, value: str):
        super().__init__(value)


class GUID:
    """Linux-compatible GUID class using Python's uuid module."""
    
    def __init__(self, guid_uuid: uuid.UUID):
        """Create GUID from UUID."""
        self._uuid = guid_uuid
    
    @staticmethod
    def from_str(value: str) -> GUID:
        """Create GUID from string representation."""
        return GUID(uuid.UUID(value))
    
    @staticmethod
    def from_uuid(value: uuid.UUID) -> GUID:
        """Create GUID from UUID."""
        return GUID(value)
    
    @property
    def uuid(self) -> uuid.UUID:
        """Return UUID representation."""
        return self._uuid
    
    def __str__(self) -> str:
        """Return string representation."""
        return str(self._uuid).upper()
    
    def __eq__(self, other) -> bool:
        """Check equality."""
        if isinstance(other, GUID):
            return self._uuid == other._uuid
        elif isinstance(other, uuid.UUID):
            return self._uuid == other
        return False
    
    def __lt__(self, other) -> bool:
        """Less than comparison."""
        return str(self) < str(other)
    
    def __hash__(self) -> int:
        """Return hash."""
        return hash(self._uuid)


# Create predefined GUID instances compatible with Windows version
GUID_Keyboard = GUID(UUID_Keyboard)
GUID_Virtual = GUID(UUID_Virtual) 
GUID_Invalid = GUID(UUID_Invalid)

# Create intermediate output GUID (consistent UUID for application use)
_UUID_IntermediateOutput = uuid.uuid5(uuid.NAMESPACE_OID, "IntermediateOutput")
GUID_IntermediateOutput = GUID(_UUID_IntermediateOutput)

# Export UUID versions for compatibility
UUID_IntermediateOutput = GUID_IntermediateOutput.uuid


class InputType(Enum):
    """Enumeration of valid input types."""
    
    Axis = 1
    Button = 2  
    Hat = 3
    
    @staticmethod
    def from_ctype(value: int):
        """Convert from numeric value."""
        if value == 1:
            return InputType.Axis
        elif value == 2:
            return InputType.Button
        elif value == 3:
            return InputType.Hat
        else:
            raise DILLError(f"Invalid input type value {value}")


class DeviceActionType(Enum):
    """Represents device state changes."""
    
    Connected = 1
    Disconnected = 2
    
    @staticmethod
    def from_ctype(value: int):
        """Convert from numeric value."""
        if value == 1:
            return DeviceActionType.Connected
        elif value == 2:
            return DeviceActionType.Disconnected
        else:
            raise DILLError(f"Invalid device action type {value}")


class InputEvent:
    """Linux-compatible input event wrapper."""
    
    def __init__(self, linput_event: LinputInputEvent):
        """Create from linput InputEvent."""
        self.device_guid = GUID(linput_event.device_guid)
        
        # Convert input types
        if linput_event.input_type == LinputInputType.JoystickAxis:
            self.input_type = InputType.Axis
        elif linput_event.input_type == LinputInputType.JoystickButton:
            self.input_type = InputType.Button
        elif linput_event.input_type == LinputInputType.JoystickHat:
            self.input_type = InputType.Hat
        else:
            self.input_type = InputType.Button  # Default fallback
        
        self.input_index = linput_event.input_id
        
        # Convert values - DILL expects integer values
        if hasattr(linput_event, 'raw_value') and linput_event.raw_value is not None:
            self.value = int(linput_event.raw_value)
        elif isinstance(linput_event.value, bool):
            self.value = 1 if linput_event.value else 0
        elif isinstance(linput_event.value, (int, float)):
            if self.input_type == InputType.Axis:
                # Convert from [-1.0, 1.0] to DirectInput range
                self.value = int(linput_event.value * 32767)
            else:
                self.value = int(linput_event.value)
        else:
            self.value = 0


class AxisMap:
    """Linux-compatible axis map."""
    
    def __init__(self, axis_index: int, linear_index: int):
        self.axis_index = axis_index
        self.linear_index = linear_index


class DeviceSummary:
    """Linux-compatible device summary wrapper."""
    
    def __init__(self, linput_summary: LinputDeviceSummary):
        """Create from linput DeviceSummary."""
        self.device_guid = GUID(linput_summary.device_guid)
        self.vendor_id = linput_summary.vendor_id
        self.product_id = linput_summary.product_id
        self.joystick_id = 0  # Not used in Linux
        self.name = linput_summary.name
        self.axis_count = linput_summary.axis_count
        self.button_count = linput_summary.button_count
        self.hat_count = linput_summary.hat_count
        
        # Convert axis map
        self.axis_map = []
        self.axis_lookup = {}
        for axis_mapping in linput_summary.axis_map:
            axis_map = AxisMap(axis_mapping.axis_id, axis_mapping.axis_index)
            self.axis_map.append(axis_map)
            self.axis_lookup[axis_mapping.axis_id] = axis_mapping.axis_index
        
        # Pad axis map to 8 entries (Windows DILL compatibility)
        while len(self.axis_map) < 8:
            self.axis_map.append(AxisMap(0, 0))
        
        self.vjoy_id = -1
        self._is_virtual = linput_summary.is_virtual
    
    @property
    def is_virtual(self) -> bool:
        """Check if device is virtual."""
        return self._is_virtual
    
    def set_vjoy_id(self, vjoy_id: int) -> None:
        """Set vJoy ID for virtual devices."""
        if self.is_virtual:
            self.vjoy_id = vjoy_id


class DILL:
    """Linux-compatible DILL interface using linput backend."""
    
    _initialized = False
    _device_change_callback = None
    _input_event_callback = None
    _input_manager = None
    
    @staticmethod
    def initialize():
        """Initialize the DILL system."""
        if not DILL._initialized and LINPUT_AVAILABLE:
            try:
                linput.initialize()
                
                # Get input manager and set up callbacks
                DILL._input_manager = linput.get_device_manager()
                if DILL._input_event_callback:
                    DILL._input_manager.set_input_event_callback(DILL._linput_input_callback)
                if DILL._device_change_callback:
                    DILL._input_manager.set_device_change_callback(DILL._linput_device_callback)
                
                DILL._initialized = True
                print("✅ DILL compatibility layer initialized with linput backend")
            except Exception as e:
                print(f"❌ DILL initialization failed: {e}")
                raise DILLError(f"Failed to initialize Linux input backend: {e}")
        elif not LINPUT_AVAILABLE:
            raise DILLError("linput module not available")
    
    @staticmethod
    def shutdown():
        """Shutdown the DILL system."""
        if DILL._initialized and LINPUT_AVAILABLE:
            try:
                linput.shutdown()
                DILL._initialized = False
                DILL._input_manager = None
                print("✅ DILL compatibility layer shutdown")
            except Exception as e:
                print(f"⚠ DILL shutdown error: {e}")
    
    @staticmethod
    def get_device_count() -> int:
        """Get number of devices."""
        if not DILL._initialized:
            return 0
        try:
            return len(linput.get_joystick_devices())
        except Exception:
            return 0
    
    @staticmethod
    def get_device_information_by_index(index: int) -> DeviceSummary:
        """Get device information by index."""
        if not DILL._initialized:
            raise DILLError("DILL not initialized")
        
        try:
            devices = linput.get_joystick_devices()
            if 0 <= index < len(devices):
                return DeviceSummary(devices[index])
            raise DILLError(f"Invalid device index: {index}")
        except Exception as e:
            raise DILLError(f"Failed to get device {index}: {e}")
    
    @staticmethod
    def get_device_information_by_guid(guid: GUID) -> DeviceSummary:
        """Get device information by GUID."""
        if not DILL._initialized:
            raise DILLError("DILL not initialized")
        
        if not LINPUT_AVAILABLE:
            raise DILLError("Linput backend not available")
        
        # Handle null GUID case gracefully (common when no devices are connected)
        null_guid = uuid.UUID('00000000-0000-0000-0000-000000000000')
        if guid.uuid == null_guid:
            # Return a dummy device summary for null GUID
            from linput.types import DeviceSummary as LinputDeviceSummary
            dummy_device = LinputDeviceSummary(
                device_guid=null_guid,
                name="No Device",
                vendor_id=0,
                product_id=0,
                axis_count=0,
                button_count=0,
                hat_count=0,
                axis_map=[],
                is_virtual=False,
                vjoy_id=0,
                device_path=""
            )
            return DeviceSummary(dummy_device)
        
        try:
            import linput
            devices = linput.get_joystick_devices()
            for device in devices:
                if device.device_guid == guid.uuid:
                    return DeviceSummary(device)
            raise DILLError(f"Device with GUID {guid} not found")
        except Exception as e:
            raise DILLError(f"Failed to find device {guid}: {e}")
    
    @staticmethod
    def set_device_change_callback(callback: Callable[[DeviceSummary, DeviceActionType], None]):
        """Set device change callback."""
        DILL._device_change_callback = callback
        if DILL._input_manager:
            DILL._input_manager.set_device_change_callback(DILL._linput_device_callback)
    
    @staticmethod
    def set_input_event_callback(callback: Callable[[InputEvent], None]):
        """Set input event callback."""
        DILL._input_event_callback = callback
        if DILL._input_manager:
            DILL._input_manager.set_input_event_callback(DILL._linput_input_callback)
    
    @staticmethod
    def _linput_input_callback(linput_event):
        """Convert linput event to DILL event and forward."""
        if DILL._input_event_callback:
            try:
                dill_event = InputEvent(linput_event)
                DILL._input_event_callback(dill_event)
            except Exception as e:
                print(f"⚠ Error in input event callback: {e}")
    
    @staticmethod
    def _linput_device_callback(device_summary, action_type):
        """Convert linput device change to DILL device change and forward."""
        if DILL._device_change_callback:
            try:
                from linput.types import DeviceActionType as LinputDeviceActionType
                dill_summary = DeviceSummary(device_summary)
                # Convert action type
                if action_type == LinputDeviceActionType.Connected:
                    dill_action = DeviceActionType.Connected
                else:
                    dill_action = DeviceActionType.Disconnected
                
                DILL._device_change_callback(dill_summary, dill_action)
            except Exception as e:
                print(f"⚠ Error in device change callback: {e}")


# Compatibility functions for direct module usage
def initialize():
    """Initialize DILL."""
    DILL.initialize()

def shutdown():
    """Shutdown DILL."""
    DILL.shutdown()

def get_device_count() -> int:
    """Get device count."""
    return DILL.get_device_count()

def get_device_information_by_index(index: int) -> DeviceSummary:
    """Get device by index."""
    return DILL.get_device_information_by_index(index)

def get_device_information_by_guid(guid: GUID) -> DeviceSummary:
    """Get device by GUID."""
    return DILL.get_device_information_by_guid(guid)

def set_device_change_callback(callback):
    """Set device change callback."""
    DILL.set_device_change_callback(callback)

def set_input_event_callback(callback):
    """Set input event callback."""
    DILL.set_input_event_callback(callback)
