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

"""Macro manager for scheduling and dispatching macro execution."""

from __future__ import annotations

import collections
import functools
import logging
import time
from threading import Event, Lock, Thread

from gremlin.common import SingletonDecorator
from gremlin.config import Configuration

# Import repeat classes for type checking
# These will be imported from macro_modules.repeat after extraction
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gremlin.macro_modules.macro import Macro
    from gremlin.macro_modules.repeat import CountRepeat, HoldRepeat, ToggleRepeat
    from gremlin.macro_modules.actions import PauseAction

MacroEntry = collections.namedtuple(
    "MacroEntry",
    ["macro", "state"]
)


@SingletonDecorator
class MacroManager:
    """Manages the proper dispatching and scheduling of macros."""

    def __init__(self):
        """Initializes the instance."""
        self._active = {}
        self._queue = []
        self._flags = {}
        self._flags_lock = Lock()
        self._queue_lock = Lock()

        # Default delay between subsequent message dispatch. This is to get
        # around some games not picking up messages if they are sent in too
        # quick a succession.
        self.default_delay = Configuration().value(
           "action", "macro", "default-delay"
        )

        self._is_executing_exclusive = False
        self._is_running = False
        self._schedule_event = Event()

        self._run_scheduler_thread = None

    def start(self) -> None:
        """Starts the scheduler."""
        self._active = {}
        self._flags = {}
        self._is_running = True
        if self._run_scheduler_thread is None:
            self._run_scheduler_thread = Thread(target=self._run_scheduler)
        if not self._run_scheduler_thread.is_alive():
            self._run_scheduler_thread.start()

    def stop(self) -> None:
        """Stops the scheduler."""
        self._is_running = False
        if self._run_scheduler_thread is not None and \
                self._run_scheduler_thread.is_alive():

            # Terminate the scheduler
            self._schedule_event.set()
            self._run_scheduler_thread.join()
            self._run_scheduler_thread = None

            # Terminate any macro that is still active
            with self._flags_lock:
                for key in self._flags:
                    self._flags[key] = False

    def queue_macro(self, macro: Macro) -> None:
        """Queues a macro in the schedule taking the repeat type into account.

        Args:
            macro: the macro to add to the scheduler
        """
        # Import here to avoid circular dependency
        from gremlin.macro_modules.repeat import ToggleRepeat
        
        if isinstance(macro.repeat, ToggleRepeat) and macro.id in self._active:
            self.terminate_macro(macro)
        else:
            # Preprocess macro to contain pauses as necessary
            self._preprocess_macro(macro)
            with self._queue_lock:
                self._queue.append(MacroEntry(macro, True))
            self._schedule_event.set()

    def terminate_macro(self, macro: Macro) -> None:
        """Adds a termination request for a macro to the execution queue.

        Args:
            macro: the macro to terminate
        """
        self._queue.append(MacroEntry(macro, False))
        self._schedule_event.set()

    def _run_scheduler(self) -> None:
        """Dispatches macros as required."""
        while self._is_running:
            # Wake up when the event triggers and reset it
            self._schedule_event.wait()
            self._schedule_event.clear()

            # Run scheduled macros and ensure exclusive ones run separately
            # from all other macros
            with self._queue_lock:
                entries_to_remove = []
                has_exclusive = False
                for entry in self._queue:
                    # Terminate macro if needed
                    if entry.state is False:
                        if entry.macro.id in self._flags \
                                and self._flags[entry.macro.id]:
                            # Terminate currently running macro
                            with self._flags_lock:
                                self._flags[entry.macro.id] = False

                            # Remove all queued up macros with the same id as
                            # they should have been impossible to queue up
                            # in the first place
                            removal_list = []
                            for queue_entry in self._queue:
                                if queue_entry.macro.id == entry.macro.id:
                                    removal_list.append(queue_entry)
                            for queue_entry in removal_list:
                                self._queue.remove(queue_entry)
                    # Don't run a queued macro if the same instance is already
                    # running
                    elif entry.macro.id in self._active:
                        continue
                    # Handle exclusive macros
                    elif entry.macro.is_exclusive:
                        has_exclusive = True
                        if len(self._active) == 0:
                            self._dispatch_macro(entry.macro)
                            self._is_executing_exclusive = True
                            entries_to_remove.append(entry)
                    # Start a queued up macro
                    elif not has_exclusive and not self._is_executing_exclusive:
                        self._dispatch_macro(entry.macro)
                        entries_to_remove.append(entry)

                # Remove all entries we've processed
                for entry in entries_to_remove:
                    if entry in self._queue:
                        self._queue.remove(entry)

    def _dispatch_macro(self, macro: Macro) -> None:
        """Dispatches a single macro to be run.

        Args:
            macro: the macro to dispatch
        """
        if macro.id not in self._active:
            self._active[macro.id] = macro
            Thread(target=functools.partial(self._execute_macro, macro)).start()
        else:
            logging.getLogger("system").warning(
                "Attempting to dispatch an already running macro"
            )

    def _execute_macro(self, macro: Macro) -> None:
        """Executes a given macro in a separate thread.

        This method will run all provided actions and once they all have been
        executed will remove the macro from the set of active macros and
        inform the scheduler of the completion.

        Args:
            macro: the macro object to be executed
        """
        # Import here to avoid circular dependency
        from gremlin.macro_modules.repeat import CountRepeat, HoldRepeat, ToggleRepeat
        
        # Handle macros with a repeat mode
        if macro.repeat is not None:
            delay = macro.repeat.delay

            with self._flags_lock:
                self._flags[macro.id] = True

            # Handle count repeat mode
            if isinstance(macro.repeat, CountRepeat):
                count = 0
                while count < macro.repeat.count and self._flags[macro.id]:
                    for action in macro.sequence:
                        action()
                    count += 1
                    time.sleep(delay)

            # Handle continuous repeat modes
            elif type(macro.repeat) in [HoldRepeat, ToggleRepeat]:
                while self._flags.get(macro.id, False):
                    for action in macro.sequence:
                        action()
                    time.sleep(delay)

        # Handle simple one shot macros
        else:
            for action in macro.sequence:
                action()

        # Remove macro from active set, notify manager, and remove any
        # potential callbacks
        del self._active[macro.id]
        if macro.is_exclusive:
            self._is_executing_exclusive = False
        with self._flags_lock:
            if macro.id in self._flags:
                self._flags[macro.id] = False
        self._schedule_event.set()

    def _preprocess_macro(self, macro: Macro) -> None:
        """Inserts pauses as necessary into the macro.

        Args:
            macro: the macro instance to modify
        """
        # Import here to avoid circular dependency
        from gremlin.macro_modules.actions import PauseAction
        
        new_sequence = [macro.sequence[0]]
        for a1, a2 in zip(macro.sequence[:-1], macro.sequence[1:]):
            if isinstance(a1, PauseAction) or isinstance(a2, PauseAction):
                new_sequence.append(a2)
            else:
                new_sequence.append(PauseAction(self.default_delay))
                new_sequence.append(a2)
        macro._sequence = new_sequence
