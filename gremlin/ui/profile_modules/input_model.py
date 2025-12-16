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

from typing import Optional

from PySide6 import QtCore

import gremlin.profile


class InputItemModel(QtCore.QAbstractListModel):

    """QML model class representing an InputItem instance and acting as a
    model to display the individual InputItemBindingModel instances.
    """

    # This fake single role and the roleName function are needed to have the
    # modelData property available in the QML delegate
    roles = {
        QtCore.Qt.UserRole + 1: QtCore.QByteArray("fake".encode()),
    }

    bindingsChanged = Signal()

    def __init__(
        self,
        input_item: gremlin.profile.InputItem,
        enumeration_index: int,
        parent=None
    ):
        """Exposes the list of all action sequences to the UI.

        Args:
            input_item: Profile InputItem instance to expose
            enumeration_index: Linear index reflecting the position in the
                list of device inputs
            parent: Widget to which this model is parented to
        """
        super().__init__(parent)

        self._input_item = input_item
        self._enumeration_index = enumeration_index

    @property
    def enumeration_index(self) -> int:
        return self._enumeration_index

    @Slot()
    def newActionSequence(self) -> None:
        # Create root action for the new action sqeuence
        action = PluginManager().create_instance(
            "Root",
            self._input_item.input_type
        )

        # Create binding instance and add it to the input item
        binding = gremlin.profile.InputItemBinding(self._input_item)
        binding.root_action = action
        binding.behavior = self._input_item.input_type

        self.beginInsertRows(
            QtCore.QModelIndex(),
            self.rowCount(),
            self.rowCount()
        )
        self._input_item.action_sequences.append(binding)
        self.endInsertRows()
        signal.inputItemChanged.emit(self._enumeration_index)

    @Slot(InputItemBindingModel)
    def deleteActionSequnce(self, binding: InputItemBindingModel) -> None:
        try:
            index = self._input_item.action_sequences.index(
                binding.input_item_binding
            )
            self.beginRemoveRows(QtCore.QModelIndex(), index, index)
            self._input_item.remove_item_binding(binding.input_item_binding)
            self.endRemoveRows()
            signal.inputItemChanged.emit(self._enumeration_index)
        except ValueError:
            pass

    @Slot(str, str, str)
    def dropAction(self, source: str, target: str, method: str) -> None:
        """Handles dropping an action tree element

        Args:
            source: identifier of the tree being dropped
            target: identifier of the location on which the source is dropped
            method: type of drop action to perform
        """
        # Force a UI refresh without performing any model changes if both
        # source and target item are identical, i.e. an invalid drag&drop
        if source == target:
            self.bindingsChanged.emit()
            return

        source_id = uuid.UUID(source)
        target_id = uuid.UUID(target)
        source_entry = None
        for idx, entry in enumerate(self._input_item.action_sequences):
            if entry.root_action.id == source_id:
                source_entry = self._input_item.action_sequences.pop(idx)
        if source_entry is not None:
            for idx, entry in enumerate(self._input_item.action_sequences):
                if entry.root_action.id == target_id:
                    self._input_item.action_sequences.insert(idx+1, source_entry)

        self.bindingsChanged.emit()

    def rowCount(self, parent: QtCore.QModelIndex=...) -> int:
        return len(self._input_item.action_sequences)

    def data(self, index: QtCore.QModelIndex, role: int=...) -> Any:
        return InputItemBindingModel(
            self._input_item.action_sequences[index.row()],
            parent=self
        )

    def roleNames(self) -> Dict:
        return InputItemModel.roles


@QtQml.QmlElement
