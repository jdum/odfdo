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
from __future__ import annotations

import math
from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from odfdo.table import Table
from odfdo.table_serializer import (
    TableSerializer,
    _make_serializer,
    _serialize_table_row_json,
    _serialize_table_row_python_typed,
    serialize_table,
)


def test_serialize_table_unknown_mode():
    table = Table("Test")
    with pytest.raises(ValueError, match="unknown serializer mode 'xml'"):
        serialize_table(table, "xml")


def test_serialize_table_json():
    table = Table("Test", width=3, height=2)
    table.set_value((0, 0), "Hello")
    table.set_value((1, 0), 123)
    table.set_value((0, 1), date(2025, 1, 1))
    result = serialize_table(table, "json")
    assert result == [
        ["Hello", 123],
        ["2025-01-01"],
    ]


def test_serialize_table_python():
    table = Table("Test", width=3, height=2)
    table.set_value((0, 0), "Hello")
    table.set_value((1, 0), 123)
    d = date(2025, 1, 1)
    table.set_value((0, 1), d)
    result = serialize_table(table, "python")
    assert result == [
        ["Hello", 123],
        [d],
    ]


def test_serialize_table_row_json_types():
    row = [
        "text",
        1,
        True,
        False,
        3.14,
        float("nan"),
        float("inf"),
        float("-inf"),
        Decimal("42.00"),
        Decimal("42.5"),
        Decimal("NaN"),
        Decimal("Infinity"),
        datetime(2025, 5, 12, 10, 30),
        date(2025, 5, 12),
        timedelta(hours=2, minutes=30),
        [1, 2, 3],  # fallback to str
        None,
        None,
    ]
    result = _serialize_table_row_json(row)
    assert result == [
        "text",
        1,
        True,
        False,
        3.14,
        None,
        None,
        None,
        42,
        42.5,
        None,
        None,
        "2025-05-12T10:30:00",
        "2025-05-12",
        "PT02H30M00S",
        "[1, 2, 3]",
    ]


def test_serialize_table_row_python_types():
    dec_val = Decimal("42.5")
    dt = datetime(2025, 5, 12, 10, 30)
    d = date(2025, 5, 12)
    td = timedelta(hours=2)
    row = [
        "text",
        1,
        True,
        False,
        3.14,
        float("nan"),
        float("inf"),
        Decimal("42.00"),
        dec_val,
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
        dt,
        d,
        td,
        [1, 2],  # fallback to str
        None,
        None,
    ]
    result = _serialize_table_row_python_typed(row)
    assert result[0:5] == ["text", 1, True, False, 3.14]
    assert math.isnan(result[5])
    assert math.isinf(result[6])
    assert result[7] == 42
    assert result[8] == dec_val
    assert math.isnan(result[9])
    assert math.isinf(result[10]) and result[10] > 0
    assert math.isinf(result[11]) and result[11] < 0
    assert result[12] == dt
    assert result[13] == d
    assert result[14] == td
    assert result[15] == "[1, 2]"
    assert len(result) == 16


def test_table_serializer_empty_table():
    table = Table("Empty")
    serializer = TableSerializer(_serialize_table_row_json)
    assert serializer.serialize(table) == []


def test_table_serializer_all_empty_rows():
    table = Table("EmptyRows", width=3, height=3)
    serializer = TableSerializer(_serialize_table_row_json)
    assert serializer.serialize(table) == []


def test_table_serializer_pop_trailing_empty_row():
    table = Table("Trailing", width=2, height=2)
    table.set_value((0, 0), "A")
    table.set_value((0, 1), "B")

    # Serializer that empties the second row
    def custom_serializer(row: list) -> list:
        if row and row[0] == "A":
            return ["A"]
        return []

    serializer = TableSerializer(custom_serializer)
    assert serializer.serialize(table) == [["A"]]


def test_make_serializer_defaults_and_all():
    assert _make_serializer(False, False, False) is _serialize_table_row_python_typed
    assert _make_serializer(True, True, True) is _serialize_table_row_json


def test_make_serializer_no_decimal():
    serializer = _make_serializer(no_decimal=True, no_date=False, no_nan=False)
    dt = datetime(2025, 6, 15, 12, 0)
    d = date(2025, 6, 15)
    td = timedelta(minutes=45)
    row = [
        Decimal("10.5"),
        Decimal("10.0"),
        Decimal("NaN"),
        Decimal("Infinity"),
        3.14,
        dt,
        d,
        td,
        [1, 2],
        None,
        None,
    ]
    res = serializer(row)
    assert res[0] == 10.5
    assert isinstance(res[0], float)
    assert res[1] == 10
    assert isinstance(res[1], int)
    assert math.isnan(res[2])
    assert math.isinf(res[3])
    assert res[4] == 3.14
    assert res[5] == dt
    assert res[6] == d
    assert res[7] == td
    assert res[8] == "[1, 2]"
    assert len(res) == 9


def test_make_serializer_no_date():
    serializer = _make_serializer(no_decimal=False, no_date=True, no_nan=False)
    dt = datetime(2025, 6, 15, 12, 0)
    d = date(2025, 6, 15)
    td = timedelta(minutes=45)
    dec_val = Decimal("10.5")
    row = [
        dt,
        d,
        td,
        b"bytes_data",
        "other",
        dec_val,
        Decimal("10.0"),
        Decimal("NaN"),
        Decimal("Infinity"),
        [1],
        None,
    ]
    res = serializer(row)
    assert res[0] == "2025-06-15T12:00:00"
    assert res[1] == "2025-06-15"
    assert res[2] == "PT00H45M00S"
    assert res[3] == b"bytes_data"
    assert res[4] == "other"
    assert res[5] == dec_val
    assert res[6] == 10
    assert math.isnan(res[7])
    assert math.isinf(res[8])
    assert res[9] == "[1]"
    assert len(res) == 10


def test_make_serializer_no_nan():
    serializer = _make_serializer(no_decimal=False, no_date=False, no_nan=True)
    dt = datetime(2025, 6, 15, 12, 0)
    row = [
        float("nan"),
        float("inf"),
        float("-inf"),
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
        3.14,
        Decimal("42.5"),
        Decimal("42.0"),
        dt,
        [9],
        None,
    ]
    assert serializer(row) == [
        None,
        None,
        None,
        None,
        None,
        None,
        3.14,
        Decimal("42.5"),
        42,
        dt,
        "[9]",
    ]


def test_make_serializer_no_decimal_and_no_nan():
    serializer = _make_serializer(no_decimal=True, no_date=False, no_nan=True)
    dt = datetime(2025, 6, 15, 12, 0)
    row = [
        float("nan"),
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("42.5"),
        Decimal("42.0"),
        dt,
        [9],
        None,
    ]
    assert serializer(row) == [
        None,
        None,
        None,
        42.5,
        42,
        dt,
        "[9]",
    ]


def test_serialize_table_python_with_options():
    table = Table("TestOptions", width=3, height=2)
    table.set_value((0, 0), Decimal("12.50"))
    table.set_value((1, 0), date(2025, 1, 1))
    table.set_value((2, 0), float("nan"))
    table.set_value((0, 1), "text_row")
    result = serialize_table(
        table,
        "python",
        no_decimal=True,
        no_date=True,
        no_nan=True,
    )
    assert result == [
        [12.5, "2025-01-01"],
        ["text_row"],
    ]





