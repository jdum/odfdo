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
from odfdo.shapes import DrawGroup


@pytest.fixture
def group() -> Iterable[DrawGroup]:
    shape = DrawGroup(
        name="some name",
        style="style name",
        draw_id="draw_id",
        svg_y="30cm",
        presentation_class="pres class",
        presentation_style="pres style",
        caption_id="capid",
        class_names="class1",
        z_index=4,
        end_cell_address="x10",
        end_x="10",
        end_y="20",
        table_background=True,
        anchor_type="page",
        anchor_page=42,
        xml_id="xmlid",
    )
    shape.svg_title = "title"
    yield shape


def test_drawgroup_minimal():
    group = DrawGroup()
    assert group._canonicalize() == "<draw:g></draw:g>"


def test_drawgroup_class():
    group = Element.from_tag("<draw:g/>")
    assert isinstance(group, DrawGroup)


def test_drawgroup_complete_1(group):
    assert group.name == "some name"


def test_drawgroup_complete_2(group):
    assert group.style == "style name"


def test_drawgroup_complete_3(group):
    assert group.draw_id == "draw_id"


def test_drawgroup_complete_4(group):
    assert group.svg_y == "30cm"


def test_drawgroup_complete_5(group):
    assert group.presentation_class == "pres class"


def test_drawgroup_complete_6(group):
    assert group.presentation_style == "pres style"


def test_drawgroup_complete_7(group):
    assert group.caption_id == "capid"


def test_drawgroup_complete_8(group):
    assert group.class_names == "class1"


def test_drawgroup_complete_9(group):
    assert group.z_index == 4


def test_drawgroup_complete_10(group):
    assert group.end_cell_address == "x10"


def test_drawgroup_complete_11(group):
    assert group.end_x == "10"


def test_drawgroup_complete_12(group):
    assert group.end_y == "20"


def test_drawgroup_complete_13(group):
    assert group.table_background is True


def test_drawgroup_complete_14(group):
    assert group.anchor_type == "page"


def test_drawgroup_complete_15(group):
    assert group.anchor_page == 42


def test_drawgroup_complete_16(group):
    assert group.xml_id == "xmlid"


def test_drawgroup_complete_formatted_text(group):
    assert group.get_formatted_text() == "title\n\n"
