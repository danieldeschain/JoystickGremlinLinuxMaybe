# -*- coding: utf-8; -*-

"""
Linux-compatible keyboard module for Joystick Gremlin

This module provides a Linux-native replacement for the Windows-specific
keyboard handling, using evdev key codes and our linput backend.
"""

import logging
from typing import Dict, Optional

import evdev

# Import our Linux input backend
import linput


class Key:
    """Represents a keyboard key with Linux compatibility."""
    
    def __init__(self, name: str, linux_keycode: int, scan_code: int = 0, virtual_code: Optional[int] = None):
        """
        Create a Key instance.
        
        Args:
            name: Human-readable key name
            linux_keycode: Linux evdev keycode
            scan_code: Scan code (for compatibility)
            virtual_code: Virtual key code (for Windows compatibility)
        """
        self.name = name
        self.linux_keycode = linux_keycode
        self.scan_code = scan_code
        # For Windows compatibility, use linux_keycode as virtual_code if not specified
        self.virtual_code = virtual_code if virtual_code is not None else linux_keycode

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"Key('{self.name}', {self.linux_keycode})"
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Key):
            return self.linux_keycode == other.linux_keycode
        return False
    
    def __hash__(self) -> int:
        return hash(self.linux_keycode)


# Linux keycode to Key mapping (common keys)
_LINUX_KEY_MAP: Dict[int, Key] = {
    # Letters
    evdev.ecodes.KEY_A: Key("A", evdev.ecodes.KEY_A),
    evdev.ecodes.KEY_B: Key("B", evdev.ecodes.KEY_B),
    evdev.ecodes.KEY_C: Key("C", evdev.ecodes.KEY_C),
    evdev.ecodes.KEY_D: Key("D", evdev.ecodes.KEY_D),
    evdev.ecodes.KEY_E: Key("E", evdev.ecodes.KEY_E),
    evdev.ecodes.KEY_F: Key("F", evdev.ecodes.KEY_F),
    evdev.ecodes.KEY_G: Key("G", evdev.ecodes.KEY_G),
    evdev.ecodes.KEY_H: Key("H", evdev.ecodes.KEY_H),
    evdev.ecodes.KEY_I: Key("I", evdev.ecodes.KEY_I),
    evdev.ecodes.KEY_J: Key("J", evdev.ecodes.KEY_J),
    evdev.ecodes.KEY_K: Key("K", evdev.ecodes.KEY_K),
    evdev.ecodes.KEY_L: Key("L", evdev.ecodes.KEY_L),
    evdev.ecodes.KEY_M: Key("M", evdev.ecodes.KEY_M),
    evdev.ecodes.KEY_N: Key("N", evdev.ecodes.KEY_N),
    evdev.ecodes.KEY_O: Key("O", evdev.ecodes.KEY_O),
    evdev.ecodes.KEY_P: Key("P", evdev.ecodes.KEY_P),
    evdev.ecodes.KEY_Q: Key("Q", evdev.ecodes.KEY_Q),
    evdev.ecodes.KEY_R: Key("R", evdev.ecodes.KEY_R),
    evdev.ecodes.KEY_S: Key("S", evdev.ecodes.KEY_S),
    evdev.ecodes.KEY_T: Key("T", evdev.ecodes.KEY_T),
    evdev.ecodes.KEY_U: Key("U", evdev.ecodes.KEY_U),
    evdev.ecodes.KEY_V: Key("V", evdev.ecodes.KEY_V),
    evdev.ecodes.KEY_W: Key("W", evdev.ecodes.KEY_W),
    evdev.ecodes.KEY_X: Key("X", evdev.ecodes.KEY_X),
    evdev.ecodes.KEY_Y: Key("Y", evdev.ecodes.KEY_Y),
    evdev.ecodes.KEY_Z: Key("Z", evdev.ecodes.KEY_Z),
    
    # Numbers
    evdev.ecodes.KEY_0: Key("0", evdev.ecodes.KEY_0),
    evdev.ecodes.KEY_1: Key("1", evdev.ecodes.KEY_1),
    evdev.ecodes.KEY_2: Key("2", evdev.ecodes.KEY_2),
    evdev.ecodes.KEY_3: Key("3", evdev.ecodes.KEY_3),
    evdev.ecodes.KEY_4: Key("4", evdev.ecodes.KEY_4),
    evdev.ecodes.KEY_5: Key("5", evdev.ecodes.KEY_5),
    evdev.ecodes.KEY_6: Key("6", evdev.ecodes.KEY_6),
    evdev.ecodes.KEY_7: Key("7", evdev.ecodes.KEY_7),
    evdev.ecodes.KEY_8: Key("8", evdev.ecodes.KEY_8),
    evdev.ecodes.KEY_9: Key("9", evdev.ecodes.KEY_9),
    
    # Special keys
    evdev.ecodes.KEY_SPACE: Key("Space", evdev.ecodes.KEY_SPACE),
    evdev.ecodes.KEY_ENTER: Key("Return", evdev.ecodes.KEY_ENTER),
    evdev.ecodes.KEY_ESC: Key("Escape", evdev.ecodes.KEY_ESC),
    evdev.ecodes.KEY_TAB: Key("Tab", evdev.ecodes.KEY_TAB),
    evdev.ecodes.KEY_BACKSPACE: Key("BackSpace", evdev.ecodes.KEY_BACKSPACE),
    evdev.ecodes.KEY_DELETE: Key("Delete", evdev.ecodes.KEY_DELETE),
    
    # Modifier keys
    evdev.ecodes.KEY_LEFTSHIFT: Key("Shift_L", evdev.ecodes.KEY_LEFTSHIFT),
    evdev.ecodes.KEY_RIGHTSHIFT: Key("Shift_R", evdev.ecodes.KEY_RIGHTSHIFT),
    evdev.ecodes.KEY_LEFTCTRL: Key("Control_L", evdev.ecodes.KEY_LEFTCTRL),
    evdev.ecodes.KEY_RIGHTCTRL: Key("Control_R", evdev.ecodes.KEY_RIGHTCTRL),
    evdev.ecodes.KEY_LEFTALT: Key("Alt_L", evdev.ecodes.KEY_LEFTALT),
    evdev.ecodes.KEY_RIGHTALT: Key("Alt_R", evdev.ecodes.KEY_RIGHTALT),
    evdev.ecodes.KEY_LEFTMETA: Key("Super_L", evdev.ecodes.KEY_LEFTMETA),
    evdev.ecodes.KEY_RIGHTMETA: Key("Super_R", evdev.ecodes.KEY_RIGHTMETA),
    
    # Arrow keys
    evdev.ecodes.KEY_UP: Key("Up", evdev.ecodes.KEY_UP),
    evdev.ecodes.KEY_DOWN: Key("Down", evdev.ecodes.KEY_DOWN),
    evdev.ecodes.KEY_LEFT: Key("Left", evdev.ecodes.KEY_LEFT),
    evdev.ecodes.KEY_RIGHT: Key("Right", evdev.ecodes.KEY_RIGHT),
    
    # Function keys
    evdev.ecodes.KEY_F1: Key("F1", evdev.ecodes.KEY_F1),
    evdev.ecodes.KEY_F2: Key("F2", evdev.ecodes.KEY_F2),
    evdev.ecodes.KEY_F3: Key("F3", evdev.ecodes.KEY_F3),
    evdev.ecodes.KEY_F4: Key("F4", evdev.ecodes.KEY_F4),
    evdev.ecodes.KEY_F5: Key("F5", evdev.ecodes.KEY_F5),
    evdev.ecodes.KEY_F6: Key("F6", evdev.ecodes.KEY_F6),
    evdev.ecodes.KEY_F7: Key("F7", evdev.ecodes.KEY_F7),
    evdev.ecodes.KEY_F8: Key("F8", evdev.ecodes.KEY_F8),
    evdev.ecodes.KEY_F9: Key("F9", evdev.ecodes.KEY_F9),
    evdev.ecodes.KEY_F10: Key("F10", evdev.ecodes.KEY_F10),
    evdev.ecodes.KEY_F11: Key("F11", evdev.ecodes.KEY_F11),
    evdev.ecodes.KEY_F12: Key("F12", evdev.ecodes.KEY_F12),
}


