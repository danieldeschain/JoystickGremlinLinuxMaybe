# -*- coding: utf-8; -*-

# Copyright (C) 2015 - 2024 Lionel Ott
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

from typing import Any, Optional

from PySide6 import QtCore
from PySide6.QtCore import Property, Signal


class LabelValueSelectionModel(QtCore.QAbstractListModel):

    """Generic class presenting an interface for use with Comboboxes."""

    selectionChanged = Signal()

    roles = {
        QtCore.Qt.UserRole + 1: QtCore.QByteArray("label".encode()),
        QtCore.Qt.UserRole + 2: QtCore.QByteArray("value".encode()),
        QtCore.Qt.UserRole + 3: QtCore.QByteArray("bootstrap".encode()),
        QtCore.Qt.UserRole + 4: QtCore.QByteArray("imageIcon".encode())
    }

    def __init__(
            self,
            labels: List[Any],
            values: List[str],
            bootstrap: List[str]=[],
            icons: List[str]=[],
            parent=None
    ):
        super().__init__(parent)

        assert len(values) == len(labels)

        self._labels = labels
        self._values = values
        self._bootstrap = bootstrap
        self._icons = icons
        self._current_index = 0

    def rowCount(self, parent: QtCore.QModelIndex) -> int:
        return len(self._labels)

    def data(self, index: QtCore.QModelIndex, role: int) -> Any:
        if role not in self.roleNames():
            raise GremlinError(f"Invalid role {role} in LabelValueSelectionModel")

        index = index.row()
        if role == QtCore.Qt.UserRole + 1:
            return self._labels[index]
        elif role == QtCore.Qt.UserRole + 2:
            return str(self._values[index])
        elif role == QtCore.Qt.UserRole + 3:
            return "" if index >= len(self._bootstrap) else self._bootstrap[index]
        elif role == QtCore.Qt.UserRole + 4:
            return "" if index >= len(self._icons) else self._icons[index]

    def roleNames(self) -> Dict:
        return LabelValueSelectionModel.roles

    def _get_current_value(self) -> str:
        return str(self._values[self._current_index])

    def _set_current_value(self, value_str: str) -> None:
        value = value_str
        try:
            index = self._values.index(value)
            if index != self._current_index:
                self._current_index = index
                self.selectionChanged.emit()
        except ValueError as e:
            logging.error(
                f"LabelValueSelectionModel: Attempting to set invalid "
                f"value {value_str}"
            )

    def _get_current_selection_index(self) -> int:
        return self._current_index

    currentValue = Property(
        str,
        fget=_get_current_value,
        fset=_set_current_value,
        notify=selectionChanged
    )

    currentSelectionIndex = Property(
        int,
        fget=_get_current_selection_index,
        notify=selectionChanged
    )