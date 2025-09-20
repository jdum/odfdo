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
def row(samples) -> Iterable[Table]:
    # simpletable :
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1   2	3	4	5	6	7
    document = Document(samples("simple_table.ods"))
    table = document.body.get_table(name="Example1")
    yield table.get_row(1)


@pytest.fixture
def row_repeats(samples) -> Iterable[Table]:
    # simpletable :
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1   2	3	4	5	6	7
    document = Document(samples("simple_table.ods"))
    table = document.body.get_table(name="Example1")
    yield table.get_row(0)


def test_on_empty_row():
    row = Row()
    assert row.get_values() == []
    assert row.get_values(complete=True) == []
    assert row.get_values(complete=True, get_type=True) == []
    assert row.get_values((0, 10)) == []
    assert row.get_values(cell_type="all") == []
    assert row.get_values(cell_type="All") == []
    assert row.get_values((2, 3), complete=True) == []


def test_get_values_count(row):
    assert len(row.get_values()) == 7


def test_get_values_coord(row):
    coord = (0, 8)
    assert len(row.get_values(coord)) == 7
    coord = "a1:c2"
    assert len(row.get_values(coord)) == 3
    coord = "a1:a2"
    assert len(row.get_values(coord)) == 1
    coord = "a1:EE2"
    assert len(row.get_values(coord)) == 7
    coord = "D1"
    assert len(row.get_values(coord)) == 0
    coord = "c5:a1"
    assert len(row.get_values(coord)) == 0
    coord = (5, 6)
    assert len(row.get_values(coord)) == 2
    coord = (-5, 6)
    assert len(row.get_values(coord)) == 5
    coord = (0, -1)
    assert len(row.get_values(coord)) == 7
    coord = (0, -2)
    assert len(row.get_values(coord)) == 6
    coord = (-1, -1)
    assert len(row.get_values(coord)) == 1
    coord = (1, 0)
    assert len(row.get_values(coord)) == 0


def test_get_values_cell_type(row):
    values = row.get_values(cell_type="all")
    assert len(values) == 7
    values = row.get_values(cell_type="float")
    assert len(values) == 7
    assert values == [1, 1, 1, 2, 3, 3, 3]
    values = row.get_values(cell_type="percentage")
    assert len(values) == 0
    values = row.get_values(cell_type="string")
    assert len(values) == 0


def test_get_values_cell_type2(row):
    row.append_cell(Cell(value="bob"), clone=False)
    row.append_cell(Cell(value=14, cell_type="percentage"))
    row.append_cell(Cell(value="bob2"), clone=False)
    values = row.get_values(cell_type="all")
    assert len(values) == 7 + 3
    assert values == [1, 1, 1, 2, 3, 3, 3, "bob", 14, "bob2"]
    values = row.get_values(cell_type="float")
    assert len(values) == 7
    assert values == [1, 1, 1, 2, 3, 3, 3]
    values = row.get_values(cell_type="percentage")
    assert len(values) == 1
    assert values == [14]
    values = row.get_values(cell_type="string")
    assert len(values) == 2
    assert values == ["bob", "bob2"]


def test_get_values_cell_type2_with_hole(row):
    row.append_cell(Cell(value="bob"), clone=False)
    row.append_cell(Cell(value=14, cell_type="percentage"))
    row.append_cell(Cell(value="bob2"), clone=False)
    row.set_cell(12, Cell(value="far"), clone=False)
    values = row.get_values(cell_type="all")  # aka all non empty
    assert len(values) == 11
    assert values == [1, 1, 1, 2, 3, 3, 3, "bob", 14, "bob2", "far"]
    values = row.get_values()  # difference when requestion everything
    assert len(values) == 13
    assert values == [1, 1, 1, 2, 3, 3, 3, "bob", 14, "bob2", None, None, "far"]
    values = row.get_values(cell_type="float")
    assert len(values) == 7
    assert values == [1, 1, 1, 2, 3, 3, 3]
    values = row.get_values(cell_type="percentage")
    assert len(values) == 1
    assert values == [14]
    values = row.get_values(cell_type="string")
    assert len(values) == 3
    assert values == ["bob", "bob2", "far"]
    values = row.get_values(":")  # requesting everything
    assert len(values) == 13
    assert values == [1, 1, 1, 2, 3, 3, 3, "bob", 14, "bob2", None, None, "far"]
    values = row.get_values(cell_type="float")
    assert len(values) == 7
    assert values == [1, 1, 1, 2, 3, 3, 3]
    values = row.get_values(cell_type="percentage")
    assert len(values) == 1
    assert values == [14]
    values = row.get_values(cell_type="string")
    assert len(values) == 3
    assert values == ["bob", "bob2", "far"]
    values = row.get_values(":")  # requesting everything
    assert len(values) == 13
    assert values == [1, 1, 1, 2, 3, 3, 3, "bob", 14, "bob2", None, None, "far"]
    values = row.get_values(cell_type="float")
    assert len(values) == 7
    assert values == [1, 1, 1, 2, 3, 3, 3]
    values = row.get_values(cell_type="percentage")
    assert len(values) == 1
    assert values == [14]
    values = row.get_values(cell_type="string")
    assert len(values) == 3
    assert values == ["bob", "bob2", "far"]
    values = row.get_values("")  # requesting everything 2
    assert len(values) == 13
    assert values == [1, 1, 1, 2, 3, 3, 3, "bob", 14, "bob2", None, None, "far"]
    values = row.get_values(cell_type="float")
    assert len(values) == 7
    assert values == [1, 1, 1, 2, 3, 3, 3]
    values = row.get_values(cell_type="percentage")
    assert len(values) == 1
    assert values == [14]
    values = row.get_values(cell_type="string")
    assert len(values) == 3
    assert values == ["bob", "bob2", "far"]


