# -*- coding: utf-8; -*-

# Copyright (C) 2015 - 2024 Lionel Ott
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

"""Cheatsheet helper functions - utilities and formatting."""

import gremlin
import gremlin.keyboard
from gremlin.cheatsheet_modules.data import InputItemData
from gremlin.types import InputType


def recursive(device, tree, storage):
    """Recursively parses a profile and stores the contents in
    the required form.

    :param device the device of interest
    :param tree the subtree currently being processed
    :param storage the storage for the extracted data
    """
    for parent, children in tree.items():
        # Ensure the storage structure is correctly initialized
        if parent not in storage:
            storage[parent] = {}
        for child in children:
            if child not in storage:
                storage[child] = {}

        # In case the parent mode doesn't exist skip this recursion level
        if parent not in device.modes:
            continue

        # Insert actions of parent into parent
        mode = device.modes[parent]

        # Aggregate all input items into a single list
        for items in mode.config.values():
            for item in items.values():
                if len(item.containers) > 0:
                    storage[parent][(item.input_type, item.input_id)] = \
                        InputItemData(item, None)

                    for child in children:
                        storage[child][(item.input_type, item.input_id)] = \
                            InputItemData(item, parent)

        # Recursively process the remainder of the inheritance tree
        recursive(device, children, storage)


def sort_data(data):
    """Returns a new list sorted by input type.

    :param data the data to sort
    :return the sorted data
    """
    sorted_data = []

    for input_type in InputType:
        for key, value in sorted(data.items(), key=lambda x: x[0][1]):
            if input_type == key[0]:
                sorted_data.append(
                    [format_input_name(key[0], key[1]), value[0], value[1]]
                )

    return sorted_data


def format_input_name(input_type, identifier):
    """Returns a formatted name of the provided input.

    :param input_type the type of the input
    :param identifier the identifier of the input
    :return formatted string of the provided input
    """
    type_map = {
        InputType.JoystickAxis: "Axis",
        InputType.JoystickButton: "Button",
        InputType.JoystickHat: "Hat",
        InputType.Keyboard: "Key",
    }

    if input_type == InputType.Keyboard:
        return gremlin.keyboard.key_from_code(identifier[0], identifier[1]).name
    else:
        return "{} {}".format(type_map[input_type], identifier)
