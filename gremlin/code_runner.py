# -*- coding: utf-8; -*-

# Copyright (C) 2016 Lionel Ott
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
Code runner system for Joystick Gremlin.

This module provides backward compatibility by re-exporting all classes
from the code_runner_modules package.

Module Structure:
- code_runner_modules.virtual_buttons: Virtual button implementations
- code_runner_modules.callbacks: Callback object for action execution
- code_runner_modules.runner: Main CodeRunner class
"""

from __future__ import annotations

from gremlin.code_runner_modules.virtual_buttons import (
    VirtualButton,
    VirtualAxisButton,
    VirtualHatButton,
    VirtualButtonFunctor,
)
from gremlin.code_runner_modules.callbacks import CallbackObject
from gremlin.code_runner_modules.runner import CodeRunner

__all__ = [
    "VirtualButton",
    "VirtualAxisButton",
    "VirtualHatButton",
    "VirtualButtonFunctor",
    "CallbackObject",
    "CodeRunner",
]
