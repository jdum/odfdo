# Copyright 2018-2025 Jérôme Dumonteil
# Copyright (c) 2009-2013 Ars Aperta, Itaapy, Pierlis, Talend.
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
"""Classes related to "style:page-layout"."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .element import Element, PropDef, register_element_class
from .style_base import StyleBase
from .style_utils import (
    _expand_properties_dict,
    _expand_properties_list,
    _merge_dicts,
    _set_background,
)

if TYPE_CHECKING:
    pass


class StylePageLayout(StyleBase):
    """The "style:page-layout" element represents the styles that specify the
    formatting properties of a page.

    The "style:page-layout" element is usable within the following element:
    "office:automatic-styles".
    """

    # The "style:page-layout" element has the following attributes:
    # style:name
    # style:page-usage

    _tag: str = "style:page-layout"
    _properties: tuple[PropDef, ...] = (
        PropDef("name", "style:name"),
        PropDef("page_usage", "style:page-usage"),
    )

    def __init__(
        self,
        name: str | None = None,
        page_usage: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a StylePageLayout.

        The name is not mandatory at this point but will become required when inserting in a document as a automatic style.

        The page_usage attribute specifies the type of pages that a page master should generate. Allowed values are: "all" (default), "left", "mirrored", "right".

        To set properties, pass them as keyword arguments.

        Args:

            name -- str

            page_usage -- str
        """
        self._family = "page-layout"
        tag_or_elem = kwargs.get("tag_or_elem")
        if tag_or_elem is None:
            kwargs["tag"] = "style:page-layout"
        Element.__init__(self, **kwargs)
        if self._do_init:
            kwargs.pop("tag", None)
            kwargs.pop("tag_or_elem", None)
            if name:
                self.name = name
            if page_usage:
                self.page_usage = page_usage

    @property
    def family(self) -> str | None:
        return self._family

    @family.setter
    def family(self, family: str | None) -> None:
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} family={self.family} name={self.name}>"

    @property
    def page_usage(self) -> str:
        return self._get_attribute_str_default("style:page-usage", "all")

    @page_usage.setter
    def page_usage(self, page_usage: str | None) -> None:
        self._set_attribute_str_default("style:page-usage", page_usage, "all")

    def get_properties(
        self, area: str | None = "page-layout"
    ) -> dict[str, str | dict] | None:
        """Get the mapping of page-layout properties of StylePageLayout.

        Args:

            area -- str (unused, kept for compatibility)

        Returns: dict
        """
        area = "page-layout"
        element = self.get_element(f"style:{area}-properties")
        if element is None:
            return None
        properties: dict[str, str | dict[str, Any]] = element.attributes  # type: ignore
        # Nested properties are nested dictionaries
        for child in element.children:
            properties[child.tag] = child.attributes
        return properties

    @staticmethod
    def _update_boolean_styles(props: dict[str, str | bool]) -> None:
        strike = props.get("style:text-line-through-style", "")
        if strike == "none":
            strike = ""
        underline = props.get("style:text-underline-style", "")
        if underline == "none":
            underline = ""
        props.update(
            {
                "color": props.get("fo:color") or "",
                "background_color": props.get("fo:background-color") or "",
                "italic": props.get("fo:font-style", "") == "italic",
                "bold": props.get("fo:font-weight", "") == "bold",
                "fixed": props.get("style:font-pitch", "") == "fixed",
                "underline": bool(underline),
                "strike": bool(strike),
            }
        )

    def get_list_style_properties(self) -> dict[str, str | bool]:
        """Get text properties of style as a dict, with some enhanced values.

        Enhanced values returned:
         - "color": str
         - "background_color": str
         - "italic": bool
         - "bold": bool
         - "fixed": bool
         - "underline": bool
         - "strike": bool

        Returns: dict[str, str | bool]
        """
        return self.get_text_properties()

    def get_text_properties(self) -> dict[str, str | bool]:
        """Get text properties of style as a dict, with some enhanced values.

        Enhanced values returned:
         - "color": str
         - "background_color": str
         - "italic": bool
         - "bold": bool
         - "fixed": bool
         - "underline": bool
         - "strike": bool

        Returns: dict[str, str | bool]
        """
        props = self.get_properties(area="text") or {}
        self._update_boolean_styles(props)  # type: ignore[arg-type]
        return props  # type: ignore[return-value]

    def set_properties(
        self,
        properties: dict[str, str | dict] | None = None,
        style: StyleBase | None = None,
        area: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the properties of the page-layout.

        Properties are given either as a dict or as named arguments (or both). The area is identical to the style family by default. If the properties element is missing, it is created.

        Instead of properties, you can pass a style with properties of a page-layout style. These will be copied.

        Args:

            properties -- dict

            style -- StylePageLayout

            area -- "page-layout"
        """
        if properties is None:
            properties = {}
        area = "page-layout"
        element = self.get_element(f"style:{area}-properties")
        if element is None:
            element = Element.from_tag(f"style:{area}-properties")
            self.append(element)
        if properties or kwargs:
            properties = _expand_properties_dict(_merge_dicts(properties, kwargs))
        elif style is not None:
            properties = style.get_properties()
            if properties is None:
                return
        if properties is None:
            return
        for key, value in properties.items():
            if value is None:
                element.del_attribute(key)
            elif isinstance(value, (str, bool, tuple)):
                element.set_attribute(key, value)

    def del_properties(
        self,
        properties: list[str] | None = None,
        area: str | None = None,
    ) -> None:
        """Delete the given properties, either by list argument or positional
        argument (or both).

        Args:

            properties -- list

            area -- "page-layout"
        """
        if properties is None:
            properties = []
        area = "page-layout"
        element = self.get_element(f"style:{area}-properties")
        if element is None:
            raise ValueError(
                f"properties element is inexistent for: style:{area}-properties"
            )
        for key in _expand_properties_list(properties):
            element.del_attribute(key)

    def set_background(
        self,
        color: str | None = None,
        url: str | None = None,
        position: str | None = "center",
        repeat: str | None = None,
        opacity: str | int | None = None,
        filter: str | None = None,  # noqa: A002
    ) -> None:
        """Set the background color of the page layout.

        With no argument, remove any existing background.

        The values of the position attribute are "left", "center", "right", "top", "bottom", or two white space separated values, that may appear in any order. One of these values is one of: "left", "center" or "right". The other value is one of: "top", "center" or "bottom". The default value for this attribute is "center".

        The repeat value is one of 'no-repeat', 'repeat' or 'stretch'.

        The opacity is a percentage integer (not a string with the '%' sign)

        The filter is an application-specific filter name defined elsewhere.

        Args:

            color -- '#rrggbb'

            url -- str

            position -- str

            repeat -- str

            opacity -- int

            filter -- str
        """
        _set_background(self, color, url, position, repeat, opacity, filter)

    def get_header_style(self) -> StyleBase | None:
        return self.get_element("style:header-style")  # type: ignore

    def set_header_style(self, new_style: StyleBase) -> None:
        header_style = self.get_header_style()
        if header_style is not None:
            self.delete(header_style)
        self.append(new_style)

    def get_footer_style(self) -> StyleBase | None:
        return self.get_element("style:footer-style")  # type: ignore

    def set_footer_style(self, new_style: StyleBase) -> None:
        footer_style = self.get_footer_style()
        if footer_style is not None:
            self.delete(footer_style)
        self.append(new_style)


StylePageLayout._define_attribut_property()


register_element_class(StylePageLayout)
