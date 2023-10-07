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
# Authors: Hervé Cauwelier <herve@itaapy.com>
#          Romain Gauthier <romain@itaapy.com>
"""Styles class for styles.xml part
"""
from .xmlpart import XmlPart
from .utils import _get_elements, _get_element

CONTEXT_MAPPING = {
    "paragraph": ("//office:styles", "//office:automatic-styles"),
    "text": ("//office:styles",),
    "graphic": ("//office:styles",),
    "page-layout": ("//office:automatic-styles",),
    "master-page": ("//office:master-styles",),
    "font-face": ("//office:font-face-decls",),
    "outline": ("//office:styles",),
    "date": ("//office:automatic-styles",),
    "list": ("//office:styles",),
    "presentation": ("//office:styles", "//office:automatic-styles"),
    "drawing-page": ("//office:automatic-styles",),
    "presentation-page-layout": ("//office:styles",),
    "marker": ("//office:styles",),
    "fill-image": ("//office:styles",),
    # FIXME Do they?
    "table": ("//office:automatic-styles",),
    "table-cell": ("//office:automatic-styles",),
    "table-row": ("//office:automatic-styles",),
    "table-column": ("//office:automatic-styles",),
    # FIXME: to test:
    "section": ("//office:styles", "//office:automatic-styles"),
    "chart": ("//office:styles", "//office:automatic-styles"),
}


class Styles(XmlPart):
    def _get_style_contexts(self, family, automatic=False):
        if automatic:
            return (self.get_element("//office:automatic-styles"),)
        if not family:
            # All possibilities
            return (
                self.get_element("//office:automatic-styles"),
                self.get_element("//office:styles"),
                self.get_element("//office:master-styles"),
                self.get_element("//office:font-face-decls"),
            )
        queries = CONTEXT_MAPPING.get(family)
        if queries is None:
            raise ValueError(f"unknown family: {family}")
        # print('q:', queries)
        return [self.get_element(query) for query in queries]

    def get_styles(self, family="", automatic=False):
        """Return the list of styles in the Content part, optionally limited
        to the given family, optionaly limited to automatic styles.

        Arguments:

            family -- str

            automatic -- bool

        Return: list of Style
        """
        result = []
        for context in self._get_style_contexts(family, automatic=automatic):
            if context is None:
                continue
            # print('-ctx----', automatic)
            # print(context.tag)
            # print(context.__class__)
            # print(context.serialize())
            result.extend(context.get_styles(family=family))
        return result

    def get_style(self, family, name_or_element=None, display_name=None):
        """Return the style uniquely identified by the name/family pair. If
        the argument is already a style object, it will return it.

        If the name is None, the default style is fetched.

        If the name is not the internal name but the name you gave in the
        desktop application, use display_name instead.

        Arguments:

            name_or_element -- unicode, odf_style or None

            family -- 'paragraph', 'text',  'graphic', 'table', 'list',
                      'number', 'page-layout', 'master-page'

            display_name -- unicode

        Return: odf_style or None if not found
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

    def get_master_pages(self):
        return _get_elements(self, "descendant::style:master-page")

    def get_master_page(self, position=0):
        return _get_element(self, "descendant::style:master-page", position)
