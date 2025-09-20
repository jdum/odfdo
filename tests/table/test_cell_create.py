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
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>

from datetime import date, datetime, timedelta
from decimal import Decimal as dec

import pytest

from odfdo.cell import Cell


def test_bool():
    cell = Cell(True)
    expected = (
        '<table:table-cell office:value-type="boolean" '
        'calcext:value-type="boolean" '
        'office:boolean-value="true">'
        "<text:p>true</text:p>"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


def test_bool_repr():
    cell = Cell(True, text="VRAI")
    expected = (
        '<table:table-cell office:value-type="boolean" '
        'calcext:value-type="boolean" '
        'office:boolean-value="true">'
        "<text:p>VRAI</text:p>"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


def test_int():
    cell = Cell(23)
    expected = (
        '<table:table-cell office:value-type="float" '
        'calcext:value-type="float" '
        'office:value="23" calcext:value="23">'
        "<text:p>23</text:p>"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


def test_int_repr():
    cell = Cell(23, text="00023")
    expected = (
        '<table:table-cell office:value-type="float" '
        'calcext:value-type="float" '
        'office:value="23" calcext:value="23">'
        "<text:p>00023</text:p>"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


def test_float():
    cell = Cell(3.141592654)
    expected = (
        '<table:table-cell office:value-type="float" '
        'calcext:value-type="float" '
        'office:value="3.141592654" calcext:value="3.141592654">'
        "<text:p>3.141592654</text:p>"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


def test_float_repr():
    cell = Cell(3.141592654, text="3,14")
    expected = (
        '<table:table-cell office:value-type="float" '
        'calcext:value-type="float" '
        'office:value="3.141592654" calcext:value="3.141592654">'
        "<text:p>3,14</text:p>"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


def test_decimal():
    cell = Cell(dec("2.718281828"))
    expected = (
        '<table:table-cell office:value-type="float" '
        'calcext:value-type="float" '
        'office:value="2.718281828" calcext:value="2.718281828">'
        "<text:p>2.718281828</text:p>"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


def test_decimal_repr():
    cell = Cell(dec("2.718281828"), text="2,72")
    expected = (
        '<table:table-cell office:value-type="float" '
        'calcext:value-type="float" '
        'office:value="2.718281828" calcext:value="2.718281828">'
        "<text:p>2,72</text:p>"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


def test_date():
    cell = Cell(date(2009, 6, 30))
    expected = (
        '<table:table-cell office:value-type="date" '
        'calcext:value-type="date" '
        'office:date-value="2009-06-30">'
        "<text:p>2009-06-30</text:p>"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


def test_date_value():
    cell = Cell(date(2009, 6, 30))
    assert cell.value == datetime(2009, 6, 30)
    assert cell.date == date(2009, 6, 30)


def test_date_repr():
    cell = Cell(date(2009, 6, 30), text="30/6/2009")
    expected = (
        '<table:table-cell office:value-type="date" '
        'calcext:value-type="date" '
        'office:date-value="2009-06-30">'
        "<text:p>30/6/2009</text:p>"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


def test_datetime():
    cell = Cell(datetime(2009, 6, 30, 17, 33, 18))
    expected = (
        '<table:table-cell office:value-type="date" '
        'calcext:value-type="date" '
        'office:date-value="2009-06-30T17:33:18">'
        "<text:p>2009-06-30T17:33:18</text:p>"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


def test_datetime_value():
    cell = Cell(datetime(2009, 6, 30, 17, 33, 18))
    assert cell.value == datetime(2009, 6, 30, 17, 33, 18)


def test_datetime_repr():
    cell = Cell(datetime(2009, 6, 30, 17, 33, 18), text="30/6/2009 17:33")
    expected = (
        '<table:table-cell office:value-type="date" '
        'calcext:value-type="date" '
        'office:date-value="2009-06-30T17:33:18">'
        "<text:p>30/6/2009 17:33</text:p>"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


def test_str():
    cell = Cell("red")
    expected = (
        '<table:table-cell office:value-type="string" '
        'calcext:value-type="string" '
        'office:string-value="red">'
        "<text:p>red</text:p>"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


def test_str_repr():
    cell = Cell("red", text="Red")
    expected = (
        '<table:table-cell office:value-type="string" '
        'calcext:value-type="string" '
        'office:string-value="red">'
        "<text:p>Red</text:p>"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


def test_unicode():
    cell = Cell("Plato")
    expected = (
        '<table:table-cell office:value-type="string" '
        'calcext:value-type="string" '
        'office:string-value="Plato">'
        "<text:p>Plato</text:p>"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


def test_unicode_repr():
    cell = Cell("Plato", text="P.")
    expected = (
        '<table:table-cell office:value-type="string" '
        'calcext:value-type="string" '
        'office:string-value="Plato">'
        "<text:p>P.</text:p>"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


def test_timedelta():
    cell = Cell(timedelta(0, 8))
    expected = (
        '<table:table-cell office:value-type="time" '
        'calcext:value-type="time" '
        'office:time-value="PT00H00M08S">'
        "<text:p>PT00H00M08S</text:p>"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


def test_timedelta_value():
    cell = Cell(timedelta(0, 8))
    assert cell.value == timedelta(0, 8)


def test_timedelta_repr():
    cell = Cell(timedelta(0, 8), text="00:00:08")
    expected = (
        '<table:table-cell office:value-type="time" '
        'calcext:value-type="time" '
        'office:time-value="PT00H00M08S">'
        "<text:p>00:00:08</text:p>"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


def test_percentage():
    cell = Cell(90, cell_type="percentage")
    expected = (
        '<table:table-cell office:value-type="percentage" '
        'calcext:value-type="percentage" '
        'office:value="90" calcext:value="90">'
        "<text:p>9000 %</text:p>"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


def test_percentage_repr():
    cell = Cell(90, text="9000 %", cell_type="percentage")
    expected = (
        '<table:table-cell office:value-type="percentage" '
        'calcext:value-type="percentage" '
        'office:value="90" calcext:value="90">'
        "<text:p>9000 %</text:p>"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


def test_currency():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    expected = (
        '<table:table-cell office:value-type="currency" '
        'calcext:value-type="currency" '
        'office:value="1.54" office:currency="EUR">'
        "<text:p>1.54</text:p>"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


def test_currency_property():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    assert cell.currency == "EUR"
    cell.currency = "USD"
    assert cell.currency == "USD"
    cell.currency = None
    assert cell.currency is None


def test_currency_repr():
    cell = Cell(1.54, text="1,54 €", cell_type="currency", currency="EUR")
    expected = (
        '<table:table-cell office:value-type="currency" '
        'calcext:value-type="currency" '
        'office:value="1.54" office:currency="EUR">'
        "<text:p>1,54 €</text:p>"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


def test_style():
    cell = Cell(style="Monétaire")
    expected = '<table:table-cell table:style-name="Monétaire"/>'
    assert cell.serialize() == expected


def test_bad():
    with pytest.raises(TypeError):
        Cell([])


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
        '<table:table-cell office:value-type="string" '
        'office:string-value="3">3</table:table-cell>'
    )
    assert cell.serialize() == expected


def test_string_property2():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    cell.string = "Le changement"
    expected = (
        "<table:table-cell "
        'office:value-type="string" '
        'office:string-value="Le changement">'
        "Le changement"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


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


def test_float_property2():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    cell.float = 12
    expected = (
        '<table:table-cell office:value="12.0" '
        'office:value-type="float">12.0'
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


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
