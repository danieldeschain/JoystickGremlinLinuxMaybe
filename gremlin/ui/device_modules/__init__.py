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

"""
Device modules package.

This package contains the refactored device management components:
- database: Device database and mapping (DeviceMapping, DeviceDatabase)
- models: Input identifier and device list models (InputIdentifier, DeviceListModel)
- device_model: Single device model (Device)
- io_management: Intermediate output management (IODeviceManagementModel, IODeviceInputsModel)
- vjoy: VJoy device management (VJoyDevices)
- state: Device state tracking (AbstractDeviceState, DeviceAxisState, DeviceButtonState, DeviceHatState)
- visualization: Axis visualization and calibration (DeviceAxisSeries, AxisCalibration)
"""

# Re-export all classes for backward compatibility
from .database import DeviceMapping, DeviceDatabase
from .models import InputIdentifier, DeviceListModel

__all__ = [
    # Database
    "DeviceMapping",
    "DeviceDatabase",
    # Models
    "InputIdentifier",
    "DeviceListModel",
]
