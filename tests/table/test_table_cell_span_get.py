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

from collections.abc import Iterable

import pytest

from odfdo import Element
from odfdo.document import Document


@pytest.fixture
def table(samples) -> Iterable[Element]:
    document = Document(samples("spanned_cells.ods"))
    yield document.body.tables[0]


def test_get_table_width(table):
    assert table.width == 10


def test_get_table_height(table):
    assert table.height == 6


def test_get_table_size(table):
    assert table.size == (10, 6)


def test_get_values(table):
    expected = [
        [None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None],
        [None, "foo", None, None, None, None, "horiz", None, None, None],
        [None, None, None, None, "vert", None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None],
    ]
    assert table.get_values() == expected


def test_is_not_spanned_1(table):
    for coord in ("a1", "b1", "c1", "a2", "b2", "c2"):
        cell = table.get_cell(coord)
        assert cell.is_spanned() is False


def test_is_not_spanned_1_cov(table):
    for coord in ("a1", "b1", "c1", "a2", "b2", "c2"):
        cell = table.get_cell(coord)
        assert cell.is_spanned(covered=False) is False


def test_is_not_spanned_2(table):
    for coord in ("a4", "k20"):
        cell = table.get_cell(coord)
        assert cell.is_spanned() is False


def test_is_not_spanned_2_cov(table):
    for coord in ("a4", "k20"):
        cell = table.get_cell(coord)
        assert cell.is_spanned(covered=False) is False


def test_is_not_spanned_3(table):
    for coord in ("a3",):
        cell = table.get_cell(coord)
        assert cell.is_spanned() is False


def test_is_not_spanned_3_cov(table):
    for coord in ("a3",):
        cell = table.get_cell(coord)
        assert cell.is_spanned(covered=False) is False


def test_is_not_spanned_4(table):
    for coord in ("a4",):
        cell = table.get_cell(coord)
        assert cell.is_spanned() is False


def test_is_not_spanned_4_cov(table):
    for coord in ("a4",):
        cell = table.get_cell(coord)
        assert cell.is_spanned(covered=False) is False


def test_is_not_spanned_5(table):
    for coord in ("a5",):
        cell = table.get_cell(coord)
        assert cell.is_spanned(covered=True) is False


def test_is_not_spanned_5_cov(table):
    for coord in ("a5",):
        cell = table.get_cell(coord)
        assert cell.is_spanned(covered=False) is False


def test_is_spanned_foo(table):
    for coord in ("b3", "c3", "b4", "c4", "b5", "c5"):
        cell = table.get_cell(coord)
        assert cell.is_spanned() is True


def test_is_spanned_horiz(table):
    for coord in ("g3", "h3", "i3", "j3"):
        cell = table.get_cell(coord)
        assert cell.is_spanned() is True


def test_is_not_spanned_horiz(table):
    for coord in ("g4", "k5"):
        cell = table.get_cell(coord)
        assert cell.is_spanned() is False


def test_is_spanned_vert(table):
    for coord in ("e4", "e5", "e6"):
        cell = table.get_cell(coord)
        assert cell.is_spanned() is True


def test_is_not_spanned_vert(table):
    for coord in ("f4", "e7"):
        cell = table.get_cell(coord)
        assert cell.is_spanned() is False


def test_is_spanned_foo_cov(table):
    for coord in ("b3",):
        cell = table.get_cell(coord)
        assert cell.is_spanned(covered=False) is True


def test_is_spanned_horiz_cov(table):
    for coord in ("g3",):
        cell = table.get_cell(coord)
        assert cell.is_spanned(covered=False) is True


def test_is_not_spanned_horiz_cov(table):
    for coord in ("g4", "k5", "h3", "i3", "j3"):
        cell = table.get_cell(coord)
        assert cell.is_spanned(covered=False) is False


def test_is_spanned_vert_cov(table):
    for coord in ("e4",):
        cell = table.get_cell(coord)
        assert cell.is_spanned(covered=False) is True


