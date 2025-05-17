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
from decimal import Decimal

from odfdo.unit import Unit


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
