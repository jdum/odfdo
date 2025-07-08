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
"""DrawImage class for "draw:image" tag and DrawFillImage for
"draw:fill-image" tag."""

from __future__ import annotations

from typing import Any

from .element import Element, PropDef, register_element_class


class DrawImage(Element):
    """
    An ODF image, "draw:image".

    The "draw:image" element represents an image. An image can be
    either a link to an external resource or most often embedded into
    the document.
    """

    _tag = "draw:image"
    _properties: tuple[PropDef, ...] = (
        PropDef("url", "xlink:href"),
        PropDef("type", "xlink:type"),
        PropDef("show", "xlink:show"),
        PropDef("actuate", "xlink:actuate"),
        PropDef("filter_name", "draw:filter-name"),
    )

    def __init__(
        self,
        url: str = "",
        xlink_type: str = "simple",
        show: str = "embed",
        actuate: str = "onLoad",
        filter_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """An ODF image, "draw:image".

        When image is embedded in the document, the url parameter is a
        reference to the local document obtained by copying the source
        image into the document, ie: url = document.add_file(image_path)

        Warning: image elements must be stored in a frame "draw:frame",
        see Frame().

        Initialisation of an DrawImage.

        Arguments:

            url -- str

            type -- str

            show -- str

            actuate -- str

            filter_name -- str
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.url = url
            self.type = xlink_type
            self.show = show
            self.actuate = actuate
            self.filter_name = filter_name


DrawImage._define_attribut_property()


class DrawFillImage(DrawImage):
    """A link to a bitmap resource, "draw:fill-image"."""

    _tag = "draw:fill-image"
    _properties: tuple[PropDef, ...] = (
        PropDef("display_name", "draw:display-name"),
        PropDef("name", "draw:name"),
        PropDef("height", "svg:height"),
        PropDef("width", "svg:width"),
    )

    def __init__(
        self,
        name: str | None = None,
        display_name: str | None = None,
        height: str | None = None,
        width: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        A link to a bitmap resource, "draw:fill-image".

        The "draw:fill-image" element specifies a link to a bitmap
        resource. Fill image are not available as automatic styles.
        The "draw:fill-image" element is usable within the following element:
        "office:styles"

        Arguments:

            name -- str

            display_name -- str

            height -- str

            width -- str
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name
            self.display_name = display_name
            self.height = height
            self.width = width
        self.family = ""


DrawFillImage._define_attribut_property()

register_element_class(DrawImage)
register_element_class(DrawFillImage)
