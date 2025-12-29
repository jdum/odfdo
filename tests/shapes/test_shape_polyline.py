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

from __future__ import annotations

from collections.abc import Iterable

import pytest

from odfdo import Element
from odfdo.shapes import PolylineShape


@pytest.fixture
def polyline() -> Iterable[PolylineShape]:
    shape = PolylineShape(
        name="Name",
        size=("10cm", "20cm"),
        position=("3cm", "4cm"),
        points="pts coords",
        view_box="vb coords",
    )
    yield shape


def test_polylineshape_minimal():
    shape = PolylineShape()
    assert shape._canonicalize() == "<draw:polyline></draw:polyline>"


def test_polylineshape_class():
    shape = Element.from_tag("<draw:polyline/>")
    assert isinstance(shape, PolylineShape)


def test_polylineshape_create(polyline):
    assert polyline._canonicalize() == (
        '<draw:polyline draw:name="Name" '
        'draw:points="pts coords" '
        'svg:height="20cm" '
        'svg:viewBox="vb coords" '
        'svg:width="10cm" '
        'svg:x="3cm" '
        'svg:y="4cm">'
        "</draw:polyline>"
    )


def test_polylineshape_points(polyline):
    assert polyline.points == "pts coords"


def test_polylineshape_position_1(polyline):
    assert polyline.position == ("3cm", "4cm")


def test_polylineshape_position_2(polyline):
    assert polyline.pos_x == "3cm"


def test_polylineshape_position_3(polyline):
    assert polyline.pos_y == "4cm"


def test_polylineshape_size_1(polyline):
    assert polyline.size == ("10cm", "20cm")


def test_polylineshape_size_2(polyline):
    assert polyline.height == "20cm"


def test_polylineshape_size_3(polyline):
    assert polyline.width == "10cm"
