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

from abc import ABC, abstractmethod
import numbers
from typing import Any
from xml.etree import ElementTree

import linput
from gremlin.input_cache import Joystick
from gremlin.types import InputType, PropertyType
from gremlin import util


class AbstractVariable(ABC):

    xml_tag = "abstract"

    def __init__(
            self,
            name: str|None=None,
            description: str="",
            is_optional: bool=True
    ):
        self.name = name
        self.description = description
        self.is_optional = is_optional
        self.is_set = False

    @property
    @abstractmethod
    def value(self) -> Any:
        pass

    @value.setter
    @abstractmethod
    def value(self, value: Any) -> None:
        pass

    def from_xml(self, node: ElementTree.Element) -> None:
        self.name = util.read_property(node, "name", PropertyType.String)
        self._from_xml(node)

    def to_xml(self) -> ElementTree.Element:
        if not self.is_valid():
            return None
        node = ElementTree.Element("variable")
        node.set("type", self.xml_tag)
        util.append_property_nodes(
            node,
            [
                ["name", self.name, PropertyType.String]
            ]
        )
        self._to_xml(node)
        return node

    @abstractmethod
    def is_valid(self) -> bool:
        pass

    @abstractmethod
    def _from_xml(self, node: ElementTree.Element) -> None:
        pass

    @abstractmethod
    def _to_xml(self, node: ElementTree.Element) -> None:
        pass

    @abstractmethod
    def _assign_value_from(self, other: AbstractVariable) -> None:
        pass

    def _get_script_id(self) -> uuid.UUID|None:
        for frame in inspect.stack():
            identifier = frame.frame.f_locals.get(
                "_script_id",
                None
            )
            if isinstance(identifier, uuid.UUID):
                return identifier
        return None

    def _initialize_from_registry(self) -> None:
        idx = self._get_script_id()
        var = Script.variable_registry.get(idx, self.name)
        if isinstance(var, AbstractVariable):
            self._assign_value_from(var)


class BoolVariable(AbstractVariable):

    xml_tag = "bool"

    def __init__(
            self,
            name: str,
            description: str,
            is_optional: bool,
            initial_value: bool
    ):
        super().__init__(name, description, is_optional)

        self._value = initial_value
        self._initialize_from_registry()

    @property
    def value(self) -> bool:
        return self._value

    @value.setter
    def value(self, value: bool) -> None:
        self._value = value

    def is_valid(self) -> bool:
        return self._value in [True, False]

    def _from_xml(self, node: ElementTree.Element) -> None:
        self._value = util.read_property(node, "value", PropertyType.Bool)

    def _to_xml(self, node: ElementTree.Element) -> None:
        node.append(util.create_property_node(
            "value", self.value, PropertyType.Bool
        ))

    def _assign_value_from(self, other: BoolVariable) -> None:
        self._value = other.value


class FloatVariable(AbstractVariable):

    xml_tag = "float"

    def __init__(
            self,
            name: str,
            description: str,
            is_optional: bool,
            initial_value: float,
            min_value: float,
            max_value: float,
    ):
        super().__init__(name, description, is_optional)

        self._value = initial_value
        self._min_value = min_value
        self._max_value = max_value
        self._initialize_from_registry()

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        self._value = clamp_value(value, self._min_value, self._max_value)

    @property
    def min_value(self) -> float:
        return self._min_value

    @property
    def max_value(self) -> float:
        return self._max_value

    def is_valid(self) -> bool:
        return isinstance(self._value, numbers.Number)

    def _from_xml(self, node: ElementTree.Element) -> None:
        self._value = util.read_property(node, "value", PropertyType.Float)

    def _to_xml(self, node: ElementTree.Element) -> None:
        node.append(util.create_property_node(
            "value", self._value, PropertyType.Float
        ))

    def _assign_value_from(self, other: FloatVariable) -> None:
        self._value = other.value


class IntegerVariable(AbstractVariable):

    xml_tag = "int"

    def __init__(
            self,
            name: str,
            description: str,
            is_optional: bool,
            initial_value: int,
            min_value: int,
            max_value: int,
    ):
        super().__init__(name, description, is_optional)

        self._value = initial_value
        self._min_value = min_value
        self._max_value = max_value
        self._initialize_from_registry()

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        self._value = clamp_value(value, self._min_value, self._max_value)

    @property
    def min_value(self) -> int:
        return self._min_value

    @property
    def max_value(self) -> int:
        return self._max_value

    def is_valid(self) -> bool:
        return isinstance(self._value, int)

    def _from_xml(self, node: ElementTree.Element) -> None:
        self._value = util.read_property(node, "value", PropertyType.Int)

    def _to_xml(self, node: ElementTree.Element) -> None:
        node.append(util.create_property_node(
            "value", self._value, PropertyType.Int
        ))

    def _assign_value_from(self, other: IntegerVariable) -> None:
        self._value = other.value


