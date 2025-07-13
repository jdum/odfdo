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

import pytest

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


def test_no_nondigit():
    unit = Unit("2.54")
    assert unit.unit == "cm"


def test_no_nondigit_2():
    unit = Unit("12", "mm")
    assert unit.unit == "mm"


def test_wrong_cmp_unit_1():
    unit = Unit("12", "mm")
    unit2 = ["wrong"]
    assert unit != unit2


def test_wrong_cmp_unit_2():
    unit = Unit("12", "mm")
    unit2 = ["wrong"]
    with pytest.raises(TypeError):
        unit._check_other(unit2)


def test_wrong_cmp_unit_3():
    unit = Unit("12", "mm")
    unit2 = Unit("12", "km")
    with pytest.raises(NotImplementedError):
        unit._check_other(unit2)


def test_wrong_unit_convert():
    unit = Unit("12", "cm")
    with pytest.raises(NotImplementedError):
        unit.convert("km")


def test_wrong_unit_convert_2():
    unit = Unit("12", "micron")
    with pytest.raises(NotImplementedError):
        unit.convert("px")


def test_convert_1():
    unit = Unit("10", "in")
    converted = unit.convert("px")
    assert converted.value == 720


def test_convert_2():
    unit = Unit("10", "inch")
    converted = unit.convert("px")
    assert converted.value == 720


def test_convert_3():
    unit = Unit("254", "cm")
    converted = unit.convert("px")
    assert converted.value == 7200


def test_convert_4():
    unit = Unit("254", "mm")
    converted = unit.convert("px")
    assert converted.value == 720


def test_convert_5():
    unit = Unit("254", "m")
    converted = unit.convert("px")
    assert converted.value == 720000


def test_convert_6():
    unit = Unit("254", "km")
    converted = unit.convert("px")
    assert converted.value == 720000000


def test_convert_7():
    unit = Unit("72", "pt")
    converted = unit.convert("px")
    assert converted.value == 72


def test_convert_8():
    unit = Unit("1", "pc")
    converted = unit.convert("px")
    assert converted.value == 12


def test_convert_9():
    unit = Unit("1", "ft")
    converted = unit.convert("px")
    assert converted.value == 864


def test_convert_10():
    unit = Unit("1", "mi")
    converted = unit.convert("px")
    assert converted.value == 4561920
