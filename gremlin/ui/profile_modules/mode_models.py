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

from typing import List, Optional

from PySide6 import QtCore
from PySide6.QtCore import Slot

import gremlin.profile


class ModeListModel(QtCore.QAbstractListModel):

    """List containing model instances for each mode."""

    roles = {
        QtCore.Qt.UserRole + 1: QtCore.QByteArray("name".encode()),
        QtCore.Qt.UserRole + 2: QtCore.QByteArray("parentName".encode()),
        QtCore.Qt.UserRole + 3: QtCore.QByteArray("depth".encode()),
    }

    def __init__(self, modes: gremlin.profile.ModeHierarchy, parent=None):
        super().__init__(parent)

        self._modes = modes
        self._lookup = {}
        self._names = []
        for mode in self._modes.mode_list():
            self._names.append(mode.value)
            self._lookup[mode.value] = mode
        self._names = sorted(self._names)

    def rowCount(self, parent: QtCore.QModelIndex) -> int:
        return len(self._lookup)

    def data(self, index: QtCore.QModelIndex, role: int=...) -> Any:
        if role not in self.roleNames():
            raise GremlinError(f"Invalid role {role} in ModeListModel")

        node = self._lookup[self._names[index.row()]]
        if role == QtCore.Qt.UserRole + 1:
            return node.value
        elif role == QtCore.Qt.UserRole + 2:
            if node.parent is None:
                return ""
            else:
                return node.parent.value
        elif role == QtCore.Qt.UserRole + 3:
            return node.depth

    def roleNames(self) -> Dict:
        return ModeListModel.roles


@QtQml.QmlElement
class ModeHierarchyModel(QtCore.QAbstractListModel):

    """Model exposing the mode hierarchy and allows managing it."""

    modesChanged = Signal()

    def __init__(self, modes: gremlin.profile.ModeHierarchy, parent=None):
        super().__init__(parent)

        self._modes = modes

    @Property(type=ModeListModel, notify=modesChanged)
    def modeList(self) -> ModeListModel:
        return ModeListModel(self._modes, self)

    @Slot(str)
    def newMode(self, name: str) -> None:
        if not self._modes.mode_exists(name):
            self._modes.add_mode(name)
        self.modesChanged.emit()

    @Slot(str, str)
    def renameMode(self, old_name: str, new_name: str) -> None:
        if old_name != new_name:
            self._modes.rename_mode(old_name, new_name)
            self.modesChanged.emit()

    @Slot(str)
    def deleteMode(self, name: str) -> None:
        self._modes.delete_mode(name)
        self.modesChanged.emit()

    @Slot(str, str)
    def setParent(self, mode_name: str, parent_name: str) -> None:
        node = self._modes.find_mode(mode_name)
        if parent_name != node.parent.value:
            self._modes.set_parent(mode_name, parent_name)
            self.modesChanged.emit()

    @Slot(str, result=list)
    def validParents(self, name: str) -> List[str]:
        options = [{"value": ""}]
        for entry in self._modes.valid_parents(name):
            options.append({"value": entry})
        return options

    @Slot(result=list)
    def modeStringList(self) -> List[str]:
        return self._modes.mode_names()


@QtQml.QmlElement