class ModeVariable(AbstractVariable):

    xml_tag = "mode"

    def __init__(
            self,
            name: str,
            description: str,
            is_optional: bool
    ):
        super().__init__(name, description, is_optional)

        self._mode = shared_state.current_profile.modes.first_mode
        self._initialize_from_registry()

    @property
    def value(self) -> str:
        return self._mode

    @value.setter
    def value(self, value: str) -> None:
        self._mode = value

    def is_valid(self) -> bool:
        return self._mode in shared_state.current_profile.modes.mode_names()

    def _from_xml(self, node: ElementTree.Element) -> None:
        self._mode = util.read_property(node, "value", PropertyType.String)

    def _to_xml(self, node: ElementTree.Element) -> None:
        node.append(util.create_property_node(
            "value", self._mode, PropertyType.String
        ))

    def _assign_value_from(self, other: ModeVariable) -> None:
        self._mode = other.value


class SelectionVariable(AbstractVariable):

    xml_tag = "selection"

    def __init__(
            self,
            name: str,
            description: str,
            is_optional: bool,
            option_list: list[str],
            default_index: int=0
    ):
        super().__init__(name, description, is_optional)

        self._option_list = option_list
        self._current_index = default_index
        self._initialize_from_registry()

    @property
    def options(self) -> list[str]:
        return self._option_list

    @property
    def value(self) -> str:
        return self._option_list[self._current_index]

    @value.setter
    def value(self, value: str) -> None:
        self._current_index = self._option_list.index(value)

    def is_valid(self) -> bool:
        return True

    def _from_xml(self, node: ElementTree.Element) -> None:
        self._current_index = util.read_property(
            node, "index", PropertyType.Int
        )

    def _to_xml(self, node: ElementTree.Element) -> None:
        node.append(util.create_property_node(
            "index", self._current_index, PropertyType.Int
        ))

    def _assign_value_from(self, other: SelectionVariable) -> None:
        self._current_index = other._current_index


class StringVariable(AbstractVariable):

    xml_tag = "string"

    def __init__(
            self,
            name: str,
            description: str,
            is_optional: bool,
            initial_value: str
    ):
        super().__init__(name, description, is_optional)

        self._value = initial_value
        self._initialize_from_registry()

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        self._value = value

    def is_valid(self) -> bool:
        return isinstance(self._value, str) and len(self._value) > 0

    def _from_xml(self, node: ElementTree.Element) -> None:
        self._value = util.read_property(node, "value", PropertyType.String)

    def _to_xml(self, node: ElementTree.Element) -> None:
        node.append(util.create_property_node(
            "value", self._value, PropertyType.String
        ))

    def _assign_value_from(self, other: StringVariable) -> None:
        self._value = other.value


