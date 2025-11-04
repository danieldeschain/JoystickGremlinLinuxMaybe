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

"""MapToVjoy QML model for UI interaction."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6 import QtCore
from PySide6.QtCore import Property, Signal

from gremlin.base_classes import AbstractActionData
from gremlin.types import AxisMode, InputType
from gremlin.ui.action_model import SequenceIndex, ActionModel

if TYPE_CHECKING:
    from gremlin.ui.profile import InputItemBindingModel

class MapToVjoyModel(ActionModel):

    # Signals emitted when properties change
    vjoyDeviceIdChanged = Signal()
    vjoyInputIdChanged = Signal()
    inputTypeChanged = Signal()
    axisModeChanged = Signal()
    axisScalingChanged = Signal()
    buttonInvertedChanged = Signal()

    def __init__(
            self,
            data: AbstractActionData,
            binding_model: InputItemBindingModel,
            action_index: SequenceIndex,
            parent_index: SequenceIndex,
            parent: QtCore.QObject
    ):
        super().__init__(data, binding_model, action_index, parent_index, parent)

    def _qml_path_impl(self) -> str:
        return "file:///" + QtCore.QFile(
            "core_plugins:map_to_vjoy/MapToVjoyAction.qml"
        ).fileName()

    def _action_behavior(self) -> str:
        return  self._binding_model.get_action_model_by_sidx(
            self._parent_sequence_index.index
        ).actionBehavior

    def _get_vjoy_device_id(self) -> int:
        return self._data.vjoy_device_id

    def _set_vjoy_device_id(self, vjoy_device_id: int) -> None:
        if vjoy_device_id == self._data.vjoy_device_id:
            return
        self._data.vjoy_device_id = vjoy_device_id
        self.vjoyDeviceIdChanged.emit()

    def _get_vjoy_input_id(self) -> int:
        return self._data.vjoy_input_id

    def _set_vjoy_input_id(self, vjoy_input_id: int) -> None:
        if vjoy_input_id == self._data.vjoy_input_id:
            return
        self._data.vjoy_input_id = vjoy_input_id
        self.vjoyInputIdChanged.emit()

    def _get_vjoy_input_type(self) -> str:
        return InputType.to_string(self._data.vjoy_input_type)

    def _set_vjoy_input_type(self, input_type: str) -> None:
        input_type_tmp = InputType.to_enum(input_type)
        if input_type_tmp == self._data.vjoy_input_type:
            return
        self._data.vjoy_input_type = input_type_tmp
        self.inputTypeChanged.emit()

    def _get_axis_mode(self) -> str:
        return AxisMode.to_string(self._data.axis_mode)

    def _set_axis_mode(self, axis_mode: str) -> None:
        axis_mode_tmp = AxisMode.to_enum(axis_mode)
        if axis_mode_tmp == self._data.axis_mode:
            return
        self._data.axis_mode = axis_mode_tmp
        self.axisModeChanged.emit()

    def _get_axis_scaling(self) -> float:
        return self._data.axis_scaling

    def _set_axis_scaling(self, axis_scaling: float) -> None:
        if axis_scaling == self._data.axis_scaling:
            return
        self._data.axis_scaling = axis_scaling
        self.axisScalingChanged.emit()

    def _get_button_inverted(self) -> bool:
        return self._data.button_inverted

    def _set_button_inverted(self, button_inverted: bool) -> None:
        if button_inverted == self._data.button_inverted:
            return
        self._data.button_inverted = button_inverted
        self.buttonInvertedChanged.emit()

    # Define properties
    vjoyDeviceId = Property(
        int,
        fget=_get_vjoy_device_id,
        fset=_set_vjoy_device_id,
        notify=vjoyDeviceIdChanged
    )
    vjoyInputId = Property(
        int,
        fget=_get_vjoy_input_id,
        fset=_set_vjoy_input_id,
        notify=vjoyInputIdChanged
    )
    vjoyInputType = Property(
        str,
        fget=_get_vjoy_input_type,
        fset=_set_vjoy_input_type,
        notify=inputTypeChanged
    )
    axisMode = Property(
        str,
        fget=_get_axis_mode,
        fset=_set_axis_mode,
        notify=axisModeChanged
    )
    axisScaling = Property(
        float,
        fget=_get_axis_scaling,
        fset=_set_axis_scaling,
        notify=axisScalingChanged
    )
    buttonInverted = Property(
        bool,
        fget=_get_button_inverted,
        fset=_set_button_inverted,
        notify=buttonInvertedChanged
    )


