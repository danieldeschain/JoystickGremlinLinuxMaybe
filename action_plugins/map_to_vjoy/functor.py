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

"""MapToVjoy functor for runtime execution."""

from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING

from vjoy.vjoy import VJoyProxy

from gremlin import device_helpers, error, util
from gremlin.base_classes import AbstractFunctor, Value
from gremlin.types import ActionProperty, AxisMode, InputType

if TYPE_CHECKING:
    from action_plugins.map_to_vjoy.data import MapToVjoyData
    from gremlin.event_handler import Event


class MapToVjoyFunctor(AbstractFunctor):
    """Executes a map to vjoy action when called."""

    def __init__(self, action: MapToVjoyData):
        super().__init__(action)

        self.needs_auto_release = False
        self.thread_running = False
        self.should_stop_thread = False
        self.thread_last_update = time.time()
        self.thread = None
        self.axis_delta_value = 0.0
        self.axis_value = 0.0

    def __call__(
            self,
            event: Event,
            value: Value,
            properties: list[ActionProperty]=[]
    ) -> None:
        if not self._should_execute(value):
            return

        if self.data.vjoy_input_type == InputType.JoystickAxis:
            if self.data.axis_mode == AxisMode.Absolute:
                VJoyProxy()[self.data.vjoy_device_id] \
                    .axis(self.data.vjoy_input_id).value = value.current
            else:
                self.should_stop_thread = abs(event.value) < 0.05
                self.axis_delta_value = \
                    value.current * (self.data.axis_scaling / 1000.0)
                self.thread_last_update = time.time()
                if self.thread_running is False:
                    if isinstance(self.thread, threading.Thread):
                        self.thread.join()
                    self.thread = threading.Thread(
                        target=self.relative_axis_thread
                    )
                    self.thread.start()

        elif self.data.vjoy_input_type == InputType.JoystickButton:
            is_pressed = value.current
            if self.data.button_inverted:
                is_pressed = not is_pressed
            VJoyProxy()[self.data.vjoy_device_id] \
                .button(self.data.vjoy_input_id).is_pressed = is_pressed

            if is_pressed and ActionProperty.DisableAutoRelease not in properties:
                device_helpers.ButtonReleaseActions().register_button_release(
                    (self.data.vjoy_device_id, self.data.vjoy_input_id),
                    event,
                    self.data.button_inverted
                )

        elif self.data.vjoy_input_type == InputType.JoystickHat:
            VJoyProxy()[self.data.vjoy_device_id] \
                .hat(self.data.vjoy_input_id).direction = value.current

    def relative_axis_thread(self) -> None:
        self.thread_running = True
        vjoy_dev = VJoyProxy()[self.data.vjoy_device_id]
        self.axis_value = vjoy_dev.axis(self.data.vjoy_input_id).value
        while self.thread_running:
            # Abort if the vJoy device is no longer valid
            if not vjoy_dev.is_owned():
                self.thread_running = False
                return

            try:
                # If the vjoy value has was changed from what we set it to
                # in the last iteration, terminate the thread
                change = vjoy_dev.axis(self.data.vjoy_input_id).value - \
                        self.axis_value
                if abs(change) > 0.0001:
                    self.thread_running = False
                    self.should_stop_thread = True
                    return

                self.axis_value = util.clamp(
                    self.axis_value + self.axis_delta_value,
                    -1.0,
                    1.0
                )
                vjoy_dev.axis(self.data.vjoy_input_id).value = self.axis_value

                if self.should_stop_thread and \
                        self.thread_last_update + 1.0 < time.time():
                    self.thread_running = False
                time.sleep(0.01)
            except error.VJoyError:
                self.thread_running = False
