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

"""Callback object for executing actions in response to input events."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import dill

from gremlin import error, event_handler, mode_manager, profile
from gremlin.base_classes import Value
from gremlin.types import ActionProperty, InputType

if TYPE_CHECKING:
    from gremlin.code_runner_modules.virtual_buttons import VirtualButtonFunctor


class CallbackObject:
    """Represents the callback executed in reaction to an input."""

    c_next_virtual_identifier = 1

    def __init__(self, binding: profile.InputItemBinding):
        """Creates a new callback instance for a specific input item.

        Args:
            binding: actions bound to a single input item
        """
        self._binding = binding
        self._functor = None
        self._virtual_identifier = 0

        # Differentiate between bindings utilizing virtual buttons and those
        # that react to raw physical inputs
        if self._binding.virtual_button is not None:
            self._virtual_identifier = CallbackObject.c_next_virtual_identifier
            CallbackObject.c_next_virtual_identifier += 1
            self._virtual_event_setup()
        else:
            self._physical_event_setup()

    @property
    def always_execute(self) -> bool:
        """Returns True if the callback should be executed even when Gremlin
        is paused.

        Returns:
            True if the callback is to be always executed
        """
        actions = self._binding.root_action.get_actions()[0]
        values = [
            ActionProperty.AlwaysExecute in a.properties for a in actions
        ]
        return any(values)

    def __call__(self, event: event_handler.Event) -> None:
        """Execute callback with given event.
        
        Args:
            event: Input event triggering the callback
        """
        values = self._generate_values(event)
        for i, value in enumerate(values):
            self._functor(event, value)

            # Pause between the execution of subsequent bindings
            if i < len(values)-1:
                time.sleep(0.05)

    def _physical_event_setup(self) -> None:
        """Configures the callback object for traditional physical events."""
        self._functor = self._binding.root_action.functor(
            self._binding.root_action
        )

    def _create_virtual_event_template(self) -> event_handler.Event:
        """Create template virtual event for button handling.
        
        Returns:
            Template virtual event
        """
        return event_handler.Event(
            event_type=InputType.VirtualButton,
            identifier=self._virtual_identifier,
            device_guid=dill.GUID_Virtual,
            mode=mode_manager.ModeManager().current.name,
            is_pressed=False,
            raw_value=False
        )

    def _create_virtual_button_functor(
        self,
        vb_instance,
        virtual_event: event_handler.Event
    ) -> VirtualButtonFunctor:
        """Create functor for virtual button based on instance type.
        
        Args:
            vb_instance: Virtual button profile instance
            virtual_event: Virtual event template
            
        Returns:
            VirtualButtonFunctor for the button type
            
        Raises:
            GremlinError: If virtual button is not configured
        """
        from gremlin.code_runner_modules.virtual_buttons import (
            VirtualAxisButton,
            VirtualHatButton,
            VirtualButtonFunctor
        )
        
        if isinstance(vb_instance, profile.VirtualAxisButton):
            return VirtualButtonFunctor(
                VirtualAxisButton(
                    vb_instance.lower_limit,
                    vb_instance.upper_limit,
                    vb_instance.direction
                ),
                virtual_event
            )
        elif isinstance(vb_instance, profile.VirtualHatButton):
            return VirtualButtonFunctor(
                VirtualHatButton(vb_instance.directions),
                virtual_event
            )
        else:
            raise error.GremlinError(
                "Attempting to create virtual event setup when no virtual " +
                "button is configured."
            )

    def _create_virtual_input_item(self) -> profile.InputItem:
        """Create virtual InputItem for button event handling.
        
        Returns:
            Virtual InputItem instance
        """
        virt_item = profile.InputItem(self._binding.input_item.library)
        virt_item.device_id = dill.GUID_Virtual
        virt_item.input_type = InputType.VirtualButton
        virt_item.input_id = self._virtual_identifier
        virt_item.mode = self._binding.input_item.mode
        virt_item.action_sequences = [self._binding]
        virt_item.is_active = self._binding.input_item.is_active
        return virt_item

    def _create_virtual_binding(
        self,
        virt_item: profile.InputItem
    ) -> profile.InputItemBinding:
        """Create virtual InputItemBinding mirroring the original.
        
        Args:
            virt_item: Virtual input item
            
        Returns:
            Virtual InputItemBinding instance
        """
        virt_binding = profile.InputItemBinding(virt_item)
        virt_binding.root_action = self._binding.root_action
        virt_binding.behavior = InputType.JoystickButton
        virt_binding.virtual_button = None
        return virt_binding

    def _register_virtual_callback(
        self,
        virt_binding: profile.InputItemBinding,
        virtual_event: event_handler.Event
    ) -> None:
        """Register callback for virtual button event.
        
        Args:
            virt_binding: Virtual binding instance
            virtual_event: Virtual event template
        """
        eh = event_handler.EventHandler()
        eh.add_callback(
            dill.GUID_Virtual,
            self._binding.input_item.mode,
            virtual_event,
            CallbackObject(virt_binding)
        )

    def _virtual_event_setup(self) -> None:
        """Configures the callback object for virtual button handling.

        This creates callbacks that emit virtual button events in reaction to
        the input items physical events. The actions bound to the input item
        in turn will trigger in response to the emitted virtual events.
        """
        # Create template and functor
        virtual_event = self._create_virtual_event_template()
        vb_instance = self._binding.virtual_button
        self._functor = self._create_virtual_button_functor(vb_instance, virtual_event)

        # Create virtual item and binding
        virt_item = self._create_virtual_input_item()
        virt_binding = self._create_virtual_binding(virt_item)

        # Register callback for virtual events
        self._register_virtual_callback(virt_binding, virtual_event)

    def _generate_values(self, event: event_handler.Event) -> list:
        """Generate value objects from event.
        
        Args:
            event: Input event
            
        Returns:
            List of Value objects
            
        Raises:
            GremlinError: If event type is invalid
        """
        if event.event_type in [InputType.JoystickAxis, InputType.JoystickHat]:
            value = Value(event.value)
        elif event.event_type in [
            InputType.JoystickButton,
            InputType.Keyboard,
            InputType.VirtualButton
        ]:
            value = Value(event.is_pressed)
        else:
            raise error.GremlinError("Invalid event type")

        return [value]
