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

"""Cheatsheet modules - modular components for PDF cheatsheet generation.

This package contains focused modules for different aspects of cheatsheet generation:
- data: InputItemData class for representing input items
- layout: DeviceFloat and ModeFloat custom flowables for PDF headers
- generators: PDF document generation functions
- helpers: Utility functions for formatting and data processing
"""

# Re-export all components
from .data import InputItemData, hat_direction_abbrev
from .layout import DeviceFloat, ModeFloat
from .generators import (
    _create_document_template,
    _build_device_storage,
    _create_table_style,
    _create_mode_table,
    _add_device_section,
    generate_cheatsheet
)
from .helpers import recursive, sort_data, format_input_name

__all__ = [
    # Data structures
    "InputItemData",
    "hat_direction_abbrev",
    
    # Layout components
    "DeviceFloat",
    "ModeFloat",
    
    # Generators
    "generate_cheatsheet",
    "_create_document_template",
    "_build_device_storage",
    "_create_table_style",
    "_create_mode_table",
    "_add_device_section",
    
    # Helpers
    "recursive",
    "sort_data",
    "format_input_name",
]
