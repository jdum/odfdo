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
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>

from datetime import date, datetime, timedelta
from decimal import Decimal as dec

import pytest

from odfdo.cell import Cell


def test_string_value_property():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    assert cell.string == ""
    cell.clear()
    assert cell.string == ""
    cell.string = 25
    assert cell.string == "25"
    cell.string = "hop"
    assert cell.string == "hop"
    cell.string = None
    assert cell.string == ""
    assert cell.value == ""


def test_string_value_property2_false():
    cell = Cell()
    cell.clear()
    assert cell.string == ""
    cell.string = "hop"
    assert cell.string == "hop"
    cell.string = "false"
    assert cell.string == "false"
    cell.string = "False"
    assert cell.string == "False"
    cell.string = False
    assert cell.string == "False"


def test_string_value_property2_true():
    cell = Cell()
    cell.clear()
    assert cell.string == ""
    cell.string = "hop"
    assert cell.string == "hop"
    cell.string = "true"
    assert cell.string == "true"
    cell.string = "True"
    assert cell.string == "True"
    cell.string = True
    assert cell.string == "True"


def test_string_value_property2_none():
    cell = Cell()
    cell.clear()
    assert cell.string == ""
    cell.string = "hop"
    assert cell.string == "hop"
    cell.string = "none"
    assert cell.string == "none"
    cell.string = "None"
    assert cell.string == "None"
    cell.string = None
    assert cell.string == ""


def test_string_value_property2_number():
    cell = Cell()
    cell.clear()
    assert cell.string == ""
    cell.string = "1.23"
    assert cell.string == "1.23"
    cell.string = 1.23
    assert cell.string == "1.23"


def test_value_property_set_int():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    cell.value = 1
    assert cell.value == 1


def test_value_property_set_int_2():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    cell.value = "2"
    assert cell.value == "2"


def test_value_property_set_str():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    cell.value = "hop"
    assert cell.value == "hop"


def test_value_property_set_str_2():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    cell.value = "éû"
    assert cell.value == "éû"


def test_value_property_set_float():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    cell.value = 1.5
    assert cell.value == 1.5


def test_value_property_set_timedelta():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    cell.value = timedelta(50, 10)
    assert cell.value == timedelta(50, 10)


def test_value_property_set_timedelta_getter():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    cell.value = timedelta(50, 10)
    assert cell.duration == timedelta(50, 10)


def test_value_property_timedelta_getter_empty():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    assert cell.duration == timedelta(0)


def test_value_property_set_datetime():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    cell.value = datetime(2009, 6, 30, 0, 0)
    assert cell.value == datetime(2009, 6, 30, 0, 0)


def test_value_property_set_datetime_getter():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    cell.value = datetime(2009, 6, 30, 0, 0)
    assert cell.datetime == datetime(2009, 6, 30, 0, 0)


def test_value_property_datetime_getter_empty():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    assert cell.datetime == datetime.fromtimestamp(0)


def test_value_property_datetime_set():
    cell = Cell(datetime(2009, 6, 30, 0, 0), cell_type="date")
    cell.datetime = datetime(2009, 7, 30, 0, 0)
    assert cell.datetime == datetime(2009, 7, 30, 0, 0)


def test_value_property_date_set():
    cell = Cell(date(2009, 6, 30), cell_type="date")
    cell.date = date(2009, 7, 30)
    assert cell.datetime == datetime(2009, 7, 30)


def test_value_property_set_datetime_styled():
    cell = Cell("before", cell_type="string", style="bold")
    cell.value = datetime(2009, 6, 30, 0, 0)
    assert cell.datetime == datetime(2009, 6, 30, 0, 0)
    expected = (
        "<table:table-cell "
        'office:date-value="2009-06-30T00:00:00" '
        'office:value-type="date" '
        'table:style-name="bold">'
        "2009-06-30T00:00:00"
        "</table:table-cell>"
    )
    assert cell._canonicalize() == expected


