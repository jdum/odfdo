# Copyright 2018-2024 Jérôme Dumonteil
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
"""Manifest class for manifest.xml part.
"""
from __future__ import annotations

from .element import Element, Text
from .xmlpart import XmlPart


class Manifest(XmlPart):
    def get_paths(self) -> list[Element | Text]:
        """Return the list of full paths in the manifest.

        Return: list of str
        """
        xpath_query = "//manifest:file-entry/attribute::manifest:full-path"
        return self.xpath(xpath_query)

    def _file_entry(self, full_path: str) -> Element:
        xpath_query = (
            f'//manifest:file-entry[attribute::manifest:full-path="{full_path}"]'
        )
        result = self.xpath(xpath_query)
        if not result:
            raise KeyError(f"Path not found: '{full_path}'")
        return result[0]  # type: ignore

    def get_path_medias(self) -> list[tuple]:
        """Return the list of (full_path, media_type) pairs in the manifest.

        Return: list of str tuples
        """
        xpath_query = "//manifest:file-entry"
        result = []
        for file_entry in self.xpath(xpath_query):
            if not isinstance(file_entry, Element):
                continue
            result.append(
                (
                    file_entry.get_attribute_string("manifest:full-path"),
                    file_entry.get_attribute_string("manifest:media-type"),
                )
            )
        return result

    def get_media_type(self, full_path: str) -> str | None:
        """Get the media type of an existing path.

        Return: str
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
        """Set the media type of an existing path.

        Arguments:

            full_path -- str

            media_type -- str
        """
        file_entry = self._file_entry(full_path)
        file_entry.set_attribute("manifest:media-type", media_type)

    @staticmethod
    def make_file_entry(full_path: str, media_type: str) -> Element:
        tag = (
            f"<manifest:file-entry "
            f'manifest:media-type="{media_type}" '
            f'manifest:full-path="{full_path}"/>'
        )
        return Element.from_tag(tag)

    def add_full_path(self, full_path: str, media_type: str = "") -> None:
        # Existing?
        existing = self.get_media_type(full_path)
        if existing is not None:
            self.set_media_type(full_path, media_type)
        root = self.root
        root.append(self.make_file_entry(full_path, media_type))

    def del_full_path(self, full_path: str) -> None:
        file_entry = self._file_entry(full_path)
        self.root.delete(file_entry)
