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

"""Device list models and input identifiers."""

from __future__ import annotations

import uuid
from typing import Any, Dict

from PySide6 import QtCore, QtQml
from PySide6.QtCore import Property, Signal, Slot

import dill

from gremlin import device_initialization, event_handler
from gremlin.error import GremlinError
from gremlin.types import InputType


@QtQml.QmlElement
class InputIdentifier(QtCore.QObject):
    """Stores the identifier of a single input item."""

    changed = Signal()

    def __init__(
            self,
            device_guid: uuid.UUID | None=None,
            input_type: InputType | None=None,
            input_id: int | None=None,
            parent=None
    ):
        super().__init__(parent)

        self.device_guid = device_guid
        self.input_type = input_type
        self.input_id = input_id

    @Property(str, notify=changed)
    def label(self) -> str:
        if self.isValid:
            dev_name = dill.DILL.get_device_name(
                dill.GUID.from_uuid(self.device_guid)
            )
            return f"{dev_name} - " + \
                   f"{InputType.to_string(self.input_type).capitalize()} " + \
                   f"{self.input_id}"
        else:
            return "No input"

    @Property(bool, notify=changed)
    def isValid(self) -> bool:
        return self.device_guid is not None \
            and self.input_type is not None \
            and self.input_id is not None

    def __eq__(self, other: InputIdentifier) -> bool:
        return self.device_guid == other.device_guid and \
            self.input_type == other.input_type and \
            self.input_id == other.input_id


@QtQml.QmlElement
class DeviceListModel(QtCore.QAbstractListModel):
    """Model containing basic information about all connected devices."""

    roles = {
        QtCore.Qt.UserRole + 1: QtCore.QByteArray("name".encode()),
        QtCore.Qt.UserRole + 2: QtCore.QByteArray("axes".encode()),
        QtCore.Qt.UserRole + 3: QtCore.QByteArray("buttons".encode()),
        QtCore.Qt.UserRole + 4: QtCore.QByteArray("hats".encode()),
        QtCore.Qt.UserRole + 5: QtCore.QByteArray("pid".encode()),
        QtCore.Qt.UserRole + 6: QtCore.QByteArray("vid".encode()),
        QtCore.Qt.UserRole + 7: QtCore.QByteArray("guid".encode()),
        QtCore.Qt.UserRole + 8: QtCore.QByteArray("joy_id".encode()),
    }

    role_query = {
        "name": lambda dev: dev.name,
        "axes": lambda dev: dev.axis_count,
        "buttons": lambda dev: dev.button_count,
        "hats": lambda dev: dev.hat_count,
        "pid": lambda dev: "{:04X}".format(dev.product_id),
        "vid": lambda dev: "{:04X}".format(dev.vendor_id),
        "guid": lambda dev: str(dev.device_guid),
        "joy_id": lambda dev: dev.joystick_id,
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._devices = device_initialization.physical_devices()

        event_handler.EventListener().device_change_event.connect(
            self.update_model
        )

    def update_model(self) -> None:
        """Updates the model if the connected devices change."""
        old_count = len(self._devices)
        self._devices = device_initialization.physical_devices()
        new_count = len(self._devices)

        # Ensure the entire model is refreshed
        self.modelReset.emit()

    def rowCount(self, parent:QtCore.QModelIndex=...) -> int:
        return len(self._devices)

    def data(self, index:QtCore.QModelIndex, role:int=...) -> Any:
        if role in DeviceListModel.roles:
            role_name = DeviceListModel.roles[role].data().decode()
            return DeviceListModel.role_query[role_name](
                self._devices[index.row()]
            )
        else:
            return "Unknown"

    def roleNames(self) -> Dict:
        return DeviceListModel.roles

    @Slot(int, result=str)
    def guidAtIndex(self, index: int) -> str:
        if len(self._devices) == 0:
            return str(dill.UUID_Invalid)
        if not(0 <= index < len(self._devices)):
            raise GremlinError("Provided index out of range")

        return str(self._devices[index].device_guid)

    def _change_device_type(self, types: str) -> None:
        """Sets which device types are going to be used.

        Valid options are:
        - physical
        - virtual
        - all

        Args:
            types: the type of devices to list
        """
        if types == "physical":
            self._devices = device_initialization.physical_devices()
        elif types == "virtual":
            self._devices = device_initialization.vjoy_devices()
        elif types == "all":
            self._devices = device_initialization.joystick_devices()

        # Remove everything and then add it back to force a model update
        new_count = len(self._devices)
        self.rowsRemoved.emit(self.parent(), 0, new_count)
        self.rowsInserted.emit(self.parent(), 0, new_count)

    deviceType = Property(
        str,
        fset=_change_device_type
    )
