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
from odfdo.shapes import RegularPolygonShape


@pytest.fixture
def poly() -> Iterable[RegularPolygonShape]:
    shape = RegularPolygonShape(
        name="Name",
        corners=4,
        concave=False,
        size=("10cm", "10cm"),
        position=("3cm", "4cm"),
    )
    yield shape


@pytest.fixture
def polyconcave() -> Iterable[RegularPolygonShape]:
    shape = RegularPolygonShape(
        name="Name",
        corners=4,
        concave=True,
        sharpness="1cm",
        size=("10cm", "10cm"),
        position=("3cm", "4cm"),
    )
    yield shape


def test_regular_poly_minimal():
    shape = RegularPolygonShape()
    assert shape._canonicalize() == "<draw:regular-polygon></draw:regular-polygon>"


def test_regular_poly_class():
    shape = Element.from_tag("<draw:regular-polygon/>")
    assert isinstance(shape, RegularPolygonShape)


def test_regular_poly_create(poly):
    assert poly._canonicalize() == (
        '<draw:regular-polygon draw:corners="4" '
        'draw:name="Name" '
        'svg:height="10cm" '
        'svg:width="10cm" '
        'svg:x="3cm" '
        'svg:y="4cm">'
        "</draw:regular-polygon>"
    )


def test_regular_poly_corners(poly):
    assert poly.corners == 4


def test_regular_poly_corners_none(poly):
    # shout never happen
    poly.corners = None
    assert poly.corners is None


def test_regular_poly_concave_1(polyconcave):
    assert polyconcave.concave is True


def test_regular_poly_concave_2(polyconcave):
    assert polyconcave.sharpness == "1cm"


def test_regular_poly_position_1(poly):
    assert poly.position == ("3cm", "4cm")


def test_regular_poly_position_2(poly):
    assert poly.pos_x == "3cm"


def test_regular_poly_position_3(poly):
    assert poly.pos_y == "4cm"


def test_regular_poly_size_1(poly):
    assert poly.size == ("10cm", "10cm")


def test_regular_poly_size_2(poly):
    assert poly.height == "10cm"


def test_regular_poly_size_3(poly):
    assert poly.width == "10cm"
