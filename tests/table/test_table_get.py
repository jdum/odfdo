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
from odfdo.table import Cell, Table


@pytest.fixture
def table(samples) -> Iterable[Table]:
    # simpletable :
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1   2	3	4	5	6	7
    document = Document(samples("simple_table.ods"))
    yield document.body.get_table(name="Example1")


def test_on_empty_table():
    table = Table("Table")
    assert table.get_values() == []
    assert table.get_values(complete=True) == []
    assert table.get_values(complete=True, get_type=True) == []
    assert table.get_values((0, 10)) == []
    assert table.get_values(cell_type="all") == []
    assert table.get_values(cell_type="All") == []
    assert table.get_values((2, 3), complete=True) == []


def test_get_values_count(table):
    assert len(table.get_values()) == 4  # 4 rows
    assert len(table.get_values(cell_type="All", complete=False)) == 4  # same
    assert len(table.get_values(cell_type="All", complete=True)) == 4  # 4 lines result
    assert len(table.get_values(cell_type="All", flat=True)) == 28  # flat
    assert len(table.get_values(flat=True)) == 28  # flat


def test_get_values_coord_1(table):
    result = [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    assert table.get_values() == result
    assert table.get_values((0, 0, 6, 3)) == result
    assert table.get_values((0, 3)) == result
    assert table.get_values((0, None, 6, None)) == result
    assert table.get_values((None, None, 6, 20)) == result
    assert table.get_values((0, 0, None, None)) == result
    assert table.get_values((None, 0, 10, None)) == result
    assert table.get_values("") == result
    assert table.get_values(":") == result
    assert table.get_values("A1:G4") == result
    assert table.get_values("A1:") == result
    assert table.get_values("1:4") == result
    assert table.get_values("1:4") == result
    assert table.get_values("1:") == result
    assert table.get_values("1:10") == result
    assert table.get_values(":10") == result
    assert table.get_values("A:") == result
    assert table.get_values(":G") == result
    assert table.get_values("1:H") == result


def test_get_values_coord_2(table):
    result = [[1, 1, 1, 2, 3, 3, 3], [1, 2, 3, 4, 5, 6, 7]]
    assert table.get_values((0, 2, 7, 3)) == result
    assert table.get_values((2, 3)) == result
    assert table.get_values((0, 2, 6, None)) == result
    assert table.get_values((None, 2, None, 20)) == result
    assert table.get_values((None, 2, None, None)) == result
    assert table.get_values((None, 2, 10, None)) == result
    assert table.get_values("A3:G4") == result
    assert table.get_values("A3:") == result
    assert table.get_values("3:4") == result
    assert table.get_values("3:") == result
    assert table.get_values("3:10") == result
    assert table.get_values("A3:") == result
    assert table.get_values("3:G") == result
    assert table.get_values("3:H") == result


def test_get_values_coord_3(table):
    result = [[1, 1], [1, 1]]
    assert table.get_values((0, 0, 1, 1)) == result
    assert table.get_values((None, 0, 1, 1)) == result
    assert table.get_values((None, None, 1, 1)) == result
    assert table.get_values("A1:B2") == result
    assert table.get_values(":B2") == result


def test_get_values_coord_4(table):
    result = [[3, 3], [6, 7]]
    assert table.get_values("F3:G4") == result
    assert table.get_values("F3:") == result
    assert table.get_values("F3:RR555") == result


def test_get_values_coord_5(table):
    result = [[2, 3], [2, 3], [2, 3], [4, 5]]
    assert table.get_values("D1:E4") == result
    assert table.get_values("D:E") == result
    assert table.get_values("D1:E555") == result


def test_get_values_coord_5_flat(table):
    result = [2, 3, 2, 3, 2, 3, 4, 5]
    assert table.get_values("D1:E4", flat=True) == result


def test_get_values_coord_6(table):
    result = [[5]]
    assert table.get_values("E4") == result
    assert table.get_values("E4:E4") == result


def test_get_values_coord_6_flat(table):
    result = [5]
    assert table.get_values("E4", flat=True) == result


def test_get_values_coord_7(table):
    result = []
    assert table.get_values("E5") == result
    assert table.get_values("B3:A1") == result


def test_get_values_cell_type(table):
    result = [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    values = table.get_values(cell_type="all")
    assert values == result
    values = table.get_values(cell_type="float")
    assert values == result


def test_get_values_cell_type_no_comp(table):
    result = [
        1,
        1,
        1,
        2,
        3,
        3,
        3,
        1,
        1,
        1,
        2,
        3,
        3,
        3,
        1,
        1,
        1,
        2,
        3,
        3,
        3,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
    ]
    values = table.get_values(cell_type="all", complete=True, flat=True)
    assert values == result
    values = table.get_values(cell_type="float", complete=False, flat=True)
    assert values == result


def test_get_values_cell_type_1(table):
    result = [
        [None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None],
    ]
    values = table.get_values(cell_type="percentage")
    assert values == result


def test_get_values_cell_type_1_flat(table):
    result = [
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
        None,
        None,
        None,
        None,
    ]
    values = table.get_values(cell_type="percentage", flat=True)
    assert values == result


def test_get_values_cell_type_1_no_comp_flat(table):
    result = []
    values = table.get_values(cell_type="percentage", complete=False, flat=True)
    assert values == result


def test_get_values_cell_type_1_no_comp(table):
    result = [[], [], [], []]
    values = table.get_values(cell_type="percentage", complete=False)
    assert values == result


def test_get_values_cell_type2_with_hole(table):
    row = table.get_row(1)
    row.append_cell(Cell(value="bob"), clone=False)
    row.append_cell(Cell(value=14, cell_type="percentage"))
    row.append_cell(Cell(value="bob2"), clone=False)
    row.set_cell(12, Cell(value="far"), clone=False)
    table.append_row(row)
    result = [
        [1, 1, 1, 2, 3, 3, 3, None, None, None, None, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None, None, None, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None, None, None, None, None],
        [1, 2, 3, 4, 5, 6, 7, None, None, None, None, None, None],
        [1, 1, 1, 2, 3, 3, 3, "bob", 14, "bob2", None, None, "far"],
    ]
    assert table.get_values() == result
    assert table.get_values("A4:z4") == [result[3]]
    assert table.get_values("5:5") == [result[4]]


def test_get_values_cell_type2_with_hole_no_comp(table):
    row = table.get_row(1)
    row.append_cell(Cell(value="bob"), clone=False)
    row.append_cell(Cell(value=14, cell_type="percentage"))
    row.append_cell(Cell(value="bob2"), clone=False)
    row.set_cell(12, Cell(value="far"), clone=False)
    table.append_row(row)
    result = [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
        [1, 1, 1, 2, 3, 3, 3, "bob", 14, "bob2", None, None, "far"],
    ]
    assert table.get_values(complete=False) == result
    assert table.get_values("A4:z4", complete=False) == [result[3]]
    assert table.get_values("5:5", complete=False) == [result[4]]


def test_get_values_cell_type2_with_hole_no_comp_flat(table):
    row = table.get_row(1)
    row.append_cell(Cell(value="bob"), clone=False)
    row.append_cell(Cell(value=14, cell_type="percentage"))
    row.append_cell(Cell(value="bob2"), clone=False)
    row.set_cell(12, Cell(value="far"), clone=False)
    table.append_row(row)
    result = [
        1,
        1,
        1,
        2,
        3,
        3,
        3,
        1,
        1,
        1,
        2,
        3,
        3,
        3,
        1,
        1,
        1,
        2,
        3,
        3,
        3,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        1,
        1,
        1,
        2,
        3,
        3,
        3,
        "bob",
        14,
        "bob2",
        None,
        None,
        "far",
    ]
    result2 = [1, 2, 3, 4, 5, 6, 7]
    result3 = [1, 1, 1, 2, 3, 3, 3, "bob", 14, "bob2", None, None, "far"]
    assert (
        table.get_values(
            complete=False,
            flat=True,
        )
        == result
    )
    assert table.get_values("A4:z4", flat=True, complete=False) == result2
    assert table.get_values("5:5", flat=True, complete=False) == result3


def test_get_values_cell_type2_with_hole_get_type(table):
    row = table.get_row(1)
    row.append_cell(Cell(value="bob"), clone=False)
    row.append_cell(Cell(value=14, cell_type="percentage"))
    row.append_cell(Cell(value="bob2"), clone=False)
    row.set_cell(12, Cell(value="far"), clone=False)
    table.append_row(row)
    # result1 = [[1, 1, 1, 2, 3, 3, 3, None, None, None, None, None, None]]
    result2 = [
        [
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
    ]

    assert table.get_values("5:5", cell_type="string") == result2

    assert table.get_values("5:5", cell_type="string", complete=False, flat=True) == [
        "bob",
        "bob2",
        "far",
    ]

    assert table.get_values(
        "5:5", cell_type="string", complete=False, flat=True, get_type=True
    ) == [("bob", "string"), ("bob2", "string"), ("far", "string")]

    assert table.get_values(coord="4:5", cell_type="All", get_type=True) == [
        [
            (1, "float"),
            (2, "float"),
            (3, "float"),
            (4, "float"),
            (5, "float"),
            (6, "float"),
            (7, "float"),
            (None, None),
            (None, None),
            (None, None),
            (None, None),
            (None, None),
            (None, None),
        ],
        [
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
        ],
    ]

    assert table.get_values(
        coord="4:5", cell_type="All", get_type=True, complete=False
    ) == [
        [
            (1, "float"),
            (2, "float"),
            (3, "float"),
            (4, "float"),
            (5, "float"),
            (6, "float"),
            (7, "float"),
        ],
        [
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
        ],
    ]

    assert table.get_values(coord="4:5", cell_type="string", get_type=True) == [
        [
            (None, None),
            (None, None),
            (None, None),
            (None, None),
            (None, None),
            (None, None),
            (None, None),
            (None, None),
            (None, None),
            (None, None),
            (None, None),
            (None, None),
            (None, None),
        ],
        [
            (None, None),
            (None, None),
            (None, None),
            (None, None),
            (None, None),
            (None, None),
            (None, None),
            ("bob", "string"),
            (None, None),
            ("bob2", "string"),
            (None, None),
            (None, None),
            ("far", "string"),
        ],
    ]

    assert table.get_values(
        coord="4:5", cell_type="string", get_type=True, complete=False
    ) == [[], [("bob", "string"), ("bob2", "string"), ("far", "string")]]

    assert table.get_values(
        coord="4:J5", cell_type="string", get_type=True, complete=False
    ) == [
        [],
        [
            ("bob", "string"),
            ("bob2", "string"),
        ],
    ]
