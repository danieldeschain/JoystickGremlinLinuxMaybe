# -*- coding: utf-8; -*-

# Copyright (C) 2015 Lionel Ott
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

"""Macro container class representing a sequence of actions."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

import gremlin.error
from gremlin.base_classes import AbstractActionData
from gremlin.keyboard import key_from_name, Key

if TYPE_CHECKING:
    from gremlin.macro_modules.actions import KeyAction, PauseAction
    from gremlin.macro_modules.repeat import AbstractRepeat


class Macro:
    """Represents a macro which can be executed."""

    # Unique identifier for each macro
    _next_macro_id = 0

    def __init__(self):
        """Creates a new macro instance."""
        self._sequence = []
        self._id = Macro._next_macro_id
        Macro._next_macro_id += 1
        self.repeat = None
        self.is_exclusive = False

    @property
    def id(self) -> int:
        """Returns the unique id of this macro.

        Returns:
            unique id of this macro
        """
        return self._id

    @property
    def sequence(self) -> List[AbstractActionData]:
        """Returns the action sequence of this macro.

        Returns:
            Sequence of actions comprising the macro
        """
        return self._sequence

    def add_action(self, action: AbstractActionData) -> None:
        """Adds an action to the list of actions to perform.

        Args:
            action: the action to add
        """
        self._sequence.append(action)

    def pause(self, duration: float) -> None:
        """Adds a pause of the given duration to the macro.

        Args:
            duration: the duration of the pause in seconds
        """
        from gremlin.macro_modules.actions import PauseAction
        self._sequence.append(PauseAction(duration))

    def press(self, key: Key) -> None:
        """Presses the specified key down.

        Args:
            key: the key to press
        """
        self.action(key, True)

    def release(self, key: Key) -> None:
        """Releases the specified key.

        Args:
            key; the key to release
        """
        self.action(key, False)

    def tap(self, key: Key) -> None:
        """Taps the specified key.

        Args:
            key: the key to tap
        """
        self.action(key, True)
        self.action(key, False)

    def action(self, key: Key | str, is_pressed: bool) -> None:
        """Adds the specified action to the sequence.

        Args:
            key: the key involved in the action
            is_pressed: boolean indicating if the key is pressed
                (True) or released (False)
        """
        from gremlin.macro_modules.actions import KeyAction
        
        if isinstance(key, str):
            key = key_from_name(key)
        elif isinstance(key, Key):
            pass
        else:
            raise gremlin.error.KeyboardError("Invalid key specified")

        self._sequence.append(KeyAction(key, is_pressed))
