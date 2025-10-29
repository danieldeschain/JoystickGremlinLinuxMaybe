"""Visualization components for device axis monitoring and calibration.

This module provides time-series visualization for axis data and
interactive axis calibration functionality.
"""

# Copyright (C) 2015 - 2025 Lionel Ott
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

import logging
import math
import time
import uuid
from typing import Any, Dict

from PySide6 import QtCharts, QtCore, QtQml
from PySide6.QtCore import Property, Signal, Slot

import dill

from gremlin import event_handler, util
from gremlin.config import Configuration
from gremlin.types import InputType
from .database import DeviceDatabase


@QtQml.QmlElement
class DeviceAxisSeries(QtCore.QObject):

    windowSizeChanged = Signal()
    deviceChanged = Signal()
    axisCountChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        el = event_handler.EventListener()
        el.joystick_event.connect(self._event_callback)

        self._device = None
        self._device_uuid = None
        self._state = []
        self._identifier_map = {}
        self._window_size = 20

    def _set_guid(self, guid: str) -> None:
        if self._device is not None and guid == str(self._device.device_guid):
            return

        self._device = dill.DILL.get_device_information_by_guid(
            dill.GUID.from_str(guid)
        )
        self._device_uuid = uuid.UUID(guid)

        self._state = []
        for i in range(self._device.axis_count):
            self._identifier_map[self._device.axis_map[i].axis_index] = i
            self._state.append({
                "identifier": self._device.axis_map[i].axis_index,
                "timeSeries": []
            })
        self.deviceChanged.emit()

    def _get_window_size(self) -> int:
        return self._window_size

    def _set_window_size(self, value: int) -> None:
        if value != self._window_size:
            self._window_size = value
            self.windowSizeChanged.emit()

    def _event_callback(self, event: event_handler.Event):
        if event.device_guid != self._device_uuid:
            return

        if event.event_type == InputType.JoystickAxis:
            index = self._identifier_map[event.identifier]
            self._state[index]["timeSeries"].append(
                (time.time(), event.value)
            )

    @Property(int, notify=axisCountChanged)
    def axisCount(self) -> int:
        return self._device.axis_count

    @Slot(QtCharts.QLineSeries, int)
    def updateSeries(self, series: QtCharts.QLineSeries, identifier: int):
        data = self._state[identifier]["timeSeries"]

        if len(data) == 0:
            series.replace([
                QtCore.QPointF(0.0, 0.0),
                QtCore.QPointF(self._window_size, 0.0),
            ])
            return

        now  = time.time()
        try:
            while now - data[0][0] > self._window_size:
                data.pop(0)
        except IndexError as e:
            logging.getLogger("system").warning(f"Unexpected exception: {e}")
            return

        time_series = []
        for pt in data:
            time_series.append(QtCore.QPointF(pt[0] - now, pt[1]))
        time_series.append(QtCore.QPointF(0, data[-1][1]))
        series.replace(time_series)

    @Slot(int, result=int)
    def axisIdentifier(self, index: int) -> int:
        return self._state[index]["identifier"]

    guid = Property(
        str,
        fset=_set_guid,
        notify=deviceChanged
    )

    windowSize = Property(
        int,
        fset=_set_window_size,
        fget=_get_window_size,
        notify=windowSizeChanged
    )


