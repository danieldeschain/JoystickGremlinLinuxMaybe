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

"""Macro action classes for keyboard, mouse, joystick, and VJoy inputs."""

from __future__ import annotations

from abc import ABC, abstractmethod
import time
from typing import Tuple
import uuid
from xml.etree import ElementTree

import dill
from vjoy.vjoy import VJoyProxy

import gremlin.error
import gremlin.event_handler
import gremlin.sendinput
from gremlin import mode_manager, util
from gremlin.keyboard import send_key_down, send_key_up, key_from_code, key_from_name, Key
from gremlin.types import AxisMode, InputType, MouseButton, PropertyType


class AbstractAction(ABC):
    """Base class for all macro action."""

    @abstractmethod
    def __call__(self) -> None:
        pass

    @classmethod
    @abstractmethod
    def create(cls) -> AbstractAction:
        """Creates an empty, likely invalid instance, of the action."""
        pass

    @abstractmethod
    def to_xml(self) -> ElementTree.Element:
        pass

    @abstractmethod
    def from_xml(self, node: ElementTree.Element) -> None:
        pass

    def _create_node(self, type_name: str) -> ElementTree.Element:
        """Creates an action node of the given type.

        Args:
            type_name: name of the type of this action node

        Returns:
            An action node typed as request
        """
        node = ElementTree.Element("macro-action")
        node.set("type", type_name)
        return node


class JoystickAction(AbstractAction):
    """Joystick input action for a macro."""

    tag = "joystick"

    def __init__(
            self,
            device_guid: uuid.UUID,
            input_type: InputType,
            input_id: int | uuid.UUID,
            value: bool | float | Tuple[int, int],
            axis_mode: AxisMode=AxisMode.Absolute
    ):
        """Creates a new JoystickAction instance for use in a macro.

        Args:
            device_guid: GUID of the device generating the input
            input_type: type of input being generated
            input_id: id of the input being generated
            value: the value of the generated input
            axis_mode: if an axis is used, how to interpret the value
        """
        self.device_guid = device_guid
        self.input_type = input_type
        self.input_id = input_id
        self.value = value
        self.axis_mode = axis_mode

    @classmethod
    def create(cls) -> JoystickAction:
        return JoystickAction(
            dill.UUID_Invalid,
            InputType.JoystickButton,
            0,
            False
        )

    def __call__(self) -> None:
        """Emits an Event instance through the EventListener system."""
        el = gremlin.event_handler.EventListener()
        if self.input_type == InputType.JoystickAxis:
            event = gremlin.event_handler.Event(
                event_type=self.input_type,
                device_guid=self.device_guid,
                identifier=self.input_id,
                mode=mode_manager.ModeManager().current.name,
                value=self.value
            )
        elif self.input_type == InputType.JoystickButton:
            event = gremlin.event_handler.Event(
                event_type=self.input_type,
                device_guid=self.device_guid,
                identifier=self.input_id,
                mode=mode_manager.ModeManager().current.name,
                is_pressed=self.value
            )
        elif self.input_type == InputType.JoystickHat:
            event = gremlin.event_handler.Event(
                event_type=self.input_type,
                device_guid=self.device_guid,
                identifier=self.input_id,
                mode=mode_manager.ModeManager().current.name,
                value=self.value
            )

        el.joystick_event.emit(event)

    def to_xml(self) -> ElementTree.Element:
        node = self._create_node(self.tag)
        util.append_property_nodes(
            node,
            [
                ["device-guid", self.device_guid, PropertyType.UUID],
                ["input-type", self.input_type, PropertyType.InputType],
                ["input-id", self.input_id, PropertyType.Int],
            ]
        )
        if self.input_type == InputType.JoystickAxis:
            util.append_property_nodes(
                node,
                [
                    ["value", self.value, PropertyType.Float],
                    ["axis-mode", self.axis_mode, PropertyType.AxisMode]
                ]
            )
        elif self.input_type == InputType.JoystickButton:
            node.append(util.create_property_node(
                "value", self.value, PropertyType.Bool
            ))
        elif self.input_type == InputType.JoystickHat:
            node.append(util.create_property_node(
                "value", self.value, PropertyType.HatDirection
            ))
        return node

    def from_xml(self, node: ElementTree.Element) -> None:
        self.device_guid = util.read_property(
            node, "device-guid", PropertyType.UUID
        )
        self.input_type = util.read_property(
            node, "input-type", PropertyType.InputType
        )
        self.input_id = util.read_property(node, "input-id", PropertyType.Int)
        if self.input_type == InputType.JoystickAxis:
            self.value = util.read_property(node, "value", PropertyType.Float)
            self.axis_mode = util.read_property(
                node, "axis-mode", PropertyType.AxisMode
            )
        elif self.input_type == InputType.JoystickButton:
            self.value = util.read_property(node, "value", PropertyType.Bool)
        elif self.input_type == InputType.JoystickHat:
            self.value = util.read_property(
                node, "value", PropertyType.HatDirection
            )


