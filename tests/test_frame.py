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

from __future__ import annotations

from collections.abc import Iterable

import pytest

from odfdo.document import Document
from odfdo.element import Element
from odfdo.frame import (
    Frame,
)
from odfdo.header import Header
from odfdo.image import DrawImage
from odfdo.paragraph import Paragraph

ZOE = "你好 Zoé"


@pytest.fixture
def frame_body(samples) -> Iterable[Element]:
    document = Document(samples("frame_image.odp"))
    yield document.body


def test_frame_minimal():
    frame = Frame()
    expected = (
        '<draw:frame draw:z-index="0" svg:height="1cm" svg:width="1cm"></draw:frame>'
    )
    assert frame._canonicalize() == expected


def test_frame_minimal_2():
    frame = Element.from_tag(
        '<draw:frame draw:z-index="0" svg:height="1cm" svg:width="1cm"></draw:frame>'
    )
    assert isinstance(frame, Frame)


def test_create_frame():
    frame = Frame("A Frame", size=("10cm", "12cm"), style="Graphics")
    expected = (
        '<draw:frame draw:name="A Frame" '
        'draw:style-name="Graphics" '
        'draw:z-index="0" '
        'svg:height="12cm" '
        'svg:width="10cm">'
        "</draw:frame>"
    )
    assert frame._canonicalize() == expected


def test_create_frame_ids():
    frame = Frame(
        "A Frame",
        draw_id="some id",
        presentation_class="some classes",
        presentation_style="presentation style",
        layer="some layer",
        size=("10cm", "12cm"),
        style="Graphics",
    )
    expected = (
        '<draw:frame draw:id="some id" '
        'draw:layer="some layer" '
        'draw:name="A Frame" '
        'draw:style-name="Graphics" '
        'draw:z-index="0" '
        'presentation:class="some classes" '
        'presentation:style-name="presentation style" '
        'svg:height="12cm" '
        'svg:width="10cm">'
        "</draw:frame>"
    )
    assert frame._canonicalize() == expected


def test_create_frame_page():
    frame = Frame(
        "Another Frame",
        size=("10cm", "12cm"),
        anchor_type="page",
        anchor_page=1,
        position=("14mm", "15mm"),
        style="Graphics",
    )
    expected = (
        "<draw:frame "
        'draw:name="Another Frame" '
        'draw:style-name="Graphics" '
        'draw:z-index="0" '
        'svg:height="12cm" '
        'svg:width="10cm" '
        'svg:x="14mm" '
        'svg:y="15mm" '
        'text:anchor-page-number="1" '
        'text:anchor-type="page">'
        "</draw:frame>"
    )
    assert frame._canonicalize() == expected


def test_get_frame_list(frame_body):
    result = frame_body.get_frames()
    assert len(result) == 4


def test_get_frame_list_property(frame_body):
    result = frame_body.frames
    assert len(result) == 4


def test_get_frame_list_title(frame_body):
    result = frame_body.get_frames(title="Intitulé")
    assert len(result) == 1
    assert result[0].tag == "draw:frame"


def test_get_frame_by_name(frame_body):
    frame = frame_body.get_frame(name="odfdo")
    assert frame.tag == "draw:frame"


def test_get_frame_by_position(frame_body):
    frame = frame_body.get_frame(position=3)
    assert frame.presentation_class == "notes"


def test_get_frame_by_description(frame_body):
    frame = frame_body.get_frame(description="描述")
    assert frame.tag == "draw:frame"


def test_insert_frame(frame_body):
    body = frame_body.clone
    frame1 = Frame("frame1", size=("10cm", "12cm"), style="Graphics")
    frame2 = Frame(
        "frame2",
        size=("10cm", "13cm"),
        anchor_page=1,
        position=("10mm", "10mm"),
        style="Graphics",
    )
    body.append(frame1)
    body.append(frame2)
    result = body.get_frames(style="Graphics")
    assert len(result) == 2
    element = body.get_frame(name="frame1")
    assert element.tag == "draw:frame"
    element = body.get_frame(name="frame2")
    assert element.tag == "draw:frame"


