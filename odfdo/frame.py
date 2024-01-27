# Copyright 2018-2024 Jérôme Dumonteil
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
"""Frame class for "draw:frame".
"""
from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal
from typing import Any

from .datatype import Unit
from .element import Element, PropDef, register_element_class
from .image import DrawImage
from .paragraph import Paragraph
from .style import Style

# This DPI is computed to have:
# 640 px (width of your wiki) <==> 17 cm (width of a normal ODT page)
DPI: Decimal = 640 * Decimal("2.54") / 17


def default_frame_position_style(
    name: str = "FramePosition",
    horizontal_pos: str = "from-left",
    vertical_pos: str = "from-top",
    horizontal_rel: str = "paragraph",
    vertical_rel: str = "paragraph",
) -> Style:
    """Helper style for positioning frames in desktop applications that need
    it.

    Default arguments should be enough.

    Use the returned Style as the frame style or build a new graphic style
    with this style as the parent.
    """
    return Style(
        family="graphic",
        name=name,
        horizontal_pos=horizontal_pos,
        horizontal_rel=horizontal_rel,
        vertical_pos=vertical_pos,
        vertical_rel=vertical_rel,
    )


class AnchorMix:
    """Anchor parameter, how the element is attached to its environment.

    value can be: 'page', 'frame', 'paragraph', 'char' or 'as-char'
    """

    ANCHOR_VALUE_CHOICE = {  # noqa: RUF012
        "page",
        "frame",
        "paragraph",
        "char",
        "as-char",
    }

    @property
    def anchor_type(self) -> str | None:
        "Anchor_type getter/setter."
        return self.get_attribute_string("text:anchor-type")  # type: ignore

    @anchor_type.setter
    def anchor_type(self, anchor_type: str) -> None:
        if anchor_type not in self.ANCHOR_VALUE_CHOICE:
            raise TypeError(f"anchor_type not valid: '{anchor_type!r}'")
        self.set_attribute("text:anchor-type", anchor_type)  # type: ignore

    @property
    def anchor_page(self) -> int | None:
        """getter/setter for the number of the page when the anchor type is
        'page'.

        type : int or None
        """
        anchor_page = self.get_attribute("text:anchor-page-number")  # type: ignore
        if anchor_page is None:
            return None
        return int(anchor_page)

    @anchor_page.setter
    def anchor_page(self, anchor_page: int | None) -> None:
        self.set_attribute("text:anchor-page-number", anchor_page)  # type: ignore


class PosMix:
    """Position relative to anchor point.

    Setting the position may require a specific style for actual display on
    some graphical rendering softwares.

    Position is a (left, top) tuple with items including the unit,
    e.g. ('10cm', '15cm').
    """

    @property
    def position(self) -> tuple:
        "getter/setter"
        get_attr = self.get_attribute  # type: ignore
        return get_attr("svg:x"), get_attr("svg:y")

    @position.setter
    def position(self, position: tuple | list) -> None:
        self.pos_x = position[0]
        self.pos_y = position[1]


class ZMix:
    """z-index position

    z-index is an integer
    """

    @property
    def z_index(self) -> int | None:
        "getter/setter"
        z_index = self.get_attribute("draw:z-index")  # type: ignore
        if z_index is None:
            return None
        return int(z_index)

    @z_index.setter
    def z_index(self, z_index: int) -> None:
        self.set_attribute("draw:z-index", z_index)  # type: ignore


class SizeMix:
    """Size of the frame.

    Size is a (width, height) tuple with items including the unit,
    e.g. ('10cm', '15cm').
    """

    @property
    def size(self) -> tuple:
        "getter/setter"
        return (self.width, self.height)

    @size.setter
    def size(self, size: tuple | list) -> None:
        self.width = size[0]
        self.height = size[1]