def test_value_property_set_date():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    cell.value = date(2009, 6, 30)
    # return alwais a datetime as value
    assert cell.value == datetime(2009, 6, 30)
    assert cell.date == date(2009, 6, 30)


def test_value_property_set_date_getter():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    cell.value = date(2009, 6, 30)
    assert cell.date == date(2009, 6, 30)


def test_value_property_date_getter_empty():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    # return alwais a datetime as value
    assert cell.date == date.fromtimestamp(0)


def test_value_property_set_date_styled():
    cell = Cell("before", cell_type="string", style="bold")
    cell.value = date(2009, 6, 30)
    assert cell.date == date(2009, 6, 30)
    expected = (
        "<table:table-cell "
        'office:date-value="2009-06-30" '
        'office:value-type="date" '
        'table:style-name="bold">'
        "2009-06-30"
        "</table:table-cell>"
    )
    assert cell._canonicalize() == expected


def test_value_property_bytes():
    cell = Cell()
    cell.clear()
    assert cell.string == ""
    cell.value = "éû".encode()
    assert cell.value == "éû"


def test_value_property_none():
    cell = Cell()
    cell.clear()
    assert cell.string == ""
    cell.value = None
    assert cell.value is None
    cell.value = "hop"
    assert cell.value == "hop"
    cell.value = None
    assert cell.value is None


def test_value_property_none_2():
    cell = Cell(42, style="hop")
    cell.value = None
    expected = '<table:table-cell table:style-name="hop"></table:table-cell>'
    assert cell._canonicalize() == expected


def test_value_property_none_3():
    cell = Cell("hip", style="hop")
    cell.value = None
    expected = '<table:table-cell table:style-name="hop"></table:table-cell>'
    assert cell._canonicalize() == expected


def test_value_property_none_4():
    cell = Cell(datetime(2009, 6, 30), style="hop")
    cell.value = None
    expected = '<table:table-cell table:style-name="hop"></table:table-cell>'
    assert cell._canonicalize() == expected


def test_value_property_false():
    cell = Cell()
    cell.clear()
    assert cell.string == ""
    cell.value = False
    assert cell.value is False
    cell.value = "False"
    assert cell.value == "False"
    cell.value = "false"
    assert cell.value == "false"


def test_value_property_true():
    cell = Cell()
    cell.clear()
    assert cell.string == ""
    cell.value = True
    assert cell.value is True
    cell.value = "True"
    assert cell.value == "True"
    cell.value = "true"
    assert cell.value == "true"


def test_value_property2():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    cell.value = "3"
    expected = (
        "<table:table-cell "
        'office:string-value="3" '
        'office:value-type="string">'
        "3"
        "</table:table-cell>"
    )
    assert cell._canonicalize() == expected


def test_string_property2():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    cell.string = "Le changement"
    expected = (
        "<table:table-cell "
        'office:string-value="Le changement" '
        'office:value-type="string">'
        "Le changement"
        "</table:table-cell>"
    )
    assert cell._canonicalize() == expected


def test_string_property_style():
    cell = Cell("content", cell_type="string", style="some_style")
    cell.string = "changed"
    expected = (
        "<table:table-cell "
        'office:string-value="changed" '
        'office:value-type="string" '
        'table:style-name="some_style" '
        'calcext:value-type="string">'
        "changed"
        "</table:table-cell>"
    )
    assert cell._canonicalize() == expected


def test_float_value_property():
    cell = Cell(1.50, cell_type="currency", currency="EUR")
    assert cell.float == 1.50
    assert cell.value == dec("1.50")
    cell.clear()
    assert cell.float == 0.0
    assert cell.value is None
    cell.string = 25
    assert cell.float == 25
    assert cell.value == "25"
    cell.string = "hop"
    assert cell.float == 0.0
    assert cell.value == "hop"
    cell.float = None
    assert cell.float == 0.0
    assert cell.value == dec("0.0")
    cell.float = 12
    assert cell.float == 12
    assert cell.value == dec(12)
    cell.float = -12.0
    assert cell.float == -12.0
    assert cell.value == dec("-12.0")


