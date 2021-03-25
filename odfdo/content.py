# Copyright 2018-2020 Jérôme Dumonteil
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
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
#          Romain Gauthier <romain@itaapy.com>
"""Content class for content.xml part
"""
from .xmlpart import XmlPart


class Content(XmlPart):
    @property
    def body(self):
        return self.root.document_body

    # The following two seem useless but they match styles API

    def _get_style_contexts(self, family):
        if family == "font-face":
            return (self.get_element("//office:font-face-decls"),)
        return (
            self.get_element("//office:font-face-decls"),
            self.get_element("//office:automatic-styles"),
        )

    # Public API

    def get_styles(self, family=None):
        """Return the list of styles in the Content part, optionally limited
        to the given family.

        Arguments:

            family -- str

        Return: list of Style
        """
        result = []
        for context in self._get_style_contexts(family):
            if context is None:
                continue
            result.extend(context.get_styles(family=family))
        return result

    def get_style(self, family, name_or_element=None, display_name=None):
        """Return the style uniquely identified by the name/family pair. If
        the argument is already a style object, it will return it.

        If the name is None, the default style is fetched.

        If the name is not the internal name but the name you gave in the
        desktop application, use display_name instead.

        Arguments:

            family -- 'paragraph', 'text', 'graphic', 'table', 'list',
                      'number'

            name_or_element -- str or Style

            display_name -- str

        Return: Style or None if not found
        """
        for context in self._get_style_contexts(family):
            if context is None:
                continue
            style = context.get_style(
                family, name_or_element=name_or_element, display_name=display_name
            )
            if style is not None:
                return style
        return None