def test_get_values_cell_type2_with_hole_and_get_type(row):
    row.append_cell(Cell(value="bob"), clone=False)
    row.append_cell(Cell(value=14, cell_type="percentage"))
    row.append_cell(Cell(value="bob2"), clone=False)
    row.set_cell(12, Cell(value="far"), clone=False)
    values = row.get_values(cell_type="all", get_type=True)  # aka all non empty
    assert len(values) == 11
    assert values == [
        (1, "float"),
        (1, "float"),
        (1, "float"),
        (2, "float"),
        (3, "float"),
        (3, "float"),
        (3, "float"),
        ("bob", "string"),
        (14, "percentage"),
        ("bob2", "string"),
        ("far", "string"),
    ]
    values = row.get_values(get_type=True)  # difference when  everything
    assert len(values) == 13
    assert values == [
        (1, "float"),
        (1, "float"),
        (1, "float"),
        (2, "float"),
        (3, "float"),
        (3, "float"),
        (3, "float"),
        ("bob", "string"),
        (14, "percentage"),
        ("bob2", "string"),
        (None, None),
        (None, None),
        ("far", "string"),
    ]
    values = row.get_values(cell_type="float", get_type=True)
    assert len(values) == 7
    assert values == [
        (1, "float"),
        (1, "float"),
        (1, "float"),
        (2, "float"),
        (3, "float"),
        (3, "float"),
        (3, "float"),
    ]
    values = row.get_values(cell_type="percentage", get_type=True)
    assert len(values) == 1
    assert values == [(14, "percentage")]
    values = row.get_values(cell_type="string", get_type=True)
    assert len(values) == 3
    assert values == [("bob", "string"), ("bob2", "string"), ("far", "string")]


def test_get_values_cell_type2_complete(row):
    row.append_cell(Cell(value="bob"), clone=False)
    row.append_cell(Cell(value=14, cell_type="percentage"))
    row.append_cell(Cell(value="bob2"), clone=False)
    row.set_cell(12, Cell(value="far"), clone=False)
    values = row.get_values(cell_type="ALL", complete=True)
    assert len(values) == 13
    assert values == [1, 1, 1, 2, 3, 3, 3, "bob", 14, "bob2", None, None, "far"]
    values = row.get_values(cell_type="FLOAT", complete=True)
    assert len(values) == 13
    assert values == [1, 1, 1, 2, 3, 3, 3, None, None, None, None, None, None]
    values = row.get_values(cell_type="percentage", complete=True)
    assert len(values) == 13
    assert values == [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        14,
        None,
        None,
        None,
        None,
    ]
    values = row.get_values(cell_type="string", complete=True)
    assert len(values) == 13
    assert values == [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        "bob",
        None,
        "bob2",
        None,
        None,
        "far",
    ]


def test_get_values_cell_type_and_coord(row):
    values = row.get_values(coord=(0, 5), cell_type="all")
    assert len(values) == 6
    values = row.get_values(coord=(0, 5), cell_type="float")
    assert len(values) == 6
    values = row.get_values(coord=(0, 5), cell_type="percentage")
    assert len(values) == 0
    values = row.get_values(coord=(2, 5), cell_type="string")
    assert len(values) == 0


def test_get_values_cell_type_and_coord_strange(row):
    values = row.get_values(coord="A:F", cell_type="all")
    assert len(values) == 6
    values = row.get_values(coord="C:", cell_type="all")
    assert len(values) == 5
    values = row.get_values(coord="A : f", cell_type="float")
    assert len(values) == 6
    values = row.get_values(coord="A:F", cell_type="percentage")
    assert len(values) == 0
    values = row.get_values(coord="C:F", cell_type="string")
    assert len(values) == 0


