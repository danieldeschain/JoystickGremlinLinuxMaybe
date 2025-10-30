# -*- coding: utf-8; -*-

# Copyright (C) 2015 Lionel Ott
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
Macro system for Joystick Gremlin.

This module provides backward compatibility by re-exporting all classes
from the macro_modules package. All implementation has been moved to
focused submodules for better maintainability.

Module Structure:
- macro_modules.manager: MacroManager singleton for scheduling and execution
- macro_modules.macro: Macro container class for action sequences
- macro_modules.actions: All action classes (keyboard, mouse, joystick, VJoy)
- macro_modules.repeat: Repeat mode classes (count, toggle, hold)
"""

from __future__ import annotations

# Re-export MacroManager and MacroEntry
from gremlin.macro_modules.manager import MacroManager, MacroEntry

# Re-export Macro container
from gremlin.macro_modules.macro import Macro

# Re-export all action classes
from gremlin.macro_modules.actions import (
    AbstractAction,
    JoystickAction,
    KeyAction,
    MouseButtonAction,
    MouseMotionAction,
    PauseAction,
    VJoyAction,
)

# Re-export all repeat mode classes
from gremlin.macro_modules.repeat import (
    AbstractRepeat,
    CountRepeat,
    HoldRepeat,
    ToggleRepeat,
)

# Configuration registration (must stay in this file to ensure it runs on import)
from gremlin.config import Configuration
from gremlin.types import PropertyType

Configuration().register(
    "action",
    "macro",
    "default-delay",
    PropertyType.Float,
    0.05,
    "The default time (in seconds) the macro system waits between emitting " +
    "subsequent actions when no pauses are present.",
    {
        "min": 0.0,
        "max": 10.0
    },
    True
)

# Define __all__ for clean imports
__all__ = [
    # Manager
    "MacroManager",
    "MacroEntry",
    # Container
    "Macro",
    # Actions
    "AbstractAction",
    "JoystickAction",
    "KeyAction",
    "MouseButtonAction",
    "MouseMotionAction",
    "PauseAction",
    "VJoyAction",
    # Repeat modes
    "AbstractRepeat",
    "CountRepeat",
    "HoldRepeat",
    "ToggleRepeat",
]
