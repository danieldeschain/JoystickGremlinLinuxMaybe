# -*- coding: utf-8; -*-

# Copyright (C) 2016 Lionel Ott
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

"""
Map to vJoy action plugin.

This module provides backward compatibility by re-exporting all classes.
All implementation has been moved to focused submodules.

Module Structure:
- functor: MapToVjoyFunctor for runtime execution
- model: MapToVjoyModel for UI interaction  
- data: MapToVjoyData for configuration and persistence
"""

from __future__ import annotations

from action_plugins.map_to_vjoy.functor import MapToVjoyFunctor
from action_plugins.map_to_vjoy.model import MapToVjoyModel
from action_plugins.map_to_vjoy.data import MapToVjoyData

create = MapToVjoyData

__all__ = [
    "MapToVjoyFunctor",
    "MapToVjoyModel",
    "MapToVjoyData",
    "create",
]
