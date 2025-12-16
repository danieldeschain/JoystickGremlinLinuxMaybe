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


from __future__ import annotations

from typing import List, Optional

from PySide6 import QtCore, QtQml
from PySide6.QtCore import Property, Signal

import gremlin.profile
from gremlin.types import AxisButtonDirection, HatDirection
from gremlin.util import clamp


class VirtualButtonModel(QtCore.QObject):

    """Represents both axis and hat virtual buttons."""

    lowerLimitChanged = Signal()
    upperLimitChanged = Signal()
    directionChanged = Signal()
    hatDirectionChanged = Signal()

    def __init__(
        self,
        virtual_button: gremlin.profile.AbstractVirtualButton,
        parent: Optional[QtCore.QObject]=None
    ):
        """Creates a new instance.

        Args:
            virtual_button: the profile class representing the instance's data
            parent: parent object of the widget
        """
        super().__init__(parent)

        self.virtual_button = virtual_button

    def _get_lower_limit(self) -> float:
        return self.virtual_button.lower_limit

    def _set_lower_limit(self, value: float) -> None:
        if value != self.virtual_button.lower_limit:
            self.virtual_button.lower_limit = clamp(value, -1.0, 1.0)
            self.lowerLimitChanged.emit()

    def _get_upper_limit(self) -> float:
        return self.virtual_button.upper_limit

    def _set_upper_limit(self, value: float) -> None:
        if value != self.virtual_button.upper_limit:
            self.virtual_button.upper_limit = clamp(value, -1.0, 1.0)
            self.upperLimitChanged.emit()

    def _get_direction(self) -> str:
        return AxisButtonDirection.to_string(self.virtual_button.direction)

    def _set_direction(self, value: str) -> None:
        direction = AxisButtonDirection.to_enum(value.lower())
        if direction != self.virtual_button.direction:
            self.virtual_button.direction = direction
            self.directionChanged.emit()

    def _get_hat_state(self, hat_direction):
        return hat_direction in self.virtual_button.directions

    def _set_hat_state(self, hat_direction, is_active):
        if is_active:
            if hat_direction not in self.virtual_button.directions:
                self.virtual_button.directions.append(hat_direction)
                self.hatDirectionChanged.emit()
        else:
            if hat_direction in self.virtual_button.directions:
                index = self.virtual_button.directions.index(hat_direction)
                del self.virtual_button.directions[index]
                self.hatDirectionChanged.emit()

    lowerLimit = Property(
        float,
        fget=_get_lower_limit,
        fset=_set_lower_limit,
        notify=lowerLimitChanged
    )
    upperLimit = Property(
        float,
        fget=_get_upper_limit,
        fset=_set_upper_limit,
        notify=upperLimitChanged
    )
    direction = Property(
        str,
        fget=_get_direction,
        fset=_set_direction,
        notify=directionChanged
    )

    hatNorth = Property(
        bool,
        fget=lambda cls: VirtualButtonModel._get_hat_state(cls, HatDirection.North),
        fset=lambda cls, x: VirtualButtonModel._set_hat_state(cls, HatDirection.North, x),
        notify=hatDirectionChanged
    )
    hatNorthEast = Property(
        bool,
        fget=lambda cls: VirtualButtonModel._get_hat_state(cls, HatDirection.NorthEast),
        fset=lambda cls, x: VirtualButtonModel._set_hat_state(cls, HatDirection.NorthEast, x),
        notify=hatDirectionChanged
    )
    hatEast = Property(
        bool,
        fget=lambda cls: VirtualButtonModel._get_hat_state(cls, HatDirection.East),
        fset=lambda cls, x: VirtualButtonModel._set_hat_state(cls, HatDirection.East, x),
        notify=hatDirectionChanged
    )
    hatSouthEast = Property(
        bool,
        fget=lambda cls: VirtualButtonModel._get_hat_state(cls, HatDirection.SouthEast),
        fset=lambda cls, x: VirtualButtonModel._set_hat_state(cls, HatDirection.SouthEast, x),
        notify=hatDirectionChanged
    )
    hatSouth = Property(
        bool,
        fget=lambda cls: VirtualButtonModel._get_hat_state(cls, HatDirection.South),
        fset=lambda cls, x: VirtualButtonModel._set_hat_state(cls, HatDirection.South, x),
        notify=hatDirectionChanged
    )
    hatSouthWest = Property(
        bool,
        fget=lambda cls: VirtualButtonModel._get_hat_state(cls, HatDirection.SouthWest),
        fset=lambda cls, x: VirtualButtonModel._set_hat_state(cls, HatDirection.SouthWest, x),
        notify=hatDirectionChanged
    )
    hatWest = Property(
        bool,
        fget=lambda cls: VirtualButtonModel._get_hat_state(cls, HatDirection.West),
        fset=lambda cls, x: VirtualButtonModel._set_hat_state(cls, HatDirection.West, x),
        notify=hatDirectionChanged
    )
    hatNorthWest = Property(
        bool,
        fget=lambda cls: VirtualButtonModel._get_hat_state(cls, HatDirection.NorthWest),
        fset=lambda cls, x: VirtualButtonModel._set_hat_state(cls, HatDirection.NorthWest, x),
        notify=hatDirectionChanged
    )


