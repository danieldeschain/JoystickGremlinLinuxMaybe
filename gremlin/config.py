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

"""Configuration management - coordinating facade for all config operations.

This module provides a unified interface to configuration management,
delegating to focused submodules for specific responsibilities.
"""

import uuid
from typing import Any

from gremlin import common
from gremlin.types import PropertyType
from gremlin.config_modules import (
    ConfigurationCore,
    ConfigurationPersistence,
    ConfigurationRegistry,
    ConfigurationAccessors,
    ConfigurationMetadata,
    ConfigurationStructure,
    ConfigurationCalibration,
)


@common.SingletonDecorator
class Configuration:
    """Responsible for loading and saving configuration data.
    
    This class acts as a facade, coordinating between specialized modules
    for different aspects of configuration management.
    """

    def __init__(self):
        """Creates a new instance, loading the current configuration."""
        self._core = ConfigurationCore()
        self._persistence = ConfigurationPersistence()
        self._registry = ConfigurationRegistry()
        self._accessors = ConfigurationAccessors()
        self._metadata = ConfigurationMetadata()
        self._structure = ConfigurationStructure()
        self._calibration = ConfigurationCalibration()
        
        self._data = self._core._data
        self._last_reload = self._core._last_reload
        self.load()

    def count(self) -> int:
        """Returns the number of parameters stored."""
        return self._core.count()

    def _should_skip_reload(self) -> bool:
        """Returns True if the last load() was less than 1 second ago."""
        return self._core._should_skip_reload()

    def load(self):
        """Loads the configuration file's content."""
        if self._should_skip_reload():
            return

        self._data, self._last_reload = self._persistence.load(
            self._data,
            self._last_reload
        )
        self._core._data = self._data
        self._core._last_reload = self._last_reload
        self.save()

    def save(self):
        """Writes the configuration file to disk."""
        self._persistence.save(self._data)

    def register(
        self,
        section: str,
        group: str,
        name: str,
        data_type: PropertyType,
        initial_value: Any,
        description: str,
        properties: dict[str, Any],
        expose: bool = False
    ) -> None:
        """Registers a new configuration parameter."""
        self._registry.register(
            self._data,
            section,
            group,
            name,
            data_type,
            initial_value,
            description,
            properties,
            expose
        )
        try:
            self.save()
        except TypeError as e:
            key = (section, group, name)
            print(key, self._data[key])
            print(e)

    def purge_unused(self):
        """Removes all options that have failed to be registered."""
        self._registry.purge_unused(self._data)
        self.save()

    def get(self, section: str, group: str, name: str, entry: str) -> Any:
        """Gets the value of a specific parameter entry."""
        return self._accessors.get(self._data, section, group, name, entry)

    def set(self, section: str, group: str, name: str, value: Any) -> None:
        """Sets the value of a specific parameter."""
        self._accessors.set(self._data, section, group, name, value)
        self.save()

    def exists(self, section: str, group: str, name: str) -> bool:
        """Returns True if the specified entry exists."""
        return self._accessors.exists(self._data, section, group, name)

    def value(self, section: str, group: str, name: str) -> Any:
        """Returns the value associated with the given parameter."""
        return self._accessors.value(self._data, section, group, name)

    def data_type(self, section: str, group: str, name: str) -> Any:
        """Returns the data type of the specified entry."""
        return self._metadata.data_type(self._data, section, group, name)

    def description(self, section: str, group: str, name: str) -> str:
        """Returns the description associated with the given parameter."""
        return self._metadata.description(self._data, section, group, name)

    def properties(self, section: str, group: str, name: str) -> dict[str, Any]:
        """Returns the properties associated with the given parameter."""
        return self._metadata.properties(self._data, section, group, name)

    def expose(self, section: str, group: str, name: str) -> bool:
        """Returns whether to expose a parameter in the UI."""
        return self._metadata.expose(self._data, section, group, name)

    def sections(self, only_exposed: bool = True) -> list[str]:
        """Returns the list of all sections."""
        return self._structure.sections(self._data, only_exposed)

    def groups(self, section: str, only_exposed: bool = True) -> list[str]:
        """Returns the list of groups used within a section."""
        return self._structure.groups(self._data, section, only_exposed)

    def entries(
            self,
            section: str,
            group: str,
            only_exposed: bool = True
    ) -> list[str]:
        """Returns the list of entry names for a group within a section."""
        return self._structure.entries(self._data, section, group, only_exposed)

    def init_calibration(self, device_uuid: uuid.UUID, axis_id: int) -> None:
        """Registers an axis in the configuration."""
        self._calibration.init_calibration(
            self._data,
            self._registry.register,
            self._accessors.exists,
            device_uuid,
            axis_id
        )

    def get_calibration(
            self,
            device_uuid: uuid.UUID,
            axis_id: int
    ) -> list:
        """Returns the calibration data of a given axis."""
        return self._calibration.get_calibration(
            self._data,
            self._accessors.exists,
            self._accessors.value,
            device_uuid,
            axis_id
        )

    def set_calibration(
            self,
            device_uuid: uuid.UUID,
            axis_id: int,
            data: list
    ) -> None:
        """Sets the calibration data for an axis."""
        self._calibration.set_calibration(
            self._data,
            self._accessors.set,
            device_uuid,
            axis_id,
            data
        )
        self.save()
