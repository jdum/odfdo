# Copyright 2018-2025 Jérôme Dumonteil
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
from __future__ import annotations

import datetime
from collections.abc import Iterable, Iterator
from typing import cast

import pytest

from odfdo.cell import Cell
from odfdo.column import Column
from odfdo.document import Document
from odfdo.element import Element
from odfdo.header import Header
from odfdo.row import Row
from odfdo.table import Table, _get_python_value

# @pytest.fixture
# def body(samples) -> Iterable[Element]:
#     document = Document(samples("simple_table.ods"))
#     yield document.body


@pytest.fixture
def table(samples) -> Iterable[Table]:
    # simpletable :
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1   2	3	4	5	6	7
    document = Document(samples("simple_table.ods"))
    yield cast(Table, document.body.get_table(name="Example1"))


def test_get_python_value_bytes():
    src = "éù".encode()
    assert isinstance(src, bytes)
    expected = "éù"
    assert _get_python_value(src, "utf8") == expected


def test_get_python_value_int():
    assert _get_python_value("42", "utf8") == 42


def test_get_python_value_int_2():
    assert _get_python_value(42, "utf8") == 42


def test_get_python_value_float():
    assert _get_python_value("42.123", "utf8") == 42.123


def test_get_python_value_float_2():
    assert _get_python_value(42.123, "utf8") == 42.123


def test_get_python_value_bool_true():
    assert _get_python_value(True, "utf8") is True


def test_get_python_value_bool_true_2():
    assert _get_python_value("true", "utf8") is True


def test_get_python_value_bool_true_3():
    assert _get_python_value("True", "utf8") is True


def test_get_python_value_bool_false():
    assert _get_python_value(False, "utf8") is False


def test_get_python_value_bool_false_2():
    assert _get_python_value("false", "utf8") is False


def test_get_python_value_bool_false_3():
    assert _get_python_value("False", "utf8") is False


def test_get_python_value_date():
    value = "2025-01-02"
    expected = datetime.datetime(2025, 1, 2, 0, 0)
    result = _get_python_value(value, "utf8")
    assert result == expected


def test_get_python_value_datetime():
    value = "2025-01-02 12:24:36"
    expected = datetime.datetime(2025, 1, 2, 12, 24, 36)
    result = _get_python_value(value, "utf8")
    assert result == expected


def test_get_python_value_duration():
    value = "PT12H24M36S"
    expected = datetime.timedelta(hours=12, minutes=24, seconds=36)
    result = _get_python_value(value, "utf8")
    assert result == expected


def test_table_protection_key():
    table = Table("name", protected=True, protection_key="hash")
    assert table.protected
    assert table.protection_key == "hash"


def test_table_protection_key_raise():
    with pytest.raises(ValueError):
        Table("name", protected=True)


def test_table_translate_table_coordinates_list_1(table):
    result = table._translate_table_coordinates_list([4])
    assert result == (None, 4, None, 4)


def test_table_translate_table_coordinates_list_2(table):
    result = table._translate_table_coordinates_list([-2])
    assert result == (None, 2, None, 2)


def test_table_translate_table_coordinates_list_3(table):
    result = table._translate_table_coordinates_list([1, 2])
    assert result == (None, 1, None, 2)


def test_table_translate_table_coordinates_list_4(table):
    result = table._translate_table_coordinates_list([-2, 2])
    assert result == (None, 2, None, 2)


def test_table_translate_table_coordinates_list_5(table):
    result = table._translate_table_coordinates_list([-1, 2])
    assert result == (None, 3, None, 2)


def test_table_translate_table_coordinates_list_6(table):
    result = table._translate_table_coordinates_list([-2, -1])
    assert result == (None, 2, None, 3)


def test_table_translate_table_coordinates_list_7(table):
    result = table._translate_table_coordinates_list([1, 1, 1, 1])
    assert result == (1, 1, 1, 1)