def key_from_code(keycode: int) -> Key:
    """
    Get a Key object from a Linux keycode.
    
    Args:
        keycode: Linux evdev keycode
        
    Returns:
        Key object representing the key
    """
    if keycode in _LINUX_KEY_MAP:
        return _LINUX_KEY_MAP[keycode]
    else:
        # Create a generic key for unknown codes
        return Key(f"Key_{keycode}", keycode)


def key_from_name(name: str) -> Optional[Key]:
    """
    Get a Key object from a key name.
    
    Args:
        name: Key name (e.g., "A", "Return", "F1")
        
    Returns:
        Key object if found, None otherwise
    """
    # Search for key by name
    for key in _LINUX_KEY_MAP.values():
        if key.name.lower() == name.lower():
            return key
    
    # Try common name variations
    name_variations = {
        "enter": "Return",
        "ctrl": "Control_L",
        "alt": "Alt_L", 
        "shift": "Shift_L",
        "win": "Super_L",
        "windows": "Super_L",
        "cmd": "Super_L",
        "command": "Super_L",
        "esc": "Escape",
        "del": "Delete",
        "bs": "BackSpace",
        "backspace": "BackSpace",
    }
    
    if name.lower() in name_variations:
        return key_from_name(name_variations[name.lower()])
    
    return None


