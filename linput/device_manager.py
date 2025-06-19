# -*- coding: utf-8; -*-

# Copyright (C) 2025 Linux Port Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Linux Input Device Manager

Pure Linux implementation for managing input devices using evdev and pyudev.
"""

from __future__ import annotations

import asyncio
import logging
import threading
import time
import uuid
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set

import evdev
import pyudev

from .types import (
    InputEvent,
    DeviceSummary, 
    InputType,
    DeviceActionType,
    AxisMap,
    UUID_Keyboard,
    UUID_Virtual
)
from . import virtual_output


class EvdevInputError(Exception):
    """Exception raised when an error occurs in the input system."""
    
    def __init__(self, message: str):
        super().__init__(message)


class EvdevInputManager:
    """
    Linux Input Manager using evdev
    
    Manages joystick/gamepad input devices on Linux using the evdev library.
    """
    
    def __init__(self):
        """Initialize the input manager."""
        self._devices: Dict[str, evdev.InputDevice] = {}
        self._device_summaries: List[DeviceSummary] = []
        self._device_paths: Dict[uuid.UUID, str] = {}
        
        # Hat state tracking for combining X/Y events
        self._hat_state: Dict[uuid.UUID, Dict[int, Dict[str, int]]] = {}
        
        # Event callbacks
        self._input_event_callback: Optional[Callable[[InputEvent], None]] = None
        self._device_change_callback: Optional[Callable[[DeviceSummary, DeviceActionType], None]] = None
        
        # Threading for device monitoring and event processing
        self._monitor_thread: Optional[threading.Thread] = None
        self._event_thread: Optional[threading.Thread] = None
        self._running = False
        
        # Device monitoring with udev
        self._udev_context = pyudev.Context()
        self._udev_monitor = pyudev.Monitor.from_netlink(self._udev_context)
        self._udev_monitor.filter_by(subsystem='input')
        
        self._logger = logging.getLogger(__name__)
        self._logger.info("EvdevInputManager initialized")
    
    def start(self) -> None:
        """Start the input manager."""
        if self._running:
            return
        
        self._logger.info("Starting input manager...")
        self._running = True  # Set running flag BEFORE starting threads
        self._scan_devices()
        self._start_monitoring()
        self._logger.info("Input manager started")
    
    def stop(self) -> None:
        """Stop the input manager."""
        if not self._running:
            return
        
        self._logger.info("Stopping input manager...")
        self._running = False
        self._stop_monitoring()
        self._close_all_devices()
        self._logger.info("Input manager stopped")
    
    def get_device_count(self) -> int:
        """Get the number of detected joystick devices."""
        return len(self._device_summaries)
    
    def get_devices(self) -> List[DeviceSummary]:
        """Get all detected devices."""
        return self._device_summaries.copy()
    
    def get_device_by_index(self, index: int) -> DeviceSummary:
        """Get device by index."""
        if 0 <= index < len(self._device_summaries):
            return self._device_summaries[index]
        raise EvdevInputError(f"Invalid device index: {index}")
    
    def get_device_by_guid(self, device_guid: uuid.UUID) -> DeviceSummary:
        """Get device by GUID."""
        for device in self._device_summaries:
            if device.device_guid == device_guid:
                return device
        raise EvdevInputError(f"Device with GUID {device_guid} not found")
    
    def device_exists(self, device_guid: uuid.UUID) -> bool:
        """Check if device exists."""
        try:
            self.get_device_by_guid(device_guid)
            return True
        except EvdevInputError:
            return False
    
    def set_input_event_callback(self, callback: Callable[[InputEvent], None]) -> None:
        """Set callback for input events."""
        self._input_event_callback = callback
    
    def set_device_change_callback(self, callback: Callable[[DeviceSummary, DeviceActionType], None]) -> None:
        """Set callback for device changes."""
        self._device_change_callback = callback
    
    def _scan_devices(self) -> None:
        """Scan for available joystick devices."""
        self._device_summaries.clear()
        self._devices.clear()
        self._device_paths.clear()
        
        device_paths = evdev.list_devices()
        self._logger.debug(f"Found {len(device_paths)} input devices")
        
        for device_path in device_paths:
            try:
                device = evdev.InputDevice(device_path)
                if self._is_joystick_device(device):
                    summary = self._create_device_summary(device)
                    if summary:
                        self._device_summaries.append(summary)
                        self._devices[device_path] = device
                        self._device_paths[summary.device_guid] = device_path
                        
                        self._logger.info(f"Added joystick: {summary.name} ({summary.device_guid})")
                else:
                    device.close()
                        
            except (OSError, PermissionError) as e:
                self._logger.warning(f"Cannot access device {device_path}: {e}")
                continue
        
        self._logger.info(f"Found {len(self._device_summaries)} joystick devices")
    
    def _is_joystick_device(self, device: evdev.InputDevice) -> bool:
        """Check if device is a joystick/gamepad."""
        caps = device.capabilities()
        
        # Must have key or absolute axis capabilities
        has_abs = evdev.ecodes.EV_ABS in caps
        has_key = evdev.ecodes.EV_KEY in caps
        
        if not (has_abs or has_key):
            return False
        
        # Check for joystick-specific axes
        if has_abs:
            abs_axes = caps.get(evdev.ecodes.EV_ABS, [])
            joystick_axes = {
                evdev.ecodes.ABS_X, evdev.ecodes.ABS_Y,
                evdev.ecodes.ABS_RX, evdev.ecodes.ABS_RY,
                evdev.ecodes.ABS_Z, evdev.ecodes.ABS_RZ,
                evdev.ecodes.ABS_HAT0X, evdev.ecodes.ABS_HAT0Y,
                evdev.ecodes.ABS_THROTTLE, evdev.ecodes.ABS_RUDDER
            }
            if any(axis in abs_axes for axis in joystick_axes):
                return True
        
        # Check for joystick/gamepad buttons
        if has_key:
            key_codes = caps.get(evdev.ecodes.EV_KEY, [])
            # Check for joystick buttons
            joystick_btns = set(range(evdev.ecodes.BTN_JOYSTICK, evdev.ecodes.BTN_JOYSTICK + 16))
            gamepad_btns = set(range(evdev.ecodes.BTN_GAMEPAD, evdev.ecodes.BTN_GAMEPAD + 16))
            if any(btn in key_codes for btn in (joystick_btns | gamepad_btns)):
                return True
        
        return False
    
    def _create_device_summary(self, device: evdev.InputDevice) -> Optional[DeviceSummary]:
        """Create device summary from evdev device."""
        try:
            caps = device.capabilities()
            self._logger.debug(f"Creating device summary for {device.name}")
            self._logger.debug(f"  Capabilities: {list(caps.keys())}")
            
            # Check if this is a virtual device first
            is_virtual = virtual_output.is_virtual_device_name(device.name)
            
            # Generate UUID - use virtual device's UUID if available, otherwise generate one
            if is_virtual:
                # Find the virtual device and use its UUID
                virtual_devices = virtual_output.get_virtual_devices()
                device_uuid = None
                for vdev in virtual_devices:
                    if vdev.name == device.name:
                        device_uuid = vdev.device_guid
                        break
                
                if device_uuid is None:
                    # Fallback: generate UUID for virtual device
                    device_info = f"virtual:{device.name}"
                    device_uuid = uuid.uuid5(UUID_Virtual, device_info)
            else:
                # Generate deterministic UUID from device info for physical devices
                device_info = f"{device.info.vendor:04x}:{device.info.product:04x}:{device.name}:{device.path}"
                device_uuid = uuid.uuid5(uuid.NAMESPACE_OID, device_info)
            
            # Map and count axes
            axis_count = 0
            axis_map = []
            if evdev.ecodes.EV_ABS in caps:
                abs_axes = caps[evdev.ecodes.EV_ABS]
                self._logger.debug(f"  Found {len(abs_axes)} absolute axes: {[a[0] if isinstance(a, tuple) else a for a in abs_axes]}")
                
                # Standard joystick axis mapping
                standard_axes = {
                    evdev.ecodes.ABS_X: 1,      # Left stick X
                    evdev.ecodes.ABS_Y: 2,      # Left stick Y  
                    evdev.ecodes.ABS_Z: 3,      # Left trigger
                    evdev.ecodes.ABS_RX: 4,     # Right stick X
                    evdev.ecodes.ABS_RY: 5,     # Right stick Y
                    evdev.ecodes.ABS_RZ: 6,     # Right trigger
                    evdev.ecodes.ABS_THROTTLE: 7,
                    evdev.ecodes.ABS_RUDDER: 8,
                    evdev.ecodes.ABS_WHEEL: 9,
                    evdev.ecodes.ABS_GAS: 10,
                    evdev.ecodes.ABS_BRAKE: 11,
                }
                
                for evdev_axis in abs_axes:
                    evdev_code = evdev_axis[0] if isinstance(evdev_axis, tuple) else evdev_axis
                    self._logger.debug(f"Processing axis {evdev_code} (full: {evdev_axis})")
                    if evdev_code in standard_axes:
                        axis_id = standard_axes[evdev_code]
                        axis_map.append(AxisMap(axis_index=axis_id, axis_id=evdev_code))
                        axis_count += 1
                        self._logger.debug(f"  ✅ Mapped axis {evdev_code} to ID {axis_id}")
                    else:
                        self._logger.debug(f"  ❌ Axis {evdev_code} not in standard mapping")
            
            # Count buttons using comprehensive mapping
            button_count = 0
            if evdev.ecodes.EV_KEY in caps:
                key_codes = caps[evdev.ecodes.EV_KEY]
                # Use our comprehensive mapping to count ALL buttons
                mapped_buttons = set()
                for key_code in key_codes:
                    button_id = self._map_button_code_to_id(key_code)
                    if button_id is not None:
                        mapped_buttons.add(button_id)
                button_count = len(mapped_buttons)
                self._logger.debug(f"  ✅ Comprehensive button count: {button_count} (mapped button IDs: {sorted(mapped_buttons)})")
            
            # Count hat switches (D-pads)  
            hat_count = 0
            if evdev.ecodes.EV_ABS in caps:
                abs_axes_data = caps[evdev.ecodes.EV_ABS]
                # Extract just the axis codes from the (axis_code, AbsInfo) tuples
                abs_axis_codes = [axis[0] for axis in abs_axes_data]
                self._logger.debug(f"  Available axis codes: {abs_axis_codes}")
                
                # Check for hat pairs - each hat has X and Y components
                hat_pairs = [
                    (evdev.ecodes.ABS_HAT0X, evdev.ecodes.ABS_HAT0Y),
                    (evdev.ecodes.ABS_HAT1X, evdev.ecodes.ABS_HAT1Y),
                    (evdev.ecodes.ABS_HAT2X, evdev.ecodes.ABS_HAT2Y),
                    (evdev.ecodes.ABS_HAT3X, evdev.ecodes.ABS_HAT3Y)
                ]
                for hat_x, hat_y in hat_pairs:
                    if hat_x in abs_axis_codes and hat_y in abs_axis_codes:
                        hat_count += 1
                        self._logger.debug(f"  ✅ Found HAT {hat_count}: axes {hat_x}, {hat_y}")
                    elif hat_x in abs_axis_codes or hat_y in abs_axis_codes:
                        self._logger.debug(f"  ⚠️  Partial HAT found: {hat_x if hat_x in abs_axis_codes else hat_y} (missing pair)")
                
                self._logger.debug(f"  Total HATs detected: {hat_count}")
            
            self._logger.debug(f"  Device summary created: {axis_count} axes, {button_count} buttons, {hat_count} hats")
            
            # Extract joystick ID from device path (e.g., /dev/input/js0 -> 0)
            joystick_id = 0
            try:
                # Look for corresponding js device
                import glob
                js_devices = glob.glob("/dev/input/js*")
                for js_path in js_devices:
                    try:
                        js_device = evdev.InputDevice(js_path)
                        if js_device.name == device.name:
                            joystick_id = int(js_path.split('js')[-1])
                            break
                    except:
                        continue
            except:
                pass
            
            return DeviceSummary(
                device_guid=device_uuid,
                name=device.name,
                vendor_id=device.info.vendor,
                product_id=device.info.product,
                axis_count=axis_count,
                button_count=button_count,
                hat_count=hat_count,
                axis_map=axis_map,
                is_virtual=is_virtual,
                device_path=device.path,
                joystick_id=joystick_id
            )
            
        except Exception as e:
            self._logger.error(f"Failed to create device summary for {device.path}: {e}")
            return None
    
    def _start_monitoring(self) -> None:
        """Start device and event monitoring threads."""
        # Start device change monitoring
        self._monitor_thread = threading.Thread(target=self._monitor_device_changes, daemon=True)
        self._monitor_thread.start()
        
        # Start input event processing  
        self._event_thread = threading.Thread(target=self._process_input_events, daemon=True)
        self._event_thread.start()
        
        self._logger.debug("Started monitoring threads")
    
    def _stop_monitoring(self) -> None:
        """Stop monitoring threads."""
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=1.0)
        
        if self._event_thread and self._event_thread.is_alive():
            self._event_thread.join(timeout=1.0)
        
        self._logger.debug("Stopped monitoring threads")
    
    def _monitor_device_changes(self) -> None:
        """Monitor for device connection/disconnection."""
        self._logger.debug("Device change monitoring thread started")
        
        try:
            for device in iter(self._udev_monitor.poll, None):
                if not self._running:
                    break
                
                if device.action in ['add', 'remove'] and device.device_node and 'event' in device.device_node:
                    self._handle_device_change(device)
                    
        except Exception as e:
            self._logger.error(f"Device monitoring error: {e}")
    
    def _handle_device_change(self, udev_device) -> None:
        """Handle device connection/disconnection."""
        try:
            device_path = udev_device.device_node
            
            if udev_device.action == 'add':
                # Give device time to initialize
                time.sleep(0.2)
                
                try:
                    device = evdev.InputDevice(device_path)
                    if self._is_joystick_device(device):
                        summary = self._create_device_summary(device)
                        if summary:
                            self._device_summaries.append(summary)
                            self._devices[device_path] = device
                            self._device_paths[summary.device_guid] = device_path
                            
                            self._logger.info(f"Device connected: {summary.name}")
                            
                            if self._device_change_callback:
                                self._device_change_callback(summary, DeviceActionType.Connected)
                    else:
                        device.close()
                        
                except (OSError, PermissionError) as e:
                    self._logger.warning(f"Cannot access new device {device_path}: {e}")
            
            elif udev_device.action == 'remove':
                if device_path in self._devices:
                    device = self._devices.pop(device_path)
                    device.close()
                    
                    # Find and remove from summaries
                    for i, summary in enumerate(self._device_summaries):
                        if self._device_paths.get(summary.device_guid) == device_path:
                            del self._device_summaries[i]
                            del self._device_paths[summary.device_guid]
                            
                            self._logger.info(f"Device disconnected: {summary.name}")
                            
                            if self._device_change_callback:
                                self._device_change_callback(summary, DeviceActionType.Disconnected)
                            break
                            
        except Exception as e:
            self._logger.warning(f"Error handling device change: {e}")
    
    def _process_input_events(self) -> None:
        """Process input events from all devices."""
        self._logger.debug("Input event processing thread started")
        
        try:
            event_count = 0
            loop_count = 0
            while self._running:
                try:
                    loop_count += 1
                    if loop_count % 1000 == 0:  # Log every 1000 loops
                        self._logger.debug(f"Event processing loop {loop_count}, devices: {len(self._devices)}, callback set: {self._input_event_callback is not None}")
                    
                    if not self._devices:
                        time.sleep(0.1)
                        continue
                    
                    # Check each device for events
                    for device_path, device in list(self._devices.items()):
                        try:
                            # Read all available events, not just one
                            events = []
                            while True:
                                event = device.read_one()
                                if event is None:
                                    break
                                events.append(event)
                            
                            # Process all events
                            for event in events:
                                if self._input_event_callback:
                                    self._handle_input_event(device, event)
                                    event_count += 1
                                    if event_count <= 5:  # Log first 5 events
                                        self._logger.debug(f"Processing event {event_count}: type={event.type}, code={event.code}")
                                    if event_count % 100 == 0:  # Log every 100 events
                                        self._logger.debug(f"Processed {event_count} input events")
                                else:
                                    if event_count == 0:  # Log once if no callback
                                        self._logger.debug("Event found but no callback set!")
                                
                        except (OSError, IOError) as e:
                            # Device was disconnected
                            self._logger.debug(f"Device {device_path} disconnected during read: {e}")
                            if device_path in self._devices:
                                del self._devices[device_path]
                            continue
                    
                    time.sleep(0.001)  # Small delay to prevent excessive CPU usage
                    
                except Exception as e:
                    self._logger.error(f"Input event processing error: {e}")
                    import traceback
                    self._logger.error(f"Stack trace: {traceback.format_exc()}")
                    time.sleep(0.1)
                    
        except Exception as e:
            self._logger.error(f"Fatal error in event processing thread: {e}")
            import traceback
            self._logger.error(f"Fatal stack trace: {traceback.format_exc()}")
        
        self._logger.debug("Input event processing thread ended")
    
    def _handle_input_event(self, device: evdev.InputDevice, event: evdev.InputEvent) -> None:
        """Handle a single input event."""
        try:
            # Debug: Log first few events
            if not hasattr(self, '_event_debug_count'):
                self._event_debug_count = 0
            
            self._event_debug_count += 1
            if self._event_debug_count <= 5:
                self._logger.debug(f"Raw evdev event {self._event_debug_count}: type={event.type}, code={event.code}, value={event.value}")
            
            # Find device summary
            device_summary = None
            for summary in self._device_summaries:
                if self._device_paths.get(summary.device_guid) == device.path:
                    device_summary = summary
                    break
            
            if not device_summary:
                if self._event_debug_count <= 5:
                    self._logger.debug(f"No device summary found for {device.path}")
                return
            
            # Convert to our InputEvent format
            input_event = self._convert_evdev_event(device_summary, device, event)
            if input_event and self._input_event_callback:
                if self._event_debug_count <= 5:
                    self._logger.debug(f"Converted event: {input_event.input_type}, code={input_event.code}, value={input_event.value}")
                self._input_event_callback(input_event)
            elif self._event_debug_count <= 5:
                self._logger.debug(f"Event not converted or no callback: input_event={input_event}")
        
        except Exception as e:
            self._logger.error(f"Error handling input event: {e}")
    
    def _convert_evdev_event(self, device_summary: DeviceSummary, device: evdev.InputDevice, event: evdev.InputEvent) -> Optional[InputEvent]:
        """Convert evdev event to InputEvent."""
        
        if event.type == evdev.ecodes.EV_ABS:
            # Absolute axis event (analog sticks, triggers, etc.)
            axis_mapping = {
                evdev.ecodes.ABS_X: 1,
                evdev.ecodes.ABS_Y: 2,
                evdev.ecodes.ABS_Z: 3,
                evdev.ecodes.ABS_RX: 4,
                evdev.ecodes.ABS_RY: 5,
                evdev.ecodes.ABS_RZ: 6,
                evdev.ecodes.ABS_THROTTLE: 7,
                evdev.ecodes.ABS_RUDDER: 8,
                evdev.ecodes.ABS_WHEEL: 9,
                evdev.ecodes.ABS_GAS: 10,
                evdev.ecodes.ABS_BRAKE: 11,
            }
            
            if event.code in axis_mapping:
                # Regular axis - normalize to [-1.0, 1.0] using actual device capabilities
                caps = device.capabilities()
                abs_caps = caps.get(evdev.ecodes.EV_ABS, [])
                
                # Find the axis info - abs_caps is a list of (code, AbsInfo) tuples
                abs_info = None
                for axis_code, info in abs_caps:
                    if axis_code == event.code:
                        abs_info = info
                        break
                
                if abs_info:
                    # abs_info is a AbsInfo object with min, max, fuzz, flat attributes
                    min_val = abs_info.min
                    max_val = abs_info.max
                    center = (min_val + max_val) / 2.0
                    range_val = (max_val - min_val) / 2.0
                    
                    # Normalize: center becomes 0, min becomes -1, max becomes 1
                    normalized_value = (event.value - center) / range_val
                    normalized_value = max(-1.0, min(1.0, normalized_value))
                else:
                    # Fallback to old method if capabilities not available
                    normalized_value = (event.value - 32768) / 32768.0
                    normalized_value = max(-1.0, min(1.0, normalized_value))
                
                return InputEvent(
                    device_guid=device_summary.device_guid,
                    input_type=InputType.JoystickAxis,
                    code=axis_mapping[event.code],
                    value=normalized_value,
                    raw_value=event.value
                )
            
            elif event.code in {evdev.ecodes.ABS_HAT0X, evdev.ecodes.ABS_HAT0Y,
                               evdev.ecodes.ABS_HAT1X, evdev.ecodes.ABS_HAT1Y,
                               evdev.ecodes.ABS_HAT2X, evdev.ecodes.ABS_HAT2Y,
                               evdev.ecodes.ABS_HAT3X, evdev.ecodes.ABS_HAT3Y}:
                # Hat/D-pad event - combine X/Y into single direction
                hat_id = (event.code - evdev.ecodes.ABS_HAT0X) // 2 + 1
                
                # Initialize hat state for this device if needed
                if device_summary.device_guid not in self._hat_state:
                    self._hat_state[device_summary.device_guid] = {}
                if hat_id not in self._hat_state[device_summary.device_guid]:
                    self._hat_state[device_summary.device_guid][hat_id] = {'x': 0, 'y': 0}
                
                # Update the appropriate axis
                if event.code % 2 == 0:  # X axis
                    self._hat_state[device_summary.device_guid][hat_id]['x'] = event.value
                else:  # Y axis - invert for intuitive up/down direction
                    self._hat_state[device_summary.device_guid][hat_id]['y'] = -event.value
                
                # Get combined state
                hat_state = self._hat_state[device_summary.device_guid][hat_id]
                combined_value = (hat_state['x'], hat_state['y'])
                
                # Return combined hat event
                return InputEvent(
                    device_guid=device_summary.device_guid,
                    input_type=InputType.JoystickHat,
                    code=hat_id,
                    value=combined_value,
                    raw_value=event.value
                )
        
        elif event.type == evdev.ecodes.EV_KEY:
            # Button event - comprehensive mapping for all joystick manufacturers
            button_id = self._map_button_code_to_id(event.code)
            
            if button_id is not None:
                return InputEvent(
                    device_guid=device_summary.device_guid,
                    input_type=InputType.JoystickButton,
                    code=button_id,
                    value=bool(event.value),
                    is_pressed=bool(event.value),
                    raw_value=event.value
                )
        
        return None
    
    def _map_button_code_to_id(self, code: int) -> int | None:
        """Map evdev button code to sequential button ID.
        
        This method provides comprehensive mapping for all major joystick manufacturers
        by handling the various evdev button code ranges they use. The goal is to 
        present a consistent sequential button numbering (1, 2, 3...) regardless of
        the underlying hardware implementation, similar to how DirectInput works on Windows.
        
        Enhanced for comprehensive VKB support including extended button ranges.
        
        Manufacturer-specific mappings:
        - VKB: Heavy use of BTN_TRIGGER_HAPPY for base buttons, wheels, switches (codes 704-766+)
        - Virpil: Mix of standard and BTN_TRIGGER_HAPPY codes  
        - Thrustmaster: Mostly BTN_JOYSTICK range (codes 288-303)
        - CH Products: BTN_BASE range for base buttons (codes 304-309)
        - Generic controllers: BTN_GAMEPAD range (codes 304-318)
        
        Sequential Button ID Ranges:
        - 1-16: Standard joystick/gamepad buttons
        - 17-22: Base buttons (CH Products)
        - 23-86: Trigger Happy buttons (VKB, Virpil) - EXTENDED for full VKB support
        - 87-97: Additional gamepad codes
        - 98-107: D-Pad buttons 
        - 108-117: Miscellaneous buttons
        - 118-123: Gear/wheel buttons
        - 124-255: Fallback for unknown codes
        
        Args:
            code: evdev button code
            
        Returns:
            Sequential button ID (1-based) or None if not a button
        """
        
        # Range 1-16: Standard joystick buttons (BTN_TRIGGER, BTN_THUMB, etc.)
        # Used by: Thrustmaster, Logitech, most flight sticks
        # NOTE: BTN_BASE codes (294-299) overlap with this range but are handled separately below
        if evdev.ecodes.BTN_JOYSTICK <= code <= evdev.ecodes.BTN_JOYSTICK + 15:
            # Check if this is actually a BTN_BASE code that overlaps
            if evdev.ecodes.BTN_BASE <= code <= evdev.ecodes.BTN_BASE6:
                # Handle as base button instead
                return code - evdev.ecodes.BTN_BASE + 17
            else:
                return code - evdev.ecodes.BTN_JOYSTICK + 1
        
        # Range 1-16: Gamepad buttons (BTN_A, BTN_B, BTN_X, BTN_Y, etc.) 
        # Used by: Xbox controllers, generic gamepads
        # Starts at 304, no overlap with joystick range
        elif evdev.ecodes.BTN_GAMEPAD <= code <= evdev.ecodes.BTN_GAMEPAD + 15:
            return code - evdev.ecodes.BTN_GAMEPAD + 1
            
        # Range 17-22: Extended joystick base buttons (BTN_BASE through BTN_BASE6)
        # Used by: CH Products, some older joysticks
        # This range (294-299) overlaps with BTN_JOYSTICK but handled above
        elif evdev.ecodes.BTN_BASE <= code <= evdev.ecodes.BTN_BASE6:
            return code - evdev.ecodes.BTN_BASE + 17
            
        # Range 23-86: Extended Trigger Happy buttons (BTN_TRIGGER_HAPPY1-64+)
        # Used by: VKB, Virpil, high-end HOTAS with many buttons
        # VKB devices can use codes up to 766 (BTN_TRIGGER_HAPPY + 62)
        elif evdev.ecodes.BTN_TRIGGER_HAPPY <= code <= 766:
            return code - evdev.ecodes.BTN_TRIGGER_HAPPY + 23
            
        # Range 87-97: Additional gamepad codes
        # Some controllers use codes like BTN_C (306), BTN_Z (309), etc.
        elif code in {evdev.ecodes.BTN_C, evdev.ecodes.BTN_Z, evdev.ecodes.BTN_TL, 
                     evdev.ecodes.BTN_TR, evdev.ecodes.BTN_TL2, evdev.ecodes.BTN_TR2,
                     evdev.ecodes.BTN_SELECT, evdev.ecodes.BTN_START, evdev.ecodes.BTN_MODE,
                     evdev.ecodes.BTN_THUMBL, evdev.ecodes.BTN_THUMBR}:
            # Map these common gamepad codes to sequential range
            gamepad_codes = [evdev.ecodes.BTN_C, evdev.ecodes.BTN_Z, evdev.ecodes.BTN_TL,
                           evdev.ecodes.BTN_TR, evdev.ecodes.BTN_TL2, evdev.ecodes.BTN_TR2,
                           evdev.ecodes.BTN_SELECT, evdev.ecodes.BTN_START, evdev.ecodes.BTN_MODE,
                           evdev.ecodes.BTN_THUMBL, evdev.ecodes.BTN_THUMBR]
            try:
                return gamepad_codes.index(code) + 87
            except ValueError:
                pass
                
        # Range 98-107: D-Pad buttons (BTN_DPAD_UP, DOWN, LEFT, RIGHT)
        # Some controllers report D-pad as buttons instead of hat
        elif evdev.ecodes.BTN_DPAD_UP <= code <= evdev.ecodes.BTN_DPAD_RIGHT:
            return code - evdev.ecodes.BTN_DPAD_UP + 98
            
        # Range 108-117: Miscellaneous buttons (BTN_0-9)
        # Used by some specialized controllers
        elif evdev.ecodes.BTN_0 <= code <= evdev.ecodes.BTN_9:
            return code - evdev.ecodes.BTN_0 + 108
            
        # Range 118-123: Gear/wheel buttons (BTN_GEAR_DOWN, BTN_GEAR_UP, BTN_WHEEL)
        # Used by racing wheels and some flight sticks
        elif code in {evdev.ecodes.BTN_GEAR_DOWN, evdev.ecodes.BTN_GEAR_UP, evdev.ecodes.BTN_WHEEL}:
            gear_codes = [evdev.ecodes.BTN_GEAR_DOWN, evdev.ecodes.BTN_GEAR_UP, evdev.ecodes.BTN_WHEEL]
            try:
                return gear_codes.index(code) + 118
            except ValueError:
                pass
                
        # Range 124-255: Handle any other button codes we might encounter
        # This provides a fallback for unknown or manufacturer-specific codes
        elif 256 <= code <= 1000:  # Extended button code range for future devices
            # Map any remaining codes to sequential IDs starting at 124
            # This ensures we don't miss buttons from new or exotic controllers
            return min(code - 256 + 124, 255)  # Cap at 255 total buttons
            
        return None
    
    def _close_all_devices(self) -> None:
        """Close all open devices."""
        for device in self._devices.values():
            try:
                device.close()
            except Exception as e:
                self._logger.warning(f"Error closing device: {e}")
        
        self._devices.clear()
        self._device_summaries.clear()
        self._device_paths.clear()


# Global instance
_input_manager = None


def get_input_manager() -> EvdevInputManager:
    """Get the global input manager instance."""
    global _input_manager
    if _input_manager is None:
        _input_manager = EvdevInputManager()
    return _input_manager
