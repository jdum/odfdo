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

from odfdo.document import Document
from odfdo.row import Row
from odfdo.row_group import RowGroup
from odfdo.table import Table


@pytest.fixture
def table(samples) -> Iterable[Table]:
    # simple table with row group:
    #
    #   a2	b2
    #   a3	b3
    document = Document(samples("rowgroup.ods"))
    yield document.body.get_table(0)


def test_create_minimal_rg():
    rg = RowGroup()
    result = "<table:table-row-group/>"
    assert rg.serialize() == result


def test_create_rg_1():
    rg = RowGroup(height=1)
    result = "<table:table-row-group><table:table-row/></table:table-row-group>"
    assert rg.serialize() == result


def test_create_repr():
    rg = RowGroup(height=1)
    assert repr(rg) == "<RowGroup>"


def test_create_rg_2():
    rg = RowGroup(height=2)
    result = (
        "<table:table-row-group>"
        "<table:table-row/><table:table-row/>"
        "</table:table-row-group>"
    )
    assert rg.serialize() == result


def test_create_rg_1_2():
    rg = RowGroup(height=1, width=2)
    result = (
        "<table:table-row-group>"
        "<table:table-row><table:table-cell/><table:table-cell/>"
        "</table:table-row>"
        "</table:table-row-group>"
    )
    assert rg.serialize() == result


def test_create_rg_2_2():
    rg = RowGroup(height=2, width=2)
    result = (
        "<table:table-row-group>"
        "<table:table-row><table:table-cell/><table:table-cell/>"
        "</table:table-row>"
        "<table:table-row><table:table-cell/><table:table-cell/>"
        "</table:table-row>"
        "</table:table-row-group>"
    )
    assert rg.serialize() == result


def test_table_row_groups(table):
    assert len(table.row_groups) == 1


def test_table_row_groups_rows(table):
    rg = table.row_groups[0]
    count = 0
    for item in rg.children:
        if item.tag == "table:table-row":
            count += 1
    assert count == 2


def test_table_all_rows(table):
    assert len(table.rows) == 3


def test_table_cell_repeated_1(table):
    row1 = table.get_row(1)
    assert row1.get_values() == ["a2", "b2"]
    cell = table.get_cell("a2", clone=False)
    assert not cell.repeated
    cell_row = cell.parent
    rg = cell_row.parent
    assert isinstance(cell_row, Row)
    assert isinstance(rg, RowGroup)


def test_table_cell_repeated_2(table):
    cell = table.get_cell("a2", clone=False)
    cell.repeated = 3
    assert cell.repeated == 3
    row = cell.parent
    assert row.get_values() == ["a2", "a2", "a2", "b2"]
