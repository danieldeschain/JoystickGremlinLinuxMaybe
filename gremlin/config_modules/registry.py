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

"""Configuration registry - parameter registration and management."""

import logging
from typing import Any

from gremlin import error
from gremlin.types import PropertyType


_required_properties = {
    PropertyType.Bool: {},
    PropertyType.Int: {"min": int, "max": int},
    PropertyType.Float: {"min": float, "max": float},
    PropertyType.List: {},
    PropertyType.String: {},
    PropertyType.Selection: {"valid_options": list},
    PropertyType.HatDirection: {},
}


class ConfigurationRegistry:
    """Handles parameter registration and cleanup."""

    def register(
        self,
        config_data: dict,
        section: str,
        group: str,
        name: str,
        data_type: PropertyType,
        initial_value: Any,
        description: str,
        properties: dict[str, Any],
        expose: bool = False
    ) -> None:
        """Registers a new configuration parameter.

        Args:
            config_data: Configuration data dictionary
            section: overall section this parameter is associated with
            group: grouping into which the parameter belongs
            name: name by which the new parameter will be accessed
            data_type: type of data that is expected to be stored
            initial_value: initial value of the parameter
            description: description of the parameter's purpose
            properties: dictionary of relevant properties
            expose: if True expose the parameter via the UI to the user
        """
        key = (section, group, name)

        # Check the data type is a known one
        if data_type not in _required_properties:
            raise error.GremlinError(
                f"Attempting to register an entry with unsupported data type: " +
                f"{str(data_type)} in {key}"
            )

        # Ensure all required properties are present
        if data_type in _required_properties:
            for req_prop, req_type in _required_properties[data_type].items():
                if req_prop not in properties:
                    raise error.GremlinError(
                        f"Missing property '{req_prop}' of type "
                        f"{str(req_type)} in entry '{key}'"
                    )
                elif not isinstance(properties[req_prop], req_type):
                    raise error.GremlinError(
                        f"Incorrect type for property '{req_prop}', expected " +
                        f"'{req_type}' but got '{type(properties[req_prop])}' " +
                        f"in entry {key}"
                    )

        # Handle pre-existing entries
        if key in config_data:
            if config_data[key]["properties"] != properties:
                logging.getLogger("system").warning(
                    f"Properties for parameter '{key}' changed, updating"
                )
                config_data[key]["properties"] = properties

            if data_type != config_data[key]["data_type"]:
                logging.getLogger("system").warning(
                    f"Data type for parameter '{key}' changed, updating from " +
                    f"'{config_data[key]['data_type']}' to '{data_type}'")
                config_data[key]["data_type"] = data_type

            if description != config_data[key]["description"]:
                config_data[key]["description"] = description
        # Store new entry
        else:
            config_data[key] = {
                "value": initial_value,
                "data_type": data_type,
                "description": description,
                "properties": properties,
                "expose": expose
            }

        # Mark property as being registered
        config_data[key]["is_registered"] = True

    def purge_unused(self, config_data: dict) -> None:
        """Removes all options that have failed to be registered.

        Args:
            config_data: Configuration data dictionary
        """
        keys_to_delete = []
        for key, value in config_data.items():
            if not value.get("is_registered", False):
                keys_to_delete.append(key)
        for key in keys_to_delete:
            if key[0] != "calibration":
                logging.getLogger("system").warning(
                    f"Parameter '{key}' has not been registered, purging."
                )
                del config_data[key]
