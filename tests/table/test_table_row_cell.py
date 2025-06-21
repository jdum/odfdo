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
from decimal import Decimal as dec

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


def test_traverse(row):
    assert len(list(row.traverse())) == 7


def test_traverse_coord(row):
    assert len(list(row.traverse(2, None))) == 5
    assert len(list(row.traverse(2, 4))) == 3
    assert len(list(row.traverse(0, 3))) == 4
    assert len(list(row.traverse(0, 55))) == 7
    assert len(list(row.traverse(100, 55))) == 0
    assert len(list(row.traverse(100, None))) == 0
    assert len(list(row.traverse(None, 1))) == 2
    assert len(list(row.traverse(-5, 1))) == 2
    assert len(list(row.traverse(2, -1))) == 0
    assert len(list(row.traverse(-5, -1))) == 0


def test_get_cells(row):
    assert len(list(row.get_cells())) == 7


def test_get_cells_property(row):
    assert len(row.cells) == 7


def test_get_cells_on_emty_row():
    row = Row()
    assert len(row.get_cells()) == 0
    assert len(row.cells) == 0
    assert len(row.get_cells((1, 2))) == 0
    assert len(row.get_cells((-2, -3))) == 0
    assert len(row.get_cells((0, 10))) == 0


def test_get_cells_coord(row):
    coord = (0, 8)
    assert len(row.get_cells(coord)) == 7
    coord = "a1:c2"
    assert len(row.get_cells(coord)) == 3
    coord = "a1:a2"
    assert len(row.get_cells(coord)) == 1
    coord = "a1:EE2"
    assert len(row.get_cells(coord)) == 7
    coord = "D1"
    assert len(row.get_cells(coord)) == 0
    coord = "c5:a1"
    assert len(row.get_cells(coord)) == 0
    coord = (5, 6)
    assert len(row.get_cells(coord)) == 2
    coord = (-5, 6)
    assert len(row.get_cells(coord)) == 5
    coord = (0, -1)
    assert len(row.get_cells(coord)) == 7
    coord = (0, -2)
    assert len(row.get_cells(coord)) == 6
    coord = (-1, -1)
    assert len(row.get_cells(coord)) == 1
    coord = (1, 0)
    assert len(row.get_cells(coord)) == 0


def test_get_cells_regex(row):
    coordinates = [cell.x for cell in row.get_cells(content=r"3")]
    expected = [4, 5, 6]
    assert coordinates == expected


def test_get_cells_style(row):
    coordinates = [cell.x for cell in row.get_cells(style=r"ce5")]
    expected = [1, 5]
    assert coordinates == expected


def test_get_cells_cell_type(row):
    cells = row.get_cells(cell_type="all")
    assert len(cells) == 7
    cells = row.get_cells(cell_type="float")
    assert len(cells) == 7
    cells = row.get_cells(cell_type="percentage")
    assert len(cells) == 0
    cells = row.get_cells(cell_type="string")
    assert len(cells) == 0


def test_get_cells_cell_type2(row):
    row.append_cell(Cell(value="bob"), clone=False)
    row.append_cell(Cell(value=14, cell_type="percentage"))
    row.append_cell(Cell(value="bob2"), clone=False)
    cells = row.get_cells(cell_type="all")
    assert len(cells) == 7 + 3
    cells = row.get_cells(cell_type="float")
    assert len(cells) == 7
    cells = row.get_cells(cell_type="percentage")
    assert len(cells) == 1
    cells = row.get_cells(cell_type="string")
    assert len(cells) == 2


def test_get_cells_cell_type_and_coord(row):
    cells = row.get_cells(coord=(0, 5), cell_type="all")
    assert len(cells) == 6
    cells = row.get_cells(coord=(0, 5), cell_type="float")
    assert len(cells) == 6
    cells = row.get_cells(coord=(0, 5), cell_type="percentage")
    assert len(cells) == 0
    cells = row.get_cells(coord=(2, 5), cell_type="string")
    assert len(cells) == 0


