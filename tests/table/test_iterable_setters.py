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

"""Tests that value/cell setters accept any iterable, not just lists."""

from __future__ import annotations

import pytest

from odfdo.table import Cell, Row, Table


@pytest.fixture
def row():
    row = Row()
    for value in [1, 1, 1, 2, 3, 3, 3]:
        row.append_cell(Cell(value))
    yield row


# --------------------------------------------------------------------------- #
# Row
# --------------------------------------------------------------------------- #


def test_row_set_values_with_generator():
    row = Row()
    row.set_values(value for value in [1, 2, 3])
    assert row.get_values() == [1, 2, 3]


def test_row_set_values_with_tuple():
    row = Row()
    row.set_values((1, 2, 3))
    assert row.get_values() == [1, 2, 3]


def test_row_set_values_generator_start_offset(row):
    row.set_values((10, 20, 30), start=2)
    assert row.get_values() == [1, 1, 10, 20, 30, 3, 3]


def test_row_set_cells_with_generator():
    row = Row()
    row.set_cells(Cell(value=v) for v in [1, 2, 3])
    assert row.get_values() == [1, 2, 3]


def test_row_set_cells_generator_start_offset(row):
    row.set_cells((Cell(value=10), Cell(value=20)), start=1)
    assert row.get_values() == [1, 10, 20, 2, 3, 3, 3]


# --------------------------------------------------------------------------- #
# Table
# --------------------------------------------------------------------------- #


def test_table_set_values_with_generator():
    table = Table("test", width=3, height=3)
    values = ((1, 2, 3), (4, 5, 6), (7, 8, 9))
    table.set_values(values)
    assert table.get_values() == [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]


def test_table_set_values_generator_rows():
    table = Table("test", width=2, height=2)
    table.set_values((value, value + 1) for value in range(0, 4, 2))
    assert table.get_values() == [[0, 1], [2, 3]]


def test_table_set_row_values_with_generator():
    table = Table("test", width=3, height=2)
    table.set_row_values(1, (7, 8, 9))
    assert table.get_values() == [[None, None, None], [7, 8, 9]]


def test_table_set_row_cells_with_generator():
    table = Table("test", width=3, height=2)
    table.set_row_cells(0, (Cell(1), Cell(2), Cell(3)))
    assert table.get_values() == [[1, 2, 3], [None, None, None]]


def test_table_set_cells_with_generator():
    table = Table("test", width=3, height=3)
    cells = (
        (Cell(1), Cell(2), Cell(3)),
        (Cell(4), Cell(5), Cell(6)),
        (Cell(7), Cell(8), Cell(9)),
    )
    table.set_cells(cells)
    assert table.get_values() == [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]


def test_table_set_column_values_with_generator():
    table = Table("test", width=2, height=3)
    table.set_column_values(1, (10, 20, 30))
    assert table.get_values() == [
        [None, 10],
        [None, 20],
        [None, 30],
    ]


def test_table_set_column_cells_with_generator():
    table = Table("test", width=2, height=3)
    table.set_column_cells(0, (Cell(1), Cell(2), Cell(3)))
    assert table.get_values() == [
        [1, None],
        [2, None],
        [3, None],
    ]


def test_table_set_column_cells_generator_wrong_length():
    table = Table("test", width=2, height=3)
    with pytest.raises(ValueError, match="col mismatch"):
        table.set_column_cells(0, (Cell(1), Cell(2)))
