# Copyright 2018-2020 Jérôme Dumonteil
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
"""Manifest class for manifest.xml part
"""
from .element import Element
from .xmlpart import XmlPart
from .utils import to_str


class Manifest(XmlPart):
    def get_paths(self):
        """Return the list of full paths in the manifest.

        Return: list of str
        """
        expr = "//manifest:file-entry/attribute::manifest:full-path"
        return self.xpath(expr)

    def get_path_medias(self):
        """Return the list of (full_path, media_type) pairs in the manifest.

        Return: list of str tuples
        """
        expr = "//manifest:file-entry"
        result = []
        for file_entry in self.xpath(expr):
            result.append(
                (
                    file_entry.get_attribute("manifest:full-path"),
                    file_entry.get_attribute("manifest:media-type"),
                )
            )
        return result

    def get_media_type(self, full_path):
        """Get the media type of an existing path.

        Return: str
        """
        expr = (
            '//manifest:file-entry[attribute::manifest:full-path="%s"]'
            "/attribute::manifest:media-type"
        )
        result = self.xpath(expr % to_str(full_path))
        if not result:
            return None
        return to_str(result[0])

    def set_media_type(self, full_path, media_type):
        """Set the media type of an existing path.

        Arguments:

            full_path -- str

            media_type -- str
        """
        expr = '//manifest:file-entry[attribute::manifest:full-path="%s"]'
        result = self.xpath(expr % to_str(full_path))
        if not result:
            raise KeyError('path "%s" not found' % full_path)
        file_entry = result[0]
        file_entry.set_attribute("manifest:media-type", media_type)

    @staticmethod
    def make_file_entry(full_path, media_type):
        data = (
            f"<manifest:file-entry "
            f'manifest:media-type="{to_str(media_type)}" '
            f'manifest:full-path="{to_str(full_path)}"/>'
        )
        return Element.from_tag(data)

    def add_full_path(self, full_path, media_type=b""):
        # Existing?
        existing = self.get_media_type(full_path)
        if existing is not None:
            self.set_media_type(full_path, media_type)
        root = self.root
        root.append(self.make_file_entry(full_path, media_type))

    def del_full_path(self, full_path):
        expr = '//manifest:file-entry[attribute::manifest:full-path="%s"]'
        result = self.xpath(expr % to_str(full_path))
        if not result:
            raise KeyError('path "%s" not found' % full_path)
        file_entry = result[0]
        root = self.root
        root.delete(file_entry)