class KeyAction(AbstractAction):
    """Key to press or release by a macro."""

    tag = "key"

    def __init__(self, key: Key, is_pressed: bool):
        """Creates a new KeyAction object for use in a macro.

        Args:
            key: the key to use in the action
            is_pressed: True if the key should be pressed, False otherwise
        """
        if not isinstance(key, Key):
            raise gremlin.error.KeyboardError("Invalid Key instance provided")

        self.key = key
        self.is_pressed = is_pressed

    @classmethod
    def create(cls) -> KeyAction:
        return KeyAction(key_from_name("noname"), False)

    def __call__(self) -> None:
        if self.is_pressed:
            send_key_down(self.key)
        else:
            send_key_up(self.key)

    def to_xml(self) -> ElementTree.Element:
        node = self._create_node(self.tag)
        util.append_property_nodes(
            node,
            [
                ["scan-code", self.key.scan_code, PropertyType.Int],
                ["is-extended", self.key.is_extended, PropertyType.Bool],
                ["is-pressed", self.is_pressed, PropertyType.Bool],
            ]
        )
        return node

    def from_xml(self, node: ElementTree.Element) -> None:
        self.key = key_from_code(
            util.read_property(node, "scan-code", PropertyType.Int),
            util.read_property(node, "is-extended", PropertyType.Bool)
        )
        self.is_pressed = util.read_property(
            node, "is-pressed", PropertyType.Bool
        )


class MouseButtonAction(AbstractAction):
    """Mouse button action."""

    tag = "mouse-button"

    def __init__(self, button: MouseButton, is_pressed: bool):
        """Creates a new MouseButtonAction object for use in a macro.

        Args:
            button: the button to use in the action
            is_pressed: True if the button should be pressed, False otherwise
        """
        if not isinstance(button, MouseButton):
            raise gremlin.error.MouseError("Invalid mouse button provided")

        self.button = button
        self.is_pressed = is_pressed

    @classmethod
    def create(cls) -> MouseButtonAction:
        return MouseButtonAction(MouseButton.Left, False)

    def __call__(self) -> None:
        if self.button == MouseButton.WheelDown:
            gremlin.sendinput.mouse_wheel(1)
        elif self.button == MouseButton.WheelUp:
            gremlin.sendinput.mouse_wheel(-1)
        else:
            if self.is_pressed:
                gremlin.sendinput.mouse_press(self.button)
            else:
                gremlin.sendinput.mouse_release(self.button)

    def to_xml(self) -> ElementTree.Element:
        node = self._create_node(self.tag)
        util.append_property_nodes(
            node,
            [
                ["button", MouseButton.to_string(self.button), PropertyType.String],
                ["is-pressed", self.is_pressed, PropertyType.Bool],
            ]
        )
        return node

    def from_xml(self, node: ElementTree.Element) -> None:
        self.button = MouseButton.to_enum(util.read_property(
            node, "button", PropertyType.String
        ))
        self.is_pressed = util.read_property(
            node, "is-pressed", PropertyType.Bool
        )


class MouseMotionAction(AbstractAction):
    """Mouse motion action."""

    tag = "mouse-motion"

    def __init__(self, dx: float|int, dy: float|int):
        """Creates a new MouseMotionAction object for use in a macro.

        Args:
            dx: change along the X axis
            dy: change along the Y axis
        """
        self.dx = int(dx)
        self.dy = int(dy)

    @classmethod
    def create(cls) -> MouseMotionAction:
        return MouseMotionAction(0, 0)

    def __call__(self) -> None:
        gremlin.sendinput.mouse_relative_motion(self.dx, self.dy)

    def to_xml(self) -> ElementTree.Element:
        node = self._create_node(self.tag)
        util.append_property_nodes(
            node,
            [
                ["dx", self.dx, PropertyType.Int],
                ["dy", self.dy, PropertyType.Int],
            ]
        )
        return node

    def from_xml(self, node: ElementTree.Element) -> None:
        self.dx = util.read_property(node, "dx", PropertyType.Int)
        self.dy = util.read_property(node, "dy", PropertyType.Int)


