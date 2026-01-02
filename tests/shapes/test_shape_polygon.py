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
from odfdo.shapes import PolygonShape


@pytest.fixture
def polygon() -> Iterable[PolygonShape]:
    shape = PolygonShape(
        name="Name",
        size=("10cm", "20cm"),
        position=("3cm", "4cm"),
        points="pts coords",
        view_box="vb coords",
    )
    yield shape


def test_polygonshape_minimal():
    shape = PolygonShape()
    assert shape._canonicalize() == "<draw:polygon></draw:polygon>"


def test_polygonshape_class():
    shape = Element.from_tag("<draw:polygon/>")
    assert isinstance(shape, PolygonShape)


def test_polygonshape_create(polygon):
    assert polygon._canonicalize() == (
        '<draw:polygon draw:name="Name" '
        'draw:points="pts coords" '
        'svg:height="20cm" '
        'svg:viewBox="vb coords" '
        'svg:width="10cm" '
        'svg:x="3cm" '
        'svg:y="4cm">'
        "</draw:polygon>"
    )


def test_polygonshape_points(polygon):
    assert polygon.points == "pts coords"


def test_polygonshape_position_1(polygon):
    assert polygon.position == ("3cm", "4cm")


def test_polygonshape_position_2(polygon):
    assert polygon.pos_x == "3cm"


def test_polygonshape_position_3(polygon):
    assert polygon.pos_y == "4cm"


def test_polygonshape_size_1(polygon):
    assert polygon.size == ("10cm", "20cm")


def test_polygonshape_size_2(polygon):
    assert polygon.height == "20cm"


def test_polygonshape_size_3(polygon):
    assert polygon.width == "10cm"
