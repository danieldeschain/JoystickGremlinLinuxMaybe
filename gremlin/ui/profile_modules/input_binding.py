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

import uuid
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from PySide6 import QtCore, QtQml
from PySide6.QtCore import Property, Signal, Slot

import gremlin.profile
from gremlin.error import GremlinError
from gremlin.plugin_manager import PluginManager
from gremlin.signal import signal
from gremlin.types import InputType, DataInsertionMode
from gremlin.ui.action_model import ActionModel
from gremlin.ui.models import SequenceIndex

if TYPE_CHECKING:
    from action_plugins.root import RootModel
    from gremlin.base_classes import AbstractActionData


class InputItemBindingModel(QtCore.QObject):

    """Model representing an ActionTree instance."""

    behaviorChanged = Signal()
    virtualButtonChanged = Signal()
    rootActionChanged = Signal()
    inputTypeChanged = Signal()

    def __init__(
            self,
            input_item_binding: gremlin.profile.InputItemBinding,
            parent=None
    ):
        super().__init__(parent)

        self._input_item_binding = input_item_binding
        self._virtual_button_model = VirtualButtonModel(
            self._input_item_binding.virtual_button
        )

        self._action_models = {}
        self._index_lookup = {}
        self._child_lookup = {}
        self._container_index_lookup = {}
        self._create_action_models()

    def _create_action_models(self) -> None:
        # Reset storage
        self._action_models = {}
        self._index_lookup = {}
        self._child_lookup = {}
        self._container_index_lookup = {}

        # Initialize action queue
        actions = [(self.root_action, None), ]
        parent_indices = [SequenceIndex(None, None, None),]
        container_indices = [0, ]
        count = 0

        while len(actions) > 0:
            # Grab first item from the queue
            action, container = actions.pop(0)
            parent_index = parent_indices.pop(0)
            container_index = container_indices.pop(0)

            # Create model for the action and store it
            index = SequenceIndex(parent_index.index, container, count)
            model = action.model(action, self, index, parent_index, self)
            self._action_models[index] = model
            self._index_lookup[index.index] = index
            self._container_index_lookup[index] = container_index
            key = (index.parent_index, index.container_name)
            if key not in self._child_lookup:
                self._child_lookup[key] = []
            self._child_lookup[key].append(model)

            # Add all children to the list of items to process
            c_actions, c_containers = action.get_actions()
            c_index = 0
            for i in range(len(c_actions)):
                actions.append((c_actions[i], c_containers[i]))
                parent_indices.append(index)
                if i > 0:
                    if c_containers[i] != c_containers[i-1]:
                        c_index = 0
                container_indices.append(c_index)
                c_index += 1

            count += 1

    def get_child_actions(
            self,
            index: SequenceIndex | int,
            container: str
    ) -> List[ActionModel]:
        if isinstance(index, int):
            index = self._index_lookup[index]
        return self._child_lookup.get((index.index, container), [])

    def get_action_model_by_sidx(self, sidx: int) -> ActionModel:
        if sidx not in self._index_lookup:
            raise GremlinError(f"No action with sequence index {sidx} exists")
        return self._action_models[self._index_lookup[sidx]]

    def get_action_container_index(self, index: SequenceIndex) -> int:
        """Returns the linear index into the container storing the action.

        Args:
            index: sequence index of the action

        Returns:
            Linear index into the container holding the action
        """
        return self._container_index_lookup[index]

    def sync_data(self) -> None:
        self._create_action_models()
        self.rootActionChanged.emit()

    def action_information(self, index: int) -> ActionModel:
        """Returns the action model corresponding to the given index.

        Args:
            index: sequence index of the action to return

        Returns:
            ActionModel corresponding to the given index
        """
        if index not in self._index_lookup:
            raise GremlinError(f"No action with provided index: {index}")
        return self._action_models[self._index_lookup[index]]._data

    def _get_parent_identifiers(self, s_model, t_model):
        """Get parent identifiers for source and target models.
        
        Args:
            s_model: Source action model
            t_model: Target action model
            
        Returns:
            Tuple of (source_parent_id, target_parent_id)
        """
        s_parent_identifier = (
            s_model.sequence_index.parent_index,
            s_model.sequence_index.container_name
        )
        t_parent_identifier = (
            t_model.sequence_index.parent_index,
            t_model.sequence_index.container_name
        )
        return s_parent_identifier, t_parent_identifier

    def _move_to_container(self, s_model, t_model, container):
        """Move source action to specific container of target.
        
        Args:
            s_model: Source action model
            t_model: Target action model
            container: Container name
        """
        self.remove_action(s_model.sequence_index, False)
        self.append_action(
            s_model.action_data,
            t_model.sequence_index,
            container
        )

    def _move_within_same_container(self, s_model, t_model, s_parent_id, t_parent_id):
        """Move action within same container.
        
        Args:
            s_model: Source action model
            t_model: Target action model
            s_parent_id: Source parent identifier
            t_parent_id: Target parent identifier
            
        Returns:
            True if move was performed
        """
        if s_parent_id != t_parent_id:
            return False

        s_lid = self.get_action_container_index(s_model.sequence_index)
        t_lid = self.get_action_container_index(t_model.sequence_index)

        if s_lid < t_lid:
            self.append_action(s_model.action_data, t_model.sequence_index)
            self.remove_action(s_model.sequence_index, False)
            return True
        return False

    def _move_default(self, s_model, t_model):
        """Perform default move operation.
        
        Args:
            s_model: Source action model
            t_model: Target action model
        """
        self.remove_action(s_model.sequence_index, False)
        self.append_action(s_model.action_data, t_model.sequence_index)

    def move_action(
            self,
            source_idx: int,
            target_idx: int,
            container: Optional[str]=None
    ) -> None:
        """Moves the source action to the spot after the target action.

        If a container name is given then the source action will be appended to
        the container with the given name of the target action.

        Args:
            source_idx: sequence index of the action to move
            target_idx: sequence index of the action after which to place the
                moved action
            container: name of the container to insert the action into
        """
        s_model = self.get_action_model_by_sidx(source_idx)
        t_model = self.get_action_model_by_sidx(target_idx)
        s_parent_id, t_parent_id = self._get_parent_identifiers(s_model, t_model)

        if container is not None:
            self._move_to_container(s_model, t_model, container)
        else:
            move_performed = self._move_within_same_container(
                s_model, t_model, s_parent_id, t_parent_id
            )
            if not move_performed:
                self._move_default(s_model, t_model)

        self._create_action_models()
        self.rootActionChanged.emit()

    def remove_action(
            self,
            action_index: int | SequenceIndex,
            perform_sync: bool=True
    ) -> None:
        """Removes the specified action from its parent.

        The provided action_index can be either a SequenceIndex instance or an
        integer corresponding to the unique index of the action.

        Args:
            action_index: index identifying the action to remove
            perform_sync: if True data will be resynchronized and a change
                event emitted
        """
        if isinstance(action_index, int):
            action_index = self._index_lookup[action_index]

        parent_data = \
            self.get_action_model_by_sidx(action_index.parent_index).action_data
        parent_data.remove_action(
            self.get_action_container_index(action_index),
            action_index.container_name
        )

        if perform_sync:
            self._create_action_models()
            self.rootActionChanged.emit()

    def append_action(
            self,
            action_data: AbstractActionData,
            target_index: SequenceIndex,
            container: Optional[str]=None
    ) -> None:
        """Appends the provided action data after the specified action.

        Args:
            action_data: data of the action to append
            target_index: sequence index of the action after which to insert
                the new action's data
        """
        # If the parent index of the target is None the target is the single
        # RootAction and thus should be used to insert into directly.
        if target_index.parent_index is None:
            data = self.get_action_model_by_sidx(target_index.index).action_data
            data.insert_action(
                action_data,
                "children",
                DataInsertionMode.Prepend,
                0
            )
        elif container is None:
            parent_data = self.get_action_model_by_sidx(
                target_index.parent_index
            ).action_data
            parent_data.insert_action(
                action_data,
                target_index.container_name,
                DataInsertionMode.Append,
                self.get_action_container_index(target_index)
            )
        else:
            target_data = self.get_action_model_by_sidx(
                target_index.index
            ).action_data
            target_data.insert_action(
                action_data,
                container,
                DataInsertionMode.Prepend,
                0
            )

    def is_last_action_in_container(self, index: SequenceIndex) -> bool:
        """Returns whether the specified action is the last one in a container.

        Args:
            index: SequenceIndex corresponding to an action

        Returns:
            True if the specified action is the last one in its container, False
            otherwise.
        """
        indices = sorted([
            self._container_index_lookup[m.sequence_index]
            for m in self.get_child_actions(
                index.parent_index,
                index.container_name
            )
        ])
        return self._container_index_lookup[index] >= indices[-1]


    @Property(type=str, notify=inputTypeChanged)
    def inputType(self) -> str:
        return InputType.to_string(
            self._input_item_binding.input_item.input_type
        )

    @Property(type=VirtualButtonModel, notify=virtualButtonChanged)
    def virtualButton(self) -> VirtualButtonModel:
        return self._virtual_button_model

    @Property(type=ActionModel, notify=rootActionChanged)
    def rootAction(self) -> RootModel:
        return self._action_models[self._index_lookup[0]]

    @property
    def root_action(self) -> AbstractActionData:
        return self._input_item_binding.root_action

    @property
    def input_item_binding(self) -> gremlin.profile.InputItemBinding:
        return self._input_item_binding

    def _get_behavior(self) -> str:
        return InputType.to_string(self._input_item_binding.behavior)

    def _set_behavior(self, text: str) -> None:
        behavior = InputType.to_enum(text)
        if behavior != self._input_item_binding.behavior:
            self._input_item_binding.behavior = behavior
            self._input_item_binding.virtual_button = None

            # Ensure a virtual button instance exists of the correct type
            # if one is needed
            input_type = self._input_item_binding.input_item.input_type
            if input_type == InputType.JoystickAxis and \
                    behavior == InputType.JoystickButton:
                if not isinstance(
                        self._input_item_binding.virtual_button,
                        gremlin.profile.VirtualAxisButton
                ):
                    self._input_item_binding.virtual_button = \
                        gremlin.profile.VirtualAxisButton()
                    self._virtual_button_model = VirtualButtonModel(
                        self._input_item_binding.virtual_button
                    )
            elif input_type == InputType.JoystickHat and \
                    behavior == InputType.JoystickButton:
                if not isinstance(
                        self._input_item_binding.virtual_button,
                        gremlin.profile.VirtualHatButton
                ):
                    self._input_item_binding.virtual_button = \
                        gremlin.profile.VirtualHatButton()
                    self._virtual_button_model = VirtualButtonModel(
                        self._input_item_binding.virtual_button
                    )

            # Update input type of all actions
            for model in self._action_models.values():
                model.action_data.set_behavior_type(behavior)

            # Force full redraw of the action
            self.behaviorChanged.emit()
            self.rootActionChanged.emit()
            # This one might be overkill
            signal.reloadUi.emit()

    @property
    def behavior_type(self):
        return self._input_item_binding.behavior

    behavior = Property(
        str,
        fget=_get_behavior,
        fset=_set_behavior,
        notify=behaviorChanged
    )




@QtQml.QmlElement

