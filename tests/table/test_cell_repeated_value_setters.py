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
from odfdo.cell import Cell
from odfdo.row import Row
from odfdo.table import Table


def test_table_set_value_on_repeated_cell():
    table = Table("Test")
    row = Row()
    row.append_cell(Cell("initial", repeated=5))
    table.append_row(row)

    assert table.values == [["initial", "initial", "initial", "initial", "initial"]]

    table.set_value((2, 0), "modified_at_2")

    assert table.values == [
        ["initial", "initial", "modified_at_2", "initial", "initial"]
    ]


def test_table_set_value_on_repeated_cell_edges():
    table = Table("Test")
    row = Row()
    row.append_cell(Cell("initial", repeated=5))
    table.append_row(row)

    table.set_value((0, 0), "first")
    table.set_value((4, 0), "last")

    assert table.values == [["first", "initial", "initial", "initial", "last"]]


def test_row_set_value_on_repeated_cell():
    row = Row()
    row.append_cell(Cell("initial", repeated=5))

    assert row.values == ["initial", "initial", "initial", "initial", "initial"]

    row.set_value(1, "modified_at_1")

    assert row.values == ["initial", "modified_at_1", "initial", "initial", "initial"]


def test_table_values_setter_on_repeated_cells():
    table = Table("Test")
    row = Row()
    row.append_cell(Cell("initial", repeated=5))
    table.append_row(row)

    matrix = table.values
    matrix[0][3] = "modified_at_3"
    table.values = matrix

    assert table.values == [
        ["initial", "initial", "initial", "modified_at_3", "initial"]
    ]


def test_row_values_setter_on_repeated_cells():
    row = Row()
    row.append_cell(Cell("initial", repeated=5))

    vals = row.values
    vals[2] = "modified_at_2"
    row.values = vals

    assert row.values == ["initial", "initial", "modified_at_2", "initial", "initial"]


def test_direct_cell_mutation_affects_all_repeated_instances():
    table = Table("Test")
    row = Row()
    row.append_cell(Cell("initial", repeated=5))
    table.append_row(row)

    cell_node = table.get_cell((0, 0), clone=False)
    assert cell_node.repeated == 5

    cell_node.value = "shared_mutation"

    # Direct mutation on a clone=False repeated cell alters the shared XML node,
    # so all 5 repeated instances reflect the new value.
    assert table.values == [
        [
            "shared_mutation",
            "shared_mutation",
            "shared_mutation",
            "shared_mutation",
            "shared_mutation",
        ]
    ]


def test_direct_cell_property_setters_affect_all_repeated_instances():
    table = Table("Test")
    row = Row()
    row.append_cell(Cell(100, repeated=4))
    table.append_row(row)

    cell_node = table.get_cell((0, 0), clone=False)
    assert cell_node.repeated == 4

    cell_node.int = 42
    assert table.values == [[42, 42, 42, 42]]

    cell_node.string = "hello"
    assert table.values == [["hello", "hello", "hello", "hello"]]

    cell_node.bool = True
    assert table.values == [[True, True, True, True]]