def test_get_cells_cell_type_and_coord2(row):
    row.append_cell(Cell(value="bob"), clone=False)
    row.append_cell(Cell(value=14, cell_type="percentage"))
    row.append_cell(Cell(value="bob2"), clone=False)
    cells = row.get_cells(coord=(2, 9), cell_type="all")
    assert len(cells) == 8
    cells = row.get_cells(coord=(3, 9), cell_type="float")
    assert len(cells) == 4
    cells = row.get_cells(coord=(0, 5), cell_type="percentage")
    assert len(cells) == 0
    cells = row.get_cells(coord=(0, 5), cell_type="string")
    assert len(cells) == 0
    cells = row.get_cells(coord=(5, 9), cell_type="percentage")
    assert len(cells) == 1
    cells = row.get_cells(coord=(5, 9), cell_type="string")
    assert len(cells) == 2
    cells = row.get_cells(coord=(8, 9), cell_type="string")
    assert len(cells) == 1


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


def test_get_cell_int_repr(row):
    cell_5 = row.get_cell(5)
    assert repr(cell_5) == "<Cell x=5 y=1>"


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


def test_set_cell(row):
    row.set_value(1, 3.14)
    assert row.get_values() == [1, dec("3.14"), 1, 2, 3, 3, 3]
    # Test repetitions are synchronized
    assert row.width == 7


def test_set_cell_far_away(row):
    row.set_value(7 + 3, 3.14)
    assert row.get_values() == [1, 1, 1, 2, 3, 3, 3, None, None, None, dec("3.14")]
    # Test repetitions are synchronized
    assert row.width == 11


def test_set_cell_repeat(row_repeats):
    row = row_repeats
    row.set_value(1, 3.14)
    assert row.get_values() == [1, dec("3.14"), 1, 2, 3, 3, 3]
    # Test repetitions are synchronized
    assert row.width == 7


def test_set_cell_repeat_repeat(row_repeats):
    row = row_repeats
    cell = Cell(value=20, repeated=2)
    row.set_cell(1, cell)
    assert row.get_values() == [1, 20, 20, 2, 3, 3, 3]
    # Test repetitions are synchronized
    assert row.width == 7


def test_set_cell_none(row_repeats):
    row = row_repeats
    row.set_cell(1, None)
    assert row.get_values() == [1, None, 1, 2, 3, 3, 3]
    # Test repetitions are synchronized
    assert row.width == 7


def test_insert(row):
    cell = row.insert_cell(3)
    assert type(cell) is Cell
    assert cell.x == 3
    assert cell.y == 1


def test_insert_cell(row):
    cell = row.insert_cell(3, Cell("Inserted"))
    assert row.width == 8
    assert row.get_values() == [1, 1, 1, "Inserted", 2, 3, 3, 3]
    # Test repetitions are synchronized
    assert row.width == 8
    assert cell.x == 3
    assert cell.y == 1


def test_insert_cell_repeat(row_repeats):
    row = row_repeats
    cell = row.insert_cell(6, Cell("Inserted"))
    assert row.get_values() == [1, 1, 1, 2, 3, 3, "Inserted", 3]
    # Test repetitions are synchronized
    assert row.width == 8
    assert cell.x == 6
    assert cell.y == 0


def test_insert_cell_width(row_repeats):
    row = row_repeats
    assert row.width == 7
    cell = row.insert_cell(7, Cell("Inserted"))
    assert row.get_values() == [1, 1, 1, 2, 3, 3, 3, "Inserted"]
    # Test repetitions are synchronized
    assert row.width == 8
    assert cell.x == 7
    assert cell.y == 0


def test_insert_cell_repeat_repeat(row_repeats):
    row = row_repeats
    cell = row.insert_cell(6, Cell("Inserted", repeated=3))
    assert row.get_values() == [
        1,
        1,
        1,
        2,
        3,
        3,
        "Inserted",
        "Inserted",
        "Inserted",
        3,
    ]
    # Test repetitions are synchronized
    assert row.width == 10
    assert cell.x == 6
    assert cell.y == 0


def test_insert_cell_repeat_repeat_bis(row_repeats):
    row = row_repeats
    cell = row.insert_cell(1, Cell("Inserted", repeated=2))
    assert row.get_values() == [1, "Inserted", "Inserted", 1, 1, 2, 3, 3, 3]
    # Test repetitions are synchronized
    assert row.width == 9
    assert cell.x == 1
    assert cell.y == 0


def test_extend_cells(row_repeats):
    row = row_repeats
    row.extend_cells()
    assert row.width == 7