def test_is_not_spanned_vert_cov(table):
    for coord in ("f4", "e7", "e5", "e6"):
        cell = table.get_cell(coord)
        assert cell.is_spanned(covered=False) is False


def test_is_not_spanned_foo_cov(table):
    for coord in ("c3", "b4", "c4", "b5", "c5"):
        cell = table.get_cell(coord)
        assert cell.is_spanned(covered=False) is False


def test_is_not_covered_1(table):
    for coord in ("a1", "b1", "c1", "a2", "b2", "c2"):
        cell = table.get_cell(coord)
        assert cell.is_covered() is False


def test_is_not_covered_2(table):
    for coord in ("a4", "k20"):
        cell = table.get_cell(coord)
        assert cell.is_covered() is False


def test_is_not_covered_3(table):
    for coord in ("a3",):
        cell = table.get_cell(coord)
        assert cell.is_covered() is False


def test_is_not_covered_4(table):
    for coord in ("a4",):
        cell = table.get_cell(coord)
        assert cell.is_covered() is False


def test_is_not_covered_5(table):
    for coord in ("a5",):
        cell = table.get_cell(coord)
        assert cell.is_covered() is False


def test_is_not_covered_b3(table):
    for coord in ("b3",):
        cell = table.get_cell(coord)
        assert cell.is_covered() is False


def test_is_not_covered_e4(table):
    for coord in ("e4",):
        cell = table.get_cell(coord)
        assert cell.is_covered() is False


def test_is_not_covered_g3(table):
    for coord in ("g3",):
        cell = table.get_cell(coord)
        assert cell.is_covered() is False


def test_is_covered_foo(table):
    for coord in ("c3", "b4", "c4", "b5", "c5"):
        cell = table.get_cell(coord)
        assert cell.is_covered() is True


def test_is_covered_horiz(table):
    for coord in ("h3", "i3", "j3"):
        cell = table.get_cell(coord)
        assert cell.is_covered() is True


def test_is_covered_vert(table):
    for coord in ("e5", "e6"):
        cell = table.get_cell(coord)
        assert cell.is_covered() is True


def test_get_value_1(table):
    assert table.get_value("a1") is None


def test_get_value_2(table):
    assert table.get_value("b3") == "foo"


def test_get_value_3(table):
    assert table.get_value((1, 2)) == "foo"


def test_get_value_4(table):
    assert table.get_value("b4") is None


def test_get_value_5(table):
    assert table.get_value("g3") == "horiz"


def test_get_value_h3(table):
    assert table.get_value("h3") is None


def test_get_value_i3(table):
    assert table.get_value("i3") is None


def test_get_value_j3(table):
    assert table.get_value("j3") is None


def test_get_value_7(table):
    assert table.get_value("k3") is None


def test_get_value_8(table):
    assert table.get_value("e3") is None


def test_get_value_9(table):
    assert table.get_value("e4") == "vert"


def test_get_value_10(table):
    assert table.get_value("e5") is None


def test_get_value_11(table):
    assert table.get_value("e6") is None


def test_span_area_none(table):
    assert table.get_cell("a1").span_area() == (0, 0)


def test_span_area_foo(table):
    assert table.get_cell("b3").span_area() == (2, 3)


def test_span_area_foo_none(table):
    assert table.get_cell("b4").span_area() == (0, 0)


def test_span_area_horiz(table):
    assert table.get_cell("g3").span_area() == (4, 1)


def test_span_area_horiz_none(table):
    assert table.get_cell("g4").span_area() == (0, 0)


def test_span_area_vert(table):
    assert table.get_cell("e4").span_area() == (1, 3)


def test_span_area_vert_none(table):
    assert table.get_cell("e5").span_area() == (0, 0)


def test_is_spanned_when_some_attribute_missing(table):
    coord = "b3"
    cell = table.get_cell(coord)
    cell.del_attribute("table:number-columns-spanned")
    assert cell.is_spanned() is True


def test_is_spanned_when_some_attribute_missing_2(table):
    coord = "b3"
    cell = table.get_cell(coord)
    cell.del_attribute("table:number-rows-spanned")
    assert cell.is_spanned() is True
