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
Linux SendInput Replacement

Provides Linux-native input sending functionality using the linput backend,
completely replacing the Windows SendInput API.
"""

import enum
import logging
import math
import threading
import time
from typing import Optional

import linput
from gremlin.common import SingletonDecorator
from gremlin.event_handler import Event
from gremlin.types import MouseButton


@SingletonDecorator
class LinuxInputSender:
    """Linux-native input sender using linput backend."""

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._keyboard_mouse_manager = None
        self._send_lock = threading.Lock()

    def _get_manager(self):
        """Get the keyboard/mouse manager, initializing if needed."""
        if self._keyboard_mouse_manager is None:
            try:
                self._keyboard_mouse_manager = linput.get_keyboard_mouse_manager()
            except Exception as e:
                self._logger.error(f"Failed to get keyboard/mouse manager: {e}")
                raise
        return self._keyboard_mouse_manager

    def send_keyboard_event(self, key_code: int, is_pressed: bool, extended: bool = False):
        """Send a keyboard event.
        
        Args:
            key_code: The key code to send
            is_pressed: True for key press, False for key release
            extended: Extended key flag (ignored on Linux)
        """
        with self._send_lock:
            try:
                manager = self._get_manager()
                if is_pressed:
                    manager.send_key_press(key_code)
                else:
                    manager.send_key_release(key_code)
            except Exception as e:
                self._logger.error(f"Failed to send keyboard event: {e}")

    def send_mouse_event(self, button: MouseButton, is_pressed: bool, x: Optional[int] = None, y: Optional[int] = None):
        """Send a mouse event.
        
        Args:
            button: Mouse button to send
            is_pressed: True for button press, False for button release
            x: Optional X coordinate
            y: Optional Y coordinate
        """
        with self._send_lock:
            try:
                manager = self._get_manager()
                
                # Convert MouseButton enum to internal button ID
                button_map = {
                    MouseButton.Left: 1,
                    MouseButton.Right: 2,
                    MouseButton.Middle: 3,
                }
                button_id = button_map.get(button)
                
                if button_id and is_pressed:  # Only handle press events for clicks
                    manager.send_mouse_click(button_id, x, y)
                    
            except Exception as e:
                self._logger.error(f"Failed to send mouse event: {e}")

    def send_mouse_motion(self, x: int, y: int, relative: bool = False):
        """Send mouse motion.
        
        Args:
            x: X coordinate or relative movement
            y: Y coordinate or relative movement
            relative: Whether coordinates are relative (not supported on Linux with pynput)
        """
        with self._send_lock:
            try:
                manager = self._get_manager()
                if not relative:
                    manager.send_mouse_move(x, y)
                else:
                    # For relative movement, we'd need to get current position and add
                    self._logger.warning("Relative mouse movement not fully supported")
                    
            except Exception as e:
                self._logger.error(f"Failed to send mouse motion: {e}")

    def send_mouse_scroll(self, direction: int, clicks: int = 1):
        """Send mouse scroll.
        
        Args:
            direction: Scroll direction (positive = up, negative = down)
            clicks: Number of scroll clicks
        """
        with self._send_lock:
            try:
                manager = self._get_manager()
                # Convert direction to dx, dy for pynput
                dx = 0
                dy = clicks if direction > 0 else -clicks
                manager.send_mouse_scroll(dx, dy)
                
            except Exception as e:
                self._logger.error(f"Failed to send mouse scroll: {e}")

    def send_text(self, text: str):
        """Send text string.
        
        Args:
            text: Text to send
        """
        with self._send_lock:
            try:
                manager = self._get_manager()
                manager.send_text(text)
                
            except Exception as e:
                self._logger.error(f"Failed to send text: {e}")


# Legacy compatibility functions
def send_keyboard_event(key_code: int, is_pressed: bool, extended: bool = False):
    """Legacy function for sending keyboard events."""
    sender = LinuxInputSender()
    sender.send_keyboard_event(key_code, is_pressed, extended)

def send_mouse_event(button: MouseButton, is_pressed: bool, x: Optional[int] = None, y: Optional[int] = None):
    """Legacy function for sending mouse events."""
    sender = LinuxInputSender()
    sender.send_mouse_event(button, is_pressed, x, y)

def send_mouse_motion(x: int, y: int, relative: bool = False):
    """Legacy function for sending mouse motion."""
    sender = LinuxInputSender()
    sender.send_mouse_motion(x, y, relative)

def send_mouse_scroll(direction: int, clicks: int = 1):
    """Legacy function for sending mouse scroll."""
    sender = LinuxInputSender()
    sender.send_mouse_scroll(direction, clicks)

def send_text(text: str):
    """Legacy function for sending text."""
    sender = LinuxInputSender()
    sender.send_text(text)

class MouseMotion:
    """Base class of all mouse motion behaviors."""

    # Time step between calls
    delta_t = 0.01

    def __init__(self, dx: float=0, dy: float=0):
        """Creates a new instance.

        Args:
            dx: motion along the x-axis in pixels per second
            dy: motion along the y-axis in pixels per second
        """
        self.dx = dx
        self.dy = dy

        self._tick_dx_value, self._tick_dx_time = self._compute_values(self.dx)
        self._tick_dy_value, self._tick_dy_time = self._compute_values(self.dy)

        self._dx_timestamp = 0
        self._dy_timestamp = 0

    def __call__(self) -> tuple[int, int]:
        """Returns the change in x and y for this point in time.

        Returns:
            The change in (dx, dy) for this time point
        """
        if self._tick_dx_value == 0 and self._tick_dy_value == 0:
            return 0, 0

        delta_x = 0
        delta_y = 0

        cur_time = time.time()
        if self._dx_timestamp < cur_time:
            delta_x = self._tick_dx_value
            self._dx_timestamp = cur_time + self._tick_dx_time
        if self._dy_timestamp < cur_time:
            delta_y = self._tick_dy_value
            self._dy_timestamp = cur_time + self._tick_dy_time

        return delta_x, delta_y

    def _compute_values(self, delta: float) -> tuple[int, float]:
        """Computes discretization values to send integer motions.

        Args:
            delta: the amount of change in pixels per second to discretize for

        Returns:
            Discretization information in terms of cursor movement amount
            and movement interval
        """
        delta = 0.0 if abs(delta) < 1e-6 else delta
        tick_value = math.ceil(abs(delta) / 100.0)
        if tick_value == 0:
            tick_time = MouseMotion.delta_t
        else:
            tick_time = 1.0 / (abs(delta) / tick_value)
            tick_value = int(math.copysign(tick_value, delta))

        return tick_value, tick_time


class FixedMouseMotion(MouseMotion):
    """Motion generation with fixed speed."""

    def __init__(self, dx: float=0, dy: float=0):
        """Creates a new instance.

        Args:
            dx: motion along the x-axis in pixels per second
            dy: motion along the y-axis in pixels per second
        """
        super().__init__(dx, dy)


class AcceleratedMouseMotion(MouseMotion):
    """Motion generation with acceleration and deceleration."""

    def __init__(self, dx: float=0, dy: float=0, acceleration: float=100.0,
                 max_velocity: float=1000.0):
        """Creates a new instance.

        Args:
            dx: motion along the x-axis in pixels per second
            dy: motion along the y-axis in pixels per second
            acceleration: acceleration in pixels per second squared
            max_velocity: maximum velocity in pixels per second
        """
        super().__init__(dx, dy)
        self.acceleration = acceleration
        self.max_velocity = max_velocity
        self.current_velocity = 0.0


class MouseControllerImpl:
    """Centralizes sending mouse events in an organized manner."""

    def __init__(self):
        """Creates a new instance."""
        self._motion_type = None  # "Fixed" or "Accelerated"
        self._delta_generator = FixedMouseMotion(0, 0)
        self._motion_commands = {}
        self._is_running = False
        self._thread = None
        self._sender = LinuxInputSender()

    def set_absolute_motion(
            self,
            dx: Optional[float] = None,
            dy: Optional[float] = None
    ) -> None:
        """Configures a motion using absolute velocities.

        Args:
            dx: velocity along the x-axis in pixels per second
            dy: velocity along the y-axis in pixels per second
        """
        if self._motion_type == "Fixed":
            if dx is not None:
                self._delta_generator.dx = dx
            if dy is not None:
                self._delta_generator.dy = dy
        else:
            self._motion_type = "Fixed"
            self._delta_generator = FixedMouseMotion(
                dx if dx is not None else 0,
                dy if dy is not None else 0
            )

    def set_accelerated_motion(
            self,
            dx: Optional[float] = None,
            dy: Optional[float] = None,
            acceleration: float = 100.0,
            max_velocity: float = 1000.0
    ) -> None:
        """Configures motion using accelerated velocities.

        Args:
            dx: target velocity along the x-axis in pixels per second
            dy: target velocity along the y-axis in pixels per second
            acceleration: acceleration in pixels per second squared
            max_velocity: maximum velocity in pixels per second
        """
        self._motion_type = "Accelerated"
        self._delta_generator = AcceleratedMouseMotion(
            dx if dx is not None else 0,
            dy if dy is not None else 0,
            acceleration,
            max_velocity
        )

    def start(self) -> None:
        """Start the mouse controller."""
        if not self._is_running:
            self._is_running = True
            self._thread = threading.Thread(target=self._control_loop)
            self._thread.start()

    def stop(self) -> None:
        """Stop the mouse controller."""
        self._is_running = False
        if self._thread and self._thread.is_alive():
            self._thread.join()

    def _control_loop(self) -> None:
        """Main control loop for mouse motion."""
        while self._is_running:
            try:
                dx, dy = self._delta_generator()
                if dx != 0 or dy != 0:
                    self._sender.send_mouse_motion(dx, dy)
                time.sleep(MouseMotion.delta_t)
            except Exception as e:
                logging.getLogger("system").error(f"Mouse controller error: {e}")


# Singleton instances for compatibility
_mouse_controller = None

def mouse_controller() -> MouseControllerImpl:
    """Get the singleton MouseController instance."""
    global _mouse_controller
    if _mouse_controller is None:
        _mouse_controller = MouseControllerImpl()
    return _mouse_controller

# Make MouseController directly accessible at module level
def MouseController() -> MouseControllerImpl:
    """Factory function for MouseController (for compatibility with existing code)."""
    return mouse_controller()

# Additional utility functions for compatibility
def mouse_relative_motion(dx: int, dy: int):
    """Send relative mouse motion."""
    sender = LinuxInputSender()
    sender.send_mouse_motion(dx, dy, relative=True)

def mouse_press(button: MouseButton):
    """Press a mouse button."""
    sender = LinuxInputSender()
    sender.send_mouse_event(button, True)

def mouse_release(button: MouseButton):  
    """Release a mouse button."""
    sender = LinuxInputSender()
    sender.send_mouse_event(button, False)

def mouse_wheel(motion: int):
    """Send mouse wheel motion."""
    sender = LinuxInputSender()
    sender.send_mouse_scroll(1 if motion > 0 else -1, abs(motion))

# Vector2 class for compatibility
class Vector2:
    """2D vector class for compatibility."""
    
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __mul__(self, scalar: float):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __str__(self):
        return f"Vector2({self.x}, {self.y})"

# MotionType enum for compatibility
class MotionType(enum.Enum):
    Absolute = 1
    Relative = 2
