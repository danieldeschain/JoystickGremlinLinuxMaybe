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

"""Main code runner for executing profile callbacks and managing execution."""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

from vjoy.vjoy import VJoyProxy

from gremlin import audio_player, device_helpers, event_handler, macro, \
    mode_manager, profile, sendinput, user_script, util
from gremlin.code_runner_modules.callbacks import CallbackObject

if TYPE_CHECKING:
    pass


class CodeRunner:
    """Runs the actual profile code."""

    def __init__(self):
        """Creates a new code runner instance."""
        self.event_handler = event_handler.EventHandler()
        self.event_handler.add_plugin(user_script.JoystickPlugin())
        self.event_handler.add_plugin(user_script.VJoyPlugin())
        self.event_handler.add_plugin(user_script.KeyboardPlugin())

        self._profile = None
        self._running = False

    def is_running(self) -> bool:
        """Returns whether the code runner is executing code.

        Returns:
            True if code is being executed, False otherwise
        """
        return self._running

    def _determine_start_mode(self, start_mode: str) -> str:
        """Determine the actual start mode based on profile settings.
        
        Args:
            start_mode: Initial start mode
            
        Returns:
            Final start mode to use
        """
        settings = self._profile.settings
        if settings.startup_mode is not None:
            if settings.startup_mode in self._profile.modes.mode_names():
                return settings.startup_mode
        return start_mode

    def _configure_macro_settings(self) -> None:
        """Configure macro action default delay."""
        macro.MacroManager().default_delay = self._profile.settings.default_delay

    def _add_empty_mode_callbacks(self) -> None:
        """Add fake callbacks to empty modes to make them 'present'."""
        for mode_name in self._profile.modes.mode_names():
            self.event_handler.add_callback(
                0,
                mode_name,
                None,
                lambda x: x
            )

    def _register_user_callbacks(self) -> int:
        """Register all user script callbacks.
        
        Returns:
            Number of callbacks registered
        """
        callback_count = 0
        for dev_id, modes in user_script.callback_registry.registry.items():
            for mode, events in modes.items():
                for event, callback_list in events.items():
                    for callback in callback_list.values():
                        self.event_handler.add_callback(
                            dev_id,
                            mode,
                            event,
                            callback
                        )
                        callback_count += 1
        return callback_count

    def _initialize_vjoy_defaults(self) -> None:
        """Set vJoy axis default values from profile settings."""
        for vid, data in self._profile.settings.vjoy_initial_values.items():
            vjoy_proxy = VJoyProxy()[vid]
            for aid, value in data.items():
                vjoy_proxy.axis(linear_index=aid).set_absolute_value(value)

    def _connect_event_listeners(self) -> None:
        """Connect event listener signals to event handler."""
        evt_listener = event_handler.EventListener()
        evt_listener.keyboard_event.connect(
            self.event_handler.process_event
        )
        evt_listener.joystick_event.connect(
            self.event_handler.process_event
        )
        evt_listener.virtual_event.connect(
            self.event_handler.process_event
        )
        evt_listener.gremlin_active = True

    def _start_managers(self, start_mode: str) -> None:
        """Start all managers and switch to initial mode.
        
        Args:
            start_mode: Mode to switch to on startup
        """
        user_script.periodic_registry.start()
        macro.MacroManager().start()
        mode_manager.ModeManager().switch_to(
            mode_manager.Mode(start_mode, "global")
        )
        self.event_handler.resume()
        sendinput.MouseController().start()

    def start(self, profile_instance: profile.Profile, start_mode: str) -> None:
        """Starts listening to events and loads all existing callbacks.

        Args:
            profile_instance: the profile to use when generating all the callbacks
            start_mode: the mode in which to start Gremlin
        """
        self._profile = profile_instance
        self._reset_state()

        # Determine actual start mode
        start_mode = self._determine_start_mode(start_mode)
        self._configure_macro_settings()

        try:
            # Setup user scripts and callbacks
            self._setup_user_scripts()
            self._add_empty_mode_callbacks()
            self._register_user_callbacks()

            # Setup profile actions and inheritance
            self._setup_profile()
            self.event_handler.build_event_lookup(self._profile.modes.mode_list())

            # Initialize hardware and connect listeners
            self._initialize_vjoy_defaults()
            self._connect_event_listeners()

            # Start all managers
            self._start_managers(start_mode)
            self._running = True

        except ImportError as e:
            util.display_error(
                "Unable to launch due to missing user plugin: {}"
                .format(str(e))
            )

    def stop(self):
        """Stops listening to events and unloads all callbacks."""
        # Disconnect all signals
        if self._running:
            evt_lst = event_handler.EventListener()
            evt_lst.keyboard_event.disconnect(self.event_handler.process_event)
            evt_lst.joystick_event.disconnect(self.event_handler.process_event)
            evt_lst.virtual_event.disconnect(self.event_handler.process_event)
            evt_lst.gremlin_active = False
        self._running = False

        # Empty callback registry
        user_script.callback_registry.clear()
        self.event_handler.clear()

        # Stop periodic events and clear registry
        user_script.periodic_registry.stop()
        user_script.periodic_registry.clear()

        macro.MacroManager().stop()
        sendinput.MouseController().stop()

        # Remove all claims on VJoy devices
        VJoyProxy.reset()

        # Remove other possibly long-running aspects
        audio_player.AudioPlayer().stop()

    def _reset_state(self):
        """Resets all states to their default values."""
        self.event_handler._active_mode = self._profile.modes.first_mode
        self.event_handler._previous_mode = self._profile.modes.first_mode
        user_script.callback_registry.clear()
        device_helpers.ButtonReleaseActions().reset()

    def _setup_user_scripts(self):
        """Handles loading and configuring of user scripts."""
        # Retrieve the list of current paths searched by Python
        system_paths = [os.path.normcase(os.path.abspath(p)) for p in sys.path]

        # Populate custom module variable registry <-- nope
        # Update system path for the user scripts
        for script in self._profile.scripts.scripts:
            if not script.is_configured:
                continue

            # Perform system path mangling for import statements
            script_folder = str(script.path.parent)
            if script_folder not in system_paths:
                system_paths.append(script_folder)

            # Ensure script has up to date variable content
            script.reload()

        # Update the system path list searched by Python in order to locate the
        # plugins properly
        sys.path = system_paths

    def _setup_profile(self):
        """Setup profile actions by creating callback objects."""
        # Collect action sequences from physical inputs and intermediate
        # output entries
        item_list = sum(self._profile.inputs.values(), [])
        action_sequences = sum([e.action_sequences for e in item_list], [])

        # Create executable unit for each action
        for action in action_sequences:
            # Event on which to trigger this action
            event = event_handler.Event(
                event_type=action.input_item.input_type,
                device_guid=action.input_item.device_id,
                identifier=action.input_item.input_id,
                mode=action.input_item.mode
            )

            # Generate executable unit for the linked library item
            self.event_handler.add_callback(
                event.device_guid,
                action.input_item.mode,
                event,
                CallbackObject(action)
            )
