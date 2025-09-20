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


def test_get_cell_alpha(table):
    cell = table.get_cell("D3")
    assert cell.get_value() == 2
    assert cell.text_content == "2"
    assert cell.type == "float"
    assert cell.style == "ce5"
    assert cell.x == 3
    assert cell.y == 2


def test_get_cell_tuple(table):
    cell = table.get_cell((3, 2))
    assert cell.get_value() == 2
    assert cell.text_content == "2"
    assert cell.type == "float"
    assert cell.style == "ce5"
    assert cell.x == 3
    assert cell.y == 2


def test_set_cell_value(table):
    table.set_value("D3", "Changed")
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, "Changed", 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]


def test_get_cell_list(table):
    assert len(list(table.get_cells(flat=True))) == 28


def test_get_cell_list_regex(table):
    coordinates = [
        (cell.x, cell.y) for cell in table.get_cells(content=r"3", flat=True)
    ]
    expected = [
        (4, 0),
        (5, 0),
        (6, 0),
        (4, 1),
        (5, 1),
        (6, 1),
        (4, 2),
        (5, 2),
        (6, 2),
        (2, 3),
    ]
    assert coordinates == expected


def test_get_cell_list_style(table):
    coordinates = [
        (cell.x, cell.y) for cell in table.get_cells(style=r"ce5", flat=True)
    ]
    expected = [(1, 1), (5, 1), (3, 2)]
    assert coordinates == expected


def test_insert(table):
    cell = table.insert_cell("B3")
    assert type(cell) is Cell
    assert cell.x == 1
    assert cell.y == 2


def test_insert_cell(table):
    cell = table.insert_cell("B3", Cell("Inserted"))
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3, None],
        [1, 1, 1, 2, 3, 3, 3, None],
        [1, "Inserted", 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7, None],
    ]
    # Test columns are synchronized
    assert table.width == 8
    assert cell.x == 1
    assert cell.y == 2


def test_append(table):
    cell = table.append_cell(1)
    assert type(cell) is Cell
    assert cell.x == table.width - 1


def test_append_cell(table):
    cell = table.append_cell(1, Cell("Appended"))
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3, None],
        [1, 1, 1, 2, 3, 3, 3, "Appended"],
        [1, 1, 1, 2, 3, 3, 3, None],
        [1, 2, 3, 4, 5, 6, 7, None],
    ]
    # Test columns are synchronized
    assert table.width == 8
    assert cell.x == table.width - 1


def test_delete_cell(table):
    table.delete_cell("F3")
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, None],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    # Test columns are synchronized
    assert table.width == 7