class Frame(Element, AnchorMix, PosMix, ZMix, SizeMix):
    """ODF Frame "draw:frame"

    Frames are not useful by themselves. You should consider calling
    Frame.image_frame() or Frame.text_frame directly.
    """

    _tag = "draw:frame"
    _properties = (
        PropDef("name", "draw:name"),
        PropDef("draw_id", "draw:id"),
        PropDef("width", "svg:width"),
        PropDef("height", "svg:height"),
        PropDef("style", "draw:style-name"),
        PropDef("pos_x", "svg:x"),
        PropDef("pos_y", "svg:y"),
        PropDef("presentation_class", "presentation:class"),
        PropDef("layer", "draw:layer"),
        PropDef("presentation_style", "presentation:style-name"),
    )

    def __init__(  # noqa:  C901
        self,
        name: str | None = None,
        draw_id: str | None = None,
        style: str | None = None,
        position: tuple | None = None,
        size: tuple = ("1cm", "1cm"),
        z_index: int = 0,
        presentation_class: str | None = None,
        anchor_type: str | None = None,
        anchor_page: int | None = None,
        layer: str | None = None,
        presentation_style: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a frame element of the given size. Position is relative to the
        context the frame is inserted in. If positioned by page, give the page
        number and the x, y position.

        Size is a (width, height) tuple and position is a (left, top) tuple; items
        are strings including the unit, e.g. ('10cm', '15cm').

        Frames are not useful by themselves. You should consider calling:
            Frame.image_frame()
        or
            Frame.text_frame()


        Arguments:

            name -- str

            draw_id -- str

            style -- str

            position -- (str, str)

            size -- (str, str)

            z_index -- int (default 0)

            presentation_class -- str

            anchor_type -- 'page', 'frame', 'paragraph', 'char' or 'as-char'

            anchor_page -- int, page number is anchor_type is 'page'

            layer -- str

            presentation_style -- str
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.size = size
            self.z_index = z_index
            if name:
                self.name = name
            if draw_id is not None:
                self.draw_id = draw_id
            if style is not None:
                self.style = style
            if position is not None:
                self.position = position
            if presentation_class is not None:
                self.presentation_class = presentation_class
            if anchor_type:
                self.anchor_type = anchor_type
            if position and not anchor_type:
                self.anchor_type = "paragraph"
            if anchor_page is not None:
                self.anchor_page = anchor_page
            if layer is not None:
                self.layer = layer
            if presentation_style is not None:
                self.presentation_style = presentation_style

    @classmethod
    def image_frame(
        cls,
        image: Element | str,
        text: str | None = None,
        name: str | None = None,
        draw_id: str | None = None,
        style: str | None = None,
        position: tuple | None = None,
        size: tuple = ("1cm", "1cm"),
        z_index: int = 0,
        presentation_class: str | None = None,
        anchor_type: str | None = None,
        anchor_page: int | None = None,
        layer: str | None = None,
        presentation_style: str | None = None,
        **kwargs: Any,
    ) -> Element:
        """Create a ready-to-use image, since image must be embedded in a
        frame.

        The optionnal text will appear above the image.

        Arguments:

            image -- DrawImage or str, DrawImage element or URL of the image

            text -- str, text for the image

            See Frame() initialization for the other arguments

        Return: Frame
        """
        frame = cls(
            name=name,
            draw_id=draw_id,
            style=style,
            position=position,
            size=size,
            z_index=z_index,
            presentation_class=presentation_class,
            anchor_type=anchor_type,
            anchor_page=anchor_page,
            layer=layer,
            presentation_style=presentation_style,
            **kwargs,
        )
        image_element = frame.set_image(image)
        if text:
            image_element.text_content = text
        return frame

    @classmethod
    def text_frame(
        cls,
        text_or_element: Iterable[Element] | Element | str,
        text_style: str | None = None,
        name: str | None = None,
        draw_id: str | None = None,
        style: str | None = None,
        position: tuple | None = None,
        size: tuple = ("1cm", "1cm"),
        z_index: int = 0,
        presentation_class: str | None = None,
        anchor_type: str | None = None,
        anchor_page: int | None = None,
        layer: str | None = None,
        presentation_style: str | None = None,
        **kwargs: Any,
    ) -> Element:
        """Create a ready-to-use text box, since text box must be embedded in
        a frame.

        The optionnal text will appear above the image.

        Arguments:

            text_or_element -- str or Element, or list of them, text content
                               of the text box.

            text_style -- str, name of the style for the text

            See Frame() initialization for the other arguments

        Return: Frame
        """
        frame = cls(
            name=name,
            draw_id=draw_id,
            style=style,
            position=position,
            size=size,
            z_index=z_index,
            presentation_class=presentation_class,
            anchor_type=anchor_type,
            anchor_page=anchor_page,
            layer=layer,
            presentation_style=presentation_style,
            **kwargs,
        )
        frame.set_text_box(text_or_element, text_style)
        return frame

    @property
    def text_content(self) -> str:
        text_box = self.get_element("draw:text-box")
        if text_box is None:
            return ""
        return text_box.text_content

    @text_content.setter
    def text_content(self, text_or_element: Element | str) -> None:
        text_box = self.get_element("draw:text-box")
        if text_box is None:
            text_box = Element.from_tag("draw:text-box")
            self.append(text_box)
        if isinstance(text_or_element, Element):
            text_box.clear()
            text_box.append(text_or_element)
        else:
            text_box.text_content = text_or_element

    def get_image(
        self,
        position: int = 0,
        name: str | None = None,
        url: str | None = None,
        content: str | None = None,
    ) -> Element | None:
        return self.get_element("draw:image")

    def set_image(self, url_or_element: Element | str) -> Element:
        image = self.get_image()
        if image is None:
            if isinstance(url_or_element, Element):
                image = url_or_element
                self.append(image)
            else:
                image = DrawImage(url_or_element)
                self.append(image)
        else:
            if isinstance(url_or_element, Element):
                image.delete()
                image = url_or_element
                self.append(image)
            else:
                image.set_url(url_or_element)  # type: ignore
        return image

    def get_text_box(self) -> Element | None:
        return self.get_element("draw:text-box")

    def set_text_box(
        self,
        text_or_element: Iterable[Element | str] | Element | str,
        text_style: str | None = None,
    ) -> Element:
        text_box = self.get_text_box()
        if text_box is None:
            text_box = Element.from_tag("draw:text-box")
            self.append(text_box)
        else:
            text_box.clear()
        if isinstance(text_or_element, (Element, str)):
            text_or_element_list: Iterable[Element | str] = [text_or_element]
        else:
            text_or_element_list = text_or_element
        for item in text_or_element_list:
            if isinstance(item, str):
                text_box.append(Paragraph(item, style=text_style))
            else:
                text_box.append(item)
        return text_box

    @staticmethod
    def _get_formatted_text_subresult(context: dict, element: Element) -> str:
        str_list = ["  "]
        for child in element.children:
            str_list.append(child.get_formatted_text(context))
        subresult = "".join(str_list)
        subresult = subresult.replace("\n", "\n  ")
        return subresult.rstrip(" ")

    def get_formatted_text(  # noqa:  C901
        self,
        context: dict | None = None,
    ) -> str:
        if not context:
            context = {}
        result = []
        for element in self.children:
            tag = element.tag
            if tag == "draw:image":
                if context["rst_mode"]:
                    filename = element.get_attribute("xlink:href")

                    # Compute width and height
                    width, height = self.size
                    if width is not None:
                        width = Unit(width)
                        width = width.convert("px", DPI)
                    if height is not None:
                        height = Unit(height)
                        height = height.convert("px", DPI)

                    # Insert or not ?
                    if context["no_img_level"]:
                        context["img_counter"] += 1
                        ref = f"|img{context['img_counter']}|"
                        result.append(ref)
                        context["images"].append((ref, filename, (width, height)))
                    else:
                        result.append(f"\n.. image:: {filename}\n")
                        if width is not None:
                            result.append(f"   :width: {width}\n")
                        if height is not None:
                            result.append(f"   :height: {height}\n")
                else:
                    result.append(f"[Image {element.get_attribute('xlink:href')}]\n")
            elif tag == "draw:text-box":
                result.append(self._get_formatted_text_subresult(context, element))
            else:
                result.append(element.get_formatted_text(context))
        result.append("\n")
        return "".join(result)


Frame._define_attribut_property()

register_element_class(Frame)
