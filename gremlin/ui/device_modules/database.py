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

"""Device database and mapping functionality."""

from __future__ import annotations

import json
from json.decoder import JSONDecodeError
import logging
from typing import Any, Dict

import dill

from gremlin import util
from gremlin.common import SingletonDecorator
from gremlin.config import Configuration


class DeviceMapping:
    """Maps device inputs to human-readable names."""

    def __init__(self, input_map: Dict[str, Any]) -> None:
        self._input_map = input_map

    def input_name(self, input_name: str) -> str:
        """
        Returns the display name for an input based on configuration.

        Args:
            input_name - name of the original input,
                         e.g.: "Axis 1" or "Button 1" or "Hat 1"

        Returns:
            The input name based on the global configuration option
            and availability of information about the input in
            the device mapping.

            If a device exists in the device database and its mapping or
            the input are not defined, input_name() returns a default
            input name, e.g. Axis 1 or Button 1 or Hat 1.

            Note that some devices have configurable number of buttons and/or axes
            so adjusting device database information might be required in the future.
        """
        input_name_display_mode = Configuration().value(
            "global", "input-names", "input-name-display-mode"
        )

        if (
            input_name_display_mode == "Numerical" or
            input_name not in self._input_map
        ):
            return input_name

        db_input_name = self._input_map[input_name].strip()

        # return default input name if input is defined, but empty
        if len(db_input_name) == 0:
            return input_name

        # return configured input name style
        if input_name_display_mode == "Numerical + Label":
            return f"{input_name} - {db_input_name}"
        if input_name_display_mode == "Label":
            return db_input_name


@SingletonDecorator
class DeviceDatabase:
    """Provides button/axis/hat to name mapping for known devices."""

    def __init__(self) -> None:
        self._load()

    def _load(self) -> None:
        """Load device database from JSON file."""
        db_file = util.resource_path("device_db.json")
        if not util.file_exists_and_is_accessible(db_file):
            return

        load_successful = False
        json_data = {}
        try:
            json_data = json.load(open(db_file))
            load_successful = True
        except JSONDecodeError as error:
            logging.getLogger("system").error(
                    f"There was an error loading {db_file}: {error}")

        parser_successful = self._parse_device_db(json_data)

        if load_successful and parser_successful:
            self._device_db = json_data
        else:
            self._device_db = {"revision": 0, "devices": [], "mapping": {}}

    def _parse_device_db(self, device_db: Dict[str, Any]) -> bool:
        """
        Parse device_db to make sure it has a valid structure.

        This piece could be refactored with JSON schema validation code,
        if need be in the future.
        """
        parser_successful = True

        # check top structure: devices and mappings
        if (not(
            isinstance(device_db.get("mapping", None), dict) and
            isinstance(device_db.get("devices", None), list))
            ):
            logging.getLogger("system").error(
                    "DeviceDatabase is corrupt and/or is missing mapping or device information.")
            parser_successful = False

        # check that devices contain mandatory fields
        device_count = 0
        for dev in device_db["devices"]:
            if not ("product_id" in dev and
                    "vendor_id" in dev and
                    "mapping" in dev
                    ):
                logging.getLogger("system").error(
                    f"DeviceDatabase device structure is corrupt for device {dev}")
                parser_successful = False
            else:
                device_count += 1

        # don't parse mapping, just make sure there is at least 1 mapping
        mapping_count = len(device_db["mapping"])

        if parser_successful and device_count > 0 and mapping_count > 0:
            return True

        return False

    def _device_matches(self, dev: Dict[str, Any], device: dill.DeviceSummary) -> bool:
        """Check if device matches database entry."""
        return dev["product_id"] == device.product_id and dev["vendor_id"] == device.vendor_id

    def get_mapping(self, device: dill.DeviceSummary) -> DeviceMapping | None:
        """
        Get device mapping for a detected device.
        
        Returns: DeviceMapping object for the detected device, or None if not found.
        """
        if device is None:
            return None

        for dev in self._device_db["devices"]:
            if self._device_matches(dev, device):
                if dev["mapping"] not in self._device_db["mapping"]:
                    logging.getLogger("system").warning(
                        f"Unable to find device mapping for product_id={device.product_id} "
                        f"vendor_id={device.vendor_id}")
                    return None

                return DeviceMapping(self._device_db["mapping"][dev["mapping"]])

        logging.getLogger("system").warning(
            f"Unsupported device product_id={device.product_id} "
            f"vendor_id={device.vendor_id}")

        return None
