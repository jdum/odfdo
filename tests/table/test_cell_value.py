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

import math
from datetime import date, datetime, timedelta
from decimal import Decimal as dec

import pytest

from odfdo.cell import Cell
from odfdo.document import Document
from odfdo.element import Element
from odfdo.row import Row
from odfdo.table import Table


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
        "<text:p>2009-06-30T00:00:00</text:p>"
        "</table:table-cell>"
    )
    assert cell._canonicalize() == expected


def test_value_property_set_date():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    cell.value = date(2009, 6, 30)
    # return alwais a datetime as value
    assert cell.value == date(2009, 6, 30)
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
        "<text:p>2009-06-30</text:p>"
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


def test_value_property_set_text_content():
    cell = Cell(datetime(2009, 6, 30), style="hop")
    cell.clear_attrinutes()
    cell.set_text_content(None)
    expected = (
        '<table:table-cell table:style-name="hop"><text:p></text:p></table:table-cell>'
    )
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
        "<text:p>3</text:p>"
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
        "<text:p>Le changement</text:p>"
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
        "<text:p>changed</text:p>"
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
        "<text:p>3.14</text:p>"
        "</table:table-cell>"
    )
    assert cell._canonicalize() == expected


def test_decimal_value_property_5():
    cell = Cell(0.0, cell_type="currency", currency="EUR")
    cell.decimal = 3.14
    assert cell.float == 3.14
    assert cell.value == dec("3.14")
    assert cell.decimal == dec("3.14")
    assert cell.int == 3
    assert cell.bool is True


def test_int_value_property():
    cell = Cell(0, cell_type="float")
    assert cell.float == 0.0
    assert cell.value == 0
    assert cell.int == 0
    assert cell.bool is False


def test_int_value_property_2():
    cell = Cell(0, cell_type="float")
    cell.value = 4
    assert cell.float == 4.0
    assert cell.value == 4
    assert cell.int == 4
    assert cell.bool is True


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
        "<text:p>12</text:p>"
        "</table:table-cell>"
    )
    assert cell._canonicalize() == expected