def test_table_translate_table_coordinates_list_8(table):
    result = table._translate_table_coordinates_list([-1, 1, 1, 1])
    assert result == (6, 1, 1, 1)


def test_table_translate_table_coordinates_list_9(table):
    result = table._translate_table_coordinates_list([1, -1, 1, 1])
    assert result == (1, 3, 1, 1)


def test_table_translate_table_coordinates_list_10(table):
    result = table._translate_table_coordinates_list([1, 1, -1, 1])
    assert result == (1, 1, 6, 1)


def test_table_translate_table_coordinates_list_11(table):
    result = table._translate_table_coordinates_list([1, 1, 1, -1])
    assert result == (1, 1, 1, 3)


def test_table_translate_table_coordinates_list_12(table):
    result = table._translate_table_coordinates_list([-1, -1, -1, -1])
    assert result == (6, 3, 6, 3)


def test_table_translate_table_coordinates_str_1(table):
    result = table._translate_table_coordinates_str("5")
    assert result == (None, 4, None, 4)


def test_table_translate_table_coordinates_str_1b(table):
    result = table._translate_table_coordinates_str("5:5")
    assert result == (None, 4, None, 4)


def test_table_translate_table_coordinates_str_2(table):
    result = table._translate_table_coordinates_str("1:1")
    assert result == (None, 0, None, 0)


def test_table_translate_table_coordinates_str_3(table):
    result = table._translate_table_coordinates_str("2:3")
    assert result == (None, 1, None, 2)


def test_table_translate_table_coordinates_str_4(table):
    result = table._translate_table_coordinates_str("3:3")
    assert result == (None, 2, None, 2)


def test_table_translate_table_coordinates_str_5(table):
    result = table._translate_table_coordinates_str("4:3")
    assert result == (None, 3, None, 2)


def test_table_translate_table_coordinates_str_7(table):
    result = table._translate_table_coordinates_str("B2:B2")
    assert result == (1, 1, 1, 1)


def test_table_translate_table_coordinates_str_8(table):
    result = table._translate_table_coordinates_str("G2:B2")
    assert result == (6, 1, 1, 1)


def test_table_translate_table_coordinates_str_9(table):
    result = table._translate_table_coordinates_str("B4:B2")
    assert result == (1, 3, 1, 1)


def test_table_translate_table_coordinates_str_10(table):
    result = table._translate_table_coordinates_str("B2:G2")
    assert result == (1, 1, 6, 1)


def test_table_translate_table_coordinates_str_11(table):
    result = table._translate_table_coordinates_str("B2:B4")
    assert result == (1, 1, 1, 3)


def test_table_translate_table_coordinates_str_12(table):
    result = table._translate_table_coordinates_str("G4:G4")
    assert result == (6, 3, 6, 3)


def test_table_translate_column_coordinates_list_1(table):
    result = table._translate_column_coordinates_list([0])
    assert result == (0, None, 0, None)


def test_table_translate_column_coordinates_list_2(table):
    result = table._translate_column_coordinates_list([4])
    assert result == (4, None, 4, None)


def test_table_translate_column_coordinates_list_3(table):
    result = table._translate_column_coordinates_list([-2])
    assert result == (5, None, 5, None)


def test_table_translate_column_coordinates_list_4(table):
    result = table._translate_column_coordinates_list([0, 0])
    assert result == (0, None, 0, None)


def test_table_translate_column_coordinates_list_5(table):
    result = table._translate_column_coordinates_list([2, 3])
    assert result == (2, None, 3, None)


def test_table_translate_column_coordinates_list_6(table):
    result = table._translate_column_coordinates_list([-2, 3])
    assert result == (5, None, 3, None)


def test_table_translate_column_coordinates_list_7(table):
    result = table._translate_column_coordinates_list([-1, -2])
    assert result == (6, None, 5, None)


def test_table_translate_column_coordinates_list_8(table):
    result = table._translate_column_coordinates_list([0, 0, 0, 0])
    assert result == (0, 0, 0, 0)


