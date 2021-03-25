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
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
"""Frame class for "draw:frame"
"""
from .element import Element, register_element_class
from .datatype import Unit
from .image import DrawImage
from .paragraph import Paragraph
from .style import Style
from .utils import isiterable, DPI


def default_frame_position_style(
    name="FramePosition",
    horizontal_pos="from-left",
    vertical_pos="from-top",
    horizontal_rel="paragraph",
    vertical_rel="paragraph",
):
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

    anchor_value_choice = {"page", "frame", "paragraph", "char", "as-char"}

    @property
    def anchor_type(self):
        "getter/setter"
        return self.get_attribute("text:anchor-type")

    @anchor_type.setter
    def anchor_type(self, anchor_type):
        if anchor_type not in self.anchor_value_choice:
            raise ValueError("anchor_type not valid: %s" % anchor_type)
        self.set_attribute("text:anchor-type", anchor_type)

    @property
    def anchor_page(self):
        """getter/setter for the number of the page when the anchor type is
        'page'.

        type : int or None
        """
        anchor_page = self.get_attribute("text:anchor-page-number")
        if anchor_page is None:
            return None
        return int(anchor_page)

    @anchor_page.setter
    def anchor_page(self, anchor_page):
        self.set_attribute("text:anchor-page-number", anchor_page)


class PosMix:
    """Position relative to anchor point.

    Setting the position may require a specific style for actual display on
    some graphical rendering softwares.

    Position is a (left, top) tuple with items including the unit,
    e.g. ('10cm', '15cm').
    """

    @property
    def position(self):
        "getter/setter"
        get_attr = self.get_attribute
        return get_attr("svg:x"), get_attr("svg:y")

    @position.setter
    def position(self, position):
        self.pos_x = position[0]
        self.pos_y = position[1]


class ZMix:
    """z-index position

    z-index is an integer
    """

    @property
    def z_index(self):
        "getter/setter"
        z_index = self.get_attribute("draw:z-index")
        if z_index is None:
            return None
        return int(z_index)

    @z_index.setter
    def z_index(self, z_index):
        self.set_attribute("draw:z-index", z_index)


class SizeMix:
    """Size of the frame

    Size is a (width, height) tuple with items including the unit,
    e.g. ('10cm', '15cm').
    """

    @property
    def size(self):
        "getter/setter"
        return (self.width, self.height)

    @size.setter
    def size(self, size):
        self.width = size[0]
        self.height = size[1]


class Frame(Element, AnchorMix, PosMix, ZMix, SizeMix):
    """ODF Frame "draw:frame"

    Frames are not useful by themselves. You should consider calling
    Frame.image_frame() or Frame.text_frame directly.
    """

    _tag = "draw:frame"
    _properties = (
        ("name", "draw:name"),
        ("draw_id", "draw:id"),
        ("width", "svg:width"),
        ("height", "svg:height"),
        ("style", "draw:style-name"),
        ("pos_x", "svg:x"),
        ("pos_y", "svg:y"),
        ("presentation_class", "presentation:class"),
        ("layer", "draw:layer"),
        ("presentation_style", "presentation:style-name"),
    )

    def __init__(
        self,
        name=None,
        draw_id=None,
        style=None,
        position=None,
        size=("1cm", "1cm"),
        z_index=0,
        presentation_class=None,
        anchor_type=None,
        anchor_page=None,
        layer=None,
        presentation_style=None,
        **kwargs
    ):
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

        Return: Frame
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
        image,
        text=None,
        name=None,
        draw_id=None,
        style=None,
        position=None,
        size=("1cm", "1cm"),
        z_index=0,
        presentation_class=None,
        anchor_type=None,
        anchor_page=None,
        layer=None,
        presentation_style=None,
        **kwargs
    ):
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
            **kwargs
        )
        image_element = frame.set_image(image)
        if text:
            image_element.text_content = text
        return frame

    @classmethod
    def text_frame(
        cls,
        text_or_element=None,
        text_style=None,
        name=None,
        draw_id=None,
        style=None,
        position=None,
        size=("1cm", "1cm"),
        z_index=0,
        presentation_class=None,
        anchor_type=None,
        anchor_page=None,
        layer=None,
        presentation_style=None,
        **kwargs
    ):
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
            **kwargs
        )
        frame.set_text_box(text_or_element, text_style)
        return frame

    @property
    def text_content(self):
        text_box = self.get_element("draw:text-box")
        if text_box is None:
            return None
        return text_box.text_content

    @text_content.setter
    def text_content(self, text_or_element):
        text_box = self.get_element("draw:text-box")
        if text_box is None:
            text_box = Element.from_tag("draw:text-box")
            self.append(text_box)
        if isinstance(text_or_element, Element):
            text_box.clear()
            text_box.append(text_or_element)
        else:
            text_box.text_content = text_or_element

    def get_image(self, position=0, name=None, url=None, content=None):
        return self.get_element("draw:image")

    def set_image(self, url_or_element):
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
                image.set_url(url_or_element)
        return image

    def get_text_box(self):
        return self.get_element("draw:text-box")

    def set_text_box(self, text_or_element=None, text_style=None):
        text_box = self.get_text_box()
        if text_box is None:
            text_box = Element.from_tag("draw:text-box")
            self.append(text_box)
        else:
            text_box.clear()
        if not isiterable(text_or_element):
            text_or_element = [text_or_element]
        for item in text_or_element:
            if isinstance(item, str):
                item = Paragraph(item, style=text_style)
            text_box.append(item)
        return text_box

    def get_formatted_text(self, context):
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
                        ref = "|img%d|" % context["img_counter"]
                        result.append(ref)
                        context["images"].append((ref, filename, (width, height)))
                    else:
                        result.append("\n.. image:: %s\n" % filename)
                        if width is not None:
                            result.append("   :width: %s\n" % width)
                        if height is not None:
                            result.append("   :height: %s\n" % height)
                else:
                    result.append("[Image %s]\n" % element.get_attribute("xlink:href"))
            elif tag == "draw:text-box":
                subresult = ["  "]
                for e in element.children:
                    subresult.append(e.get_formatted_text(context))
                subresult = "".join(subresult)
                subresult = subresult.replace("\n", "\n  ")
                subresult.rstrip(" ")
                result.append(subresult)
            else:
                result.append(element.get_formatted_text(context))
        result.append("\n")
        return "".join(result)


Frame._define_attribut_property()

register_element_class(Frame)