@QtQml.QmlElement
class AxisCalibration(QtCore.QAbstractListModel):

    deviceChanged = Signal()

    roles = {
        QtCore.Qt.UserRole + 1: QtCore.QByteArray("identifier".encode()),
        QtCore.Qt.UserRole + 2: QtCore.QByteArray("calibratedValue".encode()),
        QtCore.Qt.UserRole + 3: QtCore.QByteArray("rawValue".encode()),
        QtCore.Qt.UserRole + 4: QtCore.QByteArray("low".encode()),
        QtCore.Qt.UserRole + 5: QtCore.QByteArray("centerLow".encode()),
        QtCore.Qt.UserRole + 6: QtCore.QByteArray("centerHigh".encode()),
        QtCore.Qt.UserRole + 7: QtCore.QByteArray("high".encode()),
        QtCore.Qt.UserRole + 8: QtCore.QByteArray("withCenter".encode()),
        QtCore.Qt.UserRole + 9: QtCore.QByteArray("unsavedChanges".encode()),
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self._event_listener = event_handler.EventListener()
        self._event_listener.joystick_event.connect(self._event_callback)

        self._device = None
        self._device_uuid = None
        self._state = []
        self._calibration_fn = []
        self._active_calibrations = []

        self._config = Configuration()
        self._device_db = DeviceDatabase()
        self._device_mapping = None

    def data(self, index: QtCore.QModelIndex, role:int=...) -> Any:
        if role not in AxisCalibration.roles:
            return None

        role_name = AxisCalibration.roles[role].data().decode()
        return self._state[index.row()][role_name]

    def setData(self, index: QtCore.QModelIndex, value: Any, role: int=...) -> None:
        if role not in AxisCalibration.roles:
            return

        # Update internal representation
        role_name = AxisCalibration.roles[role].data().decode()
        self._state[index.row()][role_name] = value
        self._state[index.row()]["unsavedChanges"] = True
        self._update_calibration(index.row())

        # Signal that the model has changed for a UI update
        self.emit_update(index.row())

    def rowCount(self, parent:QtCore.QModelIndex=...) -> int:
        if self._device is None:
            return 0

        return len(self._state)

    def roleNames(self) -> Dict:
        return AxisCalibration.roles

    def emit_update(self, index: int):
        """Emits the data update signal for the given index."""
        self.dataChanged.emit(self.index(index, 0), self.index(index, 0))

    @Slot(int)
    def reset(self, index: int) -> None:
        """Resets the calibration data of the specified axis.

        Args:
            index: index of the axis to reset
        """
        if not (0 <= index < len(self._state)):
            return

        # Reset values to defaults
        self._state[index]["low"] = -32678
        self._state[index]["centerLow"] = 0
        self._state[index]["centerHigh"] = 0
        self._state[index]["high"] = 32767
        self._state[index]["unsavedChanges"] = True

        # Reset calibration tracking data to continue calibration after a
        # reset.
        self._active_calibrations[index]["cvalues"] = [0, 0]
        self._active_calibrations[index]["evalues"] = [0, 0]

        # Update models
        self._update_calibration(index)
        self.emit_update(index)

    @Slot(int, bool)
    def calibrateCenter(self, index: int, is_active: bool) -> None:
        self._active_calibrations[index]["center"] = is_active
        self._active_calibrations[index]["extrema"] = False
        self._active_calibrations[index]["cvalues"] = [0, 0]
        if is_active:
            self._state[index]["centerLow"] = 0
            self._state[index]["centerHigh"] = 0
            self.emit_update(index)

    @Slot(int, bool)
    def calibrateExtrema(self, index: int, is_active: bool) -> None:
        self._active_calibrations[index]["extrema"] = is_active
        self._active_calibrations[index]["center"] = False
        self._active_calibrations[index]["evalues"] = [0, 0]
        if is_active:
            self._state[index]["low"] = 0
            self._state[index]["high"] = 0
            self.emit_update(index)

    @Slot(int)
    def save(self, index: int) -> None:
        """Saves the current calibration data to the configuration system.

        Args:
            index: index of the axis whose data to save
        """
        self._config.set_calibration(
            self._device_uuid,
            self._device.axis_map[index].axis_index,
            [
                self._state[index]["low"],
                self._state[index]["centerLow"],
                self._state[index]["centerHigh"],
                self._state[index]["high"],
                self._state[index]["withCenter"]
            ]
        )
        self._state[index]["unsavedChanges"] = False
        self._event_listener.reload_calibration(
            self._device.device_guid,
            self._device.axis_map[index].axis_index,
        )
        self.emit_update(index)

    def _update_calibration(self, index: int) -> None:
        """Creates the calibration function based on the stored values.

        Args:
            index: index of the axis to update the calibration function of
        """
        self._calibration_fn[index] = util.create_calibration_function(
            self._state[index]["low"],
            self._state[index]["centerLow"],
            self._state[index]["centerHigh"],
            self._state[index]["high"],
            self._state[index]["withCenter"]
        )

    def _set_guid(self, guid: str) -> None:
        if self._device is not None and guid == str(self._device.device_guid):
            return

        self._device = dill.DILL.get_device_information_by_guid(
            dill.GUID.from_str(guid)
        )
        self._device_uuid = uuid.UUID(guid)
        self._device_mapping = self._device_db.get_mapping(self._device)
        self._state = []
        self._calibration_fn = []
        self._active_calibrations = []
        self._initialize_state()
        self.deviceChanged.emit()
        self.modelReset.emit()

    def _initialize_state(self) -> None:
        for i in range(self._device.axis_count):
            # Register the device in the configuration system, does not
            # changethe calibration values if the device has previously been
            # calibrated.
            key = (self._device_uuid, self._device.axis_map[i].axis_index)
            self._config.init_calibration(*key)

            axis_name = "{} {:d}".format(
                InputType.to_string(InputType.JoystickAxis).capitalize(),
                key[1]
            )
            if self._device_mapping:
                axis_name = self._device_mapping.input_name(axis_name)

            calibration_data = self._config.get_calibration(*key)
            self._state.append({
                "identifier": axis_name,
                "rawValue": 0,
                "calibratedValue": 0,
                "low": calibration_data[0],
                "centerLow": calibration_data[1],
                "centerHigh": calibration_data[2],
                "high": calibration_data[3],
                "withCenter": calibration_data[4],
                "unsavedChanges": False
            })

            self._calibration_fn.append(None)
            self._active_calibrations.append({"center": False, "extrema": False})
            self._update_calibration(i)

    def _event_callback(self, event: event_handler.Event):
        if event.device_guid != self._device_uuid:
            return

        if event.event_type == InputType.JoystickAxis:
            index = self._device.axis_lookup[event.identifier] - 1
            state = self._state[index]

            # Update axis value information
            state["rawValue"] = event.raw_value
            state["calibratedValue"] = math.floor(
                self._calibration_fn[index](event.raw_value) * 65535 / 2
            )

            # Check if we're calibrating the axis and if so record possible
            # new calibration values
            calibration_changed = False
            if self._active_calibrations[index]["center"]:
                data = self._active_calibrations[index]["cvalues"]
                if data[0] > event.raw_value:
                    data[0] = event.raw_value
                    state["centerLow"] = event.raw_value
                    calibration_changed = True
                if data[1] < event.raw_value:
                    data[1] = event.raw_value
                    state["centerHigh"] = event.raw_value
                    calibration_changed = True
            elif self._active_calibrations[index]["extrema"]:
                data = self._active_calibrations[index]["evalues"]
                if data[0] > event.raw_value:
                    data[0] = event.raw_value
                    state["low"] = event.raw_value
                    calibration_changed = True
                if data[1] < event.raw_value:
                    data[1] = event.raw_value
                    state["high"] = event.raw_value
                    calibration_changed = True

            # Recompute the calibration function if we're actively calibrating
            if self._active_calibrations[index]["center"] or \
                    self._active_calibrations[index]["extrema"]:
                self._update_calibration(index)
                if calibration_changed == True:
                    self._state[index]["unsavedChanges"] = True

            # Signal that the model has changed for a UI update
            self.emit_update(index)

    guid = Property(
        str,
        fset=_set_guid,
        notify=deviceChanged
    )
