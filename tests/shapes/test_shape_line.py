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
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>

from __future__ import annotations

from collections.abc import Iterable

import pytest

from odfdo import Element
from odfdo.document import Document
from odfdo.draw_page import DrawPage
from odfdo.shapes import LineShape


@pytest.fixture
def body(samples) -> Iterable[Element]:
    document = Document(samples("base_shapes.odg"))
    yield document.body


@pytest.fixture
def complete_line() -> Iterable[LineShape]:
    line = LineShape(
        name="some name",
        style="style name",
        text_style="text style",
        draw_id="draw_id",
        layer="layer",
        p1=("1cm", "2cm"),
        p2=("3cm", "4cm"),
        presentation_class="pres class",
        presentation_style="pres style",
        caption_id="capid",
        class_names="class1",
        transform="tr1",
        z_index=4,
        end_cell_address="x10",
        end_x="10",
        end_y="20",
        table_background=True,
        anchor_type="page",
        anchor_page=42,
        xml_id="xmlid",
    )
    line.svg_title = "title"
    yield line


def test_lineshape_minimal():
    line = LineShape()
    assert line._canonicalize() == "<draw:line></draw:line>"


def test_lineshape_class():
    line = Element.from_tag("<draw:line/>")
    assert isinstance(line, LineShape)


def test_lineshape_create_base():
    page = DrawPage("Page1")
    line = LineShape(p1=("1cm", "2cm"), p2=("3cm", "4cm"))
    page.append(line)
    expected = (
        '<draw:page draw:id="Page1">'
        '<draw:line svg:x1="1cm" '
        'svg:x2="3cm" '
        'svg:y1="2cm" '
        'svg:y2="4cm">'
        "</draw:line></draw:page>"
    )
    assert page._canonicalize() == expected


def test_lineshape_complete_1(complete_line):
    assert complete_line.name == "some name"


def test_lineshape_complete_2(complete_line):
    assert complete_line.style == "style name"


def test_lineshape_complete_3(complete_line):
    assert complete_line.text_style == "text style"


def test_lineshape_complete_4(complete_line):
    assert complete_line.draw_id == "draw_id"


def test_lineshape_complete_5(complete_line):
    assert complete_line.layer == "layer"


def test_lineshape_complete_6(complete_line):
    assert complete_line.p1 == ("1cm", "2cm")


def test_lineshape_complete_6_x(complete_line):
    assert complete_line.x1 == "1cm"


def test_lineshape_complete_6_y(complete_line):
    assert complete_line.y1 == "2cm"


def test_lineshape_complete_7(complete_line):
    assert complete_line.p2 == ("3cm", "4cm")


def test_lineshape_complete_7_x(complete_line):
    assert complete_line.x2 == "3cm"


def test_lineshape_complete_7_y(complete_line):
    assert complete_line.y2 == "4cm"


def test_lineshape_complete_8(complete_line):
    assert complete_line.presentation_class == "pres class"


def test_lineshape_complete_9(complete_line):
    assert complete_line.presentation_style == "pres style"


def test_lineshape_complete_10(complete_line):
    assert complete_line.caption_id == "capid"


def test_lineshape_complete_11(complete_line):
    assert complete_line.class_names == "class1"


def test_lineshape_complete_12(complete_line):
    assert complete_line.transform == "tr1"


def test_lineshape_complete_13(complete_line):
    assert complete_line.z_index == 4


def test_lineshape_complete_14(complete_line):
    assert complete_line.end_cell_address == "x10"


def test_lineshape_complete_15(complete_line):
    assert complete_line.end_x == "10"


def test_lineshape_complete_16(complete_line):
    assert complete_line.end_y == "20"


def test_lineshape_complete_17(complete_line):
    assert complete_line.table_background is True


def test_lineshape_complete_18(complete_line):
    assert complete_line.anchor_type == "page"


def test_lineshape_complete_19(complete_line):
    assert complete_line.anchor_page == 42


def test_lineshape_complete_20(complete_line):
    assert complete_line.xml_id == "xmlid"


def test_lineshape_complete_formatted_text(complete_line):
    assert complete_line.get_formatted_text() == "title\n\n"


def test_page_get_draw_line_list(body):
    page = body.get_draw_page()
    lines = page.get_draw_lines()
    assert len(lines) == 2


def test_page_get_draw_line_list_regex(body):
    page = body.get_draw_page()
    lines = page.get_draw_lines(content="èche*")
    assert len(lines) == 1


def test_page_get_draw_line_list_draw_style(body):
    page = body.get_draw_page()
    lines = page.get_draw_lines(draw_style="gr2")
    assert len(lines) == 1


def test_page_get_draw_line_list_draw_text_style(body):
    page = body.get_draw_page()
    lines = page.get_draw_lines(draw_text_style="P1")
    assert len(lines) == 2


def test_page_get_draw_line_by_content(body):
    page = body.get_draw_page()
    line = page.get_draw_line(content="Ligne")
    expected = (
        '<draw:line draw:layer="layout" '
        'draw:style-name="gr1" '
        'draw:text-style-name="P1" '
        'svg:x1="3.5cm" '
        'svg:x2="10.5cm" '
        'svg:y1="2.5cm" '
        'svg:y2="12cm">'
        '<text:p text:style-name="P1">'
        "Ligne"
        "</text:p></draw:line>"
    )
    assert line._canonicalize() == expected


def test_page_get_draw_line_by_id(body):
    page = body.get_draw_page()
    line = LineShape(draw_id="an id")
    page.append(line)
    line = page.get_draw_line(id="an id")
    expected = '<draw:line draw:id="an id"></draw:line>'
    assert line._canonicalize() == expected
