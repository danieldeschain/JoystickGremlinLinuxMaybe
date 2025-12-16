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

"""Cheatsheet PDF layout components - custom flowables for headers."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import Flowable


class DeviceFloat(Flowable):
    """Creates a device header element."""

    def __init__(self, device_name):
        """Creates a new instance.

        :param device_name name of the device
        """
        super().__init__()
        self._device_name = device_name

    def draw(self):
        self.canv.setFillColor(HexColor("#364151"))
        self.canv.rect(-1.25*cm, 0.0, A4[0]+0.1*cm, cm, stroke=False, fill=True)
        self.canv.setFillColor(HexColor("#ffffff"))
        self.canv.drawCentredString(
            A4[0]/2.0,
            0.35*cm,
            self._device_name
        )

    def wrap(self, availWidth, availHeight):
        return (A4[0]-2*cm, cm)

    def split(self, availWidth, availheight):
        return []


class ModeFloat(Flowable):
    """Creates a mode header element."""

    def __init__(self, mode_name):
        """Creates a new instance.

        :param mode_name name of the mode
        """
        super().__init__()
        self._mode_name = mode_name

        self._bar_offset = 0.1*cm
        self._bar_width = 0.25*cm
        self._bar_height = 0.75*cm

    def _draw_bar(self, path, offset):
        """Draws a single angle bar element.

        :param path the path element to which to add instructions
        :param offset the
        """
        path.moveTo(offset + self._bar_offset, 0)
        path.lineTo(offset + self._bar_offset + self._bar_width, 0)
        path.lineTo(
            offset + self._bar_height + self._bar_offset + self._bar_width,
            self._bar_height
        )
        path.lineTo(
            offset + self._bar_height + self._bar_offset,
            self._bar_height
        )
        path.lineTo(offset + self._bar_offset, 0)

        return offset + self._bar_width + self._bar_offset

    def draw(self):
        self.canv.setFillColor(HexColor("#798593"))

        offset = 7*cm

        path = self.canv.beginPath()
        path.moveTo(-1.25*cm, 0)
        path.lineTo(offset, 0)
        path.lineTo(offset+self._bar_height, self._bar_height)
        path.lineTo(-1.25*cm, self._bar_height)
        path.lineTo(-1.25*cm, 0)

        offset = self._draw_bar(path, offset)
        offset = self._draw_bar(path, offset)
        offset = self._draw_bar(path, offset)

        self.canv.drawPath(path, stroke=False, fill=True)
        self.canv.setFillColor(HexColor("#000000"))
        self.canv.setFillColor(HexColor("#ffffff"))
        self.canv.drawString(
            0,
            0.25*cm,
            self._mode_name
        )

    def wrap(self, availWidth, availHeight):
        return (A4[0]-2*cm, 0.75*cm)

    def split(self, availWidth, availheight):
        return []
