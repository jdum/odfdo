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
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>

from collections.abc import Iterable

import pytest

from odfdo.document import Document
from odfdo.table import Cell, Row, Table


@pytest.fixture
def table(samples) -> Iterable[Table]:
    # simpletable :
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1   2	3	4	5	6	7
    document = Document(samples("simple_table.ods"))
    yield document.body.get_table(name="Example1")


def test_empty_row_repeat(table):
    row = Row(repeated=5)
    table.insert_row(2, row)
    value = table.get_value((3, 3))
    assert value is None
    cell = table.get_cell((4, 5))
    assert cell.x == 4
    assert cell.y == 5
    values = table.get_row_values(1)
    assert values == [1, 1, 1, 2, 3, 3, 3]
    values = table.get_row_values(2)
    assert values == [None, None, None, None, None, None, None]
    values = table.get_row_values(6)
    assert values == [None, None, None, None, None, None, None]
    values = table.get_row_values(7)
    assert values == [1, 1, 1, 2, 3, 3, 3]
    assert table.height == 9


def test_row_repeat_twice(table):
    row = Row(repeated=6)
    table.insert_row(2, row)
    cell = Cell(value=333, repeated=2)
    assert cell.x is None
    assert cell.y is None
    row = Row()
    row.insert_cell(4, cell)
    assert row.get_values() == [None, None, None, None, 333, 333]
    assert row.width == 6
    row.repeated = 3
    table.set_row(4, row)
    # initial height  # *insert* row with repeated 5
    expected = 4 + 6 + 3 - 3
    # *set* row with repeated 3
    assert table.height == expected  # *set* row with repeated 3
    expected = [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None],
        [None, None, None, None, 333, 333, None],
        [None, None, None, None, 333, 333, None],
        [None, None, None, None, 333, 333, None],
        [None, None, None, None, None, None, None],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    assert table.get_values() == expected
    row = table.get_row(6)
    assert row.get_values() == [None, None, None, None, 333, 333]
    assert row.width == 6
    cell = row.get_cell(5)
    assert cell.x == 5
    assert cell.y == 6
    assert cell.get_value() == 333


def test_cell_repeat(table):
    cell = Cell(value=55, repeated=5)
    table.insert_cell((2, 2), cell)
    expected = [
        [1, 1, 1, 2, 3, 3, 3, None, None, None, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None, None, None, None],
        [1, 1, 55, 55, 55, 55, 55, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7, None, None, None, None, None],
    ]
    assert table.get_values() == expected
    assert table.width == 12


def test_clear_cache(table):
    table.clear()
    assert table.width == 0
    assert table.height == 0


def test_lonely_cell_add_cache(table):
    table.clear()
    table.set_value((6, 7), 1)
    assert table.width == 7
    assert table.height == 8
    cell = table.get_cell((6, 7))
    assert cell.x == 6
    assert cell.y == 7
    assert cell.get_value() == 1


def test_basic_spreadsheet_case():
    table = Table("Table", width=20, height=3)
    for _r in range(2):
        table.append_row()
    assert len(table.get_rows()) == 5
    vals = []
    for row in table.get_rows():
        vals.append(len(row.get_cells()))
    assert vals == [20, 20, 20, 0, 0]
    # last_row = table.get_row(-1)
    for r in range(3):
        for c in range(10):
            table.set_value((c, r), f"cell {c} {r}")
    for r in range(3, 5):
        for c in range(10):
            table.set_value((c, r), c * 100 + r)
    assert table.size == (20, 5)
    table.rstrip()
    assert table.size == (10, 5)
    assert len(table.get_row(-1).get_cells()) == 10


def test_basic_spreadsheet_case_property():
    table = Table("Table", width=20, height=3)
    for _r in range(2):
        table.append_row()
    assert len(table.get_rows()) == 5
    vals = []
    for row in table.get_rows():
        vals.append(len(row.cells))
    assert vals == [20, 20, 20, 0, 0]
    # last_row = table.get_row(-1)
    for r in range(3):
        for c in range(10):
            table.set_value((c, r), f"cell {c} {r}")
    for r in range(3, 5):
        for c in range(10):
            table.set_value((c, r), c * 100 + r)
    assert table.size == (20, 5)
    table.rstrip()
    assert table.size == (10, 5)
    assert len(table.get_row(-1).cells) == 10
