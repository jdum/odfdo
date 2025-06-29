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
from odfdo.table import Row, Table


@pytest.fixture
def table(samples) -> Iterable[Table]:
    # simpletable :
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1   2	3	4	5	6	7
    document = Document(samples("simple_table.ods"))
    yield document.body.get_table(name="Example1")


def test_traverse_rows(table):
    assert len(list(table.traverse())) == 4


def test_get_row_values(table):
    assert table.get_row_values(3) == [1, 2, 3, 4, 5, 6, 7]


def test_get_row_list(table):
    assert len(list(table.get_rows())) == 4
    assert len(list(table.get_rows("2:3"))) == 2


def test_get_row_list_regex(table):
    coordinates = [row.y for row in table.get_rows(content=r"4")]
    assert coordinates == [3]


def test_get_row_list_style(table):
    # Set a different style manually
    row = table.get_elements("table:table-row")[2]
    row.style = "A Style"
    coordinates = [row.y for row in table.get_rows(style=r"A Style")]
    assert coordinates == [2]


def test_get_row(table):
    row = table.get_row(3)
    assert row.get_values() == [1, 2, 3, 4, 5, 6, 7]
    assert row.y == 3


def test_get_row_repeat_1(table):
    # Set a repetition manually
    row_1 = table.get_elements("table:table-row")[1]
    assert row_1._table_cache.row_map == [0, 1, 2, 3]
    row_1.repeated = 2
    assert row_1._table_cache.row_map == [0, 2, 3, 4]


def test_get_row_repeat_1_cache_id(table):
    # Set a repetition manually
    row_1 = table.get_elements("table:table-row")[1]
    row_1.repeated = 2
    assert id(row_1._table_cache) == id(table._table_cache)


def test_get_row_repeat_2(table):
    # Set a repetition manually
    row_1 = table.get_elements("table:table-row")[1]
    row_1.repeated = 2
    assert row_1.repeated == 2
    row = table.get_row(4)
    assert row.get_values() == [1, 2, 3, 4, 5, 6, 7]
    assert row.y == 4


def test_set_row(table):
    row = table.get_row(3)
    row.set_value(3, "Changed")
    row_back = table.set_row(1, row)
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, "Changed", 5, 6, 7],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    # test columns are synchronized
    assert table.width == 7
    assert row_back.y == 1


def test_set_row_repeat(table):
    # Set a repetition manually
    table.get_elements("table:table-row")[2].repeated = 3
    row = table.get_row(5)
    row.set_value(3, "Changed")
    table.set_row(2, row)
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, "Changed", 5, 6, 7],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    # test columns are synchronized
    assert table.width == 7


def test_set_row_smaller(table):
    table.set_row(0, Row(width=table.width - 1))
    assert table.height == 4


def test_set_row_bigger(table):
    table.set_row(0, Row(width=table.width + 1))
    assert table.height == 4


def test_insert(table):
    row = table.insert_row(2)
    assert type(row) is Row
    assert row.y == 2


def test_insert_row(table):
    row = table.get_row(3)
    row_back = table.insert_row(2, row)
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    # test columns are synchronized
    assert table.width == 7
    assert row_back.y == 2


def test_insert_row_repeated(table):
    # Set a repetition manually
    table.get_elements("table:table-row")[2].repeated = 3
    row = table.get_row(5)
    table.insert_row(2, row)
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    # test columns are synchronized
    assert table.width == 7


def test_insert_row_smaller(table):
    small_row = Row(width=table.width - 1)
    table.insert_row(0, small_row)
    assert table.height == 5


def test_insert_row_bigger(table):
    big_row = Row(width=table.width + 1)
    table.insert_row(0, big_row)
    assert table.height == 5


def test_append(table):
    row = table.append_row()
    assert type(row) is Row


def test_append_row(table):
    row = table.get_row(0)
    row_back = table.append_row(row)
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
        [1, 1, 1, 2, 3, 3, 3],
    ]
    # test columns are synchronized
    assert table.width == 7
    assert row_back.y == table.height - 1


def test_append_row_smaller(table):
    table.append_row(Row(width=table.width - 1))
    assert table.height == 5


def test_append_row_bigger(table):
    table.append_row(Row(width=table.width + 1))
    assert table.height == 5


def test_delete_row(table):
    table.delete_row(2)
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    # test columns are synchronized
    assert table.width == 7


def test_delete_row_repeat(table):
    # Set a repetition manually
    table.get_elements("table:table-row")[2].repeated = 3
    table.delete_row(2)
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    # Test columns are synchronized
    assert table.width == 7


def test_is_row_empty():
    table = Table("Empty", width=10, height=20)
    for y in range(20):
        assert table.is_row_empty(y) is True


def test_is_row_empty_no():
    table = Table("Not Empty", width=10, height=20)
    table.set_value((4, 9), "Bouh !")
    assert table.is_row_empty(9) is False
