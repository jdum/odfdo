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

from datetime import date as dtdate
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from odfdo.element import Element
from odfdo.meta_user_defined import MetaUserDefined


def test_meta_user_defined_class():
    data = Element.from_tag("<meta:user-defined/>")
    assert isinstance(data, MetaUserDefined)


def test_meta_user_defined_create_no_param():
    with pytest.raises(ValueError):
        MetaUserDefined()


def test_meta_user_defined_create_no_value_type():
    with pytest.raises(ValueError):
        MetaUserDefined(name="key")


def test_meta_user_defined_create_no_value_string():
    data = MetaUserDefined(name="key", value_type="string")
    assert data.value == ""


def test_meta_user_defined_create_no_value_bool():
    data = MetaUserDefined(name="key", value_type="boolean")
    assert data.value is False


def test_meta_user_defined_create_no_value_date():
    with pytest.raises((AttributeError, TypeError)):
        MetaUserDefined(name="key", value_type="date")


def test_meta_user_defined_create_no_value_float():
    data = MetaUserDefined(name="key", value_type="float")
    assert data.value == 0


def test_meta_user_defined_create_no_value_time():
    with pytest.raises(TypeError):
        MetaUserDefined(name="key", value_type="time")


def test_meta_user_defined_create_string():
    data = MetaUserDefined(name="key", value_type="string", value="value")
    assert data.value == "value"


def test_meta_user_defined_create_bool():
    data = MetaUserDefined(name="key", value_type="boolean", value=True)
    assert data.value is True


def test_meta_user_defined_create_date():
    dt = dtdate(2025, 1, 2)
    data = MetaUserDefined(name="key", value_type="date", value=dt)
    assert data.value == dtdate(2025, 1, 2)


def test_meta_user_defined_create_date_datetime():
    dt = datetime(2025, 1, 2, 10, 20, 30)
    data = MetaUserDefined(name="key", value_type="date", value=dt)
    assert data.value == dt


def test_meta_user_defined_create_date_timedelta():
    dt = timedelta(hours=3)
    data = MetaUserDefined(name="key", value_type="time", value=dt)
    assert data.value == dt


def test_meta_user_defined_create_float():
    data = MetaUserDefined(name="key", value_type="float", value=3.14)
    assert data.value == Decimal("3.14")


def test_meta_user_defined_create_int():
    data = MetaUserDefined(name="key", value_type="float", value=42)
    assert data.value == Decimal("42")


def test_meta_user_defined_from_xml():
    xml = (
        "<meta:user-defined "
        'meta:name="Référence" meta:value-type="boolean">'
        "true"
        "</meta:user-defined>"
    )
    data = Element.from_tag(xml)
    assert data.name == "Référence"
    assert data.value_type == "boolean"
    assert data.value is True


def test_meta_user_defined_missing_value_type():
    xml = '<meta:user-defined meta:name="test">hello</meta:user-defined>'
    data = Element.from_tag(xml)
    assert data.value_type == "string"
    assert data.value == "hello"


def test_meta_user_defined_unknown_value_type():
    xml = '<meta:user-defined meta:name="test" meta:value-type="unknown">foo</meta:user-defined>'
    data = Element.from_tag(xml)
    assert data.value_type == "unknown"
    with pytest.raises(TypeError, match="Unknown value type: 'unknown'"):
        _ = data.value


def test_meta_user_defined_value_to_value_type():
    assert MetaUserDefined._value_to_value_type(True) == "boolean"
    assert MetaUserDefined._value_to_value_type(42) == "float"
    assert MetaUserDefined._value_to_value_type(3.14) == "float"
    assert MetaUserDefined._value_to_value_type(Decimal("1.23")) == "float"
    assert MetaUserDefined._value_to_value_type(datetime(2025, 1, 1)) == "date"
    assert MetaUserDefined._value_to_value_type(dtdate(2025, 1, 1)) == "date"
    assert MetaUserDefined._value_to_value_type("text") == "string"
    assert MetaUserDefined._value_to_value_type(timedelta(seconds=10)) == "time"
    with pytest.raises(TypeError, match="Unexpected type"):
        MetaUserDefined._value_to_value_type([1, 2, 3])  # type: ignore[arg-type]


def test_meta_user_defined_as_dict():
    data = MetaUserDefined(name="author", value_type="string", value="Alice")
    assert data.as_dict() == {
        "meta:name": "author",
        "meta:value-type": "string",
        "value": "Alice",
    }


def test_meta_user_defined_as_dict_full():
    data = MetaUserDefined(name="author", value_type="string", value="Alice")
    assert data.as_dict_full() == {
        "name": "author",
        "value_type": "string",
        "value": "Alice",
        "text": "Alice",
    }
