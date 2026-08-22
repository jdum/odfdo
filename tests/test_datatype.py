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
# Authors: Hervé Cauwelier <herve@itaapy.com>
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from odfdo.datatype import (
    Boolean,
    Date,
    DateDecoder,
    DateTime,
    Duration,
    Unit,
    decode_heuristic,
)


def test_datetime_encode():
    date_value = datetime(2009, 0o6, 26, 11, 9, 36)
    expected = "2009-06-26T11:09:36"
    assert DateTime.encode(date_value) == expected


def test_datetime_encode_micro():
    date_value = datetime(2009, 6, 26, 11, 9, 36, 123456)
    expected = "2009-06-26T11:09:36.123456"
    assert DateTime.encode(date_value) == expected


def test_datetime_encode_UTC():
    date_value = datetime(2009, 6, 26, 11, 9, 36, tzinfo=timezone.utc)
    expected = "2009-06-26T11:09:36Z"
    assert DateTime.encode(date_value) == expected


def test_datetime_encode_micro_UTC():
    date_value = datetime(2009, 6, 26, 11, 9, 36, 123456, tzinfo=timezone.utc)
    expected = "2009-06-26T11:09:36.123456Z"
    assert DateTime.encode(date_value) == expected


def test_datetime_encode_gmt2():
    date_value = datetime(2009, 6, 26, 11, 9, 36, tzinfo=timezone(timedelta(hours=2)))
    expected = "2009-06-26T11:09:36+02:00"
    assert DateTime.encode(date_value) == expected


def test_datetime_encode_gmt_6():
    date_value = datetime(2009, 6, 26, 11, 9, 36, tzinfo=timezone(timedelta(hours=-6)))
    expected = "2009-06-26T11:09:36-06:00"
    assert DateTime.encode(date_value) == expected


def test_datetime_decode():
    date_value = "2009-06-29T14:33:21"
    expected = datetime(2009, 6, 29, 14, 33, 21)
    assert DateTime.decode(date_value) == expected


def test_datetime_decode_micro():
    date_value = "2009-06-29T14:33:21.123456"
    expected = datetime(2009, 6, 29, 14, 33, 21, 123456)
    assert DateTime.decode(date_value) == expected


def test_datetime_decode_nano():
    date_value = "2009-06-29T14:33:21.123456789"
    expected = datetime(2009, 6, 29, 14, 33, 21, 123456)
    assert DateTime.decode(date_value) == expected


def test_datetime_decode_utc():
    date_value = "2009-06-29T14:33:21Z"
    expected = datetime(2009, 6, 29, 14, 33, 21, tzinfo=timezone.utc)
    assert DateTime.decode(date_value) == expected


def test_datetime_decode_utc_00():
    date_value = "2009-06-29T14:33:21+00:00"
    expected = datetime(2009, 6, 29, 14, 33, 21, tzinfo=timezone.utc)
    assert DateTime.decode(date_value) == expected


def test_datetime_decode_gmt2():
    date_value = "2009-06-29T14:33:21+02:00"
    expected = datetime(2009, 6, 29, 14, 33, 21, tzinfo=timezone(timedelta(hours=2)))
    assert DateTime.decode(date_value) == expected


def test_datetime_decode_gmt_6():
    date_value = "2009-06-29T14:33:21-06:00"
    expected = datetime(2009, 6, 29, 14, 33, 21, tzinfo=timezone(timedelta(hours=-6)))
    assert DateTime.decode(date_value) == expected


def test_datetime_decode_utc_micro():
    date_value = "2009-06-29T14:33:21.123456Z"
    expected = datetime(2009, 6, 29, 14, 33, 21, 123456, tzinfo=timezone.utc)
    assert DateTime.decode(date_value) == expected


def test_datetime_decode_utc_00_micro():
    date_value = "2009-06-29T14:33:21.123456+00:00"
    expected = datetime(2009, 6, 29, 14, 33, 21, 123456, tzinfo=timezone.utc)
    assert DateTime.decode(date_value) == expected


def test_datetime_decode_gmt2_micro():
    date_value = "2009-06-29T14:33:21.123456+02:00"
    expected = datetime(
        2009, 6, 29, 14, 33, 21, 123456, tzinfo=timezone(timedelta(hours=2))
    )
    assert DateTime.decode(date_value) == expected


def test_datetime_decode_utc_nano():
    date_value = "2009-06-29T14:33:21.123456789Z"
    expected = datetime(2009, 6, 29, 14, 33, 21, 123456, tzinfo=timezone.utc)
    assert DateTime.decode(date_value) == expected


def test_datetime_decode_utc_00_nano():
    date_value = "2009-06-29T14:33:21.123456789+00:00"
    expected = datetime(2009, 6, 29, 14, 33, 21, 123456, tzinfo=timezone.utc)
    assert DateTime.decode(date_value) == expected


def test_datetime_decode_gmt2_nano():
    date_value = "2009-06-29T14:33:21.123456789+02:00"
    expected = datetime(
        2009, 6, 29, 14, 33, 21, 123456, tzinfo=timezone(timedelta(hours=2))
    )
    assert DateTime.decode(date_value) == expected


def test_datetime_decode_raises():
    date_value = "XXXXXX2009-06-29T14:33:21.123456789+02:00"
    with pytest.raises(ValueError):
        DateTime.decode(date_value)


