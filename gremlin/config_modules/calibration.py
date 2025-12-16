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

"""Configuration calibration - device axis calibration management."""

import uuid

from gremlin import util
from gremlin.types import PropertyType


class ConfigurationCalibration:
    """Manages device axis calibration data."""

    def init_calibration(
        self,
        config_data: dict,
        register_func,
        exists_func,
        device_uuid: uuid.UUID,
        axis_id: int
    ) -> None:
        """Registers an axis in the configuration.

        Args:
            config_data: Configuration data dictionary
            register_func: Function to register new parameters
            exists_func: Function to check if parameter exists
            device_uuid: unique id of the device
            axis_id: axis index of the axis
        """
        uuid_str = str(device_uuid).upper()
        if not exists_func(config_data, "calibration", uuid_str, str(axis_id)):
            register_func(
                config_data,
                "calibration", uuid_str, str(axis_id),
                PropertyType.List,
                [-32768, 0, 0, 32767, True],
                "",
                {},
                False
            )

    def get_calibration(
            self,
            config_data: dict,
            exists_func,
            value_func,
            device_uuid: uuid.UUID,
            axis_id: int
    ) -> list:
        """Returns the calibration data of a given axis.

        Args:
            config_data: Configuration data dictionary
            exists_func: Function to check if parameter exists
            value_func: Function to retrieve parameter value
            device_uuid: unique id of the device
            axis_id: axis index of the axis

        Returns:
            Tuple containing calibration data
        """
        uuid_str = str(device_uuid).upper()
        axis_str = str(axis_id)
        if exists_func(config_data, "calibration", uuid_str, axis_str):
            data = value_func(config_data, "calibration", uuid_str, axis_str)
            return [int(v) for v in data[:-1]] + [util.parse_bool(data[-1])]
        else:
            return [-32678, 0, 0, 32767, True]

    def set_calibration(
            self,
            config_data: dict,
            set_func,
            device_uuid: uuid.UUID,
            axis_id: int,
            data: list
    ) -> None:
        """Sets the calibration data for an axis.

        Args:
            config_data: Configuration data dictionary
            set_func: Function to set parameter value
            device_uuid: unique id of the device
            axis_id: axis index of the axis
            data: calibration data
        """
        set_func(config_data, "calibration", str(device_uuid).upper(), str(axis_id), data)
