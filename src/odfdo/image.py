# Copyright 2018-2026 Jérôme Dumonteil
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
"""DrawImage class for "draw:image" tag, DrawFillImage for "draw:fill-image"
tag, and DrawMarker for "draw:marker" tag.
"""

from __future__ import annotations

from typing import Any

from .element import Element, PropDef, PropDefBool, register_element_class
from .mixin_list import ListMixin


class DrawImage(ListMixin, Element):
    """An ODF image, "draw:image".

    The "draw:image" element represents an image. An image can be either a link
    to an external resource or most often embedded into the document.
    """

    _tag = "draw:image"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("url", "xlink:href"),
        PropDef("xlink_type", "xlink:type"),
        PropDef("show", "xlink:show"),
        PropDef("actuate", "xlink:actuate"),
        PropDef("filter_name", "draw:filter-name"),
        PropDef("mime_type", "draw:mime-type"),
        PropDef("xml_id", "xml:id"),
    )

    def __init__(
        self,
        url: str = "",
        xlink_type: str = "simple",
        show: str = "embed",
        actuate: str = "onLoad",
        filter_name: str | None = None,
        mime_type: str | None = None,
        xml_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize an ODF image, "draw:image".

        The `draw:image` element represents an image. It can be a link to an
        external resource or, more commonly, embedded within the document.

        When an image is embedded, the `url` parameter should be a reference
        to the local document, typically obtained by adding the image file
        (e.g., `url = document.add_file(image_path)`).

        Warning: Image elements should generally be stored within a `draw:frame`
        element (see `Frame` class).

        Args:
            url: The URL or internal path of the image.
            xlink_type: The XLink type, usually "simple".
            show: How the image should be shown, usually "embed".
            actuate: When the image should be loaded, usually "onLoad".
            filter_name: An optional filter name to apply to the image.
            mime_type: The MIME type of the image's content.
            xml_id: The unique XML ID.
            **kwargs: Additional keyword arguments for the parent `Element` class.
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.url = url
            self.xlink_type = xlink_type
            self.show = show
            self.actuate = actuate
            self.filter_name = filter_name
            self.mime_type = mime_type
            self.xml_id = xml_id

    def __str__(self) -> str:
        return f"({self.url})"


DrawImage._define_attribut_property()


class DrawFillImage(Element):
    """A link to a bitmap resource, "draw:fill-image"."""

    _tag = "draw:fill-image"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "draw:name"),
        PropDef("display_name", "draw:display-name"),
        PropDef("height", "svg:height"),
        PropDef("width", "svg:width"),
        PropDef("url", "xlink:href"),
        PropDef("xlink_type", "xlink:type"),
        PropDef("show", "xlink:show"),
        PropDef("actuate", "xlink:actuate"),
    )

    def __init__(
        self,
        name: str | None = None,
        display_name: str | None = None,
        height: str | None = None,
        width: str | None = None,
        url: str = "",
        xlink_type: str = "simple",
        show: str = "embed",
        actuate: str = "onLoad",
        **kwargs: Any,
    ) -> None:
        """Initialize a DrawFillImage, "draw:fill-image".

        The `draw:fill-image` element specifies a link to a bitmap resource.
        Fill images are not available as automatic styles and are typically
        used within the `office:styles` element.

        Args:
            name: The internal name of the fill image.
            display_name: The display name of the fill image.
            height: The height of the fill image (e.g., "10cm").
            width: The width of the fill image (e.g., "15cm").
            url: The URL or internal path of the image.
            xlink_type: The XLink type, usually "simple".
            show: How the image should be shown, usually "embed".
            actuate: When the image should be loaded, usually "onLoad".
            **kwargs: Additional keyword arguments for the parent `DrawImage` class.
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name
            self.display_name = display_name
            self.height = height
            self.width = width
            self.url = url
            self.xlink_type = xlink_type
            self.show = show
            self.actuate = actuate
        self.family = ""

    def __str__(self) -> str:
        return f"({self.url})"


DrawFillImage._define_attribut_property()


class DrawMarker(Element):
    """A marker, "draw:marker", which is used to draw polygons at the start
    or end point of a stroke depending on whether it is referenced by a
    "draw:marker-start" or "draw:marker-end" attribute.

    Marker geometry is defined by a svg:d attribute.

    The "draw:marker" element is usable within the "office:styles"."""

    _tag = "draw:marker"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "draw:name"),
        PropDef("display_name", "draw:display-name"),
        PropDef("svg_d", "svg:d"),
        PropDef("view_box", "svg:viewBox"),
    )

    def __init__(
        self,
        name: str | None = None,
        display_name: str | None = None,
        svg_d: str | None = None,
        view_box: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a draw marker "draw:marker".

        Args:
            name: The internal name of the fill image.
            display_name: The display name of the fill image.
            svg_d: A path data.
            view_box: The rectangle in a local coordinates system used by the
                points.
            **kwargs: Additional keyword arguments for the `DrawMarker` class.
        """
        super().__init__(**kwargs)
        if self._do_init:
            if name:
                self.name = name
            if display_name:
                self.display_name = display_name
            if svg_d:
                self.svg_d = svg_d
            if view_box:
                self.view_box = view_box
        # false family for easier parsing:
        self.family = ""


DrawMarker._define_attribut_property()


register_element_class(DrawImage)
register_element_class(DrawFillImage)
register_element_class(DrawMarker)