def test_decimal_value_property():
    cell = Cell(dec("1.50"), cell_type="currency", currency="EUR")
    assert cell.float == 1.50
    assert cell.value == dec("1.50")
    assert cell.float == 1.50
    assert cell.decimal == dec("1.50")


def test_decimal_value_property_2():
    cell = Cell(0.0, cell_type="currency", currency="EUR")
    cell.value = dec("1.56")
    assert cell.float == 1.56
    assert cell.value == dec("1.56")
    assert cell.decimal == dec("1.56")


def test_decimal_value_property_3():
    cell = Cell(0.0, cell_type="currency", currency="EUR")
    cell.decimal = "oops"
    assert cell.float == 0.0
    assert cell.value == dec("0.0")
    assert cell.decimal == dec("0.0")


def test_decimal_value_property_4():
    cell = Cell("before", cell_type="string", style="bold")
    cell.decimal = dec("3.14")
    assert cell.float == 3.14
    assert cell.value == dec("3.14")
    assert cell.decimal == dec("3.14")
    expected = (
        "<table:table-cell "
        'office:value="3.14" '
        'office:value-type="float" '
        'table:style-name="bold">'
        "3.14"
        "</table:table-cell>"
    )
    assert cell._canonicalize() == expected


def test_int_value_property():
    cell = Cell(0, cell_type="float")
    assert cell.float == 0.0
    assert cell.value == 0
    assert cell.int == 0


def test_int_value_property_2():
    cell = Cell(0, cell_type="float")
    cell.value = 4
    assert cell.float == 4.0
    assert cell.value == 4
    assert cell.int == 4


def test_int_value_property_3():
    cell = Cell(0, cell_type="float")
    cell.int = "oops"
    assert cell.float == 0.0
    assert cell.value == 0
    assert cell.int == 0


def test_int_property_4():
    cell = Cell("before", cell_type="string", style="bold")
    cell.int = 12
    expected = (
        "<table:table-cell "
        'office:value="12" '
        'office:value-type="float" '
        'table:style-name="bold">'
        "12"
        "</table:table-cell>"
    )
    assert cell._canonicalize() == expected


def test_float_property_2():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    cell.float = 12
    expected = (
        '<table:table-cell office:value="12.0" '
        'office:value-type="float">12.0'
        "</table:table-cell>"
    )
    assert cell._canonicalize() == expected


def test_float_property_3():
    cell = Cell("before", cell_type="string", style="bold")
    cell.float = 12.0
    expected = (
        "<table:table-cell "
        'office:value="12.0" '
        'office:value-type="float" '
        'table:style-name="bold">'
        "12.0"
        "</table:table-cell>"
    )
    assert cell._canonicalize() == expected


def test_bool_property():
    cell = Cell(0, cell_type="float")
    cell.bool = True
    assert cell.value is True
    assert cell.bool is True


def test_bool_property_as_numeric():
    cell = Cell(0, cell_type="float")
    cell.bool = True
    assert cell.int == 1
    assert cell.float == 1.0
    assert cell.decimal == dec("1")


def test_bool_property_2():
    cell = Cell(0, cell_type="float")
    cell.bool = False
    assert cell.value is False
    assert cell.bool is False


def test_bool_property_as_numeric_2():
    cell = Cell(0, cell_type="float")
    cell.bool = False
    assert cell.int == 0
    assert cell.float == 0.0
    assert cell.decimal == dec("0")


def test_bool_property_as_str_1():
    cell = Cell(0, cell_type="float")
    cell.bool = "True"
    assert cell.int == 1
    assert cell.float == 1.0
    assert cell.decimal == dec("1")


def test_bool_property_as_str_2():
    cell = Cell(0, cell_type="float")
    cell.bool = "true"
    assert cell.int == 1
    assert cell.float == 1.0
    assert cell.decimal == dec("1")


def test_bool_property_as_str_3():
    cell = Cell(0, cell_type="float")
    cell.bool = "False"
    assert cell.int == 0
    assert cell.float == 0.0
    assert cell.decimal == dec("0")


