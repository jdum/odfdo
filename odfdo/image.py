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
"""DrawImage class for "draw:image"
"""
from .element import Element, register_element_class


class DrawImage(Element):
    """The "draw:image" element represents an image. An image can be
    either:
    - A link to an external resource or
    - Embedded in the document (Not implemented in this version)

    Warning: image elements must be stored in a frame "draw:frame",
    see Frame().
    """

    _tag = "draw:image"
    _properties = (
        ("url", "xlink:href"),
        ("type", "xlink:type"),
        ("show", "xlink:show"),
        ("actuate", "xlink:actuate"),
        ("filter_name", "draw:filter-name"),
    )

    def __init__(
        self,
        url="",
        xlink_type="simple",
        show="embed",
        actuate="onLoad",
        filter_name=None,
        **kw
    ):
        """Initialisation of an DrawImage.

        Arguments:

            url -- str

            type -- str

            show -- str

            actuate -- str

            filter_name -- str

        Return: DrawImage
        """
        super().__init__(**kw)
        if self._do_init:
            self.url = url
            self.type = xlink_type
            self.show = show
            self.actuate = actuate
            self.filter_name = filter_name


DrawImage._define_attribut_property()


class DrawFillImage(DrawImage):
    _tag = "draw:fill-image"
    _properties = (
        ("display_name", "draw:display-name"),
        ("name", "draw:name"),
        ("height", "svg:height"),
        ("width", "svg:width"),
    )

    def __init__(self, name=None, display_name=None, height=None, width=None, **kw):
        """The "draw:fill-image" element specifies a link to a bitmap
        resource. Fill image are not available as automatic styles.
        The "draw:fill-image" element is usable within the following element:
        "office:styles"

        Arguments:

            name -- str

            display_name -- str

            height -- str

            width -- str

        Return: DrawFillImage
        """
        super().__init__(**kw)
        if self._do_init:
            self.name = name
            self.display_name = display_name
            self.height = height
            self.width = width


DrawFillImage._define_attribut_property()

register_element_class(DrawImage)
register_element_class(DrawFillImage)