def test_table_translate_column_coordinates_list_9(table):
    result = table._translate_column_coordinates_list([1, 2, 3, 4])
    assert result == (1, 2, 3, 4)


def test_table_translate_column_coordinates_list_10(table):
    result = table._translate_column_coordinates_list([-1, -2, -3, -4])
    assert result == (6, 2, 4, 0)


def test_table_translate_column_coordinates_str_1(table):
    result = table._translate_column_coordinates_str("1")
    assert result == (None, 0, None, 0)


def test_table_translate_column_coordinates_str_2(table):
    result = table._translate_column_coordinates_str("A1")
    assert result == (0, 0, 0, 0)


def test_table_translate_column_coordinates_str_3(table):
    result = table._translate_column_coordinates_str("A1:B3")
    assert result == (0, 0, 1, 2)


def test_table_translate_column_coordinates_str_4(table):
    result = table._translate_column_coordinates_str("A:A")
    assert result == (0, None, 0, None)


def test_table_translate_column_coordinates_str_5(table):
    result = table._translate_column_coordinates_str("A:B")
    assert result == (0, None, 1, None)


def test_table_translate_column_coordinates_str_6(table):
    result = table._translate_column_coordinates_str("B")
    assert result == (1, None, 1, None)


def test_table_translate_column_coordinates_1(table):
    result = table._translate_column_coordinates("B")
    assert result == (1, None, 1, None)


def test_table_translate_column_coordinates_2(table):
    result = table._translate_column_coordinates([1])
    assert result == (1, None, 1, None)


def test_translate_cell_coordinates_1(table):
    result = table._translate_cell_coordinates([1, 2])
    assert result == (1, 2)


def test_translate_cell_coordinates_2(table):
    result = table._translate_cell_coordinates([1, 2, 3, 4])
    assert result == (1, 2)


def test_translate_cell_coordinates_3(table):
    with pytest.raises(ValueError):
        table._translate_cell_coordinates([1, 2, 3])


def test_translate_cell_coordinates_4(table):
    result = table._translate_cell_coordinates("A1:d6")
    assert result == (0, 0)


def test_translate_cell_coordinates_5(table):
    result = table._translate_cell_coordinates("B2")
    assert result == (1, 1)


def test_translate_cell_coordinates_6(table):
    result = table._translate_cell_coordinates([-5, -5])
    assert result == (2, 3)


def test_table_get_formatted_text_normal_1(table):
    result = table._get_formatted_text_normal(None)
    expected = (
        "1\n1\n1\n2\n3\n3\n3\n\n"
        "1\n1\n1\n2\n3\n3\n3\n\n"
        "1\n1\n1\n2\n3\n3\n3\n\n"
        "1\n2\n3\n4\n5\n6\n7\n\n"
    )
    assert result == expected


def test_table_get_formatted_text_normal_2(table):
    table.set_value((1, 1), None)
    result = table._get_formatted_text_normal(None)
    expected = (
        "1\n1\n1\n2\n3\n3\n3\n\n"
        "1\n\n1\n2\n3\n3\n3\n\n"
        "1\n1\n1\n2\n3\n3\n3\n\n"
        "1\n2\n3\n4\n5\n6\n7\n\n"
    )
    assert result == expected


def test_table_get_formatted_text_normal_3(table):
    table.set_value((1, 1), None)
    cell = table.get_cell((1, 1))
    item = Header(1, "test")
    cell.append(item)
    table.set_cell((1, 1), cell)
    result = table._get_formatted_text_normal(None)
    expected = (
        "1\n1\n1\n2\n3\n3\n3\n\n"
        "1\ntest\n1\n2\n3\n3\n3\n\n"
        "1\n1\n1\n2\n3\n3\n3\n\n"
        "1\n2\n3\n4\n5\n6\n7\n\n"
    )
    assert result == expected


