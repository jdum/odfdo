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
from odfdo.shapes import EllipseShape


@pytest.fixture
def ellipse() -> Iterable[EllipseShape]:
    shape = EllipseShape(
        name="Name",
        size=("10cm", "20cm"),
        position=("3cm", "4cm"),
    )
    yield shape


@pytest.fixture
def body(samples) -> Iterable[Element]:
    document = Document(samples("base_shapes.odg"))
    yield document.body


def test_ellipse_minimal():
    shape = EllipseShape()
    assert shape._canonicalize() == "<draw:ellipse></draw:ellipse>"


def test_ellipse_class():
    shape = Element.from_tag("<draw:ellipse/>")
    assert isinstance(shape, EllipseShape)


def test_ellipse_kind(ellipse):
    assert ellipse.kind == "full"


def test_ellipse_kind_2(ellipse):
    ellipse.kind = "arc"
    assert ellipse.kind == "arc"


def test_ellipse_kind_3(ellipse):
    with pytest.raises(TypeError):
        ellipse.kind = "bad"


def test_ellipse_angle_1():
    shape = EllipseShape(
        name="Name",
        size=("10cm", "20cm"),
        position=("3cm", "4cm"),
        kind="arc",
        start_angle="10",
        end_angle="55",
    )
    assert shape.kind == "arc"


def test_ellipse_angle_2():
    shape = EllipseShape(
        name="Name",
        size=("10cm", "20cm"),
        position=("3cm", "4cm"),
        kind="arc",
        start_angle="10",
        end_angle="55",
    )
    assert shape.start_angle == "10"


def test_ellipse_angle_3():
    shape = EllipseShape(
        name="Name",
        size=("10cm", "20cm"),
        position=("3cm", "4cm"),
        kind="arc",
        start_angle="10",
        end_angle="55",
    )
    assert shape.end_angle == "55"


def test_ellipse_cx():
    shape = EllipseShape(
        name="Name",
        size=("10cm", "20cm"),
        position=("3cm", "4cm"),
        cx="15cm",
        cy="16cm",
    )
    assert shape.cx == "15cm"


def test_ellipse_cy():
    shape = EllipseShape(
        name="Name",
        size=("10cm", "20cm"),
        position=("3cm", "4cm"),
        cx="15cm",
        cy="16cm",
    )
    assert shape.cy == "16cm"


def test_ellipse_rx():
    shape = EllipseShape(
        name="Name",
        size=("10cm", "20cm"),
        position=("3cm", "4cm"),
        rx="17cm",
        ry="18cm",
    )
    assert shape.rx == "17cm"


def test_ellipse_ry():
    shape = EllipseShape(
        name="Name",
        size=("10cm", "20cm"),
        position=("3cm", "4cm"),
        rx="17cm",
        ry="18cm",
    )
    assert shape.ry == "18cm"


def test_ellipse_position_1(ellipse):
    assert ellipse.position == ("3cm", "4cm")


def test_ellipse_position_2(ellipse):
    assert ellipse.pos_x == "3cm"


def test_ellipse_position_3(ellipse):
    assert ellipse.pos_y == "4cm"


def test_ellipse_size_1(ellipse):
    assert ellipse.size == ("10cm", "20cm")


def test_ellipse_size_2(ellipse):
    assert ellipse.height == "20cm"


def test_ellipse_size_3(ellipse):
    assert ellipse.width == "10cm"


def test_get_draw_ellipse_list(body):
    page = body.get_draw_page()
    ellipses = page.get_draw_ellipses()
    assert len(ellipses) == 1


def test_get_draw_ellipse_list_regex(body):
    page = body.get_draw_page()
    ellipses = page.get_draw_ellipses(content="rcle")
    assert len(ellipses) == 1


def test_get_draw_ellipse_list_draw_style(body):
    page = body.get_draw_page()
    ellipses = page.get_draw_ellipses(draw_style="gr1")
    assert len(ellipses) == 1


def test_get_draw_ellipse_list_draw_text_style(body):
    page = body.get_draw_page()
    ellipses = page.get_draw_ellipses(draw_text_style="P1")
    assert len(ellipses) == 1


def test_get_draw_ellipse_by_content(body):
    page = body.get_draw_page()
    ellipse = page.get_draw_ellipse(content="Cerc")
    expected = (
        '<draw:ellipse draw:style-name="gr1" '
        'draw:text-style-name="P1" xml:id="id2" draw:id="id2" '
        'draw:layer="layout" svg:width="4cm" svg:height="3.5cm" '
        'svg:x="13.5cm" svg:y="5cm">\n'
        '  <text:p text:style-name="P1">Cercle</text:p>\n'
        "</draw:ellipse>\n"
    )
    assert ellipse.serialize(pretty=True) == expected


def test_get_draw_ellipse_by_id(body):
    page = body.get_draw_page()
    ellipse = EllipseShape(draw_id="an id")
    page.append(ellipse)
    ellipse = page.get_draw_ellipse(id="an id")
    expected = '<draw:ellipse draw:id="an id"/>'
    assert ellipse.serialize() == expected