class PhysicalInputVariable(AbstractVariable):

    xml_tag = "physical-input"

    type Identifier = tuple[uuid.UUID, InputType, int]

    def __init__(
            self,
            name: str,
            description: str,
            is_optional: bool,
            valid_types: list[InputType],
    ):
        super().__init__(name, description, is_optional)

        self._valid_types = valid_types
        self._device_guid = None
        self._input_type = valid_types[0]
        self._input_id = 1
        self._initialize_from_registry()

    @property
    def device_guid(self) -> uuid.UUID:
        return self._device_guid

    @property
    def input_type(self) -> InputType:
        return self._input_type

    @property
    def input_id(self) -> int:
        return self._input_id

    @property
    def value(self) -> Identifier:
        return (self._device_guid, self._input_type, self._input_id)

    @property
    def valid_types(self) -> list[InputType]:
        return self._valid_types

    @value.setter
    def value(self, value: Identifier) -> None:
        self._device_guid = value[0]
        self._input_type = value[1]
        self._input_id = value[2]

    def decorator(self, mode: ModeVariable) -> Callable:
        dec = self.create_decorator(mode.value)
        match self._input_type:
            case InputType.JoystickButton:
                return dec.button(self._input_id)
            case InputType.JoystickAxis:
                return dec.axis(self._input_id)
            case InputType.JoystickHat:
                return dec.hat(self._input_id)
            case _:
                raise error.GremlinError(
                    f"Received invalid input type '{self._input_type}'"
                )

    def create_decorator(self, mode: str):
        if not self.is_valid():
            return JoystickDecorator(
                "", str(dill.GUID_Invalid), ""
            )
        else:
            return JoystickDecorator(
                "device name",
                str(self._device_guid),
                mode
            )

    def is_valid(self) -> bool:
        return (
            self._device_guid is not None
            and self._input_type in self._valid_types
            and isinstance(self._input_id, int)
        )

    def _from_xml(self, node: ElementTree.Element) -> None:
        self._device_guid = util.read_property(
            node, "device-guid", PropertyType.UUID
        )
        self._input_type = util.read_property(
            node, "input-type", PropertyType.InputType
        )
        self._input_id = util.read_property(node, "input-id", PropertyType.Int)

    def _to_xml(self, node: ElementTree.Element) -> None:
        util.append_property_nodes(
            node,
            [
                ["device-guid", self._device_guid, PropertyType.UUID],
                ["input-type", self._input_type, PropertyType.InputType],
                ["input-id", self._input_id, PropertyType.Int],
            ]
        )

    def _assign_value_from(self, other: PhysicalInputVariable) -> None:
        self._valid_types = other._valid_types
        self._device_guid = other.device_guid
        self._input_type = other.input_type
        self._input_id = other.input_id


class VirtualInputVariable(AbstractVariable):

    xml_tag = "vjoy"

    def __init__(
            self,
            name: str,
            description: str,
            is_optional: bool,
            valid_types: list[InputType],
    ):
        super().__init__(name, description, is_optional)

        self._valid_types = valid_types
        self._vjoy_id = 1
        self._input_type = valid_types[0]
        self._input_id = 1
        self._initialize_from_registry()

    @property
    def value(self) -> bool:
        pass

    @value.setter
    def value(self, value: bool) -> None:
        pass

    @property
    def vjoy_id(self) -> int:
        return self._vjoy_id

    @property
    def input_id(self) -> int:
        return self._input_id

    @property
    def input_type(self) -> InputType:
        return self._input_type

    @property
    def valid_types(self) -> list[InputType]:
        return self._valid_types

    def remap(self, value: float|bool|Tuple[int, int]) -> None:
        # REFACTORED: Use linput.VirtualJoystick instead of VJoyProxy
        device = linput.VirtualJoystick.get(self._vjoy_id)
        if device is None:
            raise error.GremlinError(
                f"Virtual device {self._vjoy_id} not found"
            )
        
        match self._input_type:
            case InputType.JoystickButton:
                device.set_button(self._input_id, bool(value))
            case InputType.JoystickAxis:
                device.set_axis(self._input_id, float(value))
            case InputType.JoystickHat:
                # Hat expects tuple of (x, y) values
                if isinstance(value, tuple):
                    device.set_hat(self._input_id, value[0], value[1])
                else:
                    raise error.GremlinError(
                        f"Hat input requires tuple, got {type(value)}"
                    )
            case _:
                raise error.GremlinError(
                    f"Received invalid input type '{self._input_type}'"
                )

    def is_valid(self) -> bool:
        return (
            self._vjoy_id is not None
            and self._input_type in self._valid_types
            and isinstance(self._input_id, int)
        )

    def _from_xml(self, node: ElementTree.Element) -> None:
        self._vjoy_id = util.read_property(node, "vjoy-id", PropertyType.Int)
        self._input_type = util.read_property(
            node, "input-type", PropertyType.InputType
        )
        self._input_id = util.read_property(node, "input-id", PropertyType.Int)

    def _to_xml(self, node: ElementTree.Element) -> None:
        util.append_property_nodes(
            node,
            [
                ["vjoy-id", self._vjoy_id, PropertyType.Int],
                ["input-type", self._input_type, PropertyType.InputType],
                ["input-id", self._input_id, PropertyType.Int],
            ]
        )

    def _assign_value_from(self, other: VirtualInputVariable) -> None:
        self._valid_types = other._valid_types
        self._vjoy_id = other.vjoy_id
        self._input_type = other.input_type
        self._input_id = other.input_id


def clamp_value(value: float, min_val: float, max_val: float) -> float:
