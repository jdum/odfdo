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
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
from __future__ import annotations

from collections.abc import Iterable
from unittest.mock import patch

import pytest

from odfdo.cell import Cell
from odfdo.column import Column
from odfdo.document import Document
from odfdo.row import Row
from odfdo.table import Table
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


def test_iter_columns(table):
    assert len(list(table.iter_columns())) == 7


def test_traverse_func(table):
    # compatibility
    assert table.traverse_columns == table.iter_columns


def test_traverse_columns(table):
    assert len(list(table.traverse_columns())) == 7


def test_get_column_list(table):
    assert len(list(table.get_columns())) == 7


def test_get_column_list_property(table):
    assert len(table.columns) == 7


def test_get_column_list_style(table):
    coordinates = [col.x for col in table.get_columns(style=r"co2")]
    assert coordinates == [2, 3]


def test_get_column(table):
    column = table.get_column(3)
    assert column.style == "co2"
    assert column.x == 3
    column = table.get_column(4)
    assert column.style == "co1"
    assert column.x == 4


def test_set_column(table):
    column = table.get_column(3)
    column_back = table.set_column(4, column)
    assert column_back.x == 4
    column = table.get_column(4)
    assert column.x == 4
    assert column.style == "co2"


def test_insert(table):
    column = table.insert_column(3)
    assert type(column) is Column
    assert column.x == 3


def test_insert_column(table):
    column = table.insert_column(3, Column())
    assert table.width == 8
    assert table.get_row(0).width == 8
    assert column.x == 3


def test_append(table):
    column = table.append_column()
    assert type(column) is Column
    assert column.x == table.width - 1


def test_append_column(table):
    column = table.append_column(Column())
    assert table.width == 8
    assert table.get_row(0).width == 7
    assert column.x == table.width - 1
    # The column must be inserted between the columns and the rows
    assert type(table.children[-1]) is not Column


def test_delete_column(table):
    table.delete_column(3)
    assert table.width == 6
    assert table.get_row(0).width == 6


def test_get_column_cell_values(table):
    assert table.get_column_values(3) == [2, 2, 2, 4]


def test_set_column_cell_values(table):
    table.set_column_values(5, ["a", "b", "c", "d"])
    assert table.get_values() == [
        [1, 1, 1, 2, 3, "a", 3],
        [1, 1, 1, 2, 3, "b", 3],
        [1, 1, 1, 2, 3, "c", 3],
        [1, 2, 3, 4, 5, "d", 7],
    ]


def test_is_column_empty():
    table = Table("Empty", width=10, height=20)
    for x in range(10):
        assert table.is_column_empty(x) is True


def test_is_column_empty_no():
    table = Table("Not Empty", width=10, height=20)
    table.set_value((4, 9), "Bouh !")
    assert table.is_column_empty(4) is False


def test_get_column_values_filter():
    table = Table("Test")
    table.set_value("A1", "v1")
    table.set_value("A2", 123)
    # vals: complete=True, get_type=True
    vals = table.get_column_values(
        0,
        cell_type="string",
        complete=True,
        get_type=True,
    )
    assert len(vals) == 2
    assert vals[0] == ("v1", "string")
    assert vals[1] == (None, None)

    # vals: complete=True, get_type=False
    vals = table.get_column_values(
        0,
        cell_type="string",
        complete=True,
        get_type=False,
    )
    assert vals[1] is None

    # vals: complete=False, get_type=True
    vals = table.get_column_values(
        0,
        cell_type="string",
        complete=False,
        get_type=True,
    )
    assert len(vals) == 1


def test_get_column_values_more():
    table = Table("Test")
    table.set_value("A1", "v1")
    table.set_value("A2", 123)
    cell_float = table.get_cell("A2", clone=False)
    with patch.object(Table, "get_column_cells", return_value=[cell_float]):
        vals = table.get_column_values(
            0,
            cell_type="string",
            complete=True,
            get_type=False,
        )
        assert vals == [None]
        vals = table.get_column_values(
            0,
            cell_type="string",
            complete=True,
            get_type=True,
        )
        assert vals == [(None, None)]


