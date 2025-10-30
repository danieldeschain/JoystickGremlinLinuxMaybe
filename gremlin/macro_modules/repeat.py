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

"""Macro repeat mode classes for controlling macro execution patterns."""

from __future__ import annotations

from abc import ABC, abstractmethod
from xml.etree import ElementTree

from gremlin import util
from gremlin.types import PropertyType


class AbstractRepeat(ABC):
    """Base class for all macro repeat modes."""

    def __init__(self, delay: float):
        """Creates a new instance.

        Args:
            delay the delay between repetitions
        """
        self.delay = delay

    def to_xml(self) -> ElementTree.Element:
        """Returns an XML node encoding the repeat information.

        Returns:
            XML node containing the instance's information
        """
        node = ElementTree.Element("repeat")
        node.append(util.create_property_node(
            "delay", self.delay, PropertyType.Float)
        )
        self._to_xml_additional(node)
        return node

    def from_xml(self, node: ElementTree.Element) -> None:
        """Populates the instance's data from the provided XML node.

        Args:
            node: XML node containing data with which to populate the instance
        """
        self.delay = util.read_property(node, "delay", PropertyType.Float)
        self._from_xml_additional(node)

    @abstractmethod
    def _to_xml_additional(self, node: ElementTree.Element) -> None:
        pass

    @abstractmethod
    def _from_xml_additional(self, node: ElementTree.Element) -> None:
        pass


class CountRepeat(AbstractRepeat):
    """Repeat mode which repeats the macro a fixed number of times."""

    def __init__(self, count: int=1, delay: float=0.1):
        """Creates a new instance.

        Args:
            count: the number of times to repeat the macro
            delay: the delay between repetitions
        """
        super().__init__(delay)
        self.count = count

    def _to_xml_additional(self, node: ElementTree.Element) -> None:
        """Returns an XML node encoding the repeat information.

        Args:
            node: XML node containing the instance's information
        """
        node.set("type", "count")
        node.append(util.create_property_node(
            "count", self.count, PropertyType.Int
        ))

    def _from_xml_additional(self, node: ElementTree.Element) -> None:
        """Populates the instance's data from the provided XML node.

        Args:
            node: XML node containing data with which to populate the instance
        """
        self.count = util.read_property(node, "count", PropertyType.Int)


class ToggleRepeat(AbstractRepeat):
    """Repeat mode which repeats the macro as long as it hasn't been toggled
    off again after being toggled on."""

    def __init__(self, delay: float=0.1):
        """Creates a new instance.

        Args:
            delay the delay between repetitions
        """
        super().__init__(delay)

    def _to_xml_additional(self, node: ElementTree.Element) -> None:
        """Returns an XML node encoding the repeat information.

        Args:
            node: XML node containing the instance's information
        """
        node.set("type", "toggle")

    def _from_xml_additional(self, node: ElementTree.Element) -> None:
        """Populates the instance's data from the provided XML node.

        Args:
            node: XML node containing data with which to populate the instance
        """
        pass


class HoldRepeat(AbstractRepeat):
    """Repeat mode which repeats the macro as long as the activation condition
    is being fulfilled or held down."""

    def __init__(self, delay: float=0.1):
        """Creates a new instance.

        Args:
            delay the delay between repetitions
        """
        super().__init__(delay)

    def _to_xml_additional(self, node: ElementTree.Element) -> None:
        """Returns an XML node encoding the repeat information.

        Args:
            node: XML node containing the instance's information
        """
        node.set("type", "hold")

    def _from_xml_additional(self, node: ElementTree.Element) -> None:
        """Populates the instance's data from the provided XML node.

        Args:
            node XML node containing data with which to populate the instance
        """
        pass
