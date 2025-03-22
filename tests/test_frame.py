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

from collections.abc import Iterable

import pytest

from odfdo.document import Document
from odfdo.element import Element
from odfdo.frame import Frame
from odfdo.header import Header

ZOE = "你好 Zoé"


@pytest.fixture
def frame_body(samples) -> Iterable[Element]:
    document = Document(samples("frame_image.odp"))
    yield document.body


def test_create_frame():
    frame = Frame("A Frame", size=("10cm", "10cm"), style="Graphics")
    expected = (
        '<draw:frame svg:width="10cm" svg:height="10cm" '
        'draw:z-index="0" draw:name="A Frame" '
        'draw:style-name="Graphics"/>'
    )
    assert frame.serialize() == expected


def test_create_frame_page():
    frame = Frame(
        "Another Frame",
        size=("10cm", "10cm"),
        anchor_type="page",
        anchor_page=1,
        position=("10mm", "10mm"),
        style="Graphics",
    )
    assert frame.serialize() in (
        (
            '<draw:frame svg:width="10cm" svg:height="10cm" '
            'draw:z-index="0" draw:name="Another Frame" '
            'draw:style-name="Graphics" '
            'svg:x="10mm" svg:y="10mm" '
            'text:anchor-type="page" '
            'text:anchor-page-number="1"/>'
        ),
        (
            '<draw:frame svg:width="10cm" svg:height="10cm" '
            'draw:z-index="0" draw:name="Another Frame" '
            'text:anchor-type="page" text:anchor-page-number="1" '
            'svg:x="10mm" svg:y="10mm" '
            'draw:style-name="Graphics"/>'
        ),
    )


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
    frame1 = Frame("frame1", size=("10cm", "10cm"), style="Graphics")
    frame2 = Frame(
        "frame2",
        size=("10cm", "10cm"),
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
        '<draw:frame svg:width="1cm" svg:height="1cm" '
        'draw:z-index="0">'
        '<draw:image xlink:href="Pictures/zoe.jpg" '
        'xlink:type="simple" xlink:show="embed" '
        'xlink:actuate="onLoad"/>'
        "</draw:frame>"
    )
    assert frame.serialize() == expected


def test_create_image_frame_text():
    frame = Frame.image_frame("Pictures/zoe.jpg", text=ZOE)
    expected = (
        '<draw:frame svg:width="1cm" svg:height="1cm" '
        'draw:z-index="0">'
        '<draw:image xlink:href="Pictures/zoe.jpg" '
        'xlink:type="simple" xlink:show="embed" '
        'xlink:actuate="onLoad">'
        f"<text:p>{ZOE}</text:p>"
        "</draw:image>"
        "</draw:frame>"
    )
    assert frame.serialize() == expected


def test_create_text_frame():
    frame = Frame.text_frame(ZOE)
    expected = (
        '<draw:frame svg:width="1cm" svg:height="1cm" '
        'draw:z-index="0">'
        "<draw:text-box>"
        f"<text:p>{ZOE}</text:p>"
        "</draw:text-box>"
        "</draw:frame>"
    )
    assert frame.serialize() == expected


def test_create_text_frame_element():
    heading = Header(1, ZOE)
    frame = Frame.text_frame(heading)
    expected = (
        '<draw:frame svg:width="1cm" svg:height="1cm" '
        'draw:z-index="0">'
        "<draw:text-box>"
        f'<text:h text:outline-level="1">{ZOE}</text:h>'
        "</draw:text-box>"
        "</draw:frame>"
    )
    assert frame.serialize() == expected


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