def test_date_decode():
    date_value = "1999-12-25"
    expected = date(1999, 12, 25)
    assert Date.decode(date_value) == expected


def test_date_encode_1():
    date_value = date(1999, 12, 25)
    expected = "1999-12-25"
    assert Date.encode(date_value) == expected


def test_date_encode_2():
    date_value = datetime(1999, 12, 25, 0, 0, 0)
    expected = "1999-12-25"
    assert Date.encode(date_value) == expected


def test_duration_encode():
    duration = timedelta(0, 53, 0, 0, 6)
    expected = "PT00H06M53S"
    assert Duration.encode(duration) == expected


def test_duration_encode_raises():
    duration = []
    with pytest.raises(TypeError):
        Duration.encode(duration)


def test_duration_encode_neg():
    duration = timedelta(hours=-2)
    expected = "-PT02H00M00S"
    assert Duration.encode(duration) == expected


def test_duration_decode():
    duration = "PT12H34M56S"
    expected = timedelta(0, 56, 0, 0, 34, 12)
    assert Duration.decode(duration) == expected


def test_duration_decode_neg():
    duration = "-PT02H00M00S"
    expected = timedelta(hours=-2)
    assert Duration.decode(duration) == expected


def test_duration_decode_days():
    duration = "PT01D02H00M00S"
    expected = timedelta(days=1, hours=2)
    assert Duration.decode(duration) == expected


def test_duration_decode_raises_1():
    duration = "PT02H00M42"
    with pytest.raises(ValueError):
        Duration.decode(duration)


def test_duration_decode_raises_2():
    duration = "x-PT02H00M00S"
    with pytest.raises(ValueError):
        Duration.decode(duration)


def test_bool_encode():
    assert Boolean.encode(True) == "true"
    assert Boolean.encode(False) == "false"
    assert Boolean.encode("true") == "true"
    assert Boolean.encode("false") == "false"


def test_bool_bad_encode_on():
    with pytest.raises(TypeError):
        Boolean.encode("on")


def test_bool_encode_bytes():
    assert Boolean.encode(b"True") == "true"


def test_bool_no_more_bad_encode_one():
    assert Boolean.encode(1) == "true"


def test_bool_no_more_bad_encode_float():
    assert Boolean.encode(1.2) == "true"


def test_bool_no_more_bad_encode_decimal():
    assert Boolean.encode(Decimal("2.0")) == "true"


def test_bool_no_more_bad_encode_zero():
    assert Boolean.encode(0) == "false"


def test_bool_decode():
    assert Boolean.decode("true") is True
    assert Boolean.decode("false") is False


def test_bool_decode_idem():
    assert Boolean.decode(True) is True
    assert Boolean.decode(False) is False


def test_bool_decode_none():
    assert Boolean.decode(None) is False


def test_bool_bad_decode_true():
    with pytest.raises(ValueError):
        Boolean.decode("True")


def test_bool_bad_decode_other_type():
    with pytest.raises(ValueError):
        Boolean.decode([])


def test_bool_bad_encode_pne():
    with pytest.raises(ValueError):
        Boolean.decode("1")


def test_str_unit_compatibility():
    unit = Unit("1.847mm")
    assert unit.value == Decimal("1.847")
    assert unit.unit == "mm"


def test_decode_heuristic_date():
    assert decode_heuristic("2016-08-15") == date(2016, 8, 15)
    assert DateDecoder.decode_heuristic("2016-08-15") == date(2016, 8, 15)
    assert Date.decode_heuristic("2016-08-15") == date(2016, 8, 15)


def test_decode_heuristic_datetime():
    expected = datetime(2016, 8, 15, 15, 30, 0)
    assert decode_heuristic("2016-08-15T15:30:00") == expected
    assert decode_heuristic("2016-08-15 15:30:00") == expected
    assert DateTime.decode_heuristic("2016-08-15T15:30:00") == expected


def test_decode_heuristic_datetime_utc():
    expected = datetime(2016, 8, 15, 15, 30, 0, tzinfo=timezone.utc)
    assert decode_heuristic("2016-08-15T15:30:00Z") == expected


def test_decode_heuristic_duration():
    expected = timedelta(minutes=5, seconds=30)
    assert decode_heuristic("PT00H05M30S") == expected
    assert Duration.decode_heuristic("PT00H05M30S") == expected
    assert decode_heuristic("-PT02H00M00S") == timedelta(hours=-2)


def test_decode_heuristic_bytes():
    assert decode_heuristic(b"2016-08-15") == date(2016, 8, 15)


def test_decode_heuristic_already_decoded():
    d = date(2016, 8, 15)
    dt = datetime(2016, 8, 15, 15, 30)
    td = timedelta(hours=3)
    assert decode_heuristic(d) == d
    assert decode_heuristic(dt) == dt
    assert decode_heuristic(td) == td


def test_decode_heuristic_passthrough():
    assert decode_heuristic("not-a-date") == "not-a-date"
    assert decode_heuristic(123) == 123
    assert decode_heuristic(None) is None
    assert decode_heuristic(True) is True
    assert decode_heuristic("") == ""
    assert decode_heuristic("   ") == "   "
    assert decode_heuristic(b"\xff") == b"\xff"
    assert decode_heuristic("invalid_string_xxx") == "invalid_string_xxx"
    assert decode_heuristic("T_invalid") == "T_invalid"
