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
    assert table.width == 3


def test_get_table_height(table):
    assert table.height == 5


def test_get_table_size(table):
    assert table.size == (3, 5)


def test_get_values(table):
    expected = [
        [None, None, None],
        [None, None, None],
        [None, "foo", None],
        [None, None, None],
        [None, None, None],
    ]
    assert table.get_values() == expected


def test_is_not_spanned_1(table):
    for coord in ("a1", "b1", "c1", "a2", "b2", "c2"):
        cell = table.get_cell(coord)
        assert cell.is_spanned() is False


def test_is_not_spanned_2(table):
    for coord in ("a4", "k20"):
        cell = table.get_cell(coord)
        assert cell.is_spanned() is False


def test_is_not_spanned_3(table):
    for coord in ("a3",):
        cell = table.get_cell(coord)
        assert cell.is_spanned() is False


def test_is_not_spanned_4(table):
    for coord in ("a4",):
        cell = table.get_cell(coord)
        assert cell.is_spanned() is False


def test_is_not_spanned_5(table):
    for coord in ("a5",):
        cell = table.get_cell(coord)
        assert cell.is_spanned() is False


def test_is_spanned(table):
    for coord in ("b3", "c3", "b4", "c4", "b5", "c5"):
        cell = table.get_cell(coord)
        assert cell.is_spanned() is True


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


def test_is_covered(table):
    for coord in ("c3", "b4", "c4", "b5", "c5"):
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
