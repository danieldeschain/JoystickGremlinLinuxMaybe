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



from __future__ import annotations

import copy
import functools
import importlib
import inspect
import logging
import os
from pathlib import Path
import random
import string
from typing import Any, Callable
import uuid

from gremlin import error, event_handler, shared_state, util
from gremlin.user_script_modules.registries import CallbackRegistry, PeriodicRegistry, ScriptVariableRegistry


class Script:

    """Represents the prototype of a script."""

    variable_registry = ScriptVariableRegistry()

    def __init__(self, path: Path=Path(), name: str=""):
        """Creates a new Script."""
        self._id = uuid.uuid4()
        self.path = path
        self.name = name
        self.variables: dict[str, AbstractVariable] = {}

        if self.path.is_file():
            self._retrieve_variable_definitions()
            self.variable_registry.register_script(self)

    @property
    def id(self) -> uuid.UUID:
        """Returns the UUID of the script.

        Returns:
            Unique identifier of this script.
        """
        return self._id

    @property
    def is_configured(self) -> bool:
        """Returns if the instance is fully configured.

        Returns:
            True if the instance is fully configured, False otherwise
        """
        return all([
            var.is_valid() for var in self.variables.values() if not var.is_optional
        ])

    def has_variable(self, name: str) -> bool:
        """Returns if this instance has a particular variable.

        Args:
            name: name of the variable to check the existence of

        Returns:
            True if a variable with the given name exists, False otherwise
        """
        return name in self.variables

    def set_variable(self, name: str, variable: AbstractVariable) -> None:
        """Sets the value of a named variable.

        Args:
            name: Name of the variable object to be set
            variable: Variable to store
        """
        self.variables[name] = variable

    def get_variable(self, name: str) -> AbstractVariable:
        """Returns the variable stored under the specified name.

        Attempting to retrieve a non-existent variable will raise an error.

        Args:
            name: Name of the variable to return

        Returns:
            Variable corresponding to the specified name
        """
        if not self.has_variable(name):
            raise error.GremlinError(
                f"Script '{self.path}' does not contain a variable '{name}'"
            )
        return self.variables[name]

    def from_xml(self, node: ElementTree.Element) -> None:
        """Initializes the values of this instance based on the node's contents.

        Args:
            node: XML node containing this instance's configuration
        """
        # Remove information of this script in case the ID changes
        Script.variable_registry.remove_script(self)

        lookup = {
            "bool": BoolVariable,
            "float": FloatVariable,
            "int": IntegerVariable,
            "mode": ModeVariable,
            "physical-input": PhysicalInputVariable,
            "selection": SelectionVariable,
            "string": StringVariable,
            "vjoy": VirtualInputVariable,
        }

        self._id = util.read_uuid(node, "script", "id")
        self.path = Path(util.read_property(node, "path", PropertyType.String))
        self.name = util.read_property(node, "name", PropertyType.String)

        # Retrieve variable information from the script and instantiate them
        self._retrieve_variable_definitions()

        # Populate variables with data from the XML if they are present
        for entry in node.iter("variable"):
            name = util.read_property(entry, "name", PropertyType.String)
            # Don't parse variables that don't exist anymore, they will be
            # removed upon the next save
            if name not in self.variables:
                logging.getLogger("system").warning(
                    f"Script: Unknown variable '{name}' ignored"
                )
                continue
            type_name = entry.get("type")
            if not isinstance(self.variables[name], lookup[type_name]):
                raise error.GremlinError(
                    f"Script: Type mismatch, profile contains '{type_name}' " + \
                    f"while script expects '{self.variables[name]}'"
                )
            self.variables[name].from_xml(entry)

        # Store script values in the registry
        Script.variable_registry.register_script(self)

    def to_xml(self) -> ElementTree.Element:
        """Returns an XML node representing this instance.

        Returns:
            XML node representing this instance
        """
        node = util.create_node_from_data(
            "script",
            [
                ("path", str(self.path), PropertyType.String),
                ("name", str(self.name), PropertyType.String),
            ]
        )
        node.set("id", util.safe_format(self._id, uuid.UUID))
        for entry in self.variables.values():
            variable_node = entry.to_xml()
            if variable_node is not None:
                node.append(variable_node)
        return node

    def reload(self):
        Script.variable_registry.register_script(self)
        self.module._script_id = self.id
        self.spec.loader.exec_module(self.module)

    def _retrieve_variable_definitions(self):
        """Returns all variable definitions used in the provided script.

        Args:
            path: Path to the script file

        Returns:
            List of variiables used in the script
        """
        self.variables = {}
        if not self.path.is_file():
            raise error.GremlinError(f"Invalid script file '{self.path}'")

        self.spec = importlib.util.spec_from_file_location(
            "".join(random.choices(string.ascii_lowercase, k=16)),
            str(self.path)
        )
        self.module = importlib.util.module_from_spec(self.spec)
        self.module._script_id = self.id
        self.spec.loader.exec_module(self.module)

        for key, value in self.module.__dict__.items():
            if isinstance(value, AbstractVariable):
                if value.name in self.variables:
                    logging.getLogger("system").error(
                        f"Script: Duplicate label {value.label} present in {path}"
                    )
                self.variables[value.name] = copy.deepcopy(value)


class AbstractVariable(ABC):
