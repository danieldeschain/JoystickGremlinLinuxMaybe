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
Linux-native event hook for mouse and keyboard events.

This module provides a Linux replacement for the Windows-specific
low-level event hooks using linput.
"""

import logging
from typing import Callable, List

from gremlin.common import SingletonDecorator
from gremlin.types import MouseButton
import linput


g_keyboard_callbacks = []
g_mouse_callbacks = []


@SingletonDecorator
class MouseHook:
    """Linux-native mouse hook using linput."""
    
    def __init__(self):
        self._logger = logging.getLogger("system")
        self._callbacks: List[Callable] = []
        self._is_running = False
        self._keyboard_mouse_manager = None
    
    def start(self):
        """Start capturing mouse events."""
        if self._is_running:
            return
            
        try:
            self._keyboard_mouse_manager = linput.get_keyboard_mouse_manager()
            self._keyboard_mouse_manager.register_input_callback(self._mouse_event_handler)
            self._is_running = True
            self._logger.info("Linux mouse hook started")
        except Exception as e:
            self._logger.error(f"Failed to start mouse hook: {e}")
    
    def stop(self):
        """Stop capturing mouse events."""
        if not self._is_running:
            return
            
        try:
            if self._keyboard_mouse_manager:
                self._keyboard_mouse_manager.unregister_input_callback(self._mouse_event_handler)
            self._is_running = False
            self._keyboard_mouse_manager = None
            self._logger.info("Linux mouse hook stopped")
        except Exception as e:
            self._logger.error(f"Failed to stop mouse hook: {e}")
    
    def _mouse_event_handler(self, event: linput.InputEvent) -> None:
        """Handle mouse events from linput."""
        try:
            # Only process mouse events
            if event.input_type == linput.InputType.Mouse:
                # Convert to format expected by callbacks
                for callback in g_mouse_callbacks:
                    try:
                        callback(event)
                    except Exception as e:
                        self._logger.error(f"Error in mouse callback: {e}")
        except Exception as e:
            self._logger.error(f"Error processing mouse event: {e}")
    
    def install_mouse_hook(self, callback: Callable):
        """Install a mouse event callback."""
        if callback not in g_mouse_callbacks:
            g_mouse_callbacks.append(callback)
    
    def remove_mouse_hook(self, callback: Callable):
        """Remove a mouse event callback."""
        if callback in g_mouse_callbacks:
            g_mouse_callbacks.remove(callback)


@SingletonDecorator 
class KeyboardHook:
    """Linux-native keyboard hook using linput."""
    
    def __init__(self):
        self._logger = logging.getLogger("system")
        self._callbacks: List[Callable] = []
        self._is_running = False
        self._keyboard_mouse_manager = None
    
    def start(self):
        """Start capturing keyboard events."""
        if self._is_running:
            return
            
        try:
            self._keyboard_mouse_manager = linput.get_keyboard_mouse_manager()
            self._keyboard_mouse_manager.register_input_callback(self._keyboard_event_handler)
            self._is_running = True
            self._logger.info("Linux keyboard hook started")
        except Exception as e:
            self._logger.error(f"Failed to start keyboard hook: {e}")
    
    def stop(self):
        """Stop capturing keyboard events."""
        if not self._is_running:
            return
            
        try:
            if self._keyboard_mouse_manager:
                self._keyboard_mouse_manager.unregister_input_callback(self._keyboard_event_handler)
            self._is_running = False
            self._keyboard_mouse_manager = None
            self._logger.info("Linux keyboard hook stopped")
        except Exception as e:
            self._logger.error(f"Failed to stop keyboard hook: {e}")
    
    def _keyboard_event_handler(self, event: linput.InputEvent) -> None:
        """Handle keyboard events from linput."""
        try:
            # Only process keyboard events
            if event.input_type == linput.InputType.Key:
                # Convert to format expected by callbacks
                for callback in g_keyboard_callbacks:
                    try:
                        callback(event)
                    except Exception as e:
                        self._logger.error(f"Error in keyboard callback: {e}")
        except Exception as e:
            self._logger.error(f"Error processing keyboard event: {e}")
    
    def install_keyboard_hook(self, callback: Callable):
        """Install a keyboard event callback."""
        if callback not in g_keyboard_callbacks:
            g_keyboard_callbacks.append(callback)
    
    def remove_keyboard_hook(self, callback: Callable):
        """Remove a keyboard event callback."""
        if callback in g_keyboard_callbacks:
            g_keyboard_callbacks.remove(callback)


# Compatibility functions for global hook management
def install_mouse_hook(callback: Callable):
    """Install a global mouse hook callback."""
    MouseHook().install_mouse_hook(callback)


def remove_mouse_hook(callback: Callable):
    """Remove a global mouse hook callback."""
    MouseHook().remove_mouse_hook(callback)


def install_keyboard_hook(callback: Callable):
    """Install a global keyboard hook callback."""
    KeyboardHook().install_keyboard_hook(callback)


def remove_keyboard_hook(callback: Callable):
    """Remove a global keyboard hook callback."""
    KeyboardHook().remove_keyboard_hook(callback)