def test_create_image_frame():
    frame = Frame.image_frame("Pictures/zoe.jpg")
    expected = (
        "<draw:frame "
        'draw:z-index="0" '
        'svg:height="1cm" '
        'svg:width="1cm">'
        '<draw:image xlink:actuate="onLoad" '
        'xlink:href="Pictures/zoe.jpg" '
        'xlink:show="embed" '
        'xlink:type="simple">'
        "</draw:image>"
        "</draw:frame>"
    )
    assert frame._canonicalize() == expected


def test_image_frame_set_image_element_on_previous():
    frame = Frame.image_frame("Pictures/zoe.jpg")
    image = DrawImage("Pictures/new.jpg")
    frame.set_image(image)
    read_image = frame.get_image()
    assert read_image.url == "Pictures/new.jpg"


def test_image_frame_set_image_element_on_none():
    frame = Frame("frame name")
    image = DrawImage("Pictures/new.jpg")
    frame.set_image(image)
    read_image = frame.get_image()
    assert read_image.url == "Pictures/new.jpg"


def test_image_frame_set_image_url():
    frame = Frame.image_frame("Pictures/zoe.jpg")
    url = "Pictures/new.jpg"
    frame.set_image(url)
    read_image = frame.get_image()
    assert read_image.url == "Pictures/new.jpg"


def test_create_image_frame_text():
    frame = Frame.image_frame("Pictures/zoe.jpg", text=ZOE)
    expected = (
        "<draw:frame "
        'draw:z-index="0" '
        'svg:height="1cm" '
        'svg:width="1cm">'
        '<draw:image xlink:actuate="onLoad" '
        'xlink:href="Pictures/zoe.jpg" '
        'xlink:show="embed" '
        'xlink:type="simple">'
        f"<text:p>{ZOE}</text:p>"
        "</draw:image></draw:frame>"
    )
    assert frame._canonicalize() == expected


def test_create_text_frame():
    frame = Frame.text_frame(ZOE)
    expected = (
        '<draw:frame draw:z-index="0" '
        'svg:height="1cm" '
        'svg:width="1cm">'
        "<draw:text-box>"
        f"<text:p>{ZOE}</text:p>"
        "</draw:text-box>"
        "</draw:frame>"
    )
    assert frame._canonicalize() == expected


def test_frame_get_text_content():
    frame = Frame.text_frame(ZOE)
    expected = ZOE
    assert frame.text_content == expected


def test_frame_get_text_content_none():
    frame = Frame()
    assert frame.text_content == ""


def test_frame_set_text_content_1():
    frame = Frame()
    frame.text_content = "content"
    assert frame.text_content == "content"


def test_frame_set_text_content_2():
    frame = Frame.text_frame("previous")
    new_content = Paragraph("new")
    frame.text_content = new_content
    assert frame.text_content == "new"


def test_framset_text_box():
    frame = Frame.text_frame(ZOE)
    frame.set_text_box("some text")
    assert frame.text_content == "some text"


def test_frame_set_text_box_list():
    frame = Frame.text_frame(ZOE)
    frame.set_text_box(["some text", "second text"])
    assert frame.text_content == "some text\nsecond text"


def test_create_text_frame_element():
    heading = Header(1, ZOE)
    frame = Frame.text_frame(heading)
    expected = (
        '<draw:frame draw:z-index="0" '
        'svg:height="1cm" '
        'svg:width="1cm">'
        "<draw:text-box>"
        "<text:h "
        f'text:outline-level="1">{ZOE}</text:h>'
        "</draw:text-box>"
        "</draw:frame>"
    )
    assert frame._canonicalize() == expected


def test_get_frame(frame_body):
    body = frame_body
    frame = body.get_frame()
    assert isinstance(frame, Frame)


def test_get_frame_size():
    size = ("1cm", "2mm")
    position = ("3in", "4pt")
    frame = Frame(size=size, position=position, anchor_type="paragraph")
    assert frame.size == size


def test_set_size():
    size = ("1cm", "2mm")
    position = ("3in", "4pt")
    frame = Frame(size=size, position=position, anchor_type="paragraph")
    frame2 = frame.clone
    frame.size = position
    assert frame.size == position
    assert frame2.size == size


def test_get_frame_position():
    size = ("1cm", "2mm")
    position = ("3in", "4pt")
    frame = Frame(size=size, position=position, anchor_type="paragraph")
    assert frame.position == position


