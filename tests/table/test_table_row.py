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
from odfdo.table_cache import TableCache


@pytest.fixture
def table(samples) -> Iterable[Table]:
    # simpletable :
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1   2	3	4	5	6	7
    document = Document(samples("simple_table.ods"))
    yield document.body.get_table(name="Example1")


@pytest.fixture
def row() -> Iterable[Row]:
    row = Row(width=2, repeated=3, style="ro1")
    # Add repeated cell
    row.append(Cell(1, repeated=2))
    # Add regular cell
    row.append(Cell(style="ce5"))
    yield row


def test_row_str(row):
    assert str(row) == "1\n"


def test_row_repr(row):
    assert repr(row) == "<Row y=None>"


def test_get_row_repeated(row):
    assert row.repeated == 3


def test_set_row_repeated(row):
    row.repeated = 99
    assert row.repeated == 99
    row.repeated = 1
    assert row.repeated is None
    row.repeated = 2
    assert row.repeated == 2
    row.repeated = None
    assert row.repeated is None


def test_get_row_style(row):
    assert row.style == "ro1"


def test_get_row_width(row):
    assert row.width == 5


def test_traverse_cells(row):
    assert len(list(row.traverse())) == 5


def test_get_cell_values(row):
    assert row.get_values() == [None, None, 1, 1, None]


def test_is_empty():
    row = Row(width=100)
    assert row.is_empty() is True


def test_is_empty_no():
    row = Row(width=100)
    row.set_value(50, 1)
    assert row.is_empty() is False


def test_rstrip():
    row = Row(width=100)
    row.set_value(0, 1)
    row.set_value(1, 2)
    row.set_value(2, 3)
    row.set_cell(3, Cell(style="ce5"))
    row.rstrip()
    assert row.width == 4


def test_rstrip_aggressive():
    row = Row(width=100)
    row.set_value(0, 1)
    row.set_value(1, 2)
    row.set_value(2, 3)
    row.set_cell(3, Cell(style="ce5"))
    row.rstrip(aggressive=True)
    assert row.width == 3


def test_rstrip_empty():
    row = Row(width=100)
    row.rstrip(aggressive=True)
    assert row.width == 0


def test_table_row_repeated_cache(table):
    row = table.rows[3]
    assert not row.repeated
    row._table_cache = TableCache()
    row.repeated = 3
    assert row._table_cache.row_idx(5) == 3


def test_force_width_1():
    row = Row(width=3)
    row.set_value(0, 1)
    row.set_value(1, 2)
    row.set_value(2, 3)
    assert row.width == 3
    row.force_width(3)
    assert row.width == 3
    assert row.get_values() == [1, 2, 3]


def test_force_width_2():
    row = Row(width=3)
    row.set_value(0, 1)
    row.set_value(1, 2)
    row.set_value(2, 3)
    assert row.width == 3
    # no effect expected: foce_width do not delete, neither extend
    # # only reduce repeated of empty
    row.force_width(2)
    assert row.width == 3
    assert row.get_values() == [1, 2, 3]


def test_force_width_3():
    row = Row()
    row.set_value(0, 1)
    row.set_value(1, 2)
    row.set_value(2, 3)
    cell = Cell(repeated=4)
    row.append_cell(cell)
    cell = row.last_cell()
    assert cell.repeated == 4
    assert row.get_values() == [1, 2, 3, None, None, None, None]
    cell = row.last_cell()
    assert cell is not None
    assert cell.is_empty(aggressive=True)
    assert cell.repeated == 4
    assert row.width == 7
    assert row._current_length() == 7
    row.force_width(5)
    assert row.width == 5
    assert row.last_cell().repeated == 2


def test_current_length_1():
    row = Row()
    row.set_value(0, 1)
    row.set_value(1, 2)
    assert row._current_length() == 2


def test_current_length_2():
    row = Row()
    row.set_value(0, 1)
    assert row._current_length() == 1


def test_current_length_3():
    row = Row()
    assert row._current_length() == 1  # minimal width


def test_minimized_width():
    row = Row()
    assert row.minimized_width() == 1


def test_last_cell_none():
    row = Row()
    assert row.last_cell() is None


def test_get_elements():
    row = Row()
    result = row.get_elements("wrong")
    assert result == []
