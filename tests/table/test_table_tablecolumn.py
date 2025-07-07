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

from odfdo.column import Column
from odfdo.document import Document
from odfdo.table import Table


@pytest.fixture
def table(samples) -> Iterable[Table]:
    # simpletable :
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1   2	3	4	5	6	7
    document = Document(samples("simple_table.ods"))
    yield document.body.get_table(name="Example1")


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
