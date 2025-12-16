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

"""Configuration persistence - load and save operations."""

import json
import os
import time

from gremlin import util
from gremlin.types import PropertyType


_config_file_path = os.path.join(util.userprofile_path(), "configuration.json")


class ConfigurationPersistence:
    """Handles loading and saving configuration to/from disk."""

    def load(self, config_data: dict, last_reload: float) -> tuple[dict, float]:
        """Loads the configuration file's content.

        Args:
            config_data: Current configuration data dictionary
            last_reload: Timestamp of last reload

        Returns:
            Tuple of (updated_data, new_timestamp)
        """
        if last_reload is not None and time.time() - last_reload < 1:
            return config_data, last_reload

        # Attempt to load the configuration file if this fails set
        # default empty values.
        load_successful = False
        json_data = {}
        if os.path.isfile(_config_file_path):
            with open(_config_file_path) as hdl:
                try:
                    decoder = json.JSONDecoder()
                    json_data = decoder.decode(hdl.read())
                    load_successful = True
                except ValueError:
                    pass
        if not load_successful:
            return {}, time.time()

        # Convert data based on property types
        new_data = {}
        for section, sec_data in json_data.items():
            for group, grp_data in sec_data.items():
                for name, entry in grp_data.items():
                    data_type = PropertyType.to_enum(entry["data_type"])
                    new_data[(section, group, name)] = {
                        "value": util.property_from_string(
                            data_type,
                            entry["value"]
                        ),
                        "data_type": data_type,
                        "description": entry["description"],
                        "properties": entry["properties"],
                        "expose": entry["expose"]
                    }

        return new_data, time.time()

    def save(self, config_data: dict) -> None:
        """Writes the configuration file to disk.

        Args:
            config_data: Configuration data dictionary to save
        """
        # Convert all data to string representations
        json_data = {}
        for key, entry in config_data.items():
            section = key[0]
            group = key[1]
            name = key[2]
            if section not in json_data:
                json_data[section] = {}
            if group not in json_data[section]:
                json_data[section][group] = {}
            json_data[section][group][name] = {
                "value": util.property_to_string(
                    entry["data_type"],
                    entry["value"],
                ),
                "data_type": PropertyType.to_string(entry["data_type"]),
                "description": entry["description"],
                "properties": entry["properties"],
                "expose": entry["expose"]
            }

        # Write data to file
        with open(_config_file_path, "w") as hdl:
            encoder = json.JSONEncoder(
                sort_keys=True,
                indent=4
            )
            hdl.write(encoder.encode(json_data))
