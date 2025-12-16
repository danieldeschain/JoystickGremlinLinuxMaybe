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

"""Cheatsheet data structures - InputItemData class."""

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

from gremlin.types import InputType


# Hat direction abbreviations
hat_direction_abbrev = {
    "center": "C",
    "north": "N",
    "north-east": "NE",
    "east": "E",
    "south-east": "SE",
    "south": "S",
    "south-west": "SW",
    "west": "W",
    "north-west": "NW"
}


class InputItemData:
    """Represents the data about a single InputItem entry."""

    style = getSampleStyleSheet()["Normal"]

    def __init__(self, input_item, inherited_from):
        """Creates a new instance.

        :param input_item the InputItem instance this represents
        :param inherited_from mode from which this InputItem was inherited
        """
        self.input_item = input_item
        self.inherited_from = inherited_from

    def _extract_container_data(self):
        """Extract basic container information.
        
        Returns:
            Tuple of (containers, container_count, actionset_count, descriptions)
        """
        containers = self.input_item.containers
        container_count = len(containers)
        actionset_count = [len(c.action_sets) for c in containers]
        container_desc = [self.extract_description_actions(c) for c in containers]
        return containers, container_count, actionset_count, container_desc

    def _create_basic_info(self):
        """Create basic input information.
        
        Returns:
            Tuple of (input_name, inherited paragraph)
        """
        # Import here to avoid circular dependency
        from gremlin.cheatsheet_modules.helpers import format_input_name
        
        input_name = format_input_name(
            self.input_item.input_type,
            self.input_item.input_id
        )
        inherited = Paragraph(
            "<span color='#c0c0c0'><i>{}</i></span>".format(
                "" if self.inherited_from is None else self.inherited_from
            ),
            InputItemData.style
        )
        return input_name, inherited

    def _process_standard_input(self, input_name, container_desc, inherited):
        """Process non-hat input types.
        
        Args:
            input_name: Name of the input
            container_desc: Container descriptions
            inherited: Inherited paragraph
            
        Returns:
            List with single output entry
        """
        additional_desc = ""
        for c_descs in container_desc:
            for a_desc in c_descs:
                additional_desc += "\n{}".format(a_desc)

        description = self.input_item.description
        if len(additional_desc) > 0:
            description += additional_desc

        return [(input_name, description, inherited)]

    def _process_hat_buttons(self, container, input_name, inherited):
        """Process hat buttons container.
        
        Args:
            container: Hat buttons container
            input_name: Name of the input
            inherited: Inherited paragraph
            
        Returns:
            List of hat button outputs
        """
        hat_outputs = []
        direction_lookup = []
        if container.button_count == 4:
            direction_lookup = ["N", "E", "S", "W"]
        elif container.button_count == 8:
            direction_lookup = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

        for i, action_set in enumerate(container.action_sets):
            if len(action_set) > 0:
                hat_outputs.append((
                    "{} {}".format(input_name, direction_lookup[i]),
                    self.extract_action_set_descriptions(action_set),
                    inherited
                ))
        return hat_outputs

    def _process_virtual_button(self, container, input_name, inherited):
        """Process virtual button container.
        
        Args:
            container: Virtual button container
            input_name: Name of the input
            inherited: Inherited paragraph
            
        Returns:
            Single output entry for virtual button
        """
        c_dirs = []
        for direction in container.virtual_button.directions:
            c_dirs.append("{} {}".format(
                input_name,
                hat_direction_abbrev[direction]
            ))
        c_input_name = "\n".join(c_dirs)

        return (
            c_input_name,
            "\n".join(self.extract_description_actions(container)),
            inherited
        )

    def _process_hat_input(self, containers, input_name, inherited):
        """Process hat input type with multiple configurations.
        
        Args:
            containers: List of containers
            input_name: Name of the input
            inherited: Inherited paragraph
            
        Returns:
            List of output entries for hat
        """
        hat_outputs = []
        standard_desc = [self.input_item.description]

        for container in containers:
            if container.tag == "hat_buttons":
                hat_outputs.extend(
                    self._process_hat_buttons(container, input_name, inherited)
                )
            elif container.virtual_button is not None:
                hat_outputs.append(
                    self._process_virtual_button(container, input_name, inherited)
                )
            else:
                standard_desc.append(
                    "\n".join(self.extract_description_actions(container))
                )

        # Insert standard hat entry before specialized ones
        output = [(input_name, "\n".join(standard_desc), inherited)]
        output.extend(hat_outputs)
        return output

    def table_data(self):
        """Returns the data necessary to create the data table.

        :return table data entries
        """
        containers, _, _, container_desc = self._extract_container_data()
        input_name, inherited = self._create_basic_info()

        # Process based on input type
        if self.input_item.input_type != InputType.JoystickHat:
            return self._process_standard_input(input_name, container_desc, inherited)
        else:
            return self._process_hat_input(containers, input_name, inherited)

    def extract_description_actions(self, container):
        """Returns all description contents from Description actions.

        :param container the container instance to process
        :return description contents of all Description actions stored within
            the container
        """
        descriptions = []
        for action_set in container.action_sets:
            for action in [a for a in action_set if a.tag == "description"]:
                descriptions.append(action.description)
        return descriptions

    def extract_action_set_descriptions(self, action_set):
        """Returns a string representing the action set descriptions.

        :param action_set action set to process for descriptions
        :return string of descriptions contained in the action set
        """
        descriptions = []
        for action in [a for a in action_set if a.tag == "description"]:
            descriptions.append(action.description)
        return "\n".join(descriptions)