def test_get_column_values_none_internal():
    table = Table("Test")
    table.set_value("A1", "v1")
    with patch.object(Table, "get_column_cells", return_value=[None]):
        vals = table.get_column_values(0, complete=True, get_type=False)
        assert vals == [None]
    with patch.object(Table, "get_column_cells", return_value=[None]):
        vals = table.get_column_values(0, complete=False)
        assert vals == []


def test_get_column_values_branch_gaps():
    table = Table("T")
    table.set_value("A1", "v1")
    table.set_value("A2", 123)
    # Case 1: cell is NOT None but cell_type mismatch
    c2 = table.get_cell("A2")
    with patch.object(Table, "get_column_cells", return_value=[c2]):
        assert table.get_column_values(
            0, cell_type="string", complete=True, get_type=True
        ) == [(None, None)]
        assert table.get_column_values(
            0, cell_type="string", complete=True, get_type=False
        ) == [None]


def test_get_column_values_branch_complete_get_type_false():
    table = Table("T")
    table.set_value("A1", "v1")
    # Case mismatch AND complete=True AND get_type=False
    with patch.object(Table, "get_column_cells", return_value=[table.get_cell("A1")]):
        assert table.get_column_values(
            0, cell_type="float", complete=True, get_type=False
        ) == [None]


def test_get_column_values_complete_none_branch():
    table = Table("T")
    table.set_value("A1", "v1")
    with patch.object(Table, "get_column_cells", return_value=[None]):
        res = table.get_column_values(0, complete=True, get_type=False)
        assert res == [None]
        res = table.get_column_values(0, complete=True, get_type=True)
        assert res == [(None, None)]


def test_get_column_values_branch_complete_get_type_true_mismatch():
    table = Table("T")
    table.set_value("A1", "v1")
    # Case mismatch AND complete=True AND get_type=True
    with patch.object(Table, "get_column_cells", return_value=[table.get_cell("A1")]):
        assert table.get_column_values(
            0, cell_type="float", complete=True, get_type=True
        ) == [(None, None)]


def test_get_column_values_complete_branches_hits():
    table = Table("T")
    table.set_value("A1", "v1")
    table.set_value("A2", "v2")
    # c1 is string "v1". Let's filter by "float"
    c1 = table.get_cell("A1")
    with patch.object(Table, "get_column_cells", return_value=[c1]):
        res = table.get_column_values(
            0, cell_type="float", complete=True, get_type=True
        )
        assert res == [(None, None)]

        res = table.get_column_values(
            0, cell_type="float", complete=True, get_type=False
        )
        assert res == [None]

        res = table.get_column_values(0, cell_type="float", complete=False)
        assert res == []


def test_iter_columns_params():
    table = Table("Test")
    table.set_value("A1", "v1")
    table.set_value("B1", "v2")
    table.set_value("C1", "v3")
    assert list(table.iter_columns(start=2, end=1)) == []
    cols = list(table.iter_columns(start=1, end=1))
    assert len(cols) == 1
    cols = list(table.iter_columns(start=-1))
    assert len(cols) == 3


def test_get_columns_coord():
    table = Table("Test")
    table.set_value("A1", "v1")
    table.set_value("B1", "v2")
    table.set_value("C1", "v3")
    cols = table.get_columns(coord="B:C")
    assert len(cols) == 2


def test_get_column2_edge():
    table = Table("Test")
    col = table._get_column2(10)
    assert col.tag == "table:table-column"


def test_delete_column_outside():
    table = Table("Test")
    table.set_value("A1", "v1")
    table.delete_column(10)
    assert table.width == 1


