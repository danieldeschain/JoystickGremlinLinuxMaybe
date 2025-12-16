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

"""Configuration modules - modular configuration management components.

This package contains focused modules for different aspects of configuration:
- core: Core configuration state and lifecycle
- persistence: Load/save operations
- registry: Parameter registration
- accessors: Get/set/exists operations
- metadata: Type and description info
- structure: Sections/groups/entries navigation
- calibration: Device calibration management
"""

# Re-export all components for internal use
from .core import ConfigurationCore
from .persistence import ConfigurationPersistence
from .registry import ConfigurationRegistry
from .accessors import ConfigurationAccessors
from .metadata import ConfigurationMetadata
from .structure import ConfigurationStructure
from .calibration import ConfigurationCalibration

__all__ = [
    "ConfigurationCore",
    "ConfigurationPersistence",
    "ConfigurationRegistry",
    "ConfigurationAccessors",
    "ConfigurationMetadata",
    "ConfigurationStructure",
    "ConfigurationCalibration",
]
