# -*- coding: utf-8; -*-

# Copyright (C) 2019 Lionel Ott
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



from __future__ import annotations

from typing import Callable

# Re-export all classes from modules
from gremlin.user_script_modules.registries import CallbackRegistry, PeriodicRegistry, ScriptVariableRegistry
from gremlin.user_script_modules.plugins import JoystickDecorator, VJoyPlugin, JoystickPlugin, KeyboardPlugin
from gremlin.user_script_modules.script import Script
from gremlin.user_script_modules.variables import (
    AbstractVariable, BoolVariable, FloatVariable, IntegerVariable,
    ModeVariable, SelectionVariable, StringVariable,
    PhysicalInputVariable, VirtualInputVariable
)


def clamp_value(value: float, min_val: float, max_val: float) -> float:
    """Returns the value clamped to the provided range.

    Args:
        value: numerical value to clamp
        min_val: lower bound of the range
        max_val: upper bound of the range

    Returns:
        The input value clamped to the provided range
    """
    if min_val > max_val:
        min_val, max_val = max_val, min_val
    return min(max_val, max(min_val, value))


def keyboard(key_name: str, mode: str) -> Callable:
    """Decorator for keyboard key callbacks.

    Args:
        key_name: name of key triggering the callback
        mode: mode in which this callback is active
    """

    def wrap(callback):

        @functools.wraps(callback)
        def wrapper_fn(*args, **kwargs):
            callback(*args, **kwargs)

        key = gremlin.keyboard.key_from_name(key_name)
        event = event_handler.Event.from_key(key)
        callback_registry.add(wrapper_fn, event, mode)

        return wrapper_fn

    return wrap


def periodic(interval: float) -> Callable:
    """Decorator for periodic function callbacks.

    Args:
        interval: the duration between executions of the function
    """

    def wrap(callback):

        @functools.wraps(callback)
        def wrapper_fn(*args, **kwargs):
            callback(*args, **kwargs)

        periodic_registry.add(wrapper_fn, interval)

        return wrapper_fn

    return wrap


def _input_callback(
        input_id: int,
        device_guid: uuid.UUID,
        input_type: InputType,
        mode: str
):
    """Decorator for a specific input on a physical device.

    Args:
        device_guid: GUID of the physical device
        input_type: type of the input being wrapped in the decorator
        input_id: identifier of the axis, button, or hat being decorated
        mode: name of the mode the callback is active in
    """

    # The order of the input arguments has to be this specific one as otherwise
    # the positional argument part of the decorator breaks.

    def wrap(callback):

        @functools.wraps(callback)
        def wrapper_fn(*args, **kwargs):
            callback(*args, **kwargs)

        event = event_handler.Event(
            event_type=input_type,
            identifier=input_id,
            device_guid=device_guid,
            mode=mode
        )
        callback_registry.add(wrapper_fn, event, mode)

        return wrapper_fn

    return wrap