def test_get_column_cells_filter():
    table = Table("Test")
    table.set_value("A1", "v1")
    table.set_value("A2", "v2")
    cell1 = table.get_cell("A1", clone=False)
    cell1.style = "s1"
    cells = table.get_column_cells(0, style="s1")
    assert len(cells) == 1
    cells = table.get_column_cells(0, content="v2")
    assert len(cells) == 1
    cells = table.get_column_cells(0, cell_type="string")
    assert len(cells) == 2
    cells = table.get_column_cells(0, style="s1", complete=True)
    assert len(cells) == 2
    assert cells[0].style == "s1"
    assert cells[1] is None

    # test mismatched content
    cells = table.get_column_cells(0, content="wrong", complete=True)
    assert len(cells) == 2
    assert cells[0] is None
    assert cells[1] is None


def test_get_column_cells_none_error():
    table = Table("Test")
    table.set_value("A1", "v1")
    # Using mock to force get_cell to return None
    with patch.object(Row, "get_cell", return_value=None):
        with pytest.raises(ValueError):
            table.get_column_cells(0, cell_type="string")


def test_set_column_none():
    table = Table("Test")
    col = table.set_column(0, column=None)
    assert col.tag == "table:table-column"


def test_set_column_append():
    table = Table("Test")
    _col = table.set_column(0, Column())
    assert table.width == 1


def test_set_column_far_append():
    table = Table("Test")
    _col = table.set_column(2, Column())
    assert table.width == 3


def test_insert_column_edges():
    table = Table("Test")
    table.set_value("A1", "v1")
    table.insert_column(1, Column())
    assert table.width == 2
    table.insert_column(5, Column())
    assert table.width == 6
    table.insert_column(0, Column())
    assert table.get_value("B1") == "v1"
    assert table.width == 7


def test_is_column_empty_missing_cell():
    table = Table("Test")
    table.set_value("A1", "v1")
    assert table.is_column_empty(0) is False
    assert table.is_column_empty(1) is True


def test_append_column_repeated():
    table = Table("Test")
    col = Column(repeated=2)
    table.append_column(col, _repeated=2)
    assert table.width == 2


def test_set_column_cells_wrong_height():
    table = Table("Test")
    table.set_value("A1", "v1")
    table.set_value("A2", "v2")
    # height is 2
    with pytest.raises(ValueError, match="col mismatch"):
        table.set_column_cells(0, [Cell()])


def test_delete_column_uneven_branch_hits_final():
    table = Table("T")
    # width is 0.
    table.set_value("A1", "v")
    table.set_value("B1", "v")
    # table.width is now 2.

    # Add a row 1 with 1 cell only
    table.set_value("A2", "v")
    # row 1 width is 1. table.width is 2.

    # delete column 1 (B)
    # width = 2
    table.delete_column(1)
    assert table.get_value("A1") == "v"
    assert table.get_value("A2") == "v"


def test_delete_column_branch_part_false_hits():
    # Table width 3, row 1 width 1.
    table = Table("T")
    table.set_value("A1", "v")
    table.set_value("B1", "v")
    table.set_value("C1", "v")
    # table width 3.
    table.set_value("A2", "v")
    # row 1 width 1.
    # delete column 2 (C).
    # width becomes 2.
    table.delete_column(2)
    assert table.get_value("A2") == "v"


def test_get_column_none_internal():
    table = Table("Test")
    table.set_value("A1", "v1")
    with patch.object(Table, "_get_element_idx2", return_value=None):
        table._table_cache.col_elements = {}
        # Restore width
        table._table_cache.col_map = [0]
        with pytest.raises(ValueError):
            table.get_column(0)


def test_delete_column_uneven_rows():
    table = Table("Uneven")
    table.set_value("A2", "v2")  # row 1 width 1
    table.set_value("B1", "v1")  # row 0 width 2
    # delete column 1 (B). row 1 width is 1. x=1. 1 > 1 is False.
    table.delete_column(1)
    assert table.get_value("A1") is None
    assert table.get_value("A2") == "v2"


def test_is_column_empty_none_internal():
    table = Table("Test")
    table.set_value("A1", "v1")
    # Force get_column_cells to return [None]
    with patch.object(Table, "get_column_cells", return_value=[None]):
        assert table.is_column_empty(0) is True