def send_key_down(key: Key) -> None:
    """
    Send a key press event.
    
    Args:
        key: Key to press
    """
    try:
        keyboard_manager = linput.get_keyboard_mouse_manager()
        keyboard_manager.send_key_press(key.linux_keycode)
    except Exception as e:
        logging.getLogger(__name__).warning(f"Failed to send key down {key.name}: {e}")


def send_key_up(key: Key) -> None:
    """
    Send a key release event.
    
    Args:
        key: Key to release  
    """
    try:
        keyboard_manager = linput.get_keyboard_mouse_manager()
        keyboard_manager.send_key_release(key.linux_keycode)
    except Exception as e:
        logging.getLogger(__name__).warning(f"Failed to send key up {key.name}: {e}")


def send_key_press(key: Key, duration: float = 0.05) -> None:
    """
    Send a complete key press (down + up).
    
    Args:
        key: Key to press
        duration: Duration to hold key in seconds
    """
    send_key_down(key)
    import time
    time.sleep(duration)
    send_key_up(key)


# Common key constants for compatibility
class KeyCode:
    """Common key code constants."""
    
    # Letters
    A = _LINUX_KEY_MAP[evdev.ecodes.KEY_A]
    B = _LINUX_KEY_MAP[evdev.ecodes.KEY_B]
    C = _LINUX_KEY_MAP[evdev.ecodes.KEY_C]
    D = _LINUX_KEY_MAP[evdev.ecodes.KEY_D]
    E = _LINUX_KEY_MAP[evdev.ecodes.KEY_E]
    F = _LINUX_KEY_MAP[evdev.ecodes.KEY_F]
    G = _LINUX_KEY_MAP[evdev.ecodes.KEY_G]
    H = _LINUX_KEY_MAP[evdev.ecodes.KEY_H]
    I = _LINUX_KEY_MAP[evdev.ecodes.KEY_I]
    J = _LINUX_KEY_MAP[evdev.ecodes.KEY_J]
    K = _LINUX_KEY_MAP[evdev.ecodes.KEY_K]
    L = _LINUX_KEY_MAP[evdev.ecodes.KEY_L]
    M = _LINUX_KEY_MAP[evdev.ecodes.KEY_M]
    N = _LINUX_KEY_MAP[evdev.ecodes.KEY_N]
    O = _LINUX_KEY_MAP[evdev.ecodes.KEY_O]
    P = _LINUX_KEY_MAP[evdev.ecodes.KEY_P]
    Q = _LINUX_KEY_MAP[evdev.ecodes.KEY_Q]
    R = _LINUX_KEY_MAP[evdev.ecodes.KEY_R]
    S = _LINUX_KEY_MAP[evdev.ecodes.KEY_S]
    T = _LINUX_KEY_MAP[evdev.ecodes.KEY_T]
    U = _LINUX_KEY_MAP[evdev.ecodes.KEY_U]
    V = _LINUX_KEY_MAP[evdev.ecodes.KEY_V]
    W = _LINUX_KEY_MAP[evdev.ecodes.KEY_W]
    X = _LINUX_KEY_MAP[evdev.ecodes.KEY_X]
    Y = _LINUX_KEY_MAP[evdev.ecodes.KEY_Y]
    Z = _LINUX_KEY_MAP[evdev.ecodes.KEY_Z]
    
    # Numbers
    N0 = _LINUX_KEY_MAP[evdev.ecodes.KEY_0]
    N1 = _LINUX_KEY_MAP[evdev.ecodes.KEY_1]
    N2 = _LINUX_KEY_MAP[evdev.ecodes.KEY_2]
    N3 = _LINUX_KEY_MAP[evdev.ecodes.KEY_3]
    N4 = _LINUX_KEY_MAP[evdev.ecodes.KEY_4]
    N5 = _LINUX_KEY_MAP[evdev.ecodes.KEY_5]
    N6 = _LINUX_KEY_MAP[evdev.ecodes.KEY_6]
    N7 = _LINUX_KEY_MAP[evdev.ecodes.KEY_7]
    N8 = _LINUX_KEY_MAP[evdev.ecodes.KEY_8]
    N9 = _LINUX_KEY_MAP[evdev.ecodes.KEY_9]
    
    # Special keys
    SPACE = _LINUX_KEY_MAP[evdev.ecodes.KEY_SPACE]
    ENTER = _LINUX_KEY_MAP[evdev.ecodes.KEY_ENTER]
    ESCAPE = _LINUX_KEY_MAP[evdev.ecodes.KEY_ESC]
    TAB = _LINUX_KEY_MAP[evdev.ecodes.KEY_TAB]
    BACKSPACE = _LINUX_KEY_MAP[evdev.ecodes.KEY_BACKSPACE]
    DELETE = _LINUX_KEY_MAP[evdev.ecodes.KEY_DELETE]
    
    # Modifiers
    SHIFT_L = _LINUX_KEY_MAP[evdev.ecodes.KEY_LEFTSHIFT]
    SHIFT_R = _LINUX_KEY_MAP[evdev.ecodes.KEY_RIGHTSHIFT]
    CTRL_L = _LINUX_KEY_MAP[evdev.ecodes.KEY_LEFTCTRL]
    CTRL_R = _LINUX_KEY_MAP[evdev.ecodes.KEY_RIGHTCTRL]
    ALT_L = _LINUX_KEY_MAP[evdev.ecodes.KEY_LEFTALT]
    ALT_R = _LINUX_KEY_MAP[evdev.ecodes.KEY_RIGHTALT]
    
    # Arrow keys
    UP = _LINUX_KEY_MAP[evdev.ecodes.KEY_UP]
    DOWN = _LINUX_KEY_MAP[evdev.ecodes.KEY_DOWN]
    LEFT = _LINUX_KEY_MAP[evdev.ecodes.KEY_LEFT]
    RIGHT = _LINUX_KEY_MAP[evdev.ecodes.KEY_RIGHT]
    
    # Function keys
    F1 = _LINUX_KEY_MAP[evdev.ecodes.KEY_F1]
    F2 = _LINUX_KEY_MAP[evdev.ecodes.KEY_F2]
    F3 = _LINUX_KEY_MAP[evdev.ecodes.KEY_F3]
    F4 = _LINUX_KEY_MAP[evdev.ecodes.KEY_F4]
    F5 = _LINUX_KEY_MAP[evdev.ecodes.KEY_F5]
    F6 = _LINUX_KEY_MAP[evdev.ecodes.KEY_F6]
    F7 = _LINUX_KEY_MAP[evdev.ecodes.KEY_F7]
    F8 = _LINUX_KEY_MAP[evdev.ecodes.KEY_F8]
    F9 = _LINUX_KEY_MAP[evdev.ecodes.KEY_F9]
    F10 = _LINUX_KEY_MAP[evdev.ecodes.KEY_F10]
    F11 = _LINUX_KEY_MAP[evdev.ecodes.KEY_F11]
    F12 = _LINUX_KEY_MAP[evdev.ecodes.KEY_F12]


# Export main interface
__all__ = [
    "Key",
    "KeyCode", 
    "key_from_code",
    "send_key_down",
    "send_key_up", 
    "send_key_press"
]