def test_bool_property_as_str_4():
    cell = Cell(0, cell_type="float")
    cell.bool = "false"
    assert cell.int == 0
    assert cell.float == 0.0
    assert cell.decimal == dec("0")


def test_bool_property_as_str_5():
    cell = Cell(0, cell_type="float")
    with pytest.raises(TypeError):
        cell.bool = "oops"


def test_bool_property_as_bytes_1():
    cell = Cell(0, cell_type="float")
    cell.bool = b"True"
    assert cell.int == 1
    assert cell.float == 1.0
    assert cell.decimal == dec("1")


def test_bool_property_as_bytes_2():
    cell = Cell(0, cell_type="float")
    cell.bool = b"true"
    assert cell.int == 1
    assert cell.float == 1.0
    assert cell.decimal == dec("1")


def test_bool_property_as_bytes_3():
    cell = Cell(0, cell_type="float")
    cell.bool = b"False"
    assert cell.int == 0
    assert cell.float == 0.0
    assert cell.decimal == dec("0")


def test_bool_property_as_bytes_4():
    cell = Cell(0, cell_type="float")
    cell.bool = b"false"
    assert cell.int == 0
    assert cell.float == 0.0
    assert cell.decimal == dec("0")


def test_bool_property_as_bytes_5():
    cell = Cell(0, cell_type="float")
    with pytest.raises(TypeError):
        cell.bool = b"oops"


def test_bool_property_as_object_1():
    cell = Cell(0, cell_type="float")
    cell.bool = []
    assert cell.bool is False
    assert cell.int == 0
    assert cell.float == 0.0
    assert cell.decimal == dec("0")


def test_bool_property_as_object_2():
    cell = Cell(0, cell_type="float")
    cell.bool = [1, 2, 3]
    assert cell.bool is True
    assert cell.int == 1
    assert cell.float == 1.0
    assert cell.decimal == dec("1")


def test_bool_property_as_bool():
    cell = Cell(0, cell_type="boolean")
    cell.bool = True
    assert cell.bool is True
    assert cell.int == 1
    assert cell.float == 1.0
    assert cell.decimal == dec("1")


def test_bool_property_text_set():
    cell = Cell(0, cell_type="boolean")
    result_text = cell.set_value_and_type(2, value_type="boolean", text="TRUE")
    assert cell.bool is True
    assert cell.int == 1
    assert cell.float == 1.0
    assert cell.decimal == dec("1")
    assert result_text == "TRUE"


def test_bool_property_style():
    cell = Cell("before", cell_type="string", style="bold")
    cell.value = True
    assert cell.bool is True

    expected = (
        "<table:table-cell "
        'office:boolean-value="true" '
        'office:value-type="boolean" '
        'table:style-name="bold">'
        "true"
        "</table:table-cell>"
    )
    assert cell._canonicalize() == expected


def test_decimal_property():
    cell = Cell(0, cell_type="float")
    cell.decimal = dec("1.43")
    assert cell.value == dec("1.43")
    assert cell.int == 1
    assert cell.float == 1.43
    assert cell.decimal == dec("1.43")


def test_float_property():
    cell = Cell(0, cell_type="float")
    cell.float = dec("1.43")
    assert cell.value == dec("1.43")
    assert cell.int == 1
    assert cell.float == 1.43
    assert cell.decimal == dec("1.43")


def test_int_property():
    cell = Cell(0, cell_type="float")
    cell.int = 5
    assert cell.value == 5
    assert cell.int == 5
    assert cell.float == 5.0
    assert cell.decimal == dec("5")


def test_int_property_bool_true():
    cell = Cell(0, cell_type="float")
    cell.int = 1
    assert cell.bool is True


def test_int_property_bool_false():
    cell = Cell(0, cell_type="float")
    cell.int = 0
    assert cell.bool is False


def test_bad_value():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    with pytest.raises(TypeError):
        cell.value = []
