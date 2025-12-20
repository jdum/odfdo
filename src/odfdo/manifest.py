# Copyright 2018-2025 Jérôme Dumonteil
# Copyright (c) 2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Authors (odfdo project): jerome.dumonteil@gmail.com
# The odfdo project is a derivative work of the lpod-python project:
# https://github.com/lpod/lpod-python
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
"""Representation of the "manifest.xml" part."""

from __future__ import annotations

from .element import Element
from .xmlpart import XmlPart


class Manifest(XmlPart):
    """Representation of the "manifest.xml" part."""

    def get_paths(self) -> list[str]:
        """Get a list of all full paths (`manifest:full-path`) declared in the manifest.

        Returns:
            list[str]: A list of strings, where each string is a full path.
        """
        xpath_query = "//manifest:file-entry/attribute::manifest:full-path"
        return [str(e) for e in self.xpath(xpath_query)]  # Explicitly cast EText to str

    def _file_entry(self, full_path: str) -> Element:
        """Internal helper to find a specific `manifest:file-entry` element.

        Args:
            full_path: The full path of the file entry to find.

        Returns:
            Element: The `manifest:file-entry` element.

        Raises:
            KeyError: If the specified `full_path` is not found in the manifest.
        """
        xpath_query = (
            f'//manifest:file-entry[attribute::manifest:full-path="{full_path}"]'
        )
        result = self.xpath(xpath_query)
        if not result:
            raise KeyError(f"Path not found: '{full_path}'")
        return result[0]  # type: ignore

    def get_path_medias(self) -> list[tuple[str | None, str | None]]:
        """Get a list of all (full_path, media_type) pairs declared in the manifest.

        Returns:
            list[tuple[str | None, str | None]]: A list of tuples, where each
                tuple contains the full path and its corresponding media type.
                Attribute values can be `None` if not found.
        """
        xpath_query = "//manifest:file-entry"
        result = []
        for file_entry in self.xpath(xpath_query):
            if not isinstance(file_entry, Element):  # pragma: no cover
                continue
            result.append(
                (
                    file_entry.get_attribute_string("manifest:full-path"),
                    file_entry.get_attribute_string("manifest:media-type"),
                )
            )
        return result

    def get_media_type(self, full_path: str) -> str | None:
        """Get the media type associated with a specific full path in the manifest.

        Args:
            full_path: The full path of the file entry.

        Returns:
            str | None: The media type string, or `None` if the path is not found.
        """
        xpath_query = (
            f'//manifest:file-entry[attribute::manifest:full-path="{full_path}"]'
            "/attribute::manifest:media-type"
        )
        result = self.xpath(xpath_query)
        if not result:
            return None
        return str(result[0])

    def set_media_type(self, full_path: str, media_type: str) -> None:
        """Set the media type for an existing file entry in the manifest.

        Args:
            full_path: The full path of the file entry.
            media_type: The new media type to set.
        """
        file_entry = self._file_entry(full_path)
        file_entry.set_attribute("manifest:media-type", media_type)

    @staticmethod
    def make_file_entry(full_path: str, media_type: str) -> Element:
        """Create a new `manifest:file-entry` element.

        Args:
            full_path: The full path for the file entry.
            media_type: The media type for the file entry.

        Returns:
            Element: A new `manifest:file-entry` element.
        """
        tag = (
            f"<manifest:file-entry "
            f'manifest:media-type="{media_type}" '
            f'manifest:full-path="{full_path}"/>'
        )
        return Element.from_tag(tag)

    def add_full_path(self, full_path: str, media_type: str = "") -> None:
        """Add a new file entry to the manifest, or update an existing one.

        If a file entry with the given `full_path` already exists, its media
        type is updated. Otherwise, a new `manifest:file-entry` element is
        created and added.

        Args:
            full_path: The full path of the file to add or update.
            media_type: The media type of the file.
        """
        # Existing?
        existing = self.get_media_type(full_path)
        if existing is not None:
            self.set_media_type(full_path, media_type)
        root = self.root
        root.append(self.make_file_entry(full_path, media_type))

    def del_full_path(self, full_path: str) -> None:
        """Delete a file entry from the manifest.

        Args:
            full_path: The full path of the file entry to delete.

        Raises:
            KeyError: If the specified `full_path` is not found in the manifest.
        """
        file_entry = self._file_entry(full_path)
        self.root.delete(file_entry)
