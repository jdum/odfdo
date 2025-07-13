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

from datetime import date, timedelta

import pytest

from odfdo.variable import VarSet


def test_et_set_value_type_bytes():
    et = VarSet()
    result = et.set_value_and_type(b"byt")
    assert result == "byt"


def test_et_set_value_type_bytes_and_type():
    et = VarSet()
    result = et.set_value_and_type(b"byt", value_type=b"string")
    assert result == "byt"


def test_et_set_value_type_bytes_and_text():
    et = VarSet()
    result = et.set_value_and_type(123, value_type=b"int", text=b"123")
    assert result == "123"


def test_et_set_value_type_bytes_and_currency():
    et = VarSet()
    result = et.set_value_and_type(123, value_type=b"int", currency=b"EUR")
    assert result == "123"


def test_et_set_value_date():
    et = VarSet()
    dt = date(1977, 12, 25)
    result = et.set_value_and_type(dt)
    assert result == "1977-12-25"


def test_et_set_value_date_typed():
    et = VarSet()
    dt = date(1977, 12, 25)
    result = et.set_value_and_type(dt, value_type="date")
    assert result == "1977-12-25"


def test_et_set_value_str():
    et = VarSet()
    result = et.set_value_and_type("some string")
    assert result == "some string"


def test_et_set_value_time():
    et = VarSet()
    td = timedelta(hours=2)
    result = et.set_value_and_type(td)
    assert result == "PT02H00M00S"


def test_et_set_value_time_typed():
    et = VarSet()
    td = timedelta(hours=2)
    result = et.set_value_and_type(td, value_type="time")
    assert result == "PT02H00M00S"


def test_et_set_value_wrong_type():
    et = VarSet()
    with pytest.raises(TypeError):
        et.set_value_and_type([])


def test_et_set_value_wrong_type_ignored():
    et = VarSet()
    result = et.set_value_and_type(123, value_type=42)
    assert result == "123"


def test_et_get_value_no_bool_type():
    et = VarSet()
    et.set_value_and_type(True)
    # wrong type forced:
    et.set_attribute("office:value-type", True)
    with pytest.raises(TypeError):
        et.get_value()


def test_et_get_value_with_value_type():
    et = VarSet()
    et.set_value_and_type(True)
    et.get_value(value_type="boolean")


def test_et_get_value_with_wrong_value_type():
    et = VarSet()
    et.set_value_and_type(True)
    with pytest.raises(TypeError):
        et.get_value(value_type="wrong")


def test_et_get_value_with_strange_content_none_value_type():
    et = VarSet()
    et.set_value_and_type(None, value_type="string")
    result = et.get_value()
    assert result is None


def test_et_get_value_with_strange_content_none_value_type_text():
    et = VarSet()
    et.set_value_and_type(None, value_type="string")
    result = et.get_value(value_type="string")
    assert result is None


def test_et_get_value_with_strange_content_none_value_type_no_text():
    et = VarSet()
    et.set_value_and_type(None, value_type="string")
    result = et.get_value(value_type="string", try_get_text=False)
    assert result is None


def test_et_get_value_with_bad_date():
    et = VarSet()
    et.set_value_and_type(123, value_type="date")
    with pytest.raises(ValueError):
        et.get_value(value_type="date")


def test_et_get_value_time():
    et = VarSet()
    et.set_value_and_type(timedelta(hours=2), value_type="time")
    result = et.get_value(value_type="time")
    assert result == timedelta(hours=2)
