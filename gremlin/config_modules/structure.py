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

"""Configuration structure - sections, groups, and entries navigation."""


class ConfigurationStructure:
    """Provides navigation through configuration structure."""

    def sections(self, config_data: dict, only_exposed: bool = True) -> list[str]:
        """Returns the list of all sections.

        Args:
            config_data: Configuration data dictionary
            only_exposed: If True, only return sections containing data
                exposed to the user

        Returns:
            List containing the name of all sections present.
        """
        section_names = []
        for key in config_data.keys():
            if len(self.groups(config_data, key[0], only_exposed)) > 0:
                section_names.append(key[0])
        return sorted(set(section_names))

    def groups(self, config_data: dict, section: str, only_exposed: bool = True) -> list[str]:
        """Returns the list of groups used within a section.

        Args:
            config_data: Configuration data dictionary
            section: name of the section for which to return the groups
            only_exposed: filters out all groups which would contain no
                entries once non exposed entries have been filtered out

        Returns:
            The list of groups occurring within the given section.
        """
        group_names = []
        for key in config_data.keys():
            if key[0] == section and \
                    len(self.entries(config_data, key[0], key[1], only_exposed)) > 0:
                group_names.append(key[1])
        return sorted(set(group_names))

    def entries(
            self,
            config_data: dict,
            section: str,
            group: str,
            only_exposed: bool = True
    ) -> list[str]:
        """Returns the list of entry names for a group within a section.

        Args:
            config_data: Configuration data dictionary
            section: name of the section for which to return entries
            group: name of the group for which to return entries
            only_exposed: if True only exposed entries are returned, if False
                every entry is

        Returns:
            The list of groups occurring within the given section.
        """
        # Import here to avoid circular dependency
        from gremlin.config_modules.metadata import ConfigurationMetadata
        metadata = ConfigurationMetadata()

        if only_exposed:
            return sorted(list(set(
                [key[2] for key in config_data.keys() if
                 key[0] == section and key[1] == group and
                 metadata.expose(config_data, section, group, key[2])]
            )))
        else:
            return sorted(list(set(
                [key[2] for key in config_data.keys() if
                    key[0] == section and key[1] == group]
            )))