def test_float_property_2():
    cell = Cell(1.54, cell_type="currency", currency="EUR")
    cell.float = 12
    expected = (
        '<table:table-cell office:value="12.0" '
        'office:value-type="float">'
        "<text:p>12.0</text:p>"
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
        "<text:p>12.0</text:p>"
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
        "<text:p>true</text:p>"
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


def test_value_property_nan():
    cell = Cell(float("nan"), cell_type="float")
    assert math.isnan(cell.value)
    cell.value = float("nan")
    assert math.isnan(cell.value)


def test_value_property_inf():
    cell = Cell(float("inf"), cell_type="float")
    assert cell.value == float("inf")
    cell.value = float("inf")
    assert cell.value == float("inf")


def test_value_property_minus_inf():
    cell = Cell(float("-inf"), cell_type="float")
    assert cell.value == float("-inf")
    cell.value = float("-inf")
    assert cell.value == float("-inf")


def test_value_property_decimal_nan():
    cell_nan = Cell(dec("nan"), cell_type="float")
    assert math.isnan(cell_nan.value)


def test_value_property_decimal_inf():
    cell_inf = Cell(dec("inf"), cell_type="float")
    assert cell_inf.value == float("inf")


def test_value_property_decimal_minus_inf():
    cell_minf = Cell(dec("-inf"), cell_type="float")
    assert cell_minf.value == float("-inf")


def test_cell_xml_attributes_nan():
    cell = Cell()
    cell.set_attribute("office:value-type", "float")
    for variant in ("NaN", "nan", "NAN"):
        cell.set_attribute("office:value", variant)
        assert math.isnan(cell.value)


def test_cell_xml_attributes_inf():
    cell = Cell()
    cell.set_attribute("office:value-type", "float")
    for variant in (
        "INF",
        "+INF",
        "inf",
        "+inf",
        "Infinity",
        "+Infinity",
        "infinity",
        "+infinity",
    ):
        cell.set_attribute("office:value", variant)
        assert cell.value == float("inf")


def test_cell_xml_attributes_minf():
    cell = Cell()
    cell.set_attribute("office:value-type", "float")
    for variant in ("-INF", "-inf", "-Infinity", "-infinity"):
        cell.set_attribute("office:value", variant)
        assert cell.value == float("-inf")


def test_cell_value_setter_nan_float():
    cell = Cell()
    cell.value = float("nan")
    assert math.isnan(cell.value)
    assert cell.get_attribute("office:value") == "NaN"


def test_cell_value_setter_inf_float():
    cell = Cell()
    cell.value = float("inf")
    assert cell.value == float("inf")
    assert cell.get_attribute("office:value") == "INF"


def test_cell_value_setter_minf_float():
    cell = Cell()
    cell.value = float("-inf")
    assert cell.value == float("-inf")
    assert cell.get_attribute("office:value") == "-INF"


def test_cell_float_setter_string_variants_inf():
    cell = Cell()
    cell.float = "infinity"
    assert cell.value == float("inf")
    assert cell.get_attribute("office:value") == "INF"


def test_cell_float_setter_string_variants_minf():
    cell = Cell()
    cell.float = "-infinity"
    assert cell.value == float("-inf")
    assert cell.get_attribute("office:value") == "-INF"


def test_cell_float_setter_string_variants_nan():
    cell = Cell()
    cell.float = "nan"
    assert math.isnan(cell.value)
    assert cell.get_attribute("office:value") == "NaN"


def test_cell_float_setter_string_pi():
    cell = Cell()
    cell.float = "3.14"
    assert cell.value == dec("3.14")
    assert cell.get_attribute("office:value") == "3.14"


def test_cell_decimal_setter_nan_variants():
    cell = Cell()
    for val in ("nan", "NaN", float("nan"), dec("nan")):
        cell.decimal = val
        assert math.isnan(cell.float)
        assert cell.get_attribute("office:value") == "NaN"


def test_cell_decimal_setter_inf_variants():
    cell = Cell()
    for val in ("inf", "INF", "infinity", "Infinity", float("inf"), dec("inf")):
        cell.decimal = val
        assert cell.float == float("inf")
        assert cell.get_attribute("office:value") == "INF"


def test_cell_decimal_setter_minf_variants():
    cell = Cell()
    for val in ("-inf", "-INF", "-infinity", "-Infinity", float("-inf"), dec("-inf")):
        cell.decimal = val
        assert cell.float == float("-inf")
        assert cell.get_attribute("office:value") == "-INF"


def test_cell_decimal_getter_nan():
    cell = Cell()
    cell.set_attribute("office:value-type", "float")
    cell.set_attribute("office:value", "NaN")
    assert cell.decimal.is_nan()


def test_cell_decimal_getter_inf():
    cell = Cell()
    cell.set_attribute("office:value", "INF")
    assert cell.decimal.is_infinite() and cell.decimal > 0


def test_cell_decimal_getter_minf():
    cell = Cell()
    cell.set_attribute("office:value", "-INF")
    assert cell.decimal.is_infinite() and cell.decimal < 0


def test_cell_float_getter_from_string_value():
    cell = Cell()
    cell.set_attribute("office:string-value", "12.34")
    assert cell.float == 12.34
    assert cell.decimal == dec("12.34")


def test_cell_decimal_setter_negative_infinity():
    cell = Cell()
    cell.decimal = float("-inf")
    assert cell.float == float("-inf")
    assert cell.get_attribute("office:value") == "-INF"


def test_cell_value_date_with_time():
    cell = Cell()
    cell.set_attribute("office:value-type", "date")
    cell.set_attribute("office:date-value", "2023-01-01T12:34:56")
    assert cell.value == datetime(2023, 1, 1, 12, 34, 56)


def test_cell_value_float_missing_office_value():
    cell = Cell()
    cell.set_attribute("office:value-type", "float")
    assert cell.value is None


def test_cell_value_float_invalid_office_value():
    cell = Cell()
    cell.set_attribute("office:value-type", "float")
    cell.set_attribute("office:value", "invalid-float-abc")
    assert cell.value is None


def test_cell_value_string_from_paragraphs():
    cell = Cell()
    cell.set_attribute("office:value-type", "string")
    cell.append(Element.from_tag("<text:p>First Line</text:p>"))
    cell.append(Element.from_tag("<text:p>Second Line</text:p>"))
    assert cell.value == "First Line\nSecond Line"


def test_cell_repeated_setter_attached_to_row():
    row = Row()
    cell = Cell("test")
    row.append(cell)
    cell.repeated = 3
    assert cell.repeated == 3


def test_cell_is_empty_with_style():
    cell = Cell()
    cell.style = "CustomStyle"
    assert cell.is_empty(aggressive=False) is False
    assert cell.is_empty(aggressive=True) is True


def test_cell_value_nan_inf_ods_file_roundtrip(tmp_path):
    doc = Document("spreadsheet")
    table = doc.body.tables[0]

    c_nan = Cell(float("nan"))
    c_inf = Cell(float("inf"))
    c_minf = Cell(float("-inf"))

    table.set_cell((0, 0), c_nan)
    table.set_cell((1, 0), c_inf)
    table.set_cell((2, 0), c_minf)

    file_path = tmp_path / "nan_inf_roundtrip.ods"
    doc.save(file_path)

    doc_loaded = Document(file_path)
    t_loaded = doc_loaded.body.tables[0]

    cell_nan = t_loaded.get_cell((0, 0))
    cell_inf = t_loaded.get_cell((1, 0))
    cell_minf = t_loaded.get_cell((2, 0))

    # XML attribute verification (ODF standard casing)
    assert cell_nan.get_attribute("office:value-type") == "float"
    assert cell_nan.get_attribute("office:value") == "NaN"
    assert math.isnan(cell_nan.value)

    assert cell_inf.get_attribute("office:value-type") == "float"
    assert cell_inf.get_attribute("office:value") == "INF"
    assert cell_inf.value == float("inf")

    assert cell_minf.get_attribute("office:value-type") == "float"
    assert cell_minf.get_attribute("office:value") == "-INF"
    assert cell_minf.value == float("-inf")


def test_cell_is_empty_falsy_values():
    assert Cell(0).is_empty() is False
    assert Cell(0.0).is_empty() is False
    assert Cell(False).is_empty() is False
    assert Cell("").is_empty() is False
    assert Cell().is_empty() is True
    assert Cell(None).is_empty() is True


def test_table_strip_preserves_falsy_values():
    table = Table("test", width=3, height=3)
    table.set_value("A1", 1)
    table.set_value("B1", 0)
    table.set_value("C1", False)
    assert (table.height, table.width) == (3, 3)
    table.rstrip()
    assert (table.height, table.width) == (1, 3)
    assert table.get_value("B1") == 0
    assert table.get_value("C1") is False

    table2 = Table("test2", width=3, height=3)
    table2.set_value("A1", False)
    table2.set_value("B1", 0)
    table2.set_value("C1", 1)
    table2.strip()
    assert (table2.height, table2.width) == (1, 3)
    assert table2.get_value("A1") is False
    assert table2.get_value("B1") == 0