def test_table_get_formatted_text_rst_1(table):
    ctx = {"no_img_level": 0}
    result = table._get_formatted_text_rst(ctx)
    expected = (
        "\n"
        "== == == == == == == \n"
        "1  1  1  2  3  3  3  \n"
        "1  1  1  2  3  3  3  \n"
        "1  1  1  2  3  3  3  \n"
        "1  2  3  4  5  6  7  \n"
        "== == == == == == == \n\n"
    )
    assert result == expected


def test_table_get_formatted_text_rst_2(table):
    table.set_value((1, 1), None)
    cell = table.get_cell((1, 1))
    item = Header(1, "test")
    cell.append(item)
    table.set_cell((1, 1), cell)
    ctx = {
        "no_img_level": 0,
        "rst_mode": True,
    }
    result = table._get_formatted_text_rst(ctx)
    expected = (
        "\n"
        "== ========= == == == == == \n"
        "1  1         1  2  3  3  3  \n"
        "1  test      1  2  3  3  3  \n"
        "   ####                     \n"
        "1  1         1  2  3  3  3  \n"
        "1  2         3  4  5  6  7  \n"
        "== ========= == == == == == \n\n"
    )
    assert result == expected


def test_table_get_formatted_text_rst_3(table):
    table.set_value((1, 1), None)
    cell = table.get_cell((1, 1))
    item = Header(1, "test")
    cell.append(item)
    table.set_cell((1, 1), cell)
    ctx = {
        "no_img_level": 0,
        "rst_mode": True,
    }
    table.set_value((1, 2), "")
    result = table._get_formatted_text_rst(ctx)
    expected = (
        "\n== ========= == == == == == \n"
        "1  1         1  2  3  3  3  \n"
        "1  test      1  2  3  3  3  \n"
        "   ####                     \n"
        "1            1  2  3  3  3  \n"
        "1  2         3  4  5  6  7  \n"
        "== ========= == == == == == \n\n"
    )
    assert result == expected


def test_table_get_formatted_text_rst_empty():
    table = Table("empty")
    ctx = {
        "no_img_level": 0,
        "rst_mode": True,
    }
    result = table._get_formatted_text_rst(ctx)
    expected = ""
    assert result == expected


def test_table_get_formatted_text_rst_empty_2():
    table = Table("empty", 1, 1)
    ctx = {
        "no_img_level": 0,
        "rst_mode": True,
    }
    result = table._get_formatted_text_rst(ctx)
    expected = ""
    assert result == expected


def test_table_printable_1(table):
    result = table.printable
    expected = False
    assert result is expected


def test_table_printable_2():
    table = table = Table("empty", 1, 1)
    result = table.printable
    expected = True
    assert result is expected


def test_table_printable_3(table):
    table.printable = True
    result = table.printable
    expected = True
    assert result is expected


def test_table_printable_4(table):
    table.printable = False
    result = table.printable
    expected = False
    assert result is expected


def test_table_ranges_1(table):
    result = table.print_ranges
    expected = []
    assert result == expected


def test_table_ranges_2(table):
    table.print_ranges = ["A1:B2", "A4:C4"]
    result = table.print_ranges
    expected = ["A1:B2", "A4:C4"]
    assert result == expected


def test_table_get_formatted_text_1(table):
    result = table.get_formatted_text(None)
    expected = (
        "1\n1\n1\n2\n3\n3\n3\n\n"
        "1\n1\n1\n2\n3\n3\n3\n\n"
        "1\n1\n1\n2\n3\n3\n3\n\n"
        "1\n2\n3\n4\n5\n6\n7\n\n"
    )
    assert result == expected


def test_table_get_formatted_text_2(table):
    ctx = {
        "no_img_level": 0,
        "rst_mode": True,
    }
    result = table.get_formatted_text(ctx)
    expected = (
        "\n"
        "== == == == == == == \n"
        "1  1  1  2  3  3  3  \n"
        "1  1  1  2  3  3  3  \n"
        "1  1  1  2  3  3  3  \n"
        "1  2  3  4  5  6  7  \n"
        "== == == == == == == \n\n"
    )
    assert result == expected


