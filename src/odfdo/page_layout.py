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

from typing import Any, ClassVar, Union, cast

from .element import Element, PropDef, PropDefBool, register_element_class
from .style_base import StyleBase
from .style_props import StyleProps
from .style_utils import (
    _set_background,
)


class StylePageLayout(StyleProps):
    """The "style:page-layout" element represents the styles that specify the
    formatting properties of a page.

    The "style:page-layout" element is usable within the following element:
    "office:automatic-styles".
    """

    # The "style:page-layout" element has the following attributes:
    # style:name
    # style:page-usage

    _tag: str = "style:page-layout"
    _properties: tuple[PropDef | PropDefBool, ...] = (PropDef("name", "style:name"),)
    PAGE_USAGE: ClassVar = {"all", "left", "right", "mirrored"}

    def __init__(
        self,
        name: str | None = None,
        page_usage: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a StylePageLayout element.

        The `name` is not mandatory at creation but becomes required when
        inserting into a document as an automatic style.

        Args:
            name: The name of the page layout style.
            page_usage: The type of pages the layout applies to.
                Allowed values are "all" (default), "left", "mirrored", "right".
            **kwargs: Additional keyword arguments for the parent `Element` class.
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
        """Get the family of the style.

        For `StylePageLayout`, this is always "page-layout".

        Returns:
            str | None: The family name.
        """
        return self._family

    @family.setter
    def family(self, family: str | None) -> None:
        """Setter for the family property (no-op as family is fixed)."""
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} family={self.family} name={self.name}>"

    @property
    def page_usage(self) -> str:
        """Get the `style:page-usage` attribute.

        Specifies the type of pages that a page master should generate.

        Returns:
            str: The page usage type. Defaults to "all".
        """
        return self._get_attribute_str_default("style:page-usage", "all")

    @page_usage.setter
    def page_usage(self, page_usage: str | None) -> None:
        """Set the `style:page-usage` attribute.

        Args:
            page_usage: The page usage type. Allowed values are
                "all", "left", "right", "mirrored". Invalid values default to "all".
        """
        if page_usage not in self.PAGE_USAGE:
            page_usage = "all"
        self._set_attribute_str_default("style:page-usage", page_usage, "all")

    def get_properties(
        self, area: str | None = "page-layout"
    ) -> dict[str, str | dict] | None:
        """Retrieve the page-layout properties of the `StylePageLayout`.

        Args:
            area: The area for which to retrieve properties.
                (Parameter is kept for compatibility but internally fixed to "page-layout").

        Returns:
            dict[str, str | dict] | None: A dictionary mapping property names to their values.
        """
        return super().get_properties(area="page-layout")

    def set_properties(
        self,
        properties: dict[str, str | dict] | None = None,
        style: StyleBase | None = None,
        area: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the properties for the page-layout.

        Properties can be provided either as a dictionary, as a `StyleBase` object,
        or as keyword arguments. The `area` is internally fixed to "page-layout".

        Args:
            properties: A dictionary of properties to set.
            style: A `StyleBase` object from which to copy properties.
            area: The area for which to set properties.
                (Parameter is kept for compatibility but internally fixed to "page-layout").
            **kwargs: Additional keyword arguments for properties to set.
        """
        return super().set_properties(
            properties=properties, style=style, area="page-layout", **kwargs
        )

    def del_properties(
        self,
        properties: list[str] | None = None,
        area: str | None = None,
    ) -> None:
        """Delete specific properties from the page-layout.

        Args:
            properties: A list of property names to delete.
            area: The area from which to delete properties.
                (Parameter is kept for compatibility but internally fixed to "page-layout").
        """
        return super().del_properties(properties=properties, area="page-layout")

    def set_background(
        self,
        color: str | None = None,
        url: str | None = None,
        position: str | None = "center",
        repeat: str | None = None,
        opacity: str | int | None = None,
        filter: str | None = None,  # noqa: A002
    ) -> None:
        """Set the background properties for the page layout.

        This can configure a background color or an image. If no arguments are
        provided, any existing background is removed.

        Args:
            color: The background color in '#RRGGBB' format.
            url: The URL of a background image.
            position: The position of the background image. Can be
                "left", "center", "right", "top", "bottom", or a combination
                of two (e.g., "top center"). Defaults to "center".
            repeat: How the background image repeats. Can be
                "no-repeat", "repeat", or "stretch".
            opacity: The opacity of the background image as
                a percentage integer (0-100).
            filter: An application-specific filter name for the background image.
        """
        _set_background(self, color, url, position, repeat, opacity, filter)

    def get_header_style(self) -> StyleBase | None:
        """Get the `style:header-style` element within the page layout.

        Returns:
            StyleBase | None: The `StyleBase` instance representing the header
                style, or `None` if no header style is defined.
        """
        return cast(Union[None, StyleBase], self.get_element("style:header-style"))

    def set_header_style(self, new_style: StyleBase) -> None:
        """Set or replace the `style:header-style` element within the page layout.

        Args:
            new_style: The new header style to set.
        """
        header_style = self.get_header_style()
        if header_style is not None:
            self.delete(header_style)
        self.append(new_style)

    def get_footer_style(self) -> StyleBase | None:
        """Get the `style:footer-style` element within the page layout.

        Returns:
            StyleBase | None: The `StyleBase` instance representing the footer
                style, or `None` if no footer style is defined.
        """
        return cast(Union[None, StyleBase], self.get_element("style:footer-style"))

    def set_footer_style(self, new_style: StyleBase) -> None:
        """Set or replace the `style:footer-style` element within the page layout.

        Args:
            new_style: The new footer style to set.
        """
        footer_style = self.get_footer_style()
        if footer_style is not None:
            self.delete(footer_style)
        self.append(new_style)


StylePageLayout._define_attribut_property()


register_element_class(StylePageLayout)
