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

"""Virtual button classes for treating axis and hat inputs as buttons."""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import List, TYPE_CHECKING

from gremlin import event_handler, fsm
from gremlin.types import AxisButtonDirection, HatDirection

if TYPE_CHECKING:
    pass


class VirtualButton(metaclass=ABCMeta):
    """Implements a button like interface."""

    def __init__(self):
        """Creates a new instance."""
        self._fsm = self._initialize_fsm()

    def _initialize_fsm(self):
        """Initializes the state of the button FSM."""
        states = ["up", "down"]
        actions = ["press", "release"]
        transitions = {
            ("up", "press"): fsm.Transition([self._press], "down"),
            ("up", "release"): fsm.Transition([self._noop], "up"),
            ("down", "release"): fsm.Transition([self._release], "up"),
            ("down", "press"): fsm.Transition([self._noop], "down")
        }
        return fsm.FiniteStateMachine("up", states, actions, transitions)

    @abstractmethod
    def __call__(self, event: event_handler.Event) -> List[bool]:
        """Process the input event and updates the value as needed.

        Args:
            event: The input event to process

        Returns:
            List of states to process
        """
        pass

    def _press(self) -> bool:
        """Executes the "press" action."""
        return True

    def _release(self) -> bool:
        """Executes the "release" action."""
        return True

    def _noop(self) -> bool:
        """Performs "noop" action."""
        return False


class VirtualAxisButton(VirtualButton):
    """Treats axis positions as button presses."""

    def __init__(
            self,
            lower_limit: float,
            upper_limit: float,
            direction: AxisButtonDirection
    ):
        super().__init__()
        self._lower_limit = lower_limit
        self._upper_limit = upper_limit
        self._direction = direction
        self._last_value = None

    def __call__(self, event: event_handler.Event) -> List[bool]:
        forced_activation = False
        direction = AxisButtonDirection.Anywhere
        if self._last_value is None:
            self._last_value = event.value
        else:
            # Check if we moved over the activation region between two
            # consecutive measurements
            if self._last_value < self._lower_limit and \
                    event.value > self._upper_limit:
                forced_activation = True
            elif self._last_value > self._upper_limit and \
                    event.value < self._lower_limit:
                forced_activation = True

            # Determine direction in which the axis is moving
            if self._last_value < event.value:
                direction = AxisButtonDirection.Below
            elif self._last_value > event.value:
                direction = AxisButtonDirection.Above

        self._last_value = event.value

        # If the input moved across the activation an activation will be
        # emitted as a single pulse.
        states = []
        if forced_activation:
            self._fsm.perform("press")
            self._fsm.perform("release")
            states = [True, False]
        inside_range = self._lower_limit <= event.value <= self._upper_limit
        valid_direction = direction == self._direction or \
            self._direction == AxisButtonDirection.Anywhere
        if inside_range and valid_direction:
            states = [True] if self._fsm.perform("press") else []
        else:
            states = [False] if self._fsm.perform("release") else []

        return states


class VirtualHatButton(VirtualButton):
    """Treats directional hat events as a button."""

    def __init__(self, directions):
        super().__init__()
        self._directions = directions

    def __call__(self, event: event_handler.Event) -> List[bool]:
        is_pressed = HatDirection.to_enum(event.value) in self._directions
        action = "press" if is_pressed else "release"
        has_changed = self._fsm.perform(action)
        return [is_pressed] if has_changed else []


class VirtualButtonFunctor:
    """Functor that emits virtual button events based on physical inputs."""

    def __init__(
        self,
        virtual_button: VirtualButton,
        event_template: event_handler.Event
    ):
        self._virtual_button = virtual_button
        self._event_template = event_template
        self._event_listener = event_handler.EventListener()

    def __call__(self, event: event_handler.Event, value) -> None:
        """Process event and emit virtual button events.
        
        Args:
            event: Input event to process
            value: Value object (unused but required for callback signature)
        """
        states = self._virtual_button(event)
        for state in states:
            new_event = self._event_template.clone()
            new_event.is_pressed = state
            new_event.raw_value = state
            self._event_listener.virtual_event.emit(new_event)
