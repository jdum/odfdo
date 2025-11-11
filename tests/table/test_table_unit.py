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

# from collections.abc import Iterable
# import pytest
# from odfdo import Element
# from odfdo.document import Document
# from odfdo.table import Table, _get_python_value
from odfdo.table import _get_python_value

# @pytest.fixture
# def body(samples) -> Iterable[Element]:
#     document = Document(samples("simple_table.ods"))
#     yield document.body


# @pytest.fixture
# def table(samples) -> Iterable[Table]:
#     # simpletable :
#     #   1	1	1	2	3	3	3
#     #   1	1	1	2	3	3	3
#     #   1	1	1	2	3	3	3
#     #   1   2	3	4	5	6	7
#     document = Document(samples("simple_table.ods"))
#     yield document.body.get_table(name="Example1")


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
