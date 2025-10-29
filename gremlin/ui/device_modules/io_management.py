"""Intermediate Output (IO) device management models.

This module provides models for managing intermediate output devices in the UI,
allowing creation, deletion, and labeling of virtual inputs.
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

import uuid
from typing import Any, Dict, List, Tuple

from PySide6 import QtCore, QtQml
from PySide6.QtCore import Property, Signal, Slot

from gremlin import shared_state
from gremlin.error import GremlinError
from gremlin.intermediate_output import IntermediateOutput
from gremlin.types import InputType
from .models import InputIdentifier


@QtQml.QmlElement
class IODeviceManagementModel(QtCore.QAbstractListModel):

    """Model providing information about the intermedia output device."""

    roles = {
        QtCore.Qt.UserRole + 1: QtCore.QByteArray("name".encode()),
        QtCore.Qt.UserRole + 2: QtCore.QByteArray("actionCount".encode()),
        QtCore.Qt.UserRole + 3: QtCore.QByteArray("label".encode()),
    }

    deviceChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._io = IntermediateOutput()

    @Slot(str)
    def createInput(self, type_str: str) -> None:
        self.beginInsertRows(
            QtCore.QModelIndex(),
            self.rowCount(),
            self.rowCount()
        )
        self._io.create(InputType.to_enum(type_str))
        self.endInsertRows()
        self.dataChanged.emit(
            self.createIndex(0, 0),
            self.createIndex(self.rowCount(), 0)
        )

    @Slot(str, str)
    def changeName(self, old_labele: str, new_label: str) -> None:
        try:
            self._io.set_label(old_labele, new_label)
            self.dataChanged.emit(
                self.createIndex(0, 0),
                self.createIndex(self.rowCount(), 0)
            )
        except GremlinError:
            # FIXME: Somehow needs to reset the text field to the previous value
            pass

    @Slot(str)
    def deleteInput(self, label: str) -> None:
        item_index = self._label_to_index(label)
        self.beginRemoveRows(QtCore.QModelIndex(), item_index, item_index)
        self._io.delete(label)
        self.endRemoveRows()
        self.dataChanged.emit(
            self.createIndex(0, 0),
            self.createIndex(self.rowCount(), 0)
        )

    def _get_guid(self) -> str:
        return str(self._io.device_guid)

    def rowCount(self, parent:QtCore.QModelIndex=...) -> int:
        return len(self._io.labels_of_type())

    def data(self, index: QtCore.QModelIndex, role:int=...) -> Any:
        if role not in IODeviceManagementModel.roles:
            return "Unknown"

        role_name = IODeviceManagementModel.roles[role].data().decode()
        input = self._index_to_input(index.row())
        if role_name == "name":
            return f"{InputType.to_string(input.type).capitalize()} " \
                f"{input.suffix}"
        elif role_name == "actionCount":
            # FIXME: retrieve currently selected moden mae
            return shared_state.current_profile.get_input_count(
                self._io.device_guid,
                input.type,
                input.guid,
                "Default"
            )
        elif role_name == "label":
            return input.label

    @Slot(str, result=List[str])
    def validLabels(self, type_str: str) -> List[str]:
        """Returns a list of valid labels for a given input."""
        type = InputType.to_enum(type_str)
        if len(self._io.keys_of_type([type])) == 0:
            self._io.create(type)
        return self._io.keys_of_type([type])

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
        if index < 0:
            return InputIdentifier(parent=self)

        input = self._index_to_input(index)
        identifier = InputIdentifier(parent=self)
        identifier.device_guid = self._io.device_guid
        identifier.input_type = input.type
        identifier.input_id = input.guid

        return identifier

    def _name(self, identifier: Tuple[InputType, int]) -> str:
        return "{} {:d}".format(
            InputType.to_string(identifier[0]).capitalize(),
            identifier[1]
        )

    def _index_to_input(self, index: int) -> IntermediateOutput.Input:
        """Returns the label corresponding to the provided linear index.

        Args:
            index: the linear index into the list of inputs

        Returns:
            The input corresponding to the given index
        """
        return self._io[self._io.labels_of_type()[index]]

    def _label_to_index(self, label: str) -> int:
        """Returns the index corresponding to the given label.

        Args:
            label: name of the input for which to determine the index

        Returns:
            Index of the given label in the backend data storage
        """
        all_labels = self._io.labels_of_type()
        return all_labels.index(label)

    def roleNames(self) -> Dict:
        return IODeviceManagementModel.roles

    guid = Property(str, fget=_get_guid)


@QtQml.QmlElement
class IODeviceInputsModel(QtCore.QAbstractListModel):

    inputsChanged = Signal()
    selectionChanged = Signal()

    roles = {
        QtCore.Qt.UserRole + 1: QtCore.QByteArray("label".encode()),
        QtCore.Qt.UserRole + 2: QtCore.QByteArray("guid".encode())
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self._io = IntermediateOutput()
        self._valid_types = None
        self._current_index = 0
        self._current_guid = None

    def rowCount(self, parent) -> int:
        return len(self._io.labels_of_type(self._valid_types))

    def data(
            self,
            index: QtCore.QModelIndex,
            role: int=QtCore.Qt.ItemDataRole.DisplayRole
    ) -> Any:
        if role not in self.roleNames():
            raise GremlinError(f"Invalid role {role} in IODeviceInputsModel")

        input = self._io.inputs_of_type(self._valid_types)[index.row()]
        if role == QtCore.Qt.UserRole + 1:
            return input.label
        elif role == QtCore.Qt.UserRole + 2:
            return str(input.guid)

    def roleNames(self) -> Dict:
        return IODeviceInputsModel.roles

    def _set_valid_types(self, valid_types: List[str]) -> None:
        type_list = sorted([InputType.to_enum(entry) for entry in valid_types])
        if type_list != self._valid_types:
            self._valid_types = type_list
            self.inputsChanged.emit()

    def _get_current_selection_index(self) -> int:
        return self._current_index

    def _get_current_guid(self) -> str:
        return str(self._current_guid)

    def _set_current_guid(self, guid_str: str) -> None:
        guid = uuid.UUID(guid_str)
        if guid != self._current_guid:
            self._current_guid = guid
            self._current_index = 0
            for i, input in enumerate(self._io.inputs_of_type(self._valid_types)):
                if input.guid == guid:
                    self._current_index = i
            self.selectionChanged.emit()

    validTypes = Property(
        "QVariantList",
        fset=_set_valid_types,
        notify=inputsChanged
    )

    currentSelectionIndex = Property(
        int,
        fget=_get_current_selection_index,
        notify=selectionChanged
    )

    currentGuid = Property(
        str,
        fget=_get_current_guid,
        fset=_set_current_guid,
        notify=selectionChanged
    )
