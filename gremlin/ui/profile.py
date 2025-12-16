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

"""Profile UI models - re-exports from profile_modules."""

from __future__ import annotations

from gremlin.ui.profile_modules.virtual_buttons import VirtualButtonModel, HatDirectionModel
from gremlin.ui.profile_modules.input_binding import InputItemBindingModel
from gremlin.ui.profile_modules.input_model import InputItemModel
from gremlin.ui.profile_modules.mode_models import ModeListModel, ModeHierarchyModel
from gremlin.ui.profile_modules.selection_models import LabelValueSelectionModel

QML_IMPORT_NAME = "Gremlin.Profile"
QML_IMPORT_MAJOR_VERSION = 1

__all__ = [
    "VirtualButtonModel",
    "HatDirectionModel",
    "InputItemBindingModel",
    "InputItemModel",
    "ModeListModel",
    "ModeHierarchyModel",
    "LabelValueSelectionModel",
    "QML_IMPORT_NAME",
    "QML_IMPORT_MAJOR_VERSION",
]
