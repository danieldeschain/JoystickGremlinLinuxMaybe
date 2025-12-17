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

import linput
from gremlin.input_cache import Joystick, Keyboard
from gremlin.types import InputType


class JoystickDecorator:

    """Creates customized decorators for physical joystick devices."""

    def __init__(self, name: str, device_guid: str, mode: str):
        """Creates a new instance with customized decorators.

        Args:
            name: name of the device
            device_guid: the device's guid in the system
            mode: the mode in which the decorated functions should be active
        """
        self.name = name
        self.mode = mode

        # Convert string-based GUID to the actual GUID object
        try:
            self.device_guid = uuid.UUID(device_guid)
        except ValueError:
            logging.getLogger("system").error(
                f"Invalid guid value '{device_guid}' received."
            )
            self.device_guid = diill.UUID_Invalid

        # Create decorators for the different input types
        self.axis = functools.partial(
            _input_callback,
            device_guid=self.device_guid,
            input_type=InputType.JoystickAxis,
            mode=self.mode
        )
        self.button = functools.partial(
            _input_callback,
            device_guid=self.device_guid,
            input_type=InputType.JoystickButton,
            mode=self.mode
        )
        self.hat = functools.partial(
            _input_callback,
            device_guid=self.device_guid,
            input_type=InputType.JoystickHat,
            mode=self.mode
        )


class VJoyPlugin:

    """Plugin providing automatic access to virtual joystick devices.

    REFACTORED: Now uses linput.VirtualJoystick instead of Windows VJoyProxy.
    
    For a function to use this plugin it requires one of its parameters
    to be named "vjoy".
    """

    # Use linput VirtualJoystick manager instead of VJoyProxy
    vjoy = linput.VirtualJoystick

    def __init__(self):
        self.keyword = "vjoy"

    def install(self, callback: Callable, partial_fn: Callable) -> Callable:
        """Decorates the given callback function to provide access to
        virtual joystick devices.

        Only if the signature contains the plugin's keyword is the
        decorator applied.

        Args:
            callback: the callback to decorate
            partial_fn: function to create the partial function / method

        Returns:
            callback with the plugin parameter bound
        """
        return partial_fn(callback, vjoy=VJoyPlugin.vjoy)


class JoystickPlugin:

    """Plugin providing automatic access to the Joystick object.

    For a function to use this plugin it requires one of its parameters
    to be named "joy".
    """

    joystick = Joystick()

    def __init__(self):
        self.keyword = "joy"

    def install(self, callback: Callable, partial_fn: Callable) -> Callable:
        """Decorates the given callback function to provide access
        to the Joystick object.

        Only if the signature contains the plugin's keyword is the
        decorator applied.

        Args:
            callback: the callback to decorate
            partial_fn: function to create the partial function / method

        Returns:
            callback with the plugin parameter bound
        """
        return partial_fn(callback, joy=JoystickPlugin.joystick)


class KeyboardPlugin:

    """Plugin providing automatic access to the Keyboard object.

    For a function to use this plugin it requires one of its parameters
    to be named "keyboard".
    """

    keyboard = Keyboard()

    def __init__(self):
        self.keyword = "keyboard"

    def install(self, callback, partial_fn):
        """Decorates the given callback function to provide access to
        the Keyboard object.

        Args:
            callback: the callback to decorate
            partial_fn: function to create the partial function / method

        Returns:
            callback with the plugin parameter bound
        """
        return partial_fn(callback, keyboard=KeyboardPlugin.keyboard)