def test_append_cell(row):
    orig_row = row.clone
    cell = row.append_cell()
    assert isinstance(cell, Cell)
    assert cell.x == orig_row.width
    assert cell.y == 1


def test_append_cell2(row):
    orig_row = row.clone
    cell = row.append_cell(Cell("Appended"))
    assert row.get_values() == [1, 1, 1, 2, 3, 3, 3, "Appended"]
    # Test repetitions are synchronized
    assert row.width == 8
    assert cell.x == orig_row.width
    assert cell.y == 1


def test_delete_cell(row):
    row.delete_cell(3)
    assert row.get_values() == [1, 1, 1, 3, 3, 3]
    # Test repetitions are synchronized
    assert row.width == 6


def test_delete_cell_width(row):
    row.delete_cell(7)
    assert row.get_values() == [1, 1, 1, 2, 3, 3, 3]
    assert row.width == 7


def test_delete_cell_width_2(row):
    row.delete_cell(8)
    assert row.get_values() == [1, 1, 1, 2, 3, 3, 3]
    assert row.width == 7


def test_delete_cell_repeat(row_repeats):
    row = row_repeats
    row.delete_cell(-1)
    assert row.get_values() == [1, 1, 1, 2, 3, 3]
    # Test repetitions are synchronized
    assert row.width == 6


def test_set_cells_1(row):
    cells = [Cell(value=10)]
    row.set_cells(cells)
    assert row.get_values() == [10, 1, 1, 2, 3, 3, 3]
    # Test repetitions are synchronized
    assert row.width == 7


def test_set_cells_1_start_none(row):
    cells = [Cell(value=10)]
    row.set_cells(cells, start=None)
    assert row.get_values() == [10, 1, 1, 2, 3, 3, 3]
    assert row.width == 7


def test_set_cells_none(row):
    cells = None
    row.set_cells(cells)
    assert row.get_values() == [1, 1, 1, 2, 3, 3, 3]
    assert row.width == 7


def test_set_cells_2(row):
    cells = [Cell(value=10), Cell(value=20)]
    row.set_cells(cells)
    assert row.get_values() == [10, 20, 1, 2, 3, 3, 3]
    # Test repetitions are synchronized
    assert row.width == 7


def test_set_cells_3(row):
    cells = [Cell(value=10), None, Cell(value=20)]
    row.set_cells(cells)
    assert row.get_values() == [10, None, 20, 2, 3, 3, 3]
    assert row.width == 7


