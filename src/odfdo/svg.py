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
"""SvgTitle and SvgDescription classes for "svg:title" and "svg:desc" tags."""

from __future__ import annotations

from typing import Any

from .element import Element, PropDef, PropDefBool, register_element_class


class SvgMixin(Element):
    """Mixin class for elements that can contain "svg:title" and "svg:desc".

    This mixin provides methods to access and manipulate SvgTitle and
    SvgDescription.

    Used by the following implemented classes:
        - "draw:connector"
        - "draw:ellipse"
        - "draw:frame"
        - "draw:g"
        - "draw:line"
        - "draw:page"
        - "draw:rect"
    """

    @property
    def svg_title(self) -> str | None:
        """Get or set the SVG title of the element.

        Returns:
            str | None: The title string, or None if not present.
        """
        return self._get_inner_text("svg:title")

    @svg_title.setter
    def svg_title(self, title: str) -> None:
        self._set_inner_text("svg:title", title)

    @property
    def svg_description(self) -> str | None:
        """Get or set the SVG description of the element.

        Returns:
            str | None: The description string, or None if not present.
        """
        return self._get_inner_text("svg:desc")

    @svg_description.setter
    def svg_description(self, description: str) -> None:
        self._set_inner_text("svg:desc", description)


class SvgTitle(Element):
    """Store a name for a graphic object.

    The "svg:title" element has no ODF attributes, but the following property:

    Attributes:
        title (str): the name stored by the SvgTitle.
    """

    _tag: str = "svg:title"
    _properties: tuple[PropDef | PropDefBool, ...] = ()

    def __init__(self, title: str | None = None, **kwargs: Any) -> None:
        """Create a SvgTitle, "svg:title".

        The "svg:title" element is usable within the following elements:
        "dr3d:scene", "draw:area-circle", "draw:area-polygon",
        "draw:area-rectangle", "draw:caption", "draw:circle",
        "draw:connector", "draw:control", "draw:custom-shape",
        "draw:ellipse", "draw:frame", "draw:g", "draw:layer", "draw:line",
        "draw:measure", "draw:page", "draw:page-thumbnail", "draw:path",
        "draw:polygon", "draw:polyline", "draw:rect" and
        "draw:regular-polygon".

        Args:
            title: The name stored by the SvgTitle.
        """
        super().__init__(**kwargs)
        if title is not None:
            self.title = title

    @property
    def title(self) -> str:
        """Get or set the name stored by the SvgTitle.

        Returns:
            str: The name stored.
        """
        return self.text

    @title.setter
    def title(self, title: str) -> None:
        self.text = title

    def get_formatted_text(self, context: dict | None = None) -> str:
        return f"{self.title}\n"


class SvgDescription(Element):
    """Store a prose description of a graphic object that may be used to
    support accessibility.

    The "svg:desc" element has no ODF attributes, but the following property:

    Attributes:
        description (str): the description stored by the SvgDescription.
    """

    _tag: str = "svg:desc"
    _properties: tuple[PropDef | PropDefBool, ...] = ()

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        """Create a SvgDescription, "svg:desc".

        The "svg:desc" element is usable within the following elements:
        "dr3d:scene", "draw:area-circle", "draw:area-polygon",
        "draw:area-rectangle", "draw:caption", "draw:circle",
        "draw:connector", "draw:control", "draw:custom-shape",
        "draw:ellipse", "draw:frame", "draw:g", "draw:layer", "draw:line",
        "draw:measure", "draw:page", "draw:page-thumbnail", "draw:path",
        "draw:polygon", "draw:polyline", "draw:rect" and
        "draw:regular-polygon".

        Args:
            description: The description stored by the SvgDescription.
        """
        super().__init__(**kwargs)
        if description is not None:
            self.description = description

    @property
    def description(self) -> str:
        """Get or set the description stored by the SvgTitle.

        Returns:
            str: The description stored.
        """
        return self.text

    @description.setter
    def description(self, description: str) -> None:
        self.text = description

    def get_formatted_text(self, context: dict | None = None) -> str:
        return f"{self.text}\n"


register_element_class(SvgTitle)
register_element_class(SvgDescription)
