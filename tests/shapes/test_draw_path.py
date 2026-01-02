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
from odfdo.shapes import DrawPath


@pytest.fixture
def path() -> Iterable[DrawPath]:
    shape = DrawPath(
        name="Name",
        svg_d="path",
        size=("10cm", "12cm"),
        position=("3cm", "4cm"),
        view_box="view box",
    )
    yield shape


def test_draw_path_minimal():
    shape = DrawPath()
    assert shape._canonicalize() == "<draw:path></draw:path>"


def test_draw_path_class():
    shape = Element.from_tag("<draw:path/>")
    assert isinstance(shape, DrawPath)


def test_draw_path_create(path):
    assert path._canonicalize() == (
        '<draw:path draw:name="Name" '
        'svg:d="path" '
        'svg:height="12cm" '
        'svg:viewBox="view box" '
        'svg:width="10cm" '
        'svg:x="3cm" '
        'svg:y="4cm">'
        "</draw:path>"
    )


def test_draw_path_svg_d(path):
    assert path.svg_d == "path"


def test_draw_path_view_box(path):
    assert path.view_box == "view box"


def test_draw_path_position_1(path):
    assert path.position == ("3cm", "4cm")


def test_draw_path_position_2(path):
    assert path.pos_x == "3cm"


def test_draw_path_position_3(path):
    assert path.pos_y == "4cm"


def test_draw_path_size_1(path):
    assert path.size == ("10cm", "12cm")


def test_draw_path_size_2(path):
    assert path.height == "12cm"


def test_draw_path_size_3(path):
    assert path.width == "10cm"
