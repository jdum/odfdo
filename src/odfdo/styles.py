# Copyright 2018-2025 Jérôme Dumonteil
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
"""Representation of the "styles.xml" part."""

from __future__ import annotations

from .element import Element
from .style import Style
from .utils import is_RFC3066, make_xpath_query
from .xmlpart import XmlPart

CONTEXT_MAPPING = {
    "paragraph": ("//office:styles", "//office:automatic-styles"),
    "text": ("//office:styles", "//office:automatic-styles"),
    "graphic": ("//office:styles", "//office:automatic-styles"),
    "page-layout": ("//office:automatic-styles",),
    "master-page": ("//office:master-styles",),
    "font-face": ("//office:font-face-decls",),
    "outline": ("//office:styles", "//office:automatic-styles"),
    "date": ("//office:styles", "//office:automatic-styles"),
    "list": ("//office:styles", "//office:automatic-styles"),
    "presentation": ("//office:styles", "//office:automatic-styles"),
    "drawing-page": ("//office:automatic-styles",),
    "presentation-page-layout": ("//office:styles",),
    "marker": ("//office:styles",),
    "fill-image": ("//office:styles",),
    # FIXME Do they?
    "table": ("//office:styles", "//office:automatic-styles"),
    "table-cell": ("//office:styles", "//office:automatic-styles"),
    "table-row": ("//office:styles", "//office:automatic-styles"),
    "table-column": ("//office:styles", "//office:automatic-styles"),
    # FIXME: to test:
    "section": ("//office:styles", "//office:automatic-styles"),
    "chart": ("//office:styles", "//office:automatic-styles"),
}


class Styles(XmlPart):
    """Representation of the "styles.xml" part."""

    def _get_style_contexts(
        self, family: str, automatic: bool = False
    ) -> list[Element]:
        if automatic:
            elems = [self.get_element("//office:automatic-styles")]
        elif family:
            queries = CONTEXT_MAPPING.get(family) or (
                "//office:styles",
                "//office:automatic-styles",
            )
            elems = [self.get_element(query) for query in queries]
        else:
            # All possibilities
            elems = [
                self.get_element("//office:automatic-styles"),
                self.get_element("//office:styles"),
                self.get_element("//office:master-styles"),
                self.get_element("//office:font-face-decls"),
            ]
        return [e for e in elems if isinstance(e, Element)]

    def get_styles(self, family: str = "", automatic: bool = False) -> list[Element]:
        """Return the list of styles in the Content part, optionally limited
        to the given family, optionaly limited to automatic styles.

        Arguments:

            family -- str

            automatic -- bool

        Return: list of Style
        """
        result = []
        for context in self._get_style_contexts(family, automatic=automatic):
            if context is None:  # pragma: nocover
                continue
            # print('-ctx----', automatic)
            # print(context.tag)
            # print(context.__class__)
            # print(context.serialize())
            result.extend(context.get_styles(family=family))
        return result

    @property
    def default_styles(self) -> list[Style]:
        """Return the list of default styles "style:default-styles".

        Return: list of Style
        """
        result: list[Style] = self.get_elements("//style:default-style")
        return result

    def set_default_styles_language_country(self, value: str) -> None:
        """Set the default language in styles, in format "en-US"."""
        language = str(value)
        if not is_RFC3066(language):
            msg = 'Language must be "xx" lang or "xx-YY" lang-COUNTRY code (RFC3066)'
            raise TypeError(msg)
        lc = language.split("-")
        if len(lc) == 2:
            lang, country = lc
        else:
            lang = lc[0]
            country = ""
        styles = [
            s for s in self.default_styles if s.family in {"graphic", "paragraph"}
        ]
        for style in styles:
            props = style.get_properties(area="text")
            props["language"] = lang
            props["country"] = country
            style.set_properties(props, area="text")

    @property
    def default_language(self) -> str:
        """Get or set the default language from styles, in format "en-US"."""
        styles = [s for s in self.default_styles if s.family == "paragraph"]
        if not styles:
            return ""
        style = styles[0]
        props = style.get_properties(area="text")
        lang = str(props.get("fo:language", ""))
        country = str(props.get("fo:country", ""))
        if lang and country:
            return f"{lang}-{country}"
        return lang or country

    @default_language.setter
    def default_language(self, value: str) -> None:
        return self.set_default_styles_language_country(value)

    def get_style(
        self,
        family: str,
        name_or_element: str | Style | None = None,
        display_name: str | None = None,
    ) -> Style | None:
        """Return the style uniquely identified by the name/family pair. If
        the argument is already a style object, it will return it.

        If the name is None, the default style is fetched.

        If the name is not the internal name but the name you gave in the
        desktop application, use display_name instead.

        Arguments:

            family -- 'paragraph', 'text',  'graphic', 'table', 'list',
                      'number', 'page-layout', 'master-page'

            name_or_element -- str, odf_style or None

            display_name -- str or None

        Return: odf_style or None if not found
        """
        for context in self._get_style_contexts(family):
            if context is None:
                continue  # pragma: nocover
            style = context.get_style(
                family,
                name_or_element=name_or_element,
                display_name=display_name,
            )
            if style is not None:
                return style
        return None

    def get_master_pages(self) -> list[Element]:
        query = make_xpath_query("descendant::style:master-page")
        elems = self.get_elements(query)
        return [e for e in elems if isinstance(e, Element)]

    def get_master_page(self, position: int = 0) -> Element | None:
        results = self.get_master_pages()
        try:
            return results[position]
        except IndexError:
            return None