def test_get_values_cell_type_and_coord_strange_long(row):
    values = row.get_values(coord="A8:F2", cell_type="all")
    assert len(values) == 6
    values = row.get_values(coord="C5:", cell_type="all")
    assert len(values) == 5
    values = row.get_values(coord="C5:99", cell_type="all")
    assert len(values) == 5
    values = row.get_values(coord="A2 : f", cell_type="float")
    assert len(values) == 6
    values = row.get_values(coord="A:F5", cell_type="percentage")
    assert len(values) == 0
    values = row.get_values(coord="C:F4", cell_type="string")
    assert len(values) == 0


def test_get_values_cell_type_and_coord_and_get_type(row):
    values = row.get_values(coord=(0, 5), cell_type="all", get_type=True)
    assert len(values) == 6
    assert values == [
        (1, "float"),
        (1, "float"),
        (1, "float"),
        (2, "float"),
        (3, "float"),
        (3, "float"),
    ]
    values = row.get_values(coord=(0, 5), cell_type="float", get_type=True)
    assert len(values) == 6
    assert values == [
        (1, "float"),
        (1, "float"),
        (1, "float"),
        (2, "float"),
        (3, "float"),
        (3, "float"),
    ]
    values = row.get_values(coord=(0, 5), cell_type="percentage", get_type=True)
    assert len(values) == 0
    values = row.get_values(coord=(2, 5), cell_type="string", get_type=True)
    assert len(values) == 0


def test_get_values_cell_type_and_coord_and_complete(row):
    values = row.get_values(coord=(0, 5), cell_type="all", complete=True)
    assert len(values) == 6
    assert values == [1, 1, 1, 2, 3, 3]
    values = row.get_values(coord=(0, 5), cell_type="float", complete=True)
    assert len(values) == 6
    assert values == [1, 1, 1, 2, 3, 3]
    values = row.get_values(coord=(0, 5), cell_type="percentage", complete=True)
    assert len(values) == 6
    assert values == [None, None, None, None, None, None]
    values = row.get_values(coord=(2, 5), cell_type="string", complete=True)
    assert len(values) == 4
    assert values == [None, None, None, None]


def test_get_values_cell_type_and_coord2_and_complete(row):
    row.append_cell(Cell(value="bob"), clone=False)
    row.append_cell(Cell(value=14, cell_type="percentage"))
    row.append_cell(Cell(value="bob2"), clone=False)
    row.set_cell(12, Cell(value="far"), clone=False)
    values = row.get_values(coord=(2, 20), cell_type="all", complete=True)
    assert len(values) == 11
    assert values == [1, 2, 3, 3, 3, "bob", 14, "bob2", None, None, "far"]
    values = row.get_values(coord=(2, 11), cell_type="all", complete=True)
    assert len(values) == 10
    assert values == [1, 2, 3, 3, 3, "bob", 14, "bob2", None, None]
    values = row.get_values(coord=(3, 12), cell_type="float", complete=True)
    assert len(values) == 10
    assert values == [2, 3, 3, 3, None, None, None, None, None, None]
    values = row.get_values(coord=(0, 5), cell_type="percentage", complete=True)
    assert len(values) == 6
    assert values == [None, None, None, None, None, None]
    values = row.get_values(coord=(0, 5), cell_type="string", complete=True)
    assert len(values) == 6
    assert values == [None, None, None, None, None, None]
    values = row.get_values(coord=(5, 11), cell_type="percentage", complete=True)
    assert len(values) == 7
    assert values == [None, None, None, 14, None, None, None]
    values = row.get_values(coord=(6, 12), cell_type="string", complete=True)
    assert len(values) == 7
    assert values == [None, "bob", None, "bob2", None, None, "far"]
    values = row.get_values(coord=(8, 20), cell_type="string", complete=True)
    assert len(values) == 5
    assert values == [None, "bob2", None, None, "far"]


