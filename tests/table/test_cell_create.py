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


def test_timedelta_style():
    cell = Cell("before", cell_type="time", style="bold")
    duration = timedelta(days=0, hours=2, minutes=15)
    cell.value = duration
    expected = (
        "<table:table-cell "
        'office:time-value="PT02H15M00S" '
        'office:value-type="time" '
        'table:style-name="bold" '
        'calcext:value-type="time">'
        "PT02H15M00S"
        "</table:table-cell>"
    )
    assert cell._canonicalize() == expected


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
