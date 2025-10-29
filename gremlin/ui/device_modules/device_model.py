"""Device model for QML UI.

This module provides the Device class which represents a single input device
in the UI. It provides access to device information and input details.
"""

# Copyright (C) 2015 - 2025 Lionel Ott
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

from typing import Any, Dict, Tuple

from PySide6 import QtCore, QtQml
from PySide6.QtCore import Property, Signal, Slot

import dill

from gremlin import shared_state
from gremlin.types import InputType
from .database import DeviceDatabase
from .models import InputIdentifier


@QtQml.QmlElement
class Device(QtCore.QAbstractListModel):

    """Model providing access to information about a single device."""

    roles = {
        QtCore.Qt.UserRole + 1: QtCore.QByteArray("name".encode()),
        QtCore.Qt.UserRole + 2: QtCore.QByteArray("actionCount".encode()),
        QtCore.Qt.UserRole + 3: QtCore.QByteArray("description".encode()),
    }

    deviceChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._device: dill.DeviceSummary | None = None
        self._device_mapping: Dict[str, str] | None = None
        self._mode = "Default"

    @Slot(int)
    def refreshInput(self, index: int) -> None:
        """Refreshes the input at the given index.

        Args:
            index: linear index of the device's inputs to refresh
        """
        self.dataChanged.emit(
            self.createIndex(index, 0),
            self.createIndex(index, 0)
        )

    @Slot(str)
    def setMode(self, mode: str) -> None:
        self._mode = mode
        self.modelReset.emit()

    def _get_guid(self) -> str:
        if self._device is None:
            return "Unknown"
        else:
            return str(self._device.device_guid)

    def _set_guid(self, guid: str) -> None:
        if self._device is not None and guid == str(self._device.device_guid):
            return

        self._device = dill.DILL.get_device_information_by_guid(
            dill.GUID.from_str(guid)
        )

        self._device_mapping = DeviceDatabase().get_mapping(self._device)
        self.deviceChanged.emit()
        self.layoutChanged.emit()

    def rowCount(self, parent:QtCore.QModelIndex=...) -> int:
        if self._device is None:
            return 0

        return self._device.axis_count + \
               self._device.button_count + \
               self._device.hat_count

    def data(self, index: QtCore.QModelIndex, role:int=...) -> Any:
        if role not in Device.roles:
            return "Unknown"

        role_name = Device.roles[role].data().decode()
        match role_name:
            case "name":
                return self._name(self._convert_index(index.row()))
            case "actionCount":
                input_info = self._convert_index(index.row())
                return shared_state.current_profile.get_input_count(
                    self._device.device_guid.uuid,
                    input_info[0],
                    input_info[1],
                    self._mode
                )
            case "description":
                input_info = self._convert_index(index.row())
                item = shared_state.current_profile.get_input_item(
                    self._device.device_guid.uuid,
                    input_info[0],
                    input_info[1],
                    self._mode
                )
                if item and len(item.action_sequences) > 0:
                    labels = filter(
                        lambda x: x != "Root",
                        [seq.root_action.action_label for seq in item.action_sequences]
                    )
                    return " / ".join(labels)
                else:
                    return ""
            case _:
                return ""

    @Slot(int, result=InputIdentifier)
    def inputIdentifier(self, index: int) -> InputIdentifier:
        """Returns the InputIdentifier for input with the specified index.

        Args:
            index: the index of the input for which to generate the
                InpuIdentifier instance

        Returns:
            An InputIdentifier instance referring to the input item with
            the given index.
        """
        identifier = InputIdentifier(parent=self)
        identifier.device_guid = self._device.device_guid.uuid
        input_info = self._convert_index(index)
        identifier.input_type = input_info[0]
        identifier.input_id = input_info[1]

        return identifier

    def _name(self, identifier: Tuple[InputType, int]) -> str:
        input_name = "{} {:d}".format(
            InputType.to_string(identifier[0]).capitalize(),
            identifier[1]
        )

        if self._device_mapping is not None:
            return self._device_mapping.input_name(input_name)
        else:
            return input_name

    def _convert_index(self, index: int) -> Tuple[InputType, int]:
        axis_count = self._device.axis_count
        button_count = self._device.button_count
        hat_count = self._device.hat_count

        if index < axis_count:
            return (
                InputType.JoystickAxis,
                self._device.axis_map[index].axis_index
            )
        elif index < axis_count + button_count:
            return (
                InputType.JoystickButton,
                index + 1 - axis_count
            )
        else:
            return (
                InputType.JoystickHat,
                index + 1 - axis_count - button_count
            )

    def roleNames(self) -> Dict:
        return Device.roles

    guid = Property(
        str,
        fget=_get_guid,
        fset=_set_guid,
        notify=deviceChanged
    )
