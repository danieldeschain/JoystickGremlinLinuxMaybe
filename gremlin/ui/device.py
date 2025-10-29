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

"""Device management module for Joystick Gremlin.

This module has been refactored into the device_modules package.
All classes are re-exported here for backward compatibility.

See device_modules/ for the modular implementation:
- device_modules/database.py: Device database and mapping
- device_modules/models.py: Input identifier and device list models
- device_modules/device_model.py: Single device model
- device_modules/io_management.py: Intermediate output management
- device_modules/vjoy.py: VJoy device management
- device_modules/state.py: Device state tracking
- device_modules/visualization.py: Axis visualization and calibration
"""

from gremlin.config import Configuration
from gremlin.types import PropertyType

# Re-export all classes from device_modules package
from .device_modules import (
    # Database
    DeviceMapping,
    DeviceDatabase,
    # Models
    InputIdentifier,
    DeviceListModel,
    Device,
    # IO Management
    IODeviceManagementModel,
    IODeviceInputsModel,
    # VJoy
    VJoyDevices,
    # State Tracking
    AbstractDeviceState,
    DeviceAxisState,
    DeviceButtonState,
    DeviceHatState,
    # Visualization
    DeviceAxisSeries,
    AxisCalibration,
)

# QML configuration
QML_IMPORT_NAME = "Gremlin.Device"
QML_IMPORT_MAJOR_VERSION = 1

# Register configuration for input name display mode
Configuration().register(
    "global",
    "input-names",
    "input-name-display-mode",
    PropertyType.Selection,
    "Numerical & Label",
    "Defines how input name is displayed.",
    {
        "valid_options": ["Numerical", "Numerical + Label", "Label"]
    },
    True
)

__all__ = [
    # Database
    "DeviceMapping",
    "DeviceDatabase",
    # Models
    "InputIdentifier",
    "DeviceListModel",
    "Device",
    # IO Management
    "IODeviceManagementModel",
    "IODeviceInputsModel",
    # VJoy
    "VJoyDevices",
    # State Tracking
    "AbstractDeviceState",
    "DeviceAxisState",
    "DeviceButtonState",
    "DeviceHatState",
    # Visualization
    "DeviceAxisSeries",
    "AxisCalibration",
]