@QtQml.QmlElement
class HatDirectionModel(QtCore.QObject):

    """QML model representing the directions of a hat."""

    directionsChanged = Signal()

    def __init__(
        self,
        directions: List[HatDirection],
        parent: Optional[QtCore.QObject]=None
    ):
        super().__init__(parent)

        self.directions = directions

    def _get_hat_state(self, direction: HatDirection) -> bool:
        return direction in self.directions

    def _set_hat_state(self, direction: HatDirection, is_active: bool) -> None:
        if is_active:
            if direction not in self.directions:
                self.directions.append(direction)
                self.directionsChanged.emit()
        else:
            if direction in self.directions:
                index = self.directions.index(direction)
                del self.directions[index]
                self.directionsChanged.emit()

    hatNorth = Property(
        bool,
        fget=lambda cls: HatDirectionModel._get_hat_state(cls, HatDirection.North),
        fset=lambda cls, x: HatDirectionModel._set_hat_state(cls, HatDirection.North, x),
        notify=directionsChanged
    )
    hatNorthEast = Property(
        bool,
        fget=lambda cls: HatDirectionModel._get_hat_state(cls, HatDirection.NorthEast),
        fset=lambda cls, x: HatDirectionModel._set_hat_state(cls, HatDirection.NorthEast, x),
        notify=directionsChanged
    )
    hatEast = Property(
        bool,
        fget=lambda cls: HatDirectionModel._get_hat_state(cls, HatDirection.East),
        fset=lambda cls, x: HatDirectionModel._set_hat_state(cls, HatDirection.East, x),
        notify=directionsChanged
    )
    hatSouthEast = Property(
        bool,
        fget=lambda cls: HatDirectionModel._get_hat_state(cls, HatDirection.SouthEast),
        fset=lambda cls, x: HatDirectionModel._set_hat_state(cls, HatDirection.SouthEast, x),
        notify=directionsChanged
    )
    hatSouth = Property(
        bool,
        fget=lambda cls: HatDirectionModel._get_hat_state(cls, HatDirection.South),
        fset=lambda cls, x: HatDirectionModel._set_hat_state(cls, HatDirection.South, x),
        notify=directionsChanged
    )
    hatSouthWest = Property(
        bool,
        fget=lambda cls: HatDirectionModel._get_hat_state(cls, HatDirection.SouthWest),
        fset=lambda cls, x: HatDirectionModel._set_hat_state(cls, HatDirection.SouthWest, x),
        notify=directionsChanged
    )
    hatWest = Property(
        bool,
        fget=lambda cls: HatDirectionModel._get_hat_state(cls, HatDirection.West),
        fset=lambda cls, x: HatDirectionModel._set_hat_state(cls, HatDirection.West, x),
        notify=directionsChanged
    )
    hatNorthWest = Property(
        bool,
        fget=lambda cls: HatDirectionModel._get_hat_state(cls, HatDirection.NorthWest),
        fset=lambda cls, x: HatDirectionModel._set_hat_state(cls, HatDirection.NorthWest, x),
        notify=directionsChanged
    )