def test_set_cells_many(row):
    cells = []
    for i in range(10):
        cells.append(Cell(value=10 * i))
    row.set_cells(cells)
    assert row.get_values() == [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
    # Test repetitions are synchronized
    assert row.width == 10


def test_set_cells_1_start_1(row):
    cells = [Cell(value=10)]
    row.set_cells(cells, 1)
    assert row.get_values() == [1, 10, 1, 2, 3, 3, 3]
    # Test repetitions are synchronized
    assert row.width == 7


def test_set_cells_1_start_m_2(row):
    cells = [Cell(value=10)]
    row.set_cells(cells, -2)
    assert row.get_values() == [1, 1, 1, 2, 3, 10, 3]
    # Test repetitions are synchronized
    assert row.width == 7


def test_set_cells_1_start_m_6(row):
    cells = [Cell(value=10)]
    row.set_cells(cells, 6)
    assert row.get_values() == [1, 1, 1, 2, 3, 3, 10]
    # Test repetitions are synchronized
    assert row.width == 7


def test_set_cells_1_start_m_9(row):
    cells = [Cell(value=10)]
    row.set_cells(cells, 9)
    assert row.get_values() == [1, 1, 1, 2, 3, 3, 3, None, None, 10]
    # Test repetitions are synchronized
    assert row.width == 10


def test_set_cells_2_start_1(row):
    cells = [Cell(value=10), Cell(value=20)]
    row.set_cells(cells, 1)
    assert row.get_values() == [1, 10, 20, 2, 3, 3, 3]
    # Test repetitions are synchronized
    assert row.width == 7


def test_set_cells_many_start_5(row):
    cells = []
    for i in range(5):
        cells.append(Cell(value=10 * i))
    row.set_cells(cells, 5)
    assert row.get_values() == [1, 1, 1, 2, 3, 0, 10, 20, 30, 40]
    # Test repetitions are synchronized
    assert row.width == 10


def test_set_cells_many_start_far(row):
    cells = []
    for i in range(5):
        cells.append(Cell(value=10 * i))
    row.set_cells(cells, 9)
    assert row.get_values() == [1, 1, 1, 2, 3, 3, 3, None, None, 0, 10, 20, 30, 40]
    # Test repetitions are synchronized
    assert row.width == 14


def test_set_cells_3_start_1_repeats(row):
    cells = [Cell(value=10, repeated=2)]
    row.set_cells(cells, 1)
    assert row.get_values() == [1, 10, 10, 2, 3, 3, 3]
    # Test repetitions are synchronized
    assert row.width == 7


def test_set_cells_3_start_1_repeats_2(row):
    cells = [Cell(value=10, repeated=2), Cell(value=20)]
    row.set_cells(cells, 1)
    assert row.get_values() == [1, 10, 10, 20, 3, 3, 3]
    # Test repetitions are synchronized
    assert row.width == 7


def test_set_cells_3_start_1_repeats_3(row):
    cells = [Cell(value=10, repeated=2), Cell(value=20), Cell(value=30, repeated=2)]
    row.set_cells(cells, 1)
    assert row.get_values() == [1, 10, 10, 20, 30, 30, 3]
    # Test repetitions are synchronized
    assert row.width == 7


def test_set_cells_3_start_1_repeats_4(row):
    cells = [Cell(value=10, repeated=2), Cell(value=20), Cell(value=30, repeated=4)]
    row.set_cells(cells, 1)
    assert row.get_values() == [1, 10, 10, 20, 30, 30, 30, 30]
    # Test repetitions are synchronized
    assert row.width == 8


def test_set_values_empty():
    row = Row()
    row.set_values([1, 2, 3, 4])
    assert row.width == 4
    assert row.get_values() == [1, 2, 3, 4]


def test_set_values_empty_start_none():
    row = Row()
    row.set_values([1, 2, 3, 4], start=None)
    assert row.width == 4
    assert row.get_values() == [1, 2, 3, 4]


def test_set_values_on_row(row):
    row.set_values([10, 20, 30, "4"])
    assert row.width == 7
    assert row.get_values() == [10, 20, 30, "4", 3, 3, 3]


def test_set_values_on_row2(row):
    row.set_values([10, 20, 30, "4"], start=2)
    assert row.width == 7
    assert row.get_values() == [1, 1, 10, 20, 30, "4", 3]


def test_set_values_on_row3(row):
    row.set_values([10, 20, 30, "4"], start=2)
    assert row.width == 7
    assert row.get_values() == [1, 1, 10, 20, 30, "4", 3]


def test_set_values_on_row4(row):
    row.set_values([10, 20, 30, "4"], start=-2)
    assert row.width == 9
    assert row.get_values() == [1, 1, 1, 2, 3, 10, 20, 30, "4"]


def test_set_values_on_row5(row):
    row.set_values([10, 20, 30, "4"], start=8)
    assert row.width == 7 + 1 + 4
    assert row.get_values() == [1, 1, 1, 2, 3, 3, 3, None, 10, 20, 30, "4"]


def test_set_values_on_row6(row):
    row.set_values([10, 20, 30, 40, 50, 60, 70, 80], start=0)
    assert row.width == 8
    assert row.get_values() == [10, 20, 30, 40, 50, 60, 70, 80]


def test_set_values_on_row_percentage(row):
    row.set_values([10, 20], start=4, cell_type="percentage")
    assert row.width == 7
    assert row.get_values() == [1, 1, 1, 2, 10, 20, 3]
    assert row.get_values(get_type=True, cell_type="percentage") == [
        (10, "percentage"),
        (20, "percentage"),
    ]


def test_set_values_on_row_style(row):
    row.set_values([10, 20], start=3, style="bold")
    assert row.width == 7
    assert row.get_values() == [1, 1, 1, 10, 20, 3, 3]
    assert row.get_cell(4).style == "bold"


def test_set_values_on_row_curency(row):
    row.set_values([10, 20], start=3, cell_type="currency", currency="EUR")
    assert row.width == 7
    assert row.get_values() == [1, 1, 1, 10, 20, 3, 3]
    assert row.get_cell(4).get_value(get_type=True) == (20, "currency")
    assert row.get_cell(4).currency == "EUR"
