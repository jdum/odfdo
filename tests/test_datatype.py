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
# Authors: Hervé Cauwelier <herve@itaapy.com>
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from odfdo.datatype import Boolean, DateTime, Duration, Unit


def test_datetime_encode():
    date = datetime(2009, 0o6, 26, 11, 9, 36)
    expected = "2009-06-26T11:09:36"
    assert DateTime.encode(date) == expected


def test_datetime_encode_micro():
    date = datetime(2009, 6, 26, 11, 9, 36, 123456)
    expected = "2009-06-26T11:09:36.123456"
    assert DateTime.encode(date) == expected


def test_datetime_encode_UTC():
    date = datetime(2009, 6, 26, 11, 9, 36, tzinfo=timezone.utc)
    expected = "2009-06-26T11:09:36Z"
    assert DateTime.encode(date) == expected


def test_datetime_encode_micro_UTC():
    date = datetime(2009, 6, 26, 11, 9, 36, 123456, tzinfo=timezone.utc)
    expected = "2009-06-26T11:09:36.123456Z"
    assert DateTime.encode(date) == expected


def test_datetime_encode_gmt2():
    date = datetime(2009, 6, 26, 11, 9, 36, tzinfo=timezone(timedelta(hours=2)))
    expected = "2009-06-26T11:09:36+02:00"
    assert DateTime.encode(date) == expected


def test_datetime_encode_gmt_6():
    date = datetime(2009, 6, 26, 11, 9, 36, tzinfo=timezone(timedelta(hours=-6)))
    expected = "2009-06-26T11:09:36-06:00"
    assert DateTime.encode(date) == expected


def test_datetime_decode():
    date = "2009-06-29T14:33:21"
    expected = datetime(2009, 6, 29, 14, 33, 21)
    assert DateTime.decode(date) == expected


def test_datetime_decode_micro():
    date = "2009-06-29T14:33:21.123456"
    expected = datetime(2009, 6, 29, 14, 33, 21, 123456)
    assert DateTime.decode(date) == expected


def test_datetime_decode_nano():
    date = "2009-06-29T14:33:21.123456789"
    if sys.version_info.major == 3 and sys.version_info.minor >= 11:
        expected = datetime(2009, 6, 29, 14, 33, 21, 123456)
        assert DateTime.decode(date) == expected
    else:
        expected = datetime(2009, 6, 29, 14, 33, 21, 123456)
        assert DateTime.decode(date) == expected


def test_datetime_decode_utc():
    date = "2009-06-29T14:33:21Z"
    expected = datetime(2009, 6, 29, 14, 33, 21, tzinfo=timezone.utc)
    assert DateTime.decode(date) == expected


def test_datetime_decode_utc_00():
    date = "2009-06-29T14:33:21+00:00"
    expected = datetime(2009, 6, 29, 14, 33, 21, tzinfo=timezone.utc)
    assert DateTime.decode(date) == expected


def test_datetime_decode_gmt2():
    date = "2009-06-29T14:33:21+02:00"
    expected = datetime(2009, 6, 29, 14, 33, 21, tzinfo=timezone(timedelta(hours=2)))
    assert DateTime.decode(date) == expected


def test_datetime_decode_gmt_6():
    date = "2009-06-29T14:33:21-06:00"
    expected = datetime(2009, 6, 29, 14, 33, 21, tzinfo=timezone(timedelta(hours=-6)))
    assert DateTime.decode(date) == expected


def test_datetime_decode_utc_micro():
    date = "2009-06-29T14:33:21.123456Z"
    expected = datetime(2009, 6, 29, 14, 33, 21, 123456, tzinfo=timezone.utc)
    assert DateTime.decode(date) == expected


def test_datetime_decode_utc_00_micro():
    date = "2009-06-29T14:33:21.123456+00:00"
    expected = datetime(2009, 6, 29, 14, 33, 21, 123456, tzinfo=timezone.utc)
    assert DateTime.decode(date) == expected