def test_table_append_column(table):
    col = Column()
    table.append(col)
    result = list(table.iter_values())
    assert result == [
        [1, 1, 1, 2, 3, 3, 3, None],
        [1, 1, 1, 2, 3, 3, 3, None],
        [1, 1, 1, 2, 3, 3, 3, None],
        [1, 2, 3, 4, 5, 6, 7, None],
    ]


def test_table_append_row(table):
    row = Row()
    table.append(row)
    result = list(table.iter_values())
    assert result == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
        [None, None, None, None, None, None, None],
    ]


def test_table_append_somthing(table):
    elem = Element.from_tag("text:p")
    table.append(elem)
    result = list(table.iter_values())
    assert result == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]


def test_table_iter_values_1(table):
    result = table.iter_values()
    assert isinstance(result, Iterator)


def test_table_iter_values_2(table):
    result = list(table.iter_values())
    assert result == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]


def test_table_iter_values_3(table):
    coord = (2, 2, 3, 3)
    result = list(table.iter_values(coord))
    assert result == [
        [1, 2],
        [3, 4],
    ]


def test_table_iter_values_4(table):
    table.set_value((2, 2), None)
    coord = (2, 2, 3, 3)
    result = list(table.iter_values(coord))
    assert result == [
        [None, 2],
        [3, 4],
    ]


def test_table_iter_values_5(table):
    row = Row()
    row.set_values([10, 20, 30])
    table.append(row)
    result = list(table.iter_values(complete=True))
    assert result == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
        [10, 20, 30, None, None, None, None],
    ]


def test_table_iter_values_6(table):
    row = Row()
    row.set_values([10, 20, 30])
    table.append(row)
    result = list(table.iter_values(complete=True, get_type=True))
    assert result == [
        [
            (1, "float"),
            (1, "float"),
            (1, "float"),
            (2, "float"),
            (3, "float"),
            (3, "float"),
            (3, "float"),
        ],
        [
            (1, "float"),
            (1, "float"),
            (1, "float"),
            (2, "float"),
            (3, "float"),
            (3, "float"),
            (3, "float"),
        ],
        [
            (1, "float"),
            (1, "float"),
            (1, "float"),
            (2, "float"),
            (3, "float"),
            (3, "float"),
            (3, "float"),
        ],
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
            (10, "float"),
            (20, "float"),
            (30, "float"),
            (None, None),
            (None, None),
            (None, None),
            (None, None),
        ],
    ]


def test_table_iter_values_7(table):
    row = Row()
    row.set_values([10, 20, 30])
    table.append(row)
    result = list(table.iter_values(complete=False))
    assert result == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
        [10, 20, 30],
    ]


def test_table_set_values_1(table):
    table.set_values(values=[[10, 20, 30]], coord=(None, None))
    result = list(table.iter_values())
    assert result == [
        [10, 20, 30, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]


def test_table_set_values_2(table):
    table.rows[3].repeated = 4
    table.set_values(values=[[], [10, 20, 30]], coord=(1, 2))
    result = list(table.iter_values())
    assert result == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 10, 20, 30, 5, 6, 7],
        [1, 2, 3, 4, 5, 6, 7],
        [1, 2, 3, 4, 5, 6, 7],
        [1, 2, 3, 4, 5, 6, 7],
    ]


def test_table_rstrip_1(table):
    table.rstrip()
    result = list(table.iter_values(complete=True))
    assert result == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]


def test_table_rstrip_2(table):
    col = table.columns[6]
    col.repeated = 4
    table.set_column(6, col)
    result = list(table.iter_values(complete=True))
    assert result == [
        [1, 1, 1, 2, 3, 3, 3, None, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None, None],
        [1, 2, 3, 4, 5, 6, 7, None, None, None],
    ]


