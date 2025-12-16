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

"""Configuration accessors - get, set, exists, and value retrieval."""

from typing import Any

from gremlin import error, util


class ConfigurationAccessors:
    """Provides access to configuration values."""

    def get(self, config_data: dict, section: str, group: str, name: str, entry: str) -> Any:
        """Gets the value of a specific parameter entry.

        Args:
            config_data: Configuration data dictionary
            section: overall section this parameter is associated with
            group: grouping into which the parameter belongs
            name: name by which the new parameter will be accessed
            entry: name of the parameter's entry to return

        Returns:
            Value of the specified entry.
        """
        return self._retrieve_value(config_data, section, group, name, entry)

    def set(self, config_data: dict, section: str, group: str, name: str, value: Any) -> None:
        """Sets the value of a specific parameter.

        Args:
            config_data: Configuration data dictionary
            section: overall section this parameter is associated with
            group: grouping into which the parameter belongs
            name: name by which the new parameter will be accessed
            value: new value for the parameter
        """
        key = (section, group, name)
        if key not in config_data:
            raise error.GremlinError(f"No parameter with key '{key}' exists")

        _, is_valid = util.determine_value_type(
            value,
            config_data[key]["data_type"]
        )
        if is_valid:
            config_data[key]["value"] = value
        else:
            data_type = config_data[key]["data_type"]
            raise error.GremlinError(
                f"Value has wrong data type, expected: " +
                f"'{data_type}' got '{type(value)}'"
            )

    def exists(self, config_data: dict, section: str, group: str, name: str) -> bool:
        """Returns True if the specified entry exists.

        Args:
            config_data: Configuration data dictionary
            section: overall section this parameter is associated with
            group: grouping into which the parameter belongs
            name: name by which the new parameter will be accessed

        Returns:
            True if a value with the specified path exists, False otherwise.
        """
        return (section, group, name) in config_data

    def value(self, config_data: dict, section: str, group: str, name: str) -> Any:
        """Returns the value associated with the given parameter.

        Args:
            config_data: Configuration data dictionary
            section: overall section this parameter is associated with
            group: grouping into which the parameter belongs
            name: name by which the new parameter will be accessed

        Returns:
            Value associated with the given parameter
        """
        return self._retrieve_value(config_data, section, group, name, "value")

    def _retrieve_value(
        self,
        config_data: dict,
        section: str,
        group: str,
        name: str,
        entry: str
    ) -> Any:
        """Returns an entry from the storage.

        Args:
            config_data: Configuration data dictionary
            section: overall section this parameter is associated with
            group: grouping into which the parameter belongs
            name: name by which the new parameter will be accessed
            entry: name of the parameter's entry to return

        Returns:
            Value of the specified entry.
        """
        key = (section, group, name)
        if key not in config_data:
            raise error.GremlinError(f"No parameter with key {key} exists")

        return config_data[key][entry]
