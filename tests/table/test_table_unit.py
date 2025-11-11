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
from collections.abc import Iterable

import pytest

# from odfdo import Element
from odfdo.document import Document
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
    yield document.body.get_table(name="Example1")


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
