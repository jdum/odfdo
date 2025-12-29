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
from odfdo.shapes import DrawControl


@pytest.fixture
def control() -> Iterable[DrawControl]:
    shape = DrawControl(
        name="Name",
        control="control id",
        size=("10cm", "12cm"),
        position=("3cm", "4cm"),
    )
    yield shape


def test_draw_control_minimal():
    shape = DrawControl()
    assert shape._canonicalize() == "<draw:control></draw:control>"


def test_draw_control_class():
    shape = Element.from_tag("<draw:control/>")
    assert isinstance(shape, DrawControl)


def test_draw_control_control(control):
    assert control.control == "control id"


def test_draw_control_position_1(control):
    assert control.position == ("3cm", "4cm")


def test_draw_control_position_2(control):
    assert control.pos_x == "3cm"


def test_draw_control_position_3(control):
    assert control.pos_y == "4cm"


def test_draw_control_size_1(control):
    assert control.size == ("10cm", "12cm")


def test_draw_control_size_2(control):
    assert control.height == "12cm"


def test_draw_control_size_3(control):
    assert control.width == "10cm"
