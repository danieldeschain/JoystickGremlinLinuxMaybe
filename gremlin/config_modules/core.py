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

"""Configuration core - singleton and state management."""


class ConfigurationCore:
    """Core configuration state and lifecycle management."""

    def __init__(self):
        """Creates a new instance, loading the current configuration."""
        self._data = {}
        self._last_reload = None

    def count(self) -> int:
        """Returns the number of parameters stored.

        Returns:
            Number of parameters stored by the configuration.
        """
        return len(self._data)

    def _should_skip_reload(self) -> bool:
        """Returns True if the last load() was less than 1 second ago."""
        import time
        return self._last_reload is not None and time.time() - self._last_reload < 1