def test_get_column2_none_internal():
    table = Table("Test")
    table.set_value("A1", "v1")
    # We patch the CLASS TableCache
    with patch.object(TableCache, "col_idx", return_value=None):
        assert table._get_column2(0) is None
    with patch.object(Table, "_get_element_idx2", return_value=None):
        table._table_cache.col_elements = {}
        # Restore width
        table._table_cache.col_map = [0]
        assert table._get_column2(0) is None


def test_insert_column_uneven_rows():
    table = Table("Uneven")
    table.set_value("A1", "v1")  # row 0 width 1
    table.set_value("B2", "v2")  # row 1 width 2
    table.insert_column(1)
    assert table.width == 3
    assert table.get_value("A1") == "v1"
    assert table.get_value("C2") == "v2"


def test_append_column_none_internal_2():
    table = Table("Test")
    table.set_value("A1", "v1")
    with patch.object(Table, "_get_element_idx2", return_value=None):
        table._table_cache.col_elements = {}
        # Restore width
        table._table_cache.col_map = [0]
        with pytest.raises(ValueError):
            table.append_column(Column())


def test_delete_column_get_value():
    table = Table("T")
    table.set_value("A1", "v1")
    table.set_value("B2", "v2")
    # row 0 width is 1. row 1 width is 2.
    # delete column 1 (B). row 0 width is 1. x is 1. 1 > 1 is False.
    table.delete_column(1)
    # row 0 was skipped by if row.width > x
    assert table.get_value("A1") == "v1"
    # row 1 had B2 deleted, so C2 became B2? No, B2 is at x=1.
    # Actually B2 was at x=1. row 1 width was 2. 2 > 1 is True.
    # row 1.delete_cell(1) was called.
    assert table.get_value("A2") is None


def test_get_cells_none_branch_part():
    table = Table("T")
    table.set_value("A1", "v")
    # Coverage for get_cells branch where some cell is None
    # We need a row where get_cell returns None
    with patch.object(Row, "get_cell", return_value=None):
        with pytest.raises(ValueError):
            table.get_column_cells(0, cell_type="string")


def test_get_column2_cache_miss_xml_exists():
    table = Table("T")
    table.set_value("A1", "v")
    table._table_cache.col_elements = {}
    # ensure it's in the col_map
    assert 0 in table._table_cache.col_map
    col = table._get_column2(0)
    assert col.tag == "table:table-column"


def test_delete_column_shorter_row_branch():
    table = Table("T")
    table.set_value("A1", "v")
    table.set_value("B1", "v")
    # row 0 width 2
    table.set_value("A2", "v")
    # row 1 width 1
    # total width 2
    # delete column 1 (B). row 1 width is 1. width is 2. 1 >= 2 is False.
    table.delete_column(1)
    assert table.get_value("A1") == "v"
    assert table.get_value("A2") == "v"


def test_get_column2_cached_branch():
    table = Table("T")
    table.set_value("A1", "v")
    # Cache it
    _col = table._get_column2(0)
    col2 = table._get_column2(0)
    assert col2.tag == "table:table-column"


def test_get_column_cells_none_mock_branch():
    table = Table("T")
    table.set_value("A1", "v")
    with patch.object(Row, "get_cell", return_value=None):
        with pytest.raises(ValueError):
            table.get_column_cells(0, cell_type="string")


def test_insert_column_shorter_row_branch():
    table = Table("T")
    table.set_value("A1", "v")
    # width 1
    table.set_value("A2", "v")
    # insert at 5. row 0 width 1. 1 > 5 is False.
    table.insert_column(5)
    assert table.width == 6


def test_delete_column_uneven_branch_hits():
    table = Table("T")
    table.set_value("A1", "v")
    table.set_value("B1", "v")
    # row 0 width is 2.
    table.set_value("A2", "v")
    # row 1 width is 1.
    # Table width is 2.
    # delete column 1 (B).
    table.delete_column(1)
    assert table.get_value("A1") == "v"
    assert table.get_value("B1") is None
    assert table.get_value("A2") == "v"
