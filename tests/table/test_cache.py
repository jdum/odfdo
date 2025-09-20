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

from odfdo.cell import Cell
from odfdo.column import Column
from odfdo.document import Document
from odfdo.row import Row
from odfdo.table import Table
from odfdo.table_cache import RowCache, _erase_map_once, _insert_map_once


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


def test_internal_bad_insert(table):
    cache = table._table_cache
    row_map = cache.row_map
    bad_val = len(cache.row_map) + 1
    with pytest.raises(IndexError):
        _insert_map_once(row_map, bad_val, 0)


def test_internal_bad_erase(table):
    cache = table._table_cache
    row_map = cache.row_map
    bad_val = len(cache.row_map)
    with pytest.raises(IndexError):
        _erase_map_once(row_map, bad_val)


def test_internal_del_row_0(table):
    table.delete_row(0)
    assert table.height == 3


def test_internal_row_cache_str(table):
    row = table.get_row(0)
    cache = row._row_cache
    assert str(cache) == "RC cell:[2, 3, 6]"


def test_internal_row_map_length(table):
    row = table.get_row(0)
    cache = row._row_cache
    assert len(cache.cell_map) == 3
    assert cache.cell_map_length() == 3


def test_internal_row_erase_cell(table):
    row = table.get_row(0)
    cache = row._row_cache
    row.delete_cell(0)
    assert cache.cell_map_length() == 3
    assert str(cache) == "RC cell:[1, 2, 5]"


def test_internal_row_erase_cell_2(table):
    row = table.get_row(0)
    cache = row._row_cache
    row.delete_cell(0)
    row.delete_cell(0)
    assert cache.cell_map_length() == 3
    assert str(cache) == "RC cell:[0, 1, 4]"


def test_internal_row_erase_cell_3(table):
    row = table.get_row(0)
    cache = row._row_cache
    row.delete_cell(0)
    row.delete_cell(0)
    row.delete_cell(0)
    assert cache.cell_map_length() == 2
    assert str(cache) == "RC cell:[0, 3]"


def test_internal_set_cell_in_cache(table):
    row = table.get_row(0)
    cache = row._row_cache
    cell = Cell()
    with pytest.raises(ValueError):
        cache.set_cell_in_cache(42, cell, row, True)


def test_internal_set_cell_in_cache2(table):
    row = table.get_row(0)
    cache = row._row_cache
    cell = row.get_cell(0)
    cell.value = 42
    row.set_cell(0, cell)
    assert str(cache) == "RC cell:[0, 2, 3, 6]"
    assert row.get_values() == [42, 1, 1, 2, 3, 3, 3]


def test_internal_insert_cell_in_cache(table):
    row = table.get_row(0)
    cache = row._row_cache
    cell = Cell()
    with pytest.raises(ValueError):
        cache.insert_cell_in_cache(42, cell, row)


def test_internal_insert_cell_in_cache2(table):
    row = table.get_row(0)
    cache = row._row_cache
    cell = row.get_cell(0)
    cell.value = 42
    row.insert_cell(0, cell)
    assert str(cache) == "RC cell:[0, 3, 4, 7]"
    assert row.get_values() == [42, 1, 1, 1, 2, 3, 3, 3]


def test_internal_delete_cell_in_cache(table):
    row = table.get_row(0)
    cache = row._row_cache
    with pytest.raises(ValueError):
        cache.delete_cell_in_cache(42, row)


def test_internal_delete_cell_in_cache2():
    cache = RowCache()
    current_cached = cache.cached_cell(0)
    assert current_cached is None


def test_internal_cell_in_cache(table):
    row = table.get_row(0)
    cache = row._row_cache
    assert cache.cell_map == [2, 3, 6]
    assert len(cache.cell_elements) == 0
    row.get_cell(0)
    assert len(cache.cell_elements) == 1


def test_internal_cell_in_cache_then_delete(table):
    row = table.get_row(0)
    cache = row._row_cache
    assert cache.cell_map == [2, 3, 6]
    assert len(cache.cell_elements) == 0
    row.get_cell(0)
    row.delete_cell(0)
    assert len(cache.cell_elements) == 0


