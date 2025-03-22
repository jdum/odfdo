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

from odfdo import Element
from odfdo.document import Document
from odfdo.table import Row, Table


@pytest.fixture
def body(samples) -> Iterable[Element]:
    document = Document(samples("simple_table.ods"))
    yield document.body


@pytest.fixture
def table(samples) -> Iterable[Table]:
    # simpletable :
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1   2	3	4	5	6	7
    document = Document(samples("simple_table.ods"))
    yield document.body.get_table(name="Example1")


def test_get_table_list(body):
    assert len(body.get_tables()) == 3


def test_get_table_list_property(body):
    assert len(body.tables) == 3


def test_get_table_list_style(body):
    assert len(body.get_tables(style="ta1")) == 3


def test_get_table_by_name(body):
    name = "New Table"
    body.append(Table(name))
    table = body.get_table(name=name)
    assert table.name == name


def test_get_table_by_position(body):
    body.append(Table("New Table"))
    table = body.get_table(position=3)
    assert table.name == "New Table"


def test_get_table_style(table):
    assert table.style == "ta1"


def test_get_table_printable(table):
    assert table.printable is False


def test_get_table_width(table):
    assert table.width == 7


def test_get_table_height(table):
    assert table.height == 4


def test_get_table_size(table):
    assert table.size == (7, 4)


def test_get_table_size_empty():
    table = Table("Empty")
    assert table.size == (0, 0)


def test_get_table_width_after():
    table = Table("Empty")
    assert table.width == 0
    assert table.height == 0
    # The first row creates the columns
    table.append_row(Row(width=5))
    assert table.width == 5
    assert table.height == 1
    # The subsequent ones don't
    table.append_row(Row(width=5))
    assert table.width == 5
    assert table.height == 2


def test_get_values(table):
    expected = [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    assert table.get_values() == expected


def test_set_table_values_with_clear(table):
    values = [
        ["a", "b", "c", "d", "e", "f", "g"],
        ["h", "i", "j", "k", "l", "m", "n"],
        ["o", "p", "q", "r", "s", "t", "u"],
        ["v", "w", "x", "y", "z", "aa", "ab"],
    ]
    table.clear()
    table.set_values(values)
    assert table.get_values() == values


def test_set_table_values_big(table):
    values = [
        ["a", "b", "c", "d", "e", "f", "g"],
        ["h", "i", "j", "k", "l", "m", "n"],
        ["o", "p", "q", "r", "s", "t", "u"],
        ["o", "p", "q", "r", "s", "t", "u"],
        ["o", "p", "q", "r", "s", "t", "u"],
        ["o", "p", "q", "r", "s", "t", "u"],
        ["v", "w", "x", "y", "z", "aa", "ab"],
        ["v", "w", "x", "y", "z", "aa", "ab"],
    ]
    table.set_values(values)
    assert table.get_values() == values
    assert table.size == (7, 8)


def test_set_table_values_small(table):
    values = [
        ["a", "b", "c"],
        ["h", "i", "j", "k", "l", "m", "n"],
        ["o", "p", None, None, "s", "t", "u"],
    ]
    table.set_values(values)
    assert table.size == (7, 4)
    assert table.get_values() == [
        ["a", "b", "c", 2, 3, 3, 3],
        ["h", "i", "j", "k", "l", "m", "n"],
        ["o", "p", None, None, "s", "t", "u"],
        [1, 2, 3, 4, 5, 6, 7],
    ]


def test_set_table_values_small_coord(table):
    values = [
        ["a", "b", "c"],
        ["h", "i", "j", "k", "l", "m", "n"],
        ["o", "p", None, None, "s", "t", "u"],
    ]
    table.set_values(values, coord=("c2"))
    assert table.size == (9, 4)
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3, None, None],
        [1, 1, "a", "b", "c", 3, 3, None, None],
        [1, 1, "h", "i", "j", "k", "l", "m", "n"],
        [1, 2, "o", "p", None, None, "s", "t", "u"],
    ]


def test_set_table_values_small_coord_far(table):
    values = [["a", "b", "c"], ["h", None], ["o"]]
    table.set_values(values, coord=("J6"))
    assert table.size == (12, 8)
    expected = [
        [1, 1, 1, 2, 3, 3, 3, None, None, None, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None, None, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None, None, None, None],
        [1, 2, 3, 4, 5, 6, 7, None, None, None, None, None],
        [
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ],
        [None, None, None, None, None, None, None, None, None, "a", "b", "c"],
        [None, None, None, None, None, None, None, None, None, "h", None, None],
        [None, None, None, None, None, None, None, None, None, "o", None, None],
    ]
    assert table.get_values() == expected


def test_set_table_values_small_type(table):
    values = [[10, None, 30], [None, 40]]
    table.set_values(values, coord=("C4"), cell_type="percentage")
    assert table.size == (7, 5)
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 10, None, 30, 6, 7],
        [None, None, None, 40, None, None, None],
    ]
    assert table.get_values(coord="4:", get_type=True) == [
        [
            (1, "float"),
            (2, "float"),
            (10, "percentage"),
            (None, None),
            (30, "percentage"),
            (6, "float"),
            (7, "float"),
        ],
        [
            (None, None),
            (None, None),
            (None, None),
            (40, "percentage"),
            (None, None),
            (None, None),
            (None, None),
        ],
    ]


def test_rstrip_table(samples):
    document = Document(samples("styled_table.ods"))
    table = document.body.get_table(name="Feuille1").clone
    table.rstrip()
    assert table.size == (5, 9)


# simpletable :
#   1	1	1	2	3	3	3
#   1	1	1	2	3	3	3
#   1	1	1	2	3	3	3
#   1   2	3	4	5	6	7


def test_table_transpose(table):
    table.transpose()
    assert table.get_values() == [
        [1, 1, 1, 1],
        [1, 1, 1, 2],
        [1, 1, 1, 3],
        [2, 2, 2, 4],
        [3, 3, 3, 5],
        [3, 3, 3, 6],
        [3, 3, 3, 7],
    ]


def test_table_transpose_2(table):
    table.transpose("A1:G1")
    assert table.get_values() == [
        [1, None, None, None, None, None, None],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [2, 2, 3, 4, 5, 6, 7],
        [3, None, None, None, None, None, None],
        [3, None, None, None, None, None, None],
        [3, None, None, None, None, None, None],
    ]


def test_table_transpose_3(table):
    table.delete_row(3)
    table.delete_row(2)
    table.delete_row(1)
    table.transpose()
    assert table.get_values() == [[1], [1], [1], [2], [3], [3], [3]]


def test_table_transpose_4(table):
    table.transpose("F2:F4")
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3, None],
        [1, 1, 1, 2, 3, 3, 3, 6],
        [1, 1, 1, 2, 3, None, 3, None],
        [1, 2, 3, 4, 5, None, 7, None],
    ]