def test_datetime_decode_gmt2_micro():
    date = "2009-06-29T14:33:21.123456+02:00"
    expected = datetime(
        2009, 6, 29, 14, 33, 21, 123456, tzinfo=timezone(timedelta(hours=2))
    )
    assert DateTime.decode(date) == expected


def test_datetime_decode_utc_nano():
    date = "2009-06-29T14:33:21.123456789Z"
    expected = datetime(2009, 6, 29, 14, 33, 21, 123456, tzinfo=timezone.utc)
    assert DateTime.decode(date) == expected


def test_datetime_decode_utc_00_nano():
    date = "2009-06-29T14:33:21.123456789+00:00"
    expected = datetime(2009, 6, 29, 14, 33, 21, 123456, tzinfo=timezone.utc)
    assert DateTime.decode(date) == expected


def test_datetime_decode_gmt2_nano():
    date = "2009-06-29T14:33:21.123456789+02:00"
    expected = datetime(
        2009, 6, 29, 14, 33, 21, 123456, tzinfo=timezone(timedelta(hours=2))
    )
    assert DateTime.decode(date) == expected


def test_duration_encode():
    duration = timedelta(0, 53, 0, 0, 6)
    expected = "PT00H06M53S"
    assert Duration.encode(duration) == expected


def test_duration_decode():
    duration = "PT12H34M56S"
    expected = timedelta(0, 56, 0, 0, 34, 12)
    assert Duration.decode(duration) == expected


def test_bool_encode():
    assert Boolean.encode(True) == "true"
    assert Boolean.encode(False) == "false"
    assert Boolean.encode("true") == "true"
    assert Boolean.encode("false") == "false"


def test_bool_bad_encode_on():
    with pytest.raises(TypeError):
        Boolean.encode("on")


def test_bool_bad_encode_one():
    with pytest.raises(TypeError):
        Boolean.encode(1)


def test_bool_decode():
    assert Boolean.decode("true") is True
    assert Boolean.decode("false") is False


def test_bool_bad_decode_true():
    with pytest.raises(ValueError):
        Boolean.decode("True")


def test_bool_bad_encode_pne():
    with pytest.raises(ValueError):
        Boolean.decode("1")


def test_str():
    unit = Unit("1.847mm")
    assert unit.value == Decimal("1.847")
    assert unit.unit == "mm"


def test_str_str():
    unit = Unit("1.847mm")
    assert str(unit) == "1.847mm"


def test_int():
    unit = Unit(1)
    assert unit.value == Decimal("1")
    assert unit.unit == "cm"


def test_float():
    unit = Unit(3.14)
    assert unit.value == Decimal("3.14")
    assert unit.unit == "cm"


def test_encode():
    value = "1.847mm"
    unit = Unit(value)
    assert str(unit) == value


def test_eq():
    unit1 = Unit("2.54cm")
    unit2 = Unit("2.54cm")
    assert unit1 == unit2


def test_lt():
    unit1 = Unit("2.53cm")
    unit2 = Unit("2.54cm")
    assert unit1 < unit2


def test_nlt():
    unit1 = Unit("2.53cm")
    unit2 = Unit("2.54cm")
    assert not (unit1 > unit2)


def test_gt():
    unit1 = Unit("2.54cm")
    unit2 = Unit("2.53cm")
    assert unit1 > unit2


def test_ngt():
    unit1 = Unit("2.54cm")
    unit2 = Unit("2.53cm")
    assert not (unit1 < unit2)


def test_le():
    unit1 = Unit("2.54cm")
    unit2 = Unit("2.54cm")
    assert unit1 <= unit2


def test_ge():
    unit1 = Unit("2.54cm")
    unit2 = Unit("2.54cm")
    assert unit1 >= unit2


def test_convert():
    unit = Unit("10cm")
    assert unit.convert("px") == Unit("283px")