def test_internal_table_cache_str(table):
    cache = table._table_cache
    assert str(cache) == "TC row:[0, 1, 2, 3] col:[1, 3, 6]"


def test_internal_table_row_map_length(table):
    cache = table._table_cache
    assert len(cache.row_map) == 4


def test_internal_table_col_map_length(table):
    cache = table._table_cache
    assert len(cache.col_map) == 3
    assert cache.col_map_length() == 3


def test_internal_table_row_bad_idx(table):
    cache = table._table_cache
    assert cache.row_idx(1000) is None


def test_internal_table_col_bad_idx(table):
    cache = table._table_cache
    assert cache.col_idx(1000) is None


def test_internal_table_erase_row(table):
    cache = table._table_cache
    table.get_row(0)
    table.delete_row(0)
    assert len(cache.row_map) == 3
    assert str(cache) == "TC row:[0, 1, 2] col:[1, 3, 6]"


def test_internal_table_set_row_in_cache(table):
    cache = table._table_cache
    row = Row()
    with pytest.raises(ValueError):
        cache.set_row_in_cache(42, row, table, False)


def test_internal_table_set_col_in_cache(table):
    cache = table._table_cache
    col = Column()
    with pytest.raises(ValueError):
        cache.set_col_in_cache(42, col, table)


def test_internal_table_set_col_in_cache_ok(table):
    cache = table._table_cache
    col = table.get_column(0)
    table.insert_column(0, col)
    table.insert_column(-1, col)
    assert str(cache) == "TC row:[0, 1, 2, 3] col:[1, 3, 5, 7, 9, 10]"


def test_internal_table_set_col_in_cache_ok2(table):
    previous = table.width
    table.get_column(0)
    new_col = Column()
    table.set_column(0, new_col)
    assert table.width == previous


def test_internal_table_get_col_in_cache_0(table):
    cache = table._table_cache
    assert len(cache.col_elements) == 0


def test_internal_table_get_col_in_cache_1(table):
    cache = table._table_cache
    idx = cache.col_idx(0)
    assert idx == 0


def test_internal_table_get_col_in_cache_2(table):
    cache = table._table_cache
    col = cache.cached_col(0)
    assert col is None


def test_internal_table_get_col_in_cache_3(table):
    cache = table._table_cache
    col = table.get_column(0)
    col = cache.cached_col(0)
    assert isinstance(col, Column)


def test_internal_table_insert_row_in_cache(table):
    cache = table._table_cache
    row = Row()
    with pytest.raises(ValueError):
        cache.insert_row_in_cache(42, row, table)


def test_internal_table_insert_row_in_cache2(table):
    cache = table._table_cache
    row = table.get_row(0)
    table.insert_row(0, row)
    table.insert_row(0, row)
    assert str(cache) == "TC row:[0, 1, 2, 3, 4, 5] col:[1, 3, 6]"


def test_internal_table_insert_column_in_cache(table):
    cache = table._table_cache
    col = Column()
    with pytest.raises(ValueError):
        cache.insert_col_in_cache(42, col, table)


def test_internal_table_insert_column_in_cache2(table):
    cache = table._table_cache
    col = table.get_column(0)
    table.insert_column(0, col)
    table.insert_column(0, col)
    assert str(cache) == "TC row:[0, 1, 2, 3] col:[1, 3, 5, 7, 10]"


def test_internal_table_delete_row_in_cache(table):
    cache = table._table_cache
    with pytest.raises(ValueError):
        cache.delete_row_in_cache(42, table)


def test_internal_table_delete_col_in_cache(table):
    cache = table._table_cache
    with pytest.raises(ValueError):
        cache.delete_col_in_cache(42, table)


def test_internal_table_delete_col_in_cache_ok(table):
    cache = table._table_cache
    table.get_column(0)
    cache.delete_col_in_cache(0, table)
