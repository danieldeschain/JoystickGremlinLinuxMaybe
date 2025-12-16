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

"""Configuration metadata - type, description, properties, and exposure info."""

from typing import Any

from gremlin import error
from gremlin.types import PropertyType


class ConfigurationMetadata:
    """Provides access to parameter metadata."""

    def data_type(self, config_data: dict, section: str, group: str, name: str) -> PropertyType:
        """Returns the data type of the specified entry.

        Args:
            config_data: Configuration data dictionary
            section: overall section this parameter is associated with
            group: grouping into which the parameter belongs
            name: name by which the new parameter will be accessed

        Returns:
            Value associated with the given parameter
        """
        return self._retrieve_value(config_data, section, group, name, "data_type")

    def description(self, config_data: dict, section: str, group: str, name: str) -> str:
        """Returns the description associated with the given parameter.

        Args:
            config_data: Configuration data dictionary
            section: overall section this parameter is associated with
            group: grouping into which the parameter belongs
            name: name by which the new parameter will be accessed

        Returns:
            Description associated with the given parameter
        """
        return self._retrieve_value(config_data, section, group, name, "description")

    def properties(self, config_data: dict, section: str, group: str, name: str) -> dict[str, Any]:
        """Returns the properties associated with the given parameter.

        Args:
            config_data: Configuration data dictionary
            section: overall section this parameter is associated with
            group: grouping into which the parameter belongs
            name: name by which the new parameter will be accessed

        Returns:
            Properties associated with the given parameter
        """
        return self._retrieve_value(config_data, section, group, name, "properties")

    def expose(self, config_data: dict, section: str, group: str, name: str) -> bool:
        """Returns whether to expose a parameter in the UI.

        Args:
            config_data: Configuration data dictionary
            section: overall section this parameter is associated with
            group: grouping into which the parameter belongs
            name: name by which the new parameter will be accessed

        Returns:
            True if the parameter should be exposed via the UI.
        """
        return self._retrieve_value(config_data, section, group, name, "expose")

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