def test_table_rstrip_3(table):
    col = table.columns[6]
    col.repeated = 4
    table.set_column(6, col)
    table.rstrip()
    result = list(table.iter_values(complete=True))
    assert result == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]


def test_table_rstrip_4(table):
    col = table.columns[6]
    col.repeated = 4
    table.set_column(6, col)
    row = Row()
    row.set_values([10, 20, 30, 40, 50, 60, 70, 80, 90])
    table.append(row)
    result = list(table.iter_values(complete=True))
    assert result == [
        [1, 1, 1, 2, 3, 3, 3, None, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None, None],
        [1, 2, 3, 4, 5, 6, 7, None, None, None],
        [10, 20, 30, 40, 50, 60, 70, 80, 90, None],
    ]


def test_table_rstrip_5():
    table = Table("empty")
    expected = table.serialize()
    table.rstrip()
    result = table.serialize()
    assert result == expected


def test_table_transpose_1(table):
    coord = (None, None, None, None)
    table.transpose(coord)
    result = list(table.iter_values(complete=True))
    assert result == [
        [1, 1, 1, 1, None, None, None],
        [1, 1, 1, 2, None, None, None],
        [1, 1, 1, 3, None, None, None],
        [2, 2, 2, 4, None, None, None],
        [3, 3, 3, 5, None, None, None],
        [3, 3, 3, 6, None, None, None],
        [3, 3, 3, 7, None, None, None],
    ]


def test_table_is_empty(table):
    assert not table.is_empty()


def test_table_extend_rows_1(table):
    row1 = Row()
    row2 = Row()
    row2.set_values([10, 20, 30, 40, 50])
    table.extend_rows([row1, row2])
    result = list(table.iter_values(complete=True))
    assert result == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
        [None, None, None, None, None, None, None],
        [10, 20, 30, 40, 50, None, None],
    ]


def test_table_extend_rows_2(table):
    table.extend_rows([])
    result = list(table.iter_values())
    assert result == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]


def test_table_extend_rows_3(table):
    table.extend_rows()
    result = list(table.iter_values())
    assert result == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]


def test_table_extend_rows_4(table):
    row = Row()
    row.set_values([10, 20, 30, 40, 50, 60, 70, 80, 90])
    table.extend_rows([row])
    result = list(table.iter_values())
    assert result == [
        [1, 1, 1, 2, 3, 3, 3, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None],
        [1, 2, 3, 4, 5, 6, 7, None, None],
        [10, 20, 30, 40, 50, 60, 70, 80, 90],
    ]


def test_table_delete_row(table):
    table.delete_row(99)
    result = list(table.iter_values())
    assert result == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]


def test_table_get_row_values_1(table):
    result = table.get_row_values(1, get_type=True)
    assert result == [
        (1, "float"),
        (1, "float"),
        (1, "float"),
        (2, "float"),
        (3, "float"),
        (3, "float"),
        (3, "float"),
    ]


def test_table_get_row_values_2(table):
    result = table.get_row_values(1, complete=False)
    assert result == [1, 1, 1, 2, 3, 3, 3]


def test_table_set_row_cells_1(table):
    c1 = Cell(value=40)
    c2 = Cell(value=50)
    table.set_row_cells(2, [c1, c2])
    result = list(table.iter_values())
    assert result == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [40, 50, None, None, None, None, None],
        [1, 2, 3, 4, 5, 6, 7],
    ]


def test_table_set_row_cells_2(table):
    table.set_row_cells(2, [])
    result = list(table.iter_values())
    assert result == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [None, None, None, None, None, None, None],
        [1, 2, 3, 4, 5, 6, 7],
    ]


def test_table_set_row_cells_3(table):
    table.set_row_cells(2)
    result = list(table.iter_values())
    assert result == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [None, None, None, None, None, None, None],
        [1, 2, 3, 4, 5, 6, 7],
    ]
