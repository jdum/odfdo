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

from typing import TYPE_CHECKING, Union, cast

from .element import Element
from .style_base import StyleBase
from .style_containers import OfficeAutomaticStyles, OfficeMasterStyles
from .utils import is_RFC3066
from .xmlpart import XmlPart

if TYPE_CHECKING:
    from .master_page import StyleMasterPage


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
    """Representation of the "styles.xml" part of an ODF document.

    This class provides an interface to the styles defined in the "styles.xml"
    part of an ODF document, which includes automatic styles, master styles,
    and default styles.
    """

    def _get_style_contexts(
        self, family: str, automatic: bool = False
    ) -> list[Element]:
        """Get the XML contexts where styles are stored.

        Args:
            family: The style family to search for.
            automatic: Whether to only search in automatic styles.

        Returns:
            list[Element]: A list of XML elements that are contexts for styles.
        """
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

    def get_styles(self, family: str = "", automatic: bool = False) -> list[StyleBase]:
        """Return the list of styles in the Styles part.

        Optionally, the results can be limited to a specific family and/or
        to automatic styles.

        Args:
            family: The style family to filter by (e.g.,
                'paragraph', 'text').
            automatic: If True, only automatic styles are
                returned. Defaults to False.

        Returns:
            list[StyleBase]: A list of Style elements.
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
    def default_styles(self) -> list[StyleBase]:
        """Return the list of default styles ("style:default-style").

        Returns:
            list[StyleBase]: A list of default Style elements.
        """
        return cast(list[StyleBase], self.get_elements("//style:default-style"))

    def set_default_styles_language_country(self, value: str) -> None:
        """Set the default language and country in styles.

        Args:
            value: The language/country code in RFC3066 format (e.g., "en-US").

        Raises:
            TypeError: If the language code format is invalid.
        """
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
            props = style.get_properties(area="text") or {}
            props["language"] = lang
            props["country"] = country
            style.set_properties(props, area="text")

    @property
    def default_language(self) -> str:
        """Get or set the default language from styles, in "en-US" format."""
        styles = [s for s in self.default_styles if s.family == "paragraph"]
        if not styles:
            return ""
        style = styles[0]
        props = style.get_properties(area="text") or {}
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
        name_or_element: str | StyleBase | None = None,
        display_name: str | None = None,
    ) -> StyleBase | None:
        """Return the style uniquely identified by its family and name.

        If the `name_or_element` argument is already a Style object, it will be
        returned. If `name_or_element` is None, the default style for the given
        family is fetched. If the name provided is a display name, use the
        `display_name` argument instead.

        Args:
            family: The style family (e.g., 'paragraph', 'text', 'graphic').
            name_or_element: The internal name of the
                style or a Style object itself.
            display_name: The display name of the style as seen in an
                office application.

        Returns:
            StyleBase | None: The matching Style object, or None if not found.
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

    @property
    def office_master_styles(self) -> OfficeMasterStyles | None:
        """Get or set the "office:master-styles" element.

        Returns:
            OfficeMasterStyles | None: The "office:master-styles" element, or None if not found.
        """
        return cast(
            Union[None, OfficeMasterStyles], self.get_element("//office:master-styles")
        )
        return cast(
            Union[None, OfficeMasterStyles], self.get_element("//office:master-styles")
        )

    @office_master_styles.setter
    def office_master_styles(self, office_master_styles: OfficeMasterStyles) -> None:
        """Set the "office:master-styles" element.

        Args:
            office_master_styles: The "office:master-styles" element to set.
        """
        current = self.office_master_styles
        if isinstance(current, OfficeMasterStyles):
            current.delete()
        self.root.append(office_master_styles)

    @property
    def master_pages(self) -> list[StyleMasterPage]:
        """Get the list of master pages.

        Returns:
            list[StyleMasterPage]: A list of StyleMasterPage elements.
        """
        master_styles = self.office_master_styles
        if master_styles is None:
            return []
        return [
            e  # type: ignore[misc]
            for e in master_styles.children
            if isinstance(e, StyleBase) and e.tag == "style:master-page"
        ]

    def get_master_page(self, position: int = 0) -> StyleMasterPage | None:
        """Get a master page by its position.

        Args:
            position: The position (index) of the master page. Defaults to 0.

        Returns:
            StyleMasterPage | None: The StyleMasterPage element at the given position,
            or None if not found.
        """
        results = self.master_pages
        try:
            return results[position]
        except IndexError:
            return None

    @property
    def office_automatic_styles(self) -> OfficeAutomaticStyles | None:
        """Get or set the "office:automatic-styles" element.

        Returns:
            OfficeAutomaticStyles | None: The "office:automatic-styles" element,
            or None if not found.
        """
        return cast(
            Union[None, OfficeAutomaticStyles],
            self.get_element("//office:automatic-styles"),
        )

    @office_automatic_styles.setter
    def office_automatic_styles(
        self, office_automatic_styles: OfficeAutomaticStyles
    ) -> None:
        """Set the "office:automatic-styles" element.

        Args:
            office_automatic_styles: The "office:automatic-styles"
                element to set.
        """
        current = self.office_automatic_styles
        if isinstance(current, OfficeAutomaticStyles):
            current.delete()
        self.root.append(office_automatic_styles)