def test_get_values_cell_type_and_coord2_and_complete_and_get_type(row):
    row.append_cell(Cell(value="bob"), clone=False)
    row.append_cell(Cell(value=14, cell_type="percentage"))
    row.append_cell(Cell(value="bob2"), clone=False)
    row.set_cell(12, Cell(value="far"), clone=False)
    values = row.get_values(
        coord=(2, 20), cell_type="all", complete=True, get_type=True
    )
    assert len(values) == 11
    assert values == [
        (1, "float"),
        (2, "float"),
        (3, "float"),
        (3, "float"),
        (3, "float"),
        ("bob", "string"),
        (14, "percentage"),
        ("bob2", "string"),
        (None, None),
        (None, None),
        ("far", "string"),
    ]
    values = row.get_values(
        coord=(2, 11), cell_type="all", complete=True, get_type=True
    )
    assert len(values) == 10
    assert values == [
        (1, "float"),
        (2, "float"),
        (3, "float"),
        (3, "float"),
        (3, "float"),
        ("bob", "string"),
        (14, "percentage"),
        ("bob2", "string"),
        (None, None),
        (None, None),
    ]
    values = row.get_values(
        coord=(3, 12), cell_type="float", complete=True, get_type=True
    )
    assert len(values) == 10
    assert values == [
        (2, "float"),
        (3, "float"),
        (3, "float"),
        (3, "float"),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
    ]
    values = row.get_values(
        coord=(0, 5), cell_type="percentage", complete=True, get_type=True
    )
    assert len(values) == 6
    assert values == [
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
    ]
    values = row.get_values(
        coord=(0, 5), cell_type="string", complete=True, get_type=True
    )
    assert len(values) == 6
    assert values == [
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
    ]
    values = row.get_values(
        coord=(5, 11), cell_type="percentage", complete=True, get_type=True
    )
    assert len(values) == 7
    assert values == [
        (None, None),
        (None, None),
        (None, None),
        (14, "percentage"),
        (None, None),
        (None, None),
        (None, None),
    ]
    values = row.get_values(
        coord=(6, 12), cell_type="string", complete=True, get_type=True
    )
    assert len(values) == 7
    assert values == [
        (None, None),
        ("bob", "string"),
        (None, None),
        ("bob2", "string"),
        (None, None),
        (None, None),
        ("far", "string"),
    ]
    values = row.get_values(
        coord=(8, 20), cell_type="string", complete=True, get_type=True
    )
    assert len(values) == 5
    assert values == [
        (None, None),
        ("bob2", "string"),
        (None, None),
        (None, None),
        ("far", "string"),
    ]


def test_get_cell_alpha(row):
    cell_5 = row.get_cell("F")
    assert cell_5.get_value() == 3
    assert cell_5.text_content == "3"
    assert cell_5.type == "float"
    assert cell_5.style == "ce5"
    assert cell_5.x == 5
    assert cell_5.y == 1


def test_get_cell_int(row):
    cell_5 = row.get_cell(5)
    assert cell_5.get_value() == 3
    assert cell_5.text_content == "3"
    assert cell_5.type == "float"
    assert cell_5.style == "ce5"


def test_get_cell_coord(row):
    cell = row.get_cell(-1)
    assert cell.get_value() == 3
    cell = row.get_cell(-3)
    assert cell.get_value() == 3
    cell = row.get_cell(-4)
    assert cell.get_value() == 2
    cell = row.get_cell(-5)
    assert cell.get_value() == 1
    cell = row.get_cell(-1 - 7)
    assert cell.get_value() == 3
    cell = row.get_cell(-3 - 56)
    assert cell.get_value() == 3
    cell = row.get_cell(-4 - 560)
    assert cell.get_value() == 2
    cell = row.get_cell(-5 - 7000)
    assert cell.get_value() == 1
    cell = row.get_cell(8)
    assert cell.get_value() is None
    cell = row.get_cell(1000)
    assert cell.get_value() is None


def test_get_cells_coord_none(row):
    cells = row.get_cells((100, 200))
    assert len(cells) == 0


def test_get_cell_coord_none(row):
    cell = row.get_cell(2000)
    assert cell


def test_get_value_coord(row):
    row.append_cell(Cell("Appended"))
    value = row.get_value(-1)
    assert value == "Appended"
    value = row.get_value(-3)
    assert value == 3
    value = row.get_value(-4)
    assert value == 3
    value = row.get_value(-5)
    assert value == 2
    value = row.get_value(-1 - 8)
    assert value == "Appended"
    value = row.get_value(7)
    assert value == "Appended"
    value = row.get_value(8)
    assert value is None
    value = row.get_value(1000)
    assert value is None


def test_get_value_coord_with_get_type(row):
    row.append_cell(Cell("Appended"))
    value = row.get_value(-1, get_type=True)
    assert value == ("Appended", "string")
    value = row.get_value(-3, get_type=True)
    assert value == (3, "float")
    value = row.get_value(-4, get_type=True)
    assert value == (3, "float")
    value = row.get_value(-5, get_type=True)
    assert value == (2, "float")
    value = row.get_value(-1 - 8, get_type=True)
    assert value == ("Appended", "string")
    value = row.get_value(7, get_type=True)
    assert value == ("Appended", "string")
    value = row.get_value(8, get_type=True)
    assert value == (None, None)
    value = row.get_value(1000, get_type=True)
    assert value == (None, None)
