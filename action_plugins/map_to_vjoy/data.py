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

"""MapToVjoy data class for configuration and persistence."""

from __future__ import annotations

from typing import List
from xml.etree import ElementTree

from gremlin import device_initialization, error, util
from gremlin.base_classes import AbstractActionData
from gremlin.profile import Library
from gremlin.types import ActionProperty, AxisMode, InputType, PropertyType

class MapToVjoyData(AbstractActionData):

    """Action feeding a vJoy device."""

    version = 1
    name = "Map to vJoy"
    tag = "map-to-vjoy"
    icon = "\uF448"

    functor = None  # Set after import to avoid circular dependency
    model = None  # Set after import to avoid circular dependency

    properties = [
        ActionProperty.ActivateOnBoth
    ]
    input_types = [
        InputType.JoystickAxis,
        InputType.JoystickButton,
        InputType.JoystickHat,
        InputType.Keyboard
    ]

    def __init__(
            self,
            behavior_type: InputType=InputType.JoystickButton
    ):
        super().__init__(behavior_type)

        # Select an initially valid vJoy input
        device = device_initialization.vjoy_devices()[0]
        vjoy_id = device.vjoy_id
        input_id = 1
        if behavior_type == InputType.JoystickAxis:
            input_id = device.axis_map[0].axis_index

        # Model variables
        self.vjoy_device_id = vjoy_id
        self.vjoy_input_id = input_id
        self.vjoy_input_type = behavior_type
        self.axis_mode = AxisMode.Absolute
        self.axis_scaling = 1.0
        self.button_inverted = False

    @classmethod
    def can_create(cls) -> bool:
        return len(device_initialization.vjoy_devices()) > 0

    def _from_xml(self, node: ElementTree.Element, library: Library) -> None:
        self._id = util.read_action_id(node)
        self.vjoy_device_id = util.read_property(
            node, "vjoy-device-id", PropertyType.Int
        )
        self.vjoy_input_id = util.read_property(
            node, "vjoy-input-id", PropertyType.Int
        )
        self.vjoy_input_type = util.read_property(
            node, "vjoy-input-type", PropertyType.InputType
        )
        if self.vjoy_input_type == InputType.JoystickAxis:
            self.axis_mode = util.read_property(
                node, "axis-mode", PropertyType.AxisMode
            )
            self.axis_scaling = util.read_property(
                node, "axis-scaling", PropertyType.Float
            )
        if self.vjoy_input_type == InputType.JoystickButton:
            self.button_inverted = util.read_property(
                node, "button-inverted", PropertyType.Bool
            )

    def _to_xml(self) -> ElementTree.Element:
        node = util.create_action_node(MapToVjoyData.tag, self._id)
        node.append(util.create_property_node(
            "vjoy-device-id", self.vjoy_device_id, PropertyType.Int
        ))
        node.append(util.create_property_node(
            "vjoy-input-id", self.vjoy_input_id, PropertyType.Int
        ))
        node.append(util.create_property_node(
            "vjoy-input-type", self.vjoy_input_type, PropertyType.InputType
        ))
        if self.vjoy_input_type == InputType.JoystickAxis:
            node.append(util.create_property_node(
                "axis-mode", self.axis_mode, PropertyType.AxisMode
            ))
            node.append(util.create_property_node(
                "axis-scaling", self.axis_scaling, PropertyType.Float
            ))
        if self.vjoy_input_type == InputType.JoystickButton:
            node.append(util.create_property_node(
                "button-inverted", self.button_inverted, PropertyType.Bool
            ))
        return node

    def is_valid(self) -> bool:
        return True

    def _valid_selectors(self) -> List[str]:
        return []

    def _get_container(self, selector: str) -> List[AbstractActionData]:
        raise error.GremlinError(f"{self.name}: has no containers")

    def _handle_behavior_change(
        self,
        old_behavior: InputType,
        new_behavior: InputType
    ) -> None:
        self._vjoy_input_type = new_behavior


# Set functor and model after class definition to avoid circular imports
from action_plugins.map_to_vjoy.functor import MapToVjoyFunctor
from action_plugins.map_to_vjoy.model import MapToVjoyModel
MapToVjoyData.functor = MapToVjoyFunctor
MapToVjoyData.model = MapToVjoyModel

create = MapToVjoyData