class PauseAction(AbstractAction):
    """Represents the pause in a macro between pressed."""

    tag = "pause"

    def __init__(self, duration: float):
        """Creates a new Pause object for use in a macro.

        Args:
            duration: the duration in seconds of the pause
        """
        self.duration = duration

    @classmethod
    def create(cls) -> PauseAction:
        return PauseAction(0.0)

    def __call__(self) -> None:
        time.sleep(self.duration)

    def to_xml(self) -> ElementTree.Element:
        node = self._create_node(self.tag)
        node.append(util.create_property_node(
            "duration", self.duration, PropertyType.Float
        ))
        return node

    def from_xml(self, node: ElementTree.Element) -> None:
        self.duration = util.read_property(
            node, "duration", PropertyType.Float
        )


class VJoyAction(AbstractAction):
    """VJoy input action for a macro."""

    tag = "vjoy"

    def __init__(
            self,
            vjoy_id: int,
            input_type: InputType,
            input_id: int,
            value: bool | float | Tuple[int, int],
            axis_mode: AxisMode=AxisMode.Absolute
    ):
        """Creates a new JoystickAction instance for use in a macro.

        Args:
            vjoy_id: id of the vjoy device which is to be modified
            input_type: type of input being generated
            input_id: id of the input being generated
            value: the value of the generated input
            axis_type: if an axis is used, how to interpret the value
        """
        self.vjoy_id = vjoy_id
        self.input_type = input_type
        self.input_id = input_id
        self.value = value
        self.axis_mode = axis_mode

    @classmethod
    def create(cls) -> VJoyAction:
        # FIXME: Implement a function returning a valid vJoy input
        return VJoyAction(1, InputType.JoystickButton, 1, False)

    def __call__(self) -> None:
        vjoy = VJoyProxy()[self.vjoy_id]
        if self.input_type == InputType.JoystickAxis:
            if self.axis_mode == AxisMode.Absolute:
                vjoy.axis(self.input_id).value = self.value
            elif self.axis_mode == AxisMode.Relative:
                vjoy.axis(self.input_id).value = max(
                    -1.0,
                    min(1.0, vjoy.axis(self.input_id).value + self.value)
                )
        elif self.input_type == InputType.JoystickButton:
            vjoy.button(self.input_id).is_pressed = self.value
        elif self.input_type == InputType.JoystickHat:
            vjoy.hat(self.input_id).direction = self.value.value

    def to_xml(self) -> ElementTree.Element:
        node = self._create_node(self.tag)
        util.append_property_nodes(
            node,
            [
                ["vjoy-id", self.vjoy_id, PropertyType.Int],
                ["input-type", self.input_type, PropertyType.InputType],
                ["input-id", self.input_id, PropertyType.Int],
            ]
        )
        if self.input_type == InputType.JoystickAxis:
            util.append_property_nodes(
                node,
                [
                    ["value", self.value, PropertyType.Float],
                    ["axis-mode", self.axis_mode, PropertyType.AxisMode]
                ])
        elif self.input_type == InputType.JoystickButton:
            node.append(util.create_property_node(
                "value", self.value, PropertyType.Bool
            ))
        elif self.input_type == InputType.JoystickHat:
            node.append(util.create_property_node(
                "value", self.value, PropertyType.HatDirection
            ))
        return node

    def from_xml(self, node: ElementTree.Element) -> None:
        self.vjoy_id = util.read_property(node, "vjoy-id", PropertyType.Int)
        self.input_type = util.read_property(
            node, "input-type", PropertyType.InputType
        )
        self.input_id = util.read_property(node, "input-id", PropertyType.Int)
        if self.input_type == InputType.JoystickAxis:
            self.value = util.read_property(node, "value", PropertyType.Float)
            self.axis_mode = util.read_property(
                node, "axis-mode", PropertyType.AxisMode
            )
        elif self.input_type == InputType.JoystickButton:
            self.value = util.read_property(node, "value", PropertyType.Bool)
        elif self.input_type == InputType.JoystickHat:
            self.value = util.read_property(
                node, "value", PropertyType.HatDirection
            )
