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



from __future__ import annotations

import heapq
import threading
import time
from typing import Any, Callable, Dict
import uuid

from gremlin import error


class CallbackRegistry:

    """Registry of all callbacks known to the system."""

    def __init__(self):
        """Creates a new callback registry instance."""
        self._registry = {}
        self._current_id = 0

    def add(
            self,
            callback: Callable,
            event: event_handler.Event,
            mode: str
    ) -> None:
        """Adds a new callback to the registry.

        Args:
            callback: function to add as a callback
            event: the event on which to trigger the callback
            mode: the mode in which to trigger the callback
        """
        self._current_id += 1
        function_name = "{}_{:d}".format(callback.__name__, self._current_id)

        if event.device_guid not in self._registry:
            self._registry[event.device_guid] = {}
        if mode not in self._registry[event.device_guid]:
            self._registry[event.device_guid][mode] = {}
        if event not in self._registry[event.device_guid][mode]:
            self._registry[event.device_guid][mode][event] = {}

        self._registry[event.device_guid][mode][event][function_name] = callback

    @property
    def registry(self) -> dict:
        """Returns the registry dictionary.

        Returns:
            The callback registry dictionary
        """
        return self._registry

    def clear(self) -> None:
        """Clears the registry entries."""
        self._registry = {}


class PeriodicRegistry:
\n\nclass PeriodicRegistry:

    """Registry for periodically executed functions."""

    def __init__(self):
        """Creates a new instance."""
        self._registry = {}
        self._running = False
        self._thread = threading.Thread(target=self._thread_loop)
        self._queue = []
        self._plugins = []

    def start(self) -> None:
        """Starts the event loop."""
        # Only proceed if we have functions to call
        if len(self._registry) == 0:
            return

        # Only create a new thread and start it if the thread is not
        # currently running
        self._running = True
        if not self._thread.is_alive():
            self._thread = threading.Thread(target=self._thread_loop)
            self._thread.start()

    def stop(self) -> None:
        """Stops the event loop."""
        self._running = False
        if self._thread.is_alive():
            self._thread.join()

    def add(self, callback: Callable, interval: float) -> None:
        """Adds a function to execute periodically.

        Args:
            callback: the function to execute
            interval: the time in seconds between executions
        """
        self._registry[callback] = (interval, callback)

    def clear(self) -> None:
        """Clears the registry."""
        self._registry = {}

    def _install_plugins(self, callback: Callable) -> Callable:
        """Installs the current plugins into the given callback.

        Args:
            callback: the callback function to install the plugins into

        Returns:
            new callback with plugins installed
        """
        signature = inspect.signature(callback).parameters
        partial_fn = functools.partial
        if "self" in signature:
            partial_fn = functools.partialmethod
        for plugin in self._plugins:
            if plugin.keyword in signature:
                callback = plugin.install(callback, partial_fn)
        return callback

    def _thread_loop(self) -> None:
        """Main execution loop run in a separate thread."""
        # Setup plugins to use
        self._plugins = [
            JoystickPlugin(),
            VJoyPlugin(),
            KeyboardPlugin()
        ]
        callback_map = {}

        # Populate the queue
        self._queue = []
        for item in self._registry.values():
            plugin_cb = self._install_plugins(item[1])
            callback_map[plugin_cb] = item[0]
            heapq.heappush(
                self._queue,
                (time.time() + callback_map[plugin_cb], plugin_cb)
            )

        # Main thread loop
        while self._running:
            # Process all events that require running
            while self._queue[0][0] < time.time():
                item = heapq.heappop(self._queue)
                item[1]()

                heapq.heappush(
                    self._queue,
                    (time.time() + callback_map[item[1]], item[1])
                )

            # Sleep until either the next function needs to be run or
            # our timeout expires
            time.sleep(min(self._queue[0][0] - time.time(), 1.0))


callback_registry = CallbackRegistry()
periodic_registry = PeriodicRegistry()


class JoystickDecorator:
\n\nclass ScriptVariableRegistry:

    def __init__(self):
        self._registry = {}

    def clear(self):
        """Clears all registry entries."""
        self._registry = {}

    def register_script(self, script: Script) -> None:
        """Registers all variables of a script.

        This will forcibly overwrite existing entries for the same script.

        Args:
            script: the Script instance to register
        """
        self._registry[script.id] = {}
        for variable in script.variables.values():
            self._registry[script.id][variable.name] = variable

    def remove_script(self, script: Script) -> None:
        """Removes the specified script's variables.

        Args:
            script: the script to remove variables for
        """
        if script.id in self._registry:
            del self._registry[script.id]

    def set(self, script_id: uuid.UUID, variable: AbstractVariable) -> None:
        """Stores a variable in the registry.

        Args:
            script_id: unique identifier of the script
            variable: the variable to register
        """
        if script_id not in self._registry:
            self._registry[script_id] = {}
        self._registry[script_id][variable.name] = variable

    def get(self, script_id: uuid.UUID, name: str) -> AbstractVariable|None:
        """Returns a variable from the registry.

        Args:
            script_id: unique identifier of the script
            name: the name of the variable to retrieve

        Returns:
            Variable instance corresponding to the script and name
        """
        if script_id not in self._registry:
            return None
        return self._registry[script_id].get(name, None)


class Script:
