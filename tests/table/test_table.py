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

import pytest

from odfdo.document import Document
from odfdo.element import Element
from odfdo.row import Row
from odfdo.table import Table


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


def test_get_sheets_alias(body):
    assert body.get_tables == body.get_sheets


def test_get_sheets_list(body):
    assert len(body.get_sheets()) == 3


def test_get_table_list_property(body):
    assert len(body.tables) == 3


def test_get_sheets_list_property(body):
    assert len(body.sheets) == 3


def test_get_table_list_style(body):
    assert len(body.get_tables(style="ta1")) == 3


def test_get_table_by_name(body):
    name = "New Table"
    body.append(Table(name))
    table = body.get_table(name=name)
    assert table.name == name


def test_get_sheet_alias(body):
    assert body.get_sheet == body.get_table


def test_get_sheet_by_name(body):
    name = "New Table"
    body.append(Table(name))
    table = body.get_sheet(name=name)
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


def test_table_values_getter(table):
    assert table.values == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]


def test_table_values_setter():
    t = Table("Test")
    t.values = [[1, 2], [3, 4]]
    assert t.values == [[1, 2], [3, 4]]


def test_table_values_property_styled_cell_replace(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    expected_initial = [
        ["spanned text", None, None, None, "3.14", None, None],
        [None, None, None, None, None, None, 16],
        [None, None, None, None, None, None, None],
        ["blue", "orange", None, None, None, None, None],
    ]
    assert table.values == expected_initial
    style_e1 = table.get_cell("E1").style
    style_a4 = table.get_cell("A4").style
    style_b4 = table.get_cell("B4").style
    values = table.values
    values[0][0] = "modified span"
    values[1][-1] = 17
    values[3][1] = "still"
    table.values = values

    expected_after = [
        ["modified span", None, None, None, "3.14", None, None],
        [None, None, None, None, None, None, 17],
        [None, None, None, None, None, None, None],
        ["blue", "still", None, None, None, None, None],
    ]
    assert table.values == expected_after
    cell_a1 = table.get_cell("A1")
    assert cell_a1.value == "modified span"
    assert cell_a1.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1.get_attribute("table:number-rows-spanned") == "2"
    assert table.get_cell("E1").style == style_e1
    assert table.get_cell("A4").style == style_a4
    assert table.get_cell("B4").style == style_b4
    assert table.get_cell("A1").is_spanned()
    assert table.get_cell("E1").is_spanned()
    assert table.get_cell("B1").is_spanned(covered=True)


def test_table_values_setter_partiel_1(table):
    # [
    # [1, 1, 1, 2, 3, 3, 3],
    # [1, 1, 1, 2, 3, 3, 3],
    # [1, 1, 1, 2, 3, 3, 3],
    # [1, 2, 3, 4, 5, 6, 7],
    # ]

    # guard agains str iterable
    table.values = ["ab", "cd", "ef"]
    assert table.values == [
        ["ab", 1, 1, 2, 3, 3, 3],
        ["cd", 1, 1, 2, 3, 3, 3],
        ["ef", 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]


def test_table_values_setter_partiel_2(table):
    # [
    # [1, 1, 1, 2, 3, 3, 3],
    # [1, 1, 1, 2, 3, 3, 3],
    # [1, 1, 1, 2, 3, 3, 3],
    # [1, 2, 3, 4, 5, 6, 7],
    # ]

    # guard agains str iterable
    table.values = [["ab", "cd", "ef"]]
    assert table.values == [
        ["ab", "cd", "ef", 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]


def test_table_values_setter_partiel_3(table):
    # [
    # [1, 1, 1, 2, 3, 3, 3],
    # [1, 1, 1, 2, 3, 3, 3],
    # [1, 1, 1, 2, 3, 3, 3],
    # [1, 2, 3, 4, 5, 6, 7],
    # ]

    # guard agains str iterable
    table.values = ["abcd"]
    assert table.values == [
        ["abcd", 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]


def test_table_values_setter_partiel_4(table):
    # [
    # [1, 1, 1, 2, 3, 3, 3],
    # [1, 1, 1, 2, 3, 3, 3],
    # [1, 1, 1, 2, 3, 3, 3],
    # [1, 2, 3, 4, 5, 6, 7],
    # ]

    # guard agains str iterable
    table.values = "abcd"
    assert table.values == [
        ["abcd", 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
