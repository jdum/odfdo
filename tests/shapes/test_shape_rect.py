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

from __future__ import annotations

from collections.abc import Iterable

import pytest

from odfdo import Element
from odfdo.document import Document
from odfdo.draw_page import DrawPage
from odfdo.shapes import RectangleShape


@pytest.fixture
def body(samples) -> Iterable[Element]:
    document = Document(samples("base_shapes.odg"))
    yield document.body


def test_rectangleshape_minimal():
    shape = RectangleShape()
    assert shape._canonicalize() == "<draw:rect></draw:rect>"


def test_rectangleshape_class():
    shape = Element.from_tag("<draw:rect/>")
    assert isinstance(shape, RectangleShape)


def test_rectangleshape_create():
    page = DrawPage("Page1")
    rectangle = RectangleShape(size=("2cm", "1cm"), position=("3cm", "4cm"))
    page.append(rectangle)
    expected = (
        '<draw:page draw:id="Page1">'
        '<draw:rect svg:height="1cm" '
        'svg:width="2cm" svg:x="3cm" '
        'svg:y="4cm">'
        "</draw:rect></draw:page>"
    )
    assert page._canonicalize() == expected


def test_rectangleshape_corner_radius():
    shape = RectangleShape(size=("20cm", "10cm"), corner_radius="1cm")
    assert shape.corner_radius == "1cm"


def test_rectangleshape_rx():
    shape = RectangleShape(size=("20cm", "10cm"), rx="1cm")
    assert shape.rx == "1cm"


def test_rectangleshape_ry():
    shape = RectangleShape(size=("20cm", "10cm"), ry="1cm")
    assert shape.ry == "1cm"


def test_page_get_draw_rectangle_list(body):
    page = body.get_draw_page()
    rectangles = page.get_draw_rectangles()
    assert len(rectangles) == 1


def test_page_get_draw_rectangle_list_regex(body):
    page = body.get_draw_page()
    rectangles = page.get_draw_rectangles(content="angle")
    assert len(rectangles) == 1


def test_page_get_draw_rectangle_list_draw_style(body):
    page = body.get_draw_page()
    rectangles = page.get_draw_rectangles(draw_style="gr1")
    assert len(rectangles) == 1


def test_page_get_draw_rectangle_list_draw_text_style(body):
    page = body.get_draw_page()
    rectangles = page.get_draw_rectangles(draw_text_style="P1")
    assert len(rectangles) == 1


def test_page_get_draw_rectangle_by_content(body):
    page = body.get_draw_page()
    rectangle = page.get_draw_rectangle(content="Rect")
    expected = (
        '<draw:rect xml:id="id1" '
        'draw:id="id1" '
        'draw:layer="layout" '
        'draw:style-name="gr1" '
        'draw:text-style-name="P1" '
        'svg:height="7cm" '
        'svg:width="6cm" '
        'svg:x="5cm" '
        'svg:y="4.5cm">'
        '<text:p text:style-name="P1">'
        "Rectangle"
        "</text:p>"
        "</draw:rect>"
    )
    assert rectangle._canonicalize() == expected


def test_page_get_draw_rectangle_by_id(body):
    page = body.get_draw_page()
    rectangle = RectangleShape(draw_id="an id")
    page.append(rectangle)
    rectangle = page.get_draw_rectangle(id="an id")
    expected = '<draw:rect draw:id="an id"></draw:rect>'
    assert rectangle._canonicalize() == expected
