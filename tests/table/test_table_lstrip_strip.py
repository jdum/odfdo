# Copyright 2018-2026 Jérôme Dumonteil
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
from typing import cast

import pytest

from odfdo.cell import Cell
from odfdo.document import Document
from odfdo.row import Row
from odfdo.table import Table


@pytest.fixture
def table(samples) -> Iterable[Table]:
    # simpletable :
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1   2	3	4	5	6	7
    document = Document(samples("simple_table.ods"))
    yield cast(Table, document.body.get_table(name="Example1"))


@pytest.fixture
def styled_table(samples) -> Iterable[Table]:
    document = Document(samples("styled_table.ods"))
    yield cast(Table, document.body.get_table(name="Feuille1"))


@pytest.fixture
def unstriped_table_1(samples) -> Iterable[Table]:
    document = Document(samples("unstriped.ods"))
    yield cast(Table, document.body.get_table(name="Sheet1"))


@pytest.fixture
def unstriped_table_2(samples) -> Iterable[Table]:
    document = Document(samples("unstriped.ods"))
    yield cast(Table, document.body.get_table(name="Sheet2"))


def test_table_lstrip_unstriped_table_1(unstriped_table_1):
    unstriped_table_1.lstrip()
    assert unstriped_table_1.size[0] > 1000
    assert unstriped_table_1.size[1] > 1000


def test_table_lstrip_unstriped_table_1_gg(unstriped_table_1):
    unstriped_table_1.lstrip(aggressive=True)
    assert unstriped_table_1.size[0] > 1000
    assert unstriped_table_1.size[1] > 1000


def test_table_lstrip_unstriped_table_2(unstriped_table_2):
    unstriped_table_2.lstrip()
    assert unstriped_table_2.size == (5, 4)


def test_table_lstrip_unstriped_table_2_gg(unstriped_table_2):
    unstriped_table_2.lstrip(aggressive=True)
    assert unstriped_table_2.size == (5, 4)


def test_table_lstrip_styled_table(styled_table):
    before = styled_table.size
    styled_table.lstrip()
    assert styled_table.size == before


def test_table_lstrip_1(table):
    table.lstrip()
    assert table.size == (7, 4)
    result = list(table.iter_values(complete=True))
    assert result == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]


def test_table_lstrip_top_empty_rows(table):
    table.insert_row(0, Row(width=7))
    table.insert_row(0, Row(width=7))
    table.lstrip()
    assert table.size == (7, 4)
    result = list(table.iter_values(complete=True))
    assert result == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]


def test_table_lstrip_left_empty_column(table):
    for row in table.get_rows():
        row.set_value(0, None)
    table.lstrip()
    assert table.size == (6, 4)
    result = list(table.iter_values(complete=True))
    assert result == [
        [1, 1, 2, 3, 3, 3],
        [1, 1, 2, 3, 3, 3],
        [1, 1, 2, 3, 3, 3],
        [2, 3, 4, 5, 6, 7],
    ]


def test_table_lstrip_partial_rows_keep_columns(table):
    # columns are removed only when empty in every row (min leading = 0)
    for row in list(table.get_rows())[:3]:
        row.set_value(0, None)
    table.lstrip()
    assert table.size == (7, 4)


def test_table_lstrip_styled_cells_kept(table):
    for row in table.get_rows():
        row.set_cell(0, Cell(style="ce5"))
    table.lstrip()
    assert table.size == (7, 4)


def test_table_lstrip_styled_cells_aggressive(table):
    for row in table.get_rows():
        row.set_cell(0, Cell(style="ce5"))
    table.lstrip(aggressive=True)
    assert table.size == (6, 4)
    result = list(table.iter_values(complete=True))
    assert result == [
        [1, 1, 2, 3, 3, 3],
        [1, 1, 2, 3, 3, 3],
        [1, 1, 2, 3, 3, 3],
        [2, 3, 4, 5, 6, 7],
    ]


def test_table_lstrip_cache_updated(table):
    table.insert_row(0, Row(width=7))
    table.lstrip()
    assert table.get_value("A1") == 1
    assert table.size == (7, 4)


def test_table_lstrip_fully_empty_inner_row(table):
    # a fully empty inner row makes the leading-empty loop complete
    rows = table.get_rows()
    for row in rows[:3]:
        row.set_value(0, None)
    for column in range(7):
        rows[3].set_value(column, None)
    table.lstrip()
    assert table.size == (6, 4)
    result = list(table.iter_values(complete=True))
    assert result == [
        [1, 1, 2, 3, 3, 3],
        [1, 1, 2, 3, 3, 3],
        [1, 1, 2, 3, 3, 3],
        [None, None, None, None, None, None],
    ]


def test_table_lstrip_row_based():
    table = Table("t")
    for _ in range(3):
        row = Row(width=5)
        row.set_value(2, "x")
        table.append(row)
    table.lstrip()
    assert table.size == (3, 3)
    result = list(table.iter_values(complete=True))
    assert result == [
        ["x", None, None],
        ["x", None, None],
        ["x", None, None],
    ]


def test_table_lstrip_empty():
    table = Table("empty")
    expected = table._canonicalize()
    table.lstrip()
    result = table._canonicalize()
    assert result == expected


def test_table_strip_unstriped_table_1(unstriped_table_1):
    unstriped_table_1.strip()
    assert unstriped_table_1.size[0] > 1000
    assert unstriped_table_1.size[1] > 1000


def test_table_strip_unstriped_table_1_gg(unstriped_table_1):
    unstriped_table_1.strip(aggressive=True)
    assert unstriped_table_1.size == (4, 4)


def test_table_strip_unstriped_table_2(unstriped_table_2):
    unstriped_table_2.strip()
    assert unstriped_table_2.size == (5, 4)


def test_table_strip_1(table):
    table.append(Row(width=7))
    table.insert_row(0, Row(width=7))
    table.strip()
    assert table.size == (7, 4)
    result = list(table.iter_values(complete=True))
    assert result == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]


def test_table_strip_styled_cells_kept(table):
    table.append(Row(width=7))
    table.insert_row(0, Row(width=7))
    for row in table.get_rows():
        row.set_cell(0, Cell(style="ce5"))
        row.set_cell(6, Cell(style="ce5"))
    table.strip()
    # styled empty rows and columns are kept
    assert table.size == (7, 6)


def test_table_strip_styled_cells_aggressive(table):
    table.append(Row(width=7))
    table.insert_row(0, Row(width=7))
    for row in table.get_rows():
        row.set_cell(0, Cell(style="ce5"))
        row.set_cell(6, Cell(style="ce5"))
    table.strip(aggressive=True)
    assert table.size == (5, 4)
    result = list(table.iter_values(complete=True))
    assert result == [
        [1, 1, 2, 3, 3],
        [1, 1, 2, 3, 3],
        [1, 1, 2, 3, 3],
        [2, 3, 4, 5, 6],
    ]


def test_table_strip_row_based():
    table = Table("t")
    for _ in range(3):
        row = Row(width=5)
        row.set_value(2, "x")
        table.append(row)
    table.strip()
    assert table.size == (1, 3)
    result = list(table.iter_values(complete=True))
    assert result == [["x"], ["x"], ["x"]]


def test_table_strip_empty():
    table = Table("empty")
    expected = table._canonicalize()
    table.strip()
    result = table._canonicalize()
    assert result == expected
