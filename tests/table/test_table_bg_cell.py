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


import pytest

from odfdo.document import Document
from odfdo.table import Table


@pytest.fixture
def document(samples) -> Document:
    return Document(samples("test_col_cell.ods"))


@pytest.fixture
def docblue(samples) -> Document:
    return Document(samples("test_col_cell_blue.ods"))


def test_base(document):
    assert isinstance(document.body.get_table(0), Table)


def test_cell_style_props(document):
    props = document.get_cell_style_properties(0, (1, 1))
    assert props


def test_cell_style_props_far(document):
    props = document.get_cell_style_properties(0, (10000, 10000))
    assert not props


def test_cell_bg_a1(document):
    col = document.get_cell_background_color(0, ("a1"))
    assert col == "#ffffff"


def test_cell_bg_a1_default(document):
    col = document.get_cell_background_color(0, ("a1"), "#123456")
    assert col == "#123456"


def test_cell_bg_c1(document):
    col = document.get_cell_background_color(0, ("c1"))
    assert col == "#ffff00"


def test_cell_bg_b2(document):
    col = document.get_cell_background_color(0, ("b2"))
    assert col == "#55308d"


def test_cell_bg_c2(document):
    col = document.get_cell_background_color(0, ("c2"))
    assert col == "#ff3838"


def test_cell_bg_d2(document):
    col = document.get_cell_background_color(0, ("d2"))
    assert col == "#ff3838"


def test_cell_bg_g2(document):
    col = document.get_cell_background_color(0, ("g2"))
    assert col == "#ffffff"


def test_cell_bg_g2_default(document):
    col = document.get_cell_background_color(0, ("g2"), "")
    assert col == ""


def test_cell_bg_f2(document):
    # column f
    col = document.get_cell_background_color(0, ("f2"))
    assert col == "#e6e905"


def test_cell_bg_f5(document):
    # column f
    col = document.get_cell_background_color(0, ("f5"))
    assert col == "#e6e905"


def test_cell_bg_f6(document):
    # column f
    col = document.get_cell_background_color(0, ("f6"))
    assert col == "#e6e905"


def test_cell_bg_a6(document):
    col = document.get_cell_background_color(0, ("a6"))
    assert col == "#3465a4"


def test_cell_bg_b6(document):
    col = document.get_cell_background_color(0, ("b6"))
    assert col == "#3465a4"


def test_cell_bg_g6(document):
    col = document.get_cell_background_color(0, ("g6"))
    assert col == "#3465a4"


def test_cell_bg_w6(document):
    col = document.get_cell_background_color(0, ("w6"))
    assert col == "#3465a4"


def test_cell_bg_xxx6(document):
    col = document.get_cell_background_color(0, (1000, 5))
    assert col == "#3465a4"


def test_cell_bg_a7_default(document):
    col = document.get_cell_background_color(0, "a7", "#123456")
    assert col == "#123456"


def test_cell_bg_a8(document):
    col = document.get_cell_background_color(0, "a8")
    assert col == "#b4c7dc"


def test_cell_bg_b8(document):
    col = document.get_cell_background_color(0, "b8")
    assert col == "#b4c7dc"


def test_cell_bg_c8(document):
    col = document.get_cell_background_color(0, "c8")
    assert col == "#ffff6d"


def test_cell_bg_d8(document):
    col = document.get_cell_background_color(0, "d8")
    assert col == "#ff3838"


def test_cell_bg_e8(document):
    col = document.get_cell_background_color(0, "e8")
    assert col == "#b4c7dc"


def test_cell_bg_f8(document):
    # column f
    col = document.get_cell_background_color(0, ("f8"))
    assert col == "#e6e905"


def test_cell_bg_a10(document):
    col = document.get_cell_background_color(0, "a10")
    assert col == "#ed4c05"


def test_cell_bg_b10(document):
    col = document.get_cell_background_color(0, "b10")
    assert col == "#ed4c05"


def test_cell_bg_c10(document):
    col = document.get_cell_background_color(0, "c10")
    assert col == "#ed4c05"


def test_cell_bg_f10(document):
    # column f
    col = document.get_cell_background_color(0, "f10")
    assert col == "#e6e905"


def test_cell_bg_g10(document):
    col = document.get_cell_background_color(0, "g10")
    assert col == "#ed4c05"


def test_cell_bg_xx10(document):
    col = document.get_cell_background_color(0, "xx10")
    assert col == "#ed4c05"


def test_cell_bg_a12(document):
    col = document.get_cell_background_color(0, "a12")
    assert col == "#168253"


def test_cell_bg_b12(document):
    col = document.get_cell_background_color(0, "b12")
    assert col == "#168253"


def test_cell_bg_f12(document):
    # column f
    col = document.get_cell_background_color(0, "f12")
    assert col == "#e6e905"


def test_cell_bg_g12(document):
    col = document.get_cell_background_color(0, "g12")
    assert col == "#168253"


def test_cell_bg_yy12(document):
    col = document.get_cell_background_color(0, "yy12")
    assert col == "#168253"


def test_cell_bg_f14(document):
    col = document.get_cell_background_color(0, "f14")
    assert col == "#fff5ce"


def test_cell_bg_a15(document):
    col = document.get_cell_background_color(0, "a15")
    assert col == "#55215b"


def test_cell_bg_b15(document):
    col = document.get_cell_background_color(0, "b15")
    assert col == "#55215b"


def test_cell_bg_f15(document):
    col = document.get_cell_background_color(0, "f15")
    assert col == "#55215b"


def test_cell_bg_g15(document):
    col = document.get_cell_background_color(0, "g15")
    assert col == "#55215b"


def test_cell_bg_gg15(document):
    col = document.get_cell_background_color(0, "gg15")
    assert col == "#55215b"


def test_cell_bg_f16(document):
    # column f
    col = document.get_cell_background_color(0, "f16")
    assert col == "#e6e905"


def test_cell_bg_f1000(document):
    # column f
    col = document.get_cell_background_color(0, "f1000")
    assert col == "#e6e905"


def test_blue_base(docblue):
    assert isinstance(docblue.body.get_table(0), Table)


def test__blue_cell_style_props_a1(docblue):
    props = docblue.get_cell_style_properties(0, (0, 0))
    assert props


def test__blue_cell_style_props_b2(docblue):
    props = docblue.get_cell_style_properties(0, (1, 1))
    assert props


def test__blue_cell_style_props_far(docblue):
    props = docblue.get_cell_style_properties(0, (10000, 10000))
    assert props


def test_blue__cell_bg_a1(docblue):
    col = docblue.get_cell_background_color(0, ("a1"))
    assert col == "#2a6099"


def test_blue__cell_bg_b2(docblue):
    col = docblue.get_cell_background_color(0, ("b2"))
    assert col == "#ffff00"


def test_blue__cell_bg_far(docblue):
    col = docblue.get_cell_background_color(0, (1000, 10000))
    assert col == "#2a6099"