def test_set_frame_position():
    size = ("1cm", "2mm")
    position = ("3in", "4pt")
    frame = Frame(size=size, position=position, anchor_type="paragraph")
    frame2 = frame.clone
    frame2.position = size
    assert frame2.position == size


def test_get_frame_anchor_type():
    size = ("1cm", "2mm")
    position = ("3in", "4pt")
    frame = Frame(size=size, position=position, anchor_type="paragraph")
    assert frame.anchor_type == "paragraph"


def test_set_frame_anchor_type():
    size = ("1cm", "2mm")
    position = ("3in", "4pt")
    frame = Frame(size=size, position=position, anchor_type="paragraph")
    assert frame.anchor_page is None
    frame.anchor_type = "page"
    frame.anchor_page = 3
    assert frame.anchor_type == "page"
    assert frame.anchor_page == 3


def test_svg_description_1():
    frame = Element.from_tag(
        '<draw:frame svg:width="10cm" svg:height="10cm" '
        'draw:z-index="0" draw:name="Another Frame" '
        'draw:style-name="Graphics" '
        'svg:x="10mm" svg:y="10mm" '
        'text:anchor-type="page" '
        'text:anchor-page-number="1"/>'
    )
    result = frame.svg_description
    assert result is None


def test_svg_description_2():
    frame = Element.from_tag(
        '<draw:frame svg:width="10cm" svg:height="10cm" '
        'draw:z-index="0" draw:name="Another Frame" '
        'draw:style-name="Graphics" '
        'svg:x="10mm" svg:y="10mm" '
        'text:anchor-type="page" '
        'text:anchor-page-number="1"/>'
    )
    frame.svg_description = "some description"
    result = frame.svg_description
    assert result == "some description"


def test_svg_title_1():
    frame = Element.from_tag(
        '<draw:frame svg:width="10cm" svg:height="10cm" '
        'draw:z-index="0" draw:name="Another Frame" '
        'draw:style-name="Graphics" '
        'svg:x="10mm" svg:y="10mm" '
        'text:anchor-type="page" '
        'text:anchor-page-number="1"/>'
    )
    result = frame.svg_title
    assert result is None


def test_svg_title_2():
    frame = Element.from_tag(
        '<draw:frame svg:width="10cm" svg:height="10cm" '
        'draw:z-index="0" draw:name="Another Frame" '
        'draw:style-name="Graphics" '
        'svg:x="10mm" svg:y="10mm" '
        'text:anchor-type="page" '
        'text:anchor-page-number="1"/>'
    )
    frame.svg_title = "some title"
    result = frame.svg_title
    assert result == "some title"


def test_frame_get_formatted_text():
    frame = Frame.text_frame("content")
    expected = "  content\n  \n\n"
    assert frame.get_formatted_text() == expected


def test_frame_get_formatted_text_svg_title():
    frame = Frame()
    frame.svg_title = "some title"
    expected = "some title\n\n"
    assert frame.get_formatted_text() == expected


def test_frame_get_formatted_text_svg_description():
    frame = Frame()
    frame.svg_description = "some desc"
    expected = "some desc\n\n"
    assert frame.get_formatted_text() == expected


def test_frame_get_formatted_text_image():
    frame = Frame()
    frame.set_image("Pictures/image.jpg")
    expected = "[Image Pictures/image.jpg]\n\n"
    assert frame.get_formatted_text() == expected


def test_frame_get_formatted_text_image_rst():
    frame = Frame()
    frame.set_image("Pictures/image.jpg")
    expected = "\n.. image:: Pictures/image.jpg\n   :width: 37px\n   :height: 37px\n\n"
    assert frame.get_formatted_text({"rst_mode": True}) == expected


def test_frame_get_formatted_text_image_rst_no_size():
    frame = Frame()
    frame.set_image("Pictures/image.jpg")
    frame.width = None
    frame.height = None
    expected = "\n.. image:: Pictures/image.jpg\n\n"
    assert frame.get_formatted_text({"rst_mode": True}) == expected


def test_frame_get_formatted_text_image_rst_no_img():
    frame = Frame()
    frame.set_image("Pictures/image.jpg")
    expected = "|img1|\n"
    assert (
        frame.get_formatted_text(
            {"rst_mode": True, "no_img_level": True},
        )
        == expected
    )
