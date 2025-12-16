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

"""Cheatsheet PDF generators - main generation logic and document building."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import BaseDocTemplate, Spacer, Frame, PageTemplate, \
    Table, PageBreak

from gremlin.cheatsheet_modules.layout import DeviceFloat, ModeFloat
from gremlin.cheatsheet_modules.helpers import recursive


def _create_document_template(fname):
    """Create document template for cheatsheet.
    
    Args:
        fname: Filename for the PDF
        
    Returns:
        Configured document template
    """
    width, height = A4
    main_frame = Frame(cm, cm, width-2*cm, height-2*cm, showBoundary=False)
    main_template = PageTemplate(id="main", frames=[main_frame])
    return BaseDocTemplate(fname, pageTemplates=[main_template])


def _build_device_storage(profile):
    """Build device storage considering inheritance.
    
    Args:
        profile: Profile to process
        
    Returns:
        Dictionary mapping devices to their data
    """
    inheritance_tree = profile.build_inheritance_tree()
    device_storage = {}
    for key, device in profile.devices.items():
        device_storage[device] = {}
        recursive(device, inheritance_tree, device_storage[device])
    return device_storage


def _create_table_style(table_data):
    """Create table style based on data size.
    
    Args:
        table_data: Table data entries
        
    Returns:
        List of table style tuples
    """
    if len(table_data) == 1:
        return []
    return [
        ("LINEBELOW", (0, 0), (-1, -2), 0.25, HexColor("#c0c0c0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP")
    ]


def _create_mode_table(mode_data, width):
    """Create table for mode data.
    
    Args:
        mode_data: Mode data entries
        width: Page width
        
    Returns:
        Table object
    """
    table_data = []
    for entry in mode_data.values():
        table_data.extend(entry.table_data())
    
    return Table(
        table_data,
        colWidths=[
            0.15 * (width - 2 * cm),
            0.30 * (width - 2 * cm),
            0.55 * (width - 2 * cm)
        ],
        rowHeights=[None] * len(table_data),
        style=_create_table_style(table_data)
    )


def _add_device_section(story, dev, dev_data, width):
    """Add device section to story.
    
    Args:
        story: Story list to append to
        dev: Device object
        dev_data: Device data dictionary
        width: Page width
    """
    dev_float_added = False
    
    for mode_name, mode_data in dev_data.items():
        # Only proceed if we have input items
        if len(mode_data.values()) == 0:
            continue

        if not dev_float_added:
            story.append(DeviceFloat(dev.name))
            story.append(Spacer(1, 0.25 * cm))
            dev_float_added = True

        # Add heading and table
        story.append(ModeFloat(mode_name))
        story.append(_create_mode_table(mode_data, width))
        story.append(Spacer(1, 0.50 * cm))

    if dev_float_added:
        del story[-1]
        story.append(PageBreak())


def generate_cheatsheet(fname, profile):
    """Generates a cheatsheet of the provided profile.

    :param fname the file to store the cheatsheet in
    :param profile the profile to process
    """
    width, height = A4
    doc = _create_document_template(fname)
    device_storage = _build_device_storage(profile)

    story = []
    for dev, dev_data in device_storage.items():
        _add_device_section(story, dev, dev_data, width)

    doc.build(story)
