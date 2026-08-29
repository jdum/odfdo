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

from datetime import timedelta

import pytest

from odfdo.table import _decode_time_string


def test_decode_time_string_valid_hh_mm_ss():
    assert _decode_time_string("12:34:56") == timedelta(
        hours=12, minutes=34, seconds=56
    )
    assert _decode_time_string("00:00:00") == timedelta(seconds=0)
    assert _decode_time_string("23:59:59") == timedelta(
        hours=23, minutes=59, seconds=59
    )
    assert _decode_time_string("05:10:15.5") == timedelta(
        hours=5, minutes=10, seconds=15.5
    )


def test_decode_time_string_valid_hh_mm():
    assert _decode_time_string("14:30") == timedelta(hours=14, minutes=30)
    assert _decode_time_string("00:00") == timedelta(0)
    assert _decode_time_string(" 08:15 ") == timedelta(hours=8, minutes=15)


def test_decode_time_string_invalid_hours():
    with pytest.raises(ValueError):
        _decode_time_string("24:00")
    with pytest.raises(ValueError):
        _decode_time_string("-1:30")
    with pytest.raises(ValueError):
        _decode_time_string("25:10:00")


def test_decode_time_string_invalid_minutes():
    with pytest.raises(ValueError):
        _decode_time_string("10:60")
    with pytest.raises(ValueError):
        _decode_time_string("10:-1")
    with pytest.raises(ValueError):
        _decode_time_string("12:60:00")


def test_decode_time_string_invalid_seconds():
    with pytest.raises(ValueError):
        _decode_time_string("10:20:60")
    with pytest.raises(ValueError):
        _decode_time_string("10:20:-1")
    with pytest.raises(ValueError):
        _decode_time_string("10:20:60.1")


def test_decode_time_string_invalid_parts():
    with pytest.raises(ValueError, match="Invalid time string"):
        _decode_time_string("")
    with pytest.raises(ValueError, match="Invalid time string"):
        _decode_time_string("12")
    with pytest.raises(ValueError, match="Invalid time string"):
        _decode_time_string("10:20:30:40")


def test_decode_time_string_invalid_non_numeric():
    with pytest.raises(ValueError):
        _decode_time_string("ab:cd")
    with pytest.raises(ValueError):
        _decode_time_string("10:xx:00")
