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
from odfdo.shapes import CircleShape


@pytest.fixture
def circle() -> Iterable[CircleShape]:
    shape = CircleShape(
        name="Name",
        size=("10cm", "20cm"),
        position=("3cm", "4cm"),
        radius="42m",
        center=("40cm", "50cm"),
    )
    yield shape


def test_circle_minimal():
    shape = CircleShape()
    assert shape._canonicalize() == "<draw:circle></draw:circle>"


def test_circle_class():
    shape = Element.from_tag("<draw:circle/>")
    assert isinstance(shape, CircleShape)


def test_circle_kind(circle):
    assert circle.kind == "full"


def test_circle_kind_2(circle):
    circle.kind = "arc"
    assert circle.kind == "arc"


def test_circle_kind_3(circle):
    with pytest.raises(TypeError):
        circle.kind = "bad"


def test_circle_angle_1():
    shape = CircleShape(
        name="Name",
        size=("10cm", "20cm"),
        position=("3cm", "4cm"),
        kind="arc",
        start_angle="10",
        end_angle="55",
    )
    assert shape.kind == "arc"


def test_circle_angle_2():
    shape = CircleShape(
        name="Name",
        size=("10cm", "20cm"),
        position=("3cm", "4cm"),
        kind="arc",
        start_angle="10",
        end_angle="55",
    )
    assert shape.start_angle == "10"


def test_circle_angle_3():
    shape = CircleShape(
        name="Name",
        size=("10cm", "20cm"),
        position=("3cm", "4cm"),
        kind="arc",
        start_angle="10",
        end_angle="55",
    )
    assert shape.end_angle == "55"


def test_circle_center_1():
    shape = CircleShape(
        name="Name",
        size=("10cm", "20cm"),
        position=("3cm", "4cm"),
        center=("15cm", "16cm"),
    )
    assert shape.cx == "15cm"


def test_circle_cy():
    shape = CircleShape(
        name="Name",
        size=("10cm", "20cm"),
        position=("3cm", "4cm"),
        center=("15cm", "16cm"),
    )
    assert shape.cy == "16cm"


def test_circle_center():
    shape = CircleShape(
        name="Name",
        position=("3cm", "4cm"),
        center=("15cm", "16cm"),
    )
    assert shape.center == ("15cm", "16cm")


def test_circle_center_none():
    shape = CircleShape(
        name="Name",
        position=("3cm", "4cm"),
        center=("15cm", "16cm"),
    )
    shape.center = None
    assert shape.center == (None, None)


def test_circle_position_1(circle):
    assert circle.position == ("3cm", "4cm")


def test_circle_position_2(circle):
    assert circle.pos_x == "3cm"


def test_circle_position_3(circle):
    assert circle.pos_y == "4cm"


def test_circle_size_1(circle):
    assert circle.size == ("10cm", "20cm")


def test_circle_size_2(circle):
    assert circle.height == "20cm"


def test_circle_size_3(circle):
    assert circle.width == "10cm"


def test_circle_radius(circle):
    assert circle.radius == "42m"
