#!/usr/bin/env python
# Copyright 2018 Jérôme Dumonteil
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
from io import StringIO
from unittest import TestCase, main

from odfdo.document import Document
from odfdo.table import _alpha_to_digit, _digit_to_alpha
from odfdo.table import _convert_coordinates
from odfdo.table import Cell, Row, Column, Table, NamedRange
from odfdo.table import import_from_csv

csv_data = '"A float","3.14"\n"A date","1975-05-07"\n'


class TestCoordinates(TestCase):
    def test_digit_to_alpha_to_digit(self):
        for i in range(1024):
            self.assertEqual(_alpha_to_digit(_digit_to_alpha(i)), i)

    def test_alpha_to_digit_digit(self):
        self.assertEqual(_alpha_to_digit(730), 730)

    def test_alpha_to_digit_digit_alphanum(self):
        self.assertRaises(ValueError, _alpha_to_digit, "730")

    def test_digit_to_alpha_digit(self):
        self.assertEqual(_digit_to_alpha("ABC"), "ABC")

    def test_digit_to_alpha_alphanum(self):
        self.assertRaises(ValueError, _digit_to_alpha, "730")

    def test_convert_coordinates_tuple(self):
        x1, y1 = (12, 34)
        x2, y2 = _convert_coordinates((x1, y1))
        self.assertEqual((x1, y1), (x2, y2))

    def test_convert_coordinates_tuple4(self):
        coord = (12, 34, 15, 60)
        converted = _convert_coordinates(coord)
        self.assertEqual(converted, coord)

    def test_convert_coordinates_alphanum(self):
        x, y = _convert_coordinates("ABC123")
        self.assertEqual((x, y), (730, 122))

    def test_convert_coordinates_alphanum4(self):
        converted = _convert_coordinates("F7:ABC123")
        self.assertEqual(converted, (5, 6, 730, 122))

    def test_convert_coordinates_alphanum4_2(self):
        converted = _convert_coordinates("f7:ABc123")
        self.assertEqual(converted, (5, 6, 730, 122))

    def test_convert_coordinates_alphanum4_3(self):
        converted = _convert_coordinates("f7 : ABc 123 ")
        self.assertEqual(converted, (5, 6, 730, 122))

    def test_convert_coordinates_alphanum4_4(self):
        converted = _convert_coordinates("ABC 123: F7 ")
        self.assertEqual(converted, (730, 122, 5, 6))

    def test_convert_coordinates_bad(self):
        self.assertRaises(ValueError, _convert_coordinates, None)
        self.assertEqual(_convert_coordinates((None,)), (None,))
        self.assertEqual(_convert_coordinates((None, None)), (None, None))
        self.assertEqual(_convert_coordinates((1, "bad")), (1, "bad"))

    def test_convert_coordinates_bad_string(self):
        self.assertEqual(_convert_coordinates("2B"), (None, None))
        self.assertEqual(_convert_coordinates("$$$"), (None, None))
        self.assertEqual(_convert_coordinates(""), (None, None))

    def test_convert_coordinates_std(self):
        self.assertEqual(_convert_coordinates("A1"), (0, 0))
        self.assertEqual(_convert_coordinates(" a 1 "), (0, 0))
        self.assertEqual(_convert_coordinates(" aa 1 "), (26, 0))

    def test_convert_coordinates_assert(self):
        self.assertRaises(ValueError, _convert_coordinates, "A0")
        self.assertRaises(ValueError, _convert_coordinates, "A-5")

    def test_convert_coordinates_big(self):
        self.assertEqual(_convert_coordinates("AAA200001"), (26 * 26 + 26, 200000))

    def test_convert_coordinates_partial(self):
        self.assertEqual(_convert_coordinates("B"), (1, None))
        self.assertEqual(_convert_coordinates("2"), (None, 1))

    def test_convert_coordinates_partial_4(self):
        self.assertEqual(_convert_coordinates("B3:D5"), (1, 2, 3, 4))
        self.assertEqual(_convert_coordinates("B3:"), (1, 2, None, None))
        self.assertEqual(_convert_coordinates(" B  3  :  "), (1, 2, None, None))
        self.assertEqual(_convert_coordinates(":D5"), (None, None, 3, 4))
        self.assertEqual(_convert_coordinates("  :  D 5  "), (None, None, 3, 4))
        self.assertEqual(_convert_coordinates("C:D"), (2, None, 3, None))
        self.assertEqual(_convert_coordinates(" : D "), (None, None, 3, None))
        self.assertEqual(_convert_coordinates(" C :  "), (2, None, None, None))
        self.assertEqual(_convert_coordinates("2 : 3 "), (None, 1, None, 2))
        self.assertEqual(_convert_coordinates("2 :  "), (None, 1, None, None))
        self.assertEqual(_convert_coordinates(" :3  "), (None, None, None, 2))
        self.assertEqual(_convert_coordinates(" :  "), (None, None, None, None))

    def test_convert_coordinates_partial_bad_4(self):
        self.assertEqual(_convert_coordinates(" : $$$ "), (None, None, None, None))
        self.assertEqual(_convert_coordinates(" B 3: $$$ "), (1, 2, None, None))


class TestCreateCell(TestCase):
    def test_bool(self):
        cell = Cell(True)
        expected = (
            '<table:table-cell office:value-type="boolean" '
            'calcext:value-type="boolean" '
            'office:boolean-value="true">'
            "<text:p>true</text:p>"
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)

    def test_bool_repr(self):
        cell = Cell(True, text="VRAI")
        expected = (
            '<table:table-cell office:value-type="boolean" '
            'calcext:value-type="boolean" '
            'office:boolean-value="true">'
            "<text:p>VRAI</text:p>"
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)

    def test_int(self):
        cell = Cell(23)
        expected = (
            '<table:table-cell office:value-type="float" '
            'calcext:value-type="float" '
            'office:value="23" calcext:value="23">'
            "<text:p>23</text:p>"
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)

    def test_int_repr(self):
        cell = Cell(23, text="00023")
        expected = (
            '<table:table-cell office:value-type="float" '
            'calcext:value-type="float" '
            'office:value="23" calcext:value="23">'
            "<text:p>00023</text:p>"
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)

    def test_float(self):
        cell = Cell(3.141592654)
        expected = (
            '<table:table-cell office:value-type="float" '
            'calcext:value-type="float" '
            'office:value="3.141592654" calcext:value="3.141592654">'
            "<text:p>3.141592654</text:p>"
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)

    def test_float_repr(self):
        cell = Cell(3.141592654, text="3,14")
        expected = (
            '<table:table-cell office:value-type="float" '
            'calcext:value-type="float" '
            'office:value="3.141592654" calcext:value="3.141592654">'
            "<text:p>3,14</text:p>"
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)

    def test_decimal(self):
        cell = Cell(dec("2.718281828"))
        expected = (
            '<table:table-cell office:value-type="float" '
            'calcext:value-type="float" '
            'office:value="2.718281828" calcext:value="2.718281828">'
            "<text:p>2.718281828</text:p>"
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)

    def test_decimal_repr(self):
        cell = Cell(dec("2.718281828"), text="2,72")
        expected = (
            '<table:table-cell office:value-type="float" '
            'calcext:value-type="float" '
            'office:value="2.718281828" calcext:value="2.718281828">'
            "<text:p>2,72</text:p>"
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)

    def test_date(self):
        cell = Cell(date(2009, 6, 30))
        expected = (
            '<table:table-cell office:value-type="date" '
            'calcext:value-type="date" '
            'office:date-value="2009-06-30">'
            "<text:p>2009-06-30</text:p>"
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)

    def test_date_repr(self):
        cell = Cell(date(2009, 6, 30), text="30/6/2009")
        expected = (
            '<table:table-cell office:value-type="date" '
            'calcext:value-type="date" '
            'office:date-value="2009-06-30">'
            "<text:p>30/6/2009</text:p>"
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)

    def test_datetime(self):
        cell = Cell(datetime(2009, 6, 30, 17, 33, 18))
        expected = (
            '<table:table-cell office:value-type="date" '
            'calcext:value-type="date" '
            'office:date-value="2009-06-30T17:33:18">'
            "<text:p>2009-06-30T17:33:18</text:p>"
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)

    def test_datetime_repr(self):
        cell = Cell(datetime(2009, 6, 30, 17, 33, 18), text="30/6/2009 17:33")
        expected = (
            '<table:table-cell office:value-type="date" '
            'calcext:value-type="date" '
            'office:date-value="2009-06-30T17:33:18">'
            "<text:p>30/6/2009 17:33</text:p>"
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)

    def test_str(self):
        cell = Cell("red")
        expected = (
            '<table:table-cell office:value-type="string" '
            'calcext:value-type="string" '
            'office:string-value="red">'
            "<text:p>red</text:p>"
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)

    def test_str_repr(self):
        cell = Cell("red", text="Red")
        expected = (
            '<table:table-cell office:value-type="string" '
            'calcext:value-type="string" '
            'office:string-value="red">'
            "<text:p>Red</text:p>"
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)

    def test_unicode(self):
        cell = Cell("Plato")
        expected = (
            '<table:table-cell office:value-type="string" '
            'calcext:value-type="string" '
            'office:string-value="Plato">'
            "<text:p>Plato</text:p>"
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)

    def test_unicode_repr(self):
        cell = Cell("Plato", text="P.")
        expected = (
            '<table:table-cell office:value-type="string" '
            'calcext:value-type="string" '
            'office:string-value="Plato">'
            "<text:p>P.</text:p>"
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)

    def test_timedelta(self):
        cell = Cell(timedelta(0, 8))
        expected = (
            '<table:table-cell office:value-type="time" '
            'calcext:value-type="time" '
            'office:time-value="PT00H00M08S">'
            "<text:p>PT00H00M08S</text:p>"
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)

    def test_timedelta_repr(self):
        cell = Cell(timedelta(0, 8), text="00:00:08")
        expected = (
            '<table:table-cell office:value-type="time" '
            'calcext:value-type="time" '
            'office:time-value="PT00H00M08S">'
            "<text:p>00:00:08</text:p>"
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)

    def test_percentage(self):
        cell = Cell(90, cell_type="percentage")
        expected = (
            '<table:table-cell office:value-type="percentage" '
            'calcext:value-type="percentage" '
            'office:value="90" calcext:value="90">'
            "<text:p>9000 %</text:p>"
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)

    def test_percentage_repr(self):
        cell = Cell(90, text="9000 %", cell_type="percentage")
        expected = (
            '<table:table-cell office:value-type="percentage" '
            'calcext:value-type="percentage" '
            'office:value="90" calcext:value="90">'
            "<text:p>9000 %</text:p>"
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)

    def test_currency(self):
        cell = Cell(1.54, cell_type="currency", currency="EUR")
        expected = (
            '<table:table-cell office:value-type="currency" '
            'calcext:value-type="currency" '
            'office:value="1.54" office:currency="EUR">'
            "<text:p>1.54</text:p>"
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)

    def test_currency_property(self):
        cell = Cell(1.54, cell_type="currency", currency="EUR")
        self.assertEqual(cell.currency, "EUR")
        cell.currency = "USD"
        self.assertEqual(cell.currency, "USD")
        cell.currency = None
        self.assertEqual(cell.currency, None)

    def test_currency_repr(self):
        cell = Cell(1.54, text="1,54 €", cell_type="currency", currency="EUR")
        expected = (
            '<table:table-cell office:value-type="currency" '
            'calcext:value-type="currency" '
            'office:value="1.54" office:currency="EUR">'
            "<text:p>1,54 €</text:p>"
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)

    def test_style(self):
        cell = Cell(style="Monétaire")
        expected = '<table:table-cell table:style-name="Monétaire"/>'
        self.assertEqual(cell.serialize(), expected)

    def test_bad(self):
        self.assertRaises(TypeError, Cell, [])

    def test_string_value_property(self):
        cell = Cell(1.54, cell_type="currency", currency="EUR")
        self.assertEqual(cell.string, "")
        cell.clear()
        self.assertEqual(cell.string, "")
        cell.string = 25
        self.assertEqual(cell.string, "25")
        cell.string = "hop"
        self.assertEqual(cell.string, "hop")
        cell.string = None
        self.assertEqual(cell.string, "")
        self.assertEqual(cell.value, "")

    def test_value_property(self):
        cell = Cell(1.54, cell_type="currency", currency="EUR")
        cell.value = 1
        self.assertEqual(cell.value, 1)
        cell.value = "2"
        self.assertEqual(cell.value, "2")
        cell.value = "false"
        self.assertEqual(cell.value, False)
        cell.value = True
        self.assertEqual(cell.value, True)

    def test_value_property2(self):
        cell = Cell(1.54, cell_type="currency", currency="EUR")
        cell.value = "3"
        expected = (
            '<table:table-cell office:value-type="string" '
            'office:string-value="3">3</table:table-cell>'
        )
        self.assertEqual(cell.serialize(), expected)

    def test_string_property2(self):
        cell = Cell(1.54, cell_type="currency", currency="EUR")
        cell.string = "Le changement"
        expected = (
            "<table:table-cell "
            'office:value-type="string" '
            'office:string-value="Le changement">'
            "Le changement"
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)

    def test_float_value_property(self):
        cell = Cell(1.50, cell_type="currency", currency="EUR")
        self.assertEqual(cell.float, 1.50)
        self.assertEqual(cell.value, dec(1.50))
        cell.clear()
        self.assertEqual(cell.float, 0.0)
        self.assertEqual(cell.value, None)
        cell.string = 25
        self.assertEqual(cell.float, 25)
        self.assertEqual(cell.value, "25")
        cell.string = "hop"
        self.assertEqual(cell.float, 0.0)
        self.assertEqual(cell.value, "hop")
        cell.float = None
        self.assertEqual(cell.float, 0.0)
        self.assertEqual(cell.value, dec(0.0))
        cell.float = 12
        self.assertEqual(cell.float, 12)
        self.assertEqual(cell.value, dec(12))
        cell.float = -12.0
        self.assertEqual(cell.float, -12.0)
        self.assertEqual(cell.value, dec(-12.0))

    def test_float_property2(self):
        cell = Cell(1.54, cell_type="currency", currency="EUR")
        cell.float = 12
        expected = (
            '<table:table-cell office:value="12.0" '
            'office:value-type="float">12.0'
            "</table:table-cell>"
        )
        self.assertEqual(cell.serialize(), expected)


class TestCreateRow(TestCase):
    def test_default(self):
        row = Row()
        expected = "<table:table-row/>"
        self.assertEqual(row.serialize(), expected)

    def test_width(self):
        row = Row(1)
        expected = "<table:table-row><table:table-cell/></table:table-row>"
        self.assertEqual(row.serialize(), expected)

    def test_repeated(self):
        row = Row(repeated=3)
        expected = '<table:table-row table:number-rows-repeated="3"/>'
        self.assertEqual(row.serialize(), expected)

    def test_style(self):
        row = Row(style="ro1")
        expected = '<table:table-row table:style-name="ro1"/>'
        self.assertEqual(row.serialize(), expected)

    def test_all(self):
        row = Row(1, repeated=3, style="ro1")
        expected = (
            '<table:table-row table:number-rows-repeated="3" '
            'table:style-name="ro1">'
            "<table:table-cell/>"
            "</table:table-row>"
        )
        self.assertEqual(row.serialize(), expected)


class TestCreateColumn(TestCase):
    def test_default(self):
        column = Column()
        expected = "<table:table-column/>"
        self.assertEqual(column.serialize(), expected)

    def test_default_cell_style(self):
        column = Column(default_cell_style="A Style")
        expected = "<table:table-column " 'table:default-cell-style-name="A Style"/>'
        self.assertEqual(column.serialize(), expected)

    def test_style(self):
        column = Column(style="A Style")
        expected = '<table:table-column table:style-name="A Style"/>'
        self.assertEqual(column.serialize(), expected)

    def test_all(self):
        column = Column(style="co1", default_cell_style="Standard", repeated=3)
        expected = (
            "<table:table-column "
            'table:default-cell-style-name="Standard" '
            'table:number-columns-repeated="3" '
            'table:style-name="co1"/>'
        )
        self.assertEqual(column.serialize(), expected)


class TestCreateTable(TestCase):
    def test_default(self):
        table = Table("A Table")
        expected = '<table:table table:name="A Table"/>'
        self.assertEqual(table.serialize(), expected)

    def test_bad_name_1(self):
        self.assertRaises(ValueError, Table, " ")

    def test_bad_name_2(self):
        self.assertRaises(ValueError, Table, "ee'ee")

    def test_bad_name_3(self):
        self.assertRaises(ValueError, Table, "ee/ee")

    def test_bad_name_4(self):
        self.assertRaises(ValueError, Table, "ee\nee")

    def test_width_height(self):
        table = Table("A Table", width=1, height=2)
        expected = (
            '<table:table table:name="A Table">'
            "<table:table-column/>"
            "<table:table-row>"
            "<table:table-cell/>"
            "</table:table-row>"
            "<table:table-row>"
            "<table:table-cell/>"
            "</table:table-row>"
            "</table:table>"
        )
        self.assertEqual(table.serialize(), expected)

    def test_display(self):
        table = Table("Displayed")
        expected = '<table:table table:name="Displayed"/>'
        self.assertEqual(table.serialize(), expected)

    def test_display_false(self):
        table = Table("Hidden", display=False)
        expected = '<table:table table:name="Hidden" table:display="false"/>'
        self.assertEqual(table.serialize(), expected)

    def test_print(self):
        table = Table("Printable")
        expected = '<table:table table:name="Printable"/>'
        self.assertEqual(table.serialize(), expected)

    def test_print_false(self):
        table = Table("Hidden", printable=False)
        expected = '<table:table table:name="Hidden" table:print="false"/>'
        self.assertEqual(table.serialize(), expected)

    def test_print_ranges_str(self):
        table = Table("Ranges", print_ranges="E6:K12 P6:R12")
        expected = (
            '<table:table table:name="Ranges" ' 'table:print-ranges="E6:K12 P6:R12"/>'
        )
        self.assertEqual(table.serialize(), expected)

    def test_print_ranges_list(self):
        table = Table("Ranges", print_ranges=["E6:K12", "P6:R12"])
        expected = (
            '<table:table table:name="Ranges" ' 'table:print-ranges="E6:K12 P6:R12"/>'
        )
        self.assertEqual(table.serialize(), expected)

    def test_style(self):
        table = Table("A Table", style="A Style")
        expected = '<table:table table:name="A Table" ' 'table:style-name="A Style"/>'
        self.assertEqual(table.serialize(), expected)


class TestCell(TestCase):
    def setUp(self):
        self.cell = Cell(1, repeated=3, style="ce5")

    def test_get_cell_value(self):
        self.assertEqual(self.cell.get_value(), 1)
        self.assertEqual(self.cell.get_value(get_type=True), (1, "float"))

    def test_set_cell_value(self):
        cell = self.cell.clone
        cell.set_value("€")
        self.assertEqual(cell.get_value(), "€")
        self.assertEqual(cell.type, "string")
        self.assertEqual(cell.get_value(get_type=True), ("€", "string"))

    def test_get_cell_type(self):
        cell = self.cell.clone
        self.assertEqual(cell.type, "float")
        cell.set_value("€")
        self.assertEqual(cell.type, "string")

    def test_get_cell_type_percentage(self):
        cell = Cell(90, cell_type="percentage")
        self.assertEqual(cell.type, "percentage")
        self.assertEqual(cell.get_value(get_type=True), (90, "percentage"))
        cell = self.cell.clone
        cell.type = "percentage"
        self.assertEqual(cell.type, "percentage")
        self.assertEqual(cell.get_value(get_type=True), (1, "percentage"))

    def test_set_cell_type(self):
        cell = self.cell.clone
        cell.type = "time"
        self.assertEqual(cell.type, "time")

    def test_set_cell_type_date(self):
        cell = self.cell.clone
        cell.type = "date"
        self.assertEqual(cell.type, "date")

    def test_get_cell_currency(self):
        cell = Cell(123, cell_type="currency", currency="EUR")
        self.assertEqual(cell.currency, "EUR")
        self.assertEqual(cell.type, "currency")
        self.assertEqual(cell.get_value(get_type=True), (123, "currency"))

    def test_set_cell_currency(self):
        cell = Cell(123, cell_type="currency", currency="EUR")
        cell.currency = "CHF"
        self.assertEqual(cell.currency, "CHF")

    def test_get_cell_repeated(self):
        self.assertEqual(self.cell.repeated, 3)

    def test_set_cell_repeated(self):
        cell = self.cell.clone
        cell.repeated = 99
        self.assertEqual(cell.repeated, 99)
        cell.repeated = 1
        self.assertEqual(cell.repeated, None)
        cell.repeated = 2
        self.assertEqual(cell.repeated, 2)
        cell.repeated = None
        self.assertEqual(cell.repeated, None)

    def test_get_cell_style(self):
        self.assertEqual(self.cell.style, "ce5")
        self.cell.style = "something blue"
        self.assertEqual(self.cell.style, "something blue")
        self.cell.style = None
        self.assertEqual(self.cell.style, None)

    def test_set_cell_style(self):
        cell = self.cell.clone
        cell.style = "ce2"
        self.assertEqual(cell.style, "ce2")
        cell.style = None
        self.assertEqual(cell.style, None)

    def test_set_cell_formula(self):
        cell = self.cell.clone
        cell.formula = "any string"
        self.assertEqual(cell.formula, "any string")
        cell.formula = None
        self.assertEqual(cell.formula, None)


class TestRow(TestCase):
    def setUp(self):
        row = Row(width=2, repeated=3, style="ro1")
        # Add repeated cell
        row.append(Cell(1, repeated=2))
        # Add regular cell
        row.append(Cell(style="ce5"))
        self.row = row

    def test_get_row_repeated(self):
        self.assertEqual(self.row.repeated, 3)

    def test_set_row_repeated(self):
        row = self.row.clone
        row.repeated = 99
        self.assertEqual(row.repeated, 99)
        row.repeated = 1
        self.assertEqual(row.repeated, None)
        row.repeated = 2
        self.assertEqual(row.repeated, 2)
        row.repeated = None
        self.assertEqual(row.repeated, None)

    def test_get_row_style(self):
        self.assertEqual(self.row.style, "ro1")

    def test_get_row_width(self):
        self.assertEqual(self.row.width, 5)

    def test_traverse_cells(self):
        self.assertEqual(len(list(self.row.traverse())), 5)

    def test_get_cell_values(self):
        self.assertEqual(self.row.get_values(), [None, None, 1, 1, None])

    def test_is_empty(self):
        row = Row(width=100)
        self.assertEqual(row.is_empty(), True)

    def test_is_empty_no(self):
        row = Row(width=100)
        row.set_value(50, 1)
        self.assertEqual(row.is_empty(), False)

    def test_rstrip(self):
        row = Row(width=100)
        row.set_value(0, 1)
        row.set_value(1, 2)
        row.set_value(2, 3)
        row.set_cell(3, Cell(style="ce5"))
        row.rstrip()
        self.assertEqual(row.width, 4)


class TestRowCell(TestCase):

    #    simpletable :
    #      1	1	1	2	3	3	3
    #      1	1	1	2	3	3	3       self.row
    #      1	1	1	2	3	3	3
    #      1    2	3	4	5	6	7

    def setUp(self):
        document = Document("samples/simple_table.ods")
        body = document.body
        table = body.get_table(name="Example1").clone
        self.row_repeats = table.get_row(0)
        self.row = table.get_row(1)

    def test_traverse(self):
        self.assertEqual(len(list(self.row.traverse())), 7)

    def test_traverse_coord(self):
        self.assertEqual(len(list(self.row.traverse(2, None))), 5)
        self.assertEqual(len(list(self.row.traverse(2, 4))), 3)
        self.assertEqual(len(list(self.row.traverse(0, 3))), 4)
        self.assertEqual(len(list(self.row.traverse(0, 55))), 7)
        self.assertEqual(len(list(self.row.traverse(100, 55))), 0)
        self.assertEqual(len(list(self.row.traverse(100, None))), 0)
        self.assertEqual(len(list(self.row.traverse(None, 1))), 2)
        self.assertEqual(len(list(self.row.traverse(-5, 1))), 2)
        self.assertEqual(len(list(self.row.traverse(2, -1))), 0)
        self.assertEqual(len(list(self.row.traverse(-5, -1))), 0)

    def test_get_cells(self):
        self.assertEqual(len(list(self.row.get_cells())), 7)

    def test_get_cells_on_emty_row(self):
        row = Row()
        self.assertEqual(len(row.get_cells()), 0)
        self.assertEqual(len(row.get_cells((1, 2))), 0)
        self.assertEqual(len(row.get_cells((-2, -3))), 0)
        self.assertEqual(len(row.get_cells((0, 10))), 0)

    def test_get_cells_coord(self):
        coord = (0, 8)
        self.assertEqual(len(self.row.get_cells(coord)), 7)
        coord = "a1:c2"
        self.assertEqual(len(self.row.get_cells(coord)), 3)
        coord = "a1:a2"
        self.assertEqual(len(self.row.get_cells(coord)), 1)
        coord = "a1:EE2"
        self.assertEqual(len(self.row.get_cells(coord)), 7)
        coord = "D1"
        self.assertEqual(len(self.row.get_cells(coord)), 0)
        coord = "c5:a1"
        self.assertEqual(len(self.row.get_cells(coord)), 0)
        coord = (5, 6)
        self.assertEqual(len(self.row.get_cells(coord)), 2)
        coord = (-5, 6)
        self.assertEqual(len(self.row.get_cells(coord)), 5)
        coord = (0, -1)
        self.assertEqual(len(self.row.get_cells(coord)), 7)
        coord = (0, -2)
        self.assertEqual(len(self.row.get_cells(coord)), 6)
        coord = (-1, -1)
        self.assertEqual(len(self.row.get_cells(coord)), 1)
        coord = (1, 0)
        self.assertEqual(len(self.row.get_cells(coord)), 0)

    def test_get_cells_regex(self):
        coordinates = [cell.x for cell in self.row.get_cells(content=r"3")]
        expected = [4, 5, 6]
        self.assertEqual(coordinates, expected)

    def test_get_cells_style(self):
        coordinates = [cell.x for cell in self.row.get_cells(style=r"ce5")]
        expected = [1, 5]
        self.assertEqual(coordinates, expected)

    def test_get_cells_cell_type(self):
        row = self.row.clone
        cells = row.get_cells(cell_type="all")
        self.assertEqual(len(cells), 7)
        cells = row.get_cells(cell_type="float")
        self.assertEqual(len(cells), 7)
        cells = row.get_cells(cell_type="percentage")
        self.assertEqual(len(cells), 0)
        cells = row.get_cells(cell_type="string")
        self.assertEqual(len(cells), 0)

    def test_get_cells_cell_type2(self):
        row = self.row.clone
        row.append_cell(Cell(value="bob"), clone=False)
        row.append_cell(Cell(value=14, cell_type="percentage"))
        row.append_cell(Cell(value="bob2"), clone=False)
        cells = row.get_cells(cell_type="all")
        self.assertEqual(len(cells), 7 + 3)
        cells = row.get_cells(cell_type="float")
        self.assertEqual(len(cells), 7)
        cells = row.get_cells(cell_type="percentage")
        self.assertEqual(len(cells), 1)
        cells = row.get_cells(cell_type="string")
        self.assertEqual(len(cells), 2)

    def test_get_cells_cell_type_and_coord(self):
        row = self.row.clone
        cells = row.get_cells(coord=(0, 5), cell_type="all")
        self.assertEqual(len(cells), 6)
        cells = row.get_cells(coord=(0, 5), cell_type="float")
        self.assertEqual(len(cells), 6)
        cells = row.get_cells(coord=(0, 5), cell_type="percentage")
        self.assertEqual(len(cells), 0)
        cells = row.get_cells(coord=(2, 5), cell_type="string")
        self.assertEqual(len(cells), 0)

    def test_get_cells_cell_type_and_coord2(self):
        row = self.row.clone
        row.append_cell(Cell(value="bob"), clone=False)
        row.append_cell(Cell(value=14, cell_type="percentage"))
        row.append_cell(Cell(value="bob2"), clone=False)
        cells = row.get_cells(coord=(2, 9), cell_type="all")
        self.assertEqual(len(cells), 8)
        cells = row.get_cells(coord=(3, 9), cell_type="float")
        self.assertEqual(len(cells), 4)
        cells = row.get_cells(coord=(0, 5), cell_type="percentage")
        self.assertEqual(len(cells), 0)
        cells = row.get_cells(coord=(0, 5), cell_type="string")
        self.assertEqual(len(cells), 0)
        cells = row.get_cells(coord=(5, 9), cell_type="percentage")
        self.assertEqual(len(cells), 1)
        cells = row.get_cells(coord=(5, 9), cell_type="string")
        self.assertEqual(len(cells), 2)
        cells = row.get_cells(coord=(8, 9), cell_type="string")
        self.assertEqual(len(cells), 1)

    def test_get_cell_alpha(self):
        row = self.row
        cell_5 = row.get_cell("F")
        self.assertEqual(cell_5.get_value(), 3)
        self.assertEqual(cell_5.text_content, "3")
        self.assertEqual(cell_5.type, "float")
        self.assertEqual(cell_5.style, "ce5")
        self.assertEqual(cell_5.x, 5)
        self.assertEqual(cell_5.y, 1)

    def test_get_cell_int(self):
        row = self.row
        cell_5 = row.get_cell(5)
        self.assertEqual(cell_5.get_value(), 3)
        self.assertEqual(cell_5.text_content, "3")
        self.assertEqual(cell_5.type, "float")
        self.assertEqual(cell_5.style, "ce5")

    def test_get_cell_coord(self):
        row = self.row.clone
        cell = row.get_cell(-1)
        self.assertEqual(cell.get_value(), 3)
        cell = row.get_cell(-3)
        self.assertEqual(cell.get_value(), 3)
        cell = row.get_cell(-4)
        self.assertEqual(cell.get_value(), 2)
        cell = row.get_cell(-5)
        self.assertEqual(cell.get_value(), 1)
        cell = row.get_cell(-1 - 7)
        self.assertEqual(cell.get_value(), 3)
        cell = row.get_cell(-3 - 56)
        self.assertEqual(cell.get_value(), 3)
        cell = row.get_cell(-4 - 560)
        self.assertEqual(cell.get_value(), 2)
        cell = row.get_cell(-5 - 7000)
        self.assertEqual(cell.get_value(), 1)
        cell = row.get_cell(8)
        self.assertEqual(cell.get_value(), None)
        cell = row.get_cell(1000)
        self.assertEqual(cell.get_value(), None)

    def test_get_value_coord(self):
        row = self.row.clone
        row.append_cell(Cell("Appended"))
        value = row.get_value(-1)
        self.assertEqual(value, "Appended")
        value = row.get_value(-3)
        self.assertEqual(value, 3)
        value = row.get_value(-4)
        self.assertEqual(value, 3)
        value = row.get_value(-5)
        self.assertEqual(value, 2)
        value = row.get_value(-1 - 8)
        self.assertEqual(value, "Appended")
        value = row.get_value(7)
        self.assertEqual(value, "Appended")
        value = row.get_value(8)
        self.assertEqual(value, None)
        value = row.get_value(1000)
        self.assertEqual(value, None)

    def test_get_value_coord_with_get_type(self):
        row = self.row.clone
        row.append_cell(Cell("Appended"))
        value = row.get_value(-1, get_type=True)
        self.assertEqual(value, ("Appended", "string"))
        value = row.get_value(-3, get_type=True)
        self.assertEqual(value, (3, "float"))
        value = row.get_value(-4, get_type=True)
        self.assertEqual(value, (3, "float"))
        value = row.get_value(-5, get_type=True)
        self.assertEqual(value, (2, "float"))
        value = row.get_value(-1 - 8, get_type=True)
        self.assertEqual(value, ("Appended", "string"))
        value = row.get_value(7, get_type=True)
        self.assertEqual(value, ("Appended", "string"))
        value = row.get_value(8, get_type=True)
        self.assertEqual(value, (None, None))
        value = row.get_value(1000, get_type=True)
        self.assertEqual(value, (None, None))

    def test_set_cell(self):
        row = self.row.clone
        row.set_value(1, 3.14)
        self.assertEqual(row.get_values(), [1, dec("3.14"), 1, 2, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.width, 7)

    def test_set_cell_far_away(self):
        row = self.row.clone
        row.set_value(7 + 3, 3.14)
        self.assertEqual(
            row.get_values(), [1, 1, 1, 2, 3, 3, 3, None, None, None, dec("3.14")]
        )
        # Test repetitions are synchronized
        self.assertEqual(row.width, 11)

    def test_set_cell_repeat(self):
        row = self.row_repeats.clone
        row.set_value(1, 3.14)
        self.assertEqual(row.get_values(), [1, dec("3.14"), 1, 2, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.width, 7)

    def test_set_cell_repeat_repeat(self):
        row = self.row_repeats.clone
        cell = Cell(value=20, repeated=2)
        row.set_cell(1, cell)
        self.assertEqual(row.get_values(), [1, 20, 20, 2, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.width, 7)

    def test_insert(self):
        row = self.row.clone
        cell = row.insert_cell(3)
        self.assertTrue(type(cell) is Cell)
        self.assertEqual(cell.x, 3)
        self.assertEqual(cell.y, 1)

    def test_insert_cell(self):
        row = self.row.clone
        cell = row.insert_cell(3, Cell("Inserted"))
        self.assertEqual(row.width, 8)
        self.assertEqual(row.get_values(), [1, 1, 1, "Inserted", 2, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.width, 8)
        self.assertEqual(cell.x, 3)
        self.assertEqual(cell.y, 1)

    def test_insert_cell_repeat(self):
        row = self.row_repeats.clone
        cell = row.insert_cell(6, Cell("Inserted"))
        self.assertEqual(row.get_values(), [1, 1, 1, 2, 3, 3, "Inserted", 3])
        # Test repetitions are synchronized
        self.assertEqual(row.width, 8)
        self.assertEqual(cell.x, 6)
        self.assertEqual(cell.y, 0)

    def test_insert_cell_repeat_repeat(self):
        row = self.row_repeats.clone
        cell = row.insert_cell(6, Cell("Inserted", repeated=3))
        self.assertEqual(
            row.get_values(), [1, 1, 1, 2, 3, 3, "Inserted", "Inserted", "Inserted", 3]
        )
        # Test repetitions are synchronized
        self.assertEqual(row.width, 10)
        self.assertEqual(cell.x, 6)
        self.assertEqual(cell.y, 0)

    def test_insert_cell_repeat_repeat_bis(self):
        row = self.row_repeats.clone
        cell = row.insert_cell(1, Cell("Inserted", repeated=2))
        self.assertEqual(
            row.get_values(), [1, "Inserted", "Inserted", 1, 1, 2, 3, 3, 3]
        )
        # Test repetitions are synchronized
        self.assertEqual(row.width, 9)
        self.assertEqual(cell.x, 1)
        self.assertEqual(cell.y, 0)

    def test_append_cell(self):
        row = self.row.clone
        cell = row.append_cell()
        self.assertTrue(type(cell) is Cell)
        self.assertEqual(cell.x, self.row.width)
        self.assertEqual(cell.y, 1)

    def test_append_cell2(self):
        row = self.row.clone
        cell = row.append_cell(Cell("Appended"))
        self.assertEqual(row.get_values(), [1, 1, 1, 2, 3, 3, 3, "Appended"])
        # Test repetitions are synchronized
        self.assertEqual(row.width, 8)
        self.assertEqual(cell.x, self.row.width)
        self.assertEqual(cell.y, 1)

    def test_delete_cell(self):
        row = self.row.clone
        row.delete_cell(3)
        self.assertEqual(row.get_values(), [1, 1, 1, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.width, 6)

    def test_delete_cell_repeat(self):
        row = self.row_repeats.clone
        row.delete_cell(-1)
        self.assertEqual(row.get_values(), [1, 1, 1, 2, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.width, 6)

    def test_set_cells_1(self):
        row = self.row.clone
        cells = [Cell(value=10)]
        row.set_cells(cells)
        self.assertEqual(row.get_values(), [10, 1, 1, 2, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.width, 7)

    def test_set_cells_2(self):
        row = self.row.clone
        cells = [Cell(value=10), Cell(value=20)]
        row.set_cells(cells)
        self.assertEqual(row.get_values(), [10, 20, 1, 2, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.width, 7)

    def test_set_cells_many(self):
        row = self.row.clone
        cells = []
        for i in range(10):
            cells.append(Cell(value=10 * i))
        row.set_cells(cells)
        self.assertEqual(row.get_values(), [0, 10, 20, 30, 40, 50, 60, 70, 80, 90])
        # Test repetitions are synchronized
        self.assertEqual(row.width, 10)

    def test_set_cells_1_start_1(self):
        row = self.row.clone
        cells = [Cell(value=10)]
        row.set_cells(cells, 1)
        self.assertEqual(row.get_values(), [1, 10, 1, 2, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.width, 7)

    def test_set_cells_1_start_m_2(self):
        row = self.row.clone
        cells = [Cell(value=10)]
        row.set_cells(cells, -2)
        self.assertEqual(row.get_values(), [1, 1, 1, 2, 3, 10, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.width, 7)

    def test_set_cells_1_start_m_6(self):
        row = self.row.clone
        cells = [Cell(value=10)]
        row.set_cells(cells, 6)
        self.assertEqual(row.get_values(), [1, 1, 1, 2, 3, 3, 10])
        # Test repetitions are synchronized
        self.assertEqual(row.width, 7)

    def test_set_cells_1_start_m_9(self):
        row = self.row.clone
        cells = [Cell(value=10)]
        row.set_cells(cells, 9)
        self.assertEqual(row.get_values(), [1, 1, 1, 2, 3, 3, 3, None, None, 10])
        # Test repetitions are synchronized
        self.assertEqual(row.width, 10)

    def test_set_cells_2_start_1(self):
        row = self.row.clone
        cells = [Cell(value=10), Cell(value=20)]
        row.set_cells(cells, 1)
        self.assertEqual(row.get_values(), [1, 10, 20, 2, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.width, 7)

    def test_set_cells_many_start_5(self):
        row = self.row.clone
        cells = []
        for i in range(5):
            cells.append(Cell(value=10 * i))
        row.set_cells(cells, 5)
        self.assertEqual(row.get_values(), [1, 1, 1, 2, 3, 0, 10, 20, 30, 40])
        # Test repetitions are synchronized
        self.assertEqual(row.width, 10)

    def test_set_cells_many_start_far(self):
        row = self.row.clone
        cells = []
        for i in range(5):
            cells.append(Cell(value=10 * i))
        row.set_cells(cells, 9)
        self.assertEqual(
            row.get_values(), [1, 1, 1, 2, 3, 3, 3, None, None, 0, 10, 20, 30, 40]
        )
        # Test repetitions are synchronized
        self.assertEqual(row.width, 14)

    def test_set_cells_3_start_1_repeats(self):
        row = self.row.clone
        cells = [Cell(value=10, repeated=2)]
        row.set_cells(cells, 1)
        self.assertEqual(row.get_values(), [1, 10, 10, 2, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.width, 7)

    def test_set_cells_3_start_1_repeats_2(self):
        row = self.row.clone
        cells = [Cell(value=10, repeated=2), Cell(value=20)]
        row.set_cells(cells, 1)
        self.assertEqual(row.get_values(), [1, 10, 10, 20, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.width, 7)

    def test_set_cells_3_start_1_repeats_3(self):
        row = self.row.clone
        cells = [Cell(value=10, repeated=2), Cell(value=20), Cell(value=30, repeated=2)]
        row.set_cells(cells, 1)
        self.assertEqual(row.get_values(), [1, 10, 10, 20, 30, 30, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.width, 7)

    def test_set_cells_3_start_1_repeats_4(self):
        row = self.row.clone
        cells = [Cell(value=10, repeated=2), Cell(value=20), Cell(value=30, repeated=4)]
        row.set_cells(cells, 1)
        self.assertEqual(row.get_values(), [1, 10, 10, 20, 30, 30, 30, 30])
        # Test repetitions are synchronized
        self.assertEqual(row.width, 8)

    def test_set_values_empty(self):
        row = Row()
        row.set_values([1, 2, 3, 4])
        self.assertEqual(row.width, 4)
        self.assertEqual(row.get_values(), [1, 2, 3, 4])

    def test_set_values_on_row(self):
        row = self.row.clone
        row.set_values([10, 20, 30, "4"])
        self.assertEqual(row.width, 7)
        self.assertEqual(row.get_values(), [10, 20, 30, "4", 3, 3, 3])

    def test_set_values_on_row2(self):
        row = self.row.clone
        row.set_values([10, 20, 30, "4"], start=2)
        self.assertEqual(row.width, 7)
        self.assertEqual(row.get_values(), [1, 1, 10, 20, 30, "4", 3])

    def test_set_values_on_row3(self):
        row = self.row.clone
        row.set_values([10, 20, 30, "4"], start=2)
        self.assertEqual(row.width, 7)
        self.assertEqual(row.get_values(), [1, 1, 10, 20, 30, "4", 3])

    def test_set_values_on_row4(self):
        row = self.row.clone
        row.set_values([10, 20, 30, "4"], start=-2)
        self.assertEqual(row.width, 9)
        self.assertEqual(row.get_values(), [1, 1, 1, 2, 3, 10, 20, 30, "4"])

    def test_set_values_on_row5(self):
        row = self.row.clone
        row.set_values([10, 20, 30, "4"], start=8)
        self.assertEqual(row.width, 7 + 1 + 4)
        self.assertEqual(row.get_values(), [1, 1, 1, 2, 3, 3, 3, None, 10, 20, 30, "4"])

    def test_set_values_on_row6(self):
        row = self.row.clone
        row.set_values([10, 20, 30, 40, 50, 60, 70, 80], start=0)
        self.assertEqual(row.width, 8)
        self.assertEqual(row.get_values(), [10, 20, 30, 40, 50, 60, 70, 80])

    def test_set_values_on_row_percentage(self):
        row = self.row.clone
        row.set_values([10, 20], start=4, cell_type="percentage")
        self.assertEqual(row.width, 7)
        self.assertEqual(row.get_values(), [1, 1, 1, 2, 10, 20, 3])
        self.assertEqual(
            row.get_values(get_type=True, cell_type="percentage"),
            [(10, "percentage"), (20, "percentage")],
        )

    def test_set_values_on_row_style(self):
        row = self.row.clone
        row.set_values([10, 20], start=3, style="bold")
        self.assertEqual(row.width, 7)
        self.assertEqual(row.get_values(), [1, 1, 1, 10, 20, 3, 3])
        self.assertEqual(row.get_cell(4).style, "bold")

    def test_set_values_on_row_curency(self):
        row = self.row.clone
        row.set_values([10, 20], start=3, cell_type="currency", currency="EUR")
        self.assertEqual(row.width, 7)
        self.assertEqual(row.get_values(), [1, 1, 1, 10, 20, 3, 3])
        self.assertEqual(row.get_cell(4).get_value(get_type=True), (20, "currency"))
        self.assertEqual(row.get_cell(4).currency, "EUR")


class TestRowCellGetValues(TestCase):

    #    simpletable :
    #      1	1	1	2	3	3	3
    #      1	1	1	2	3	3	3       self.row
    #      1	1	1	2	3	3	3
    #      1    2	3	4	5	6	7

    def setUp(self):
        document = Document("samples/simple_table.ods")
        body = document.body
        table = body.get_table(name="Example1").clone
        self.row_repeats = table.get_row(0)
        self.row = table.get_row(1)

    def test_on_empty_row(self):
        row = Row()
        self.assertEqual(row.get_values(), [])
        self.assertEqual(row.get_values(complete=True), [])
        self.assertEqual(row.get_values(complete=True, get_type=True), [])
        self.assertEqual(row.get_values((0, 10)), [])
        self.assertEqual(row.get_values(cell_type="all"), [])
        self.assertEqual(row.get_values(cell_type="All"), [])
        self.assertEqual(row.get_values((2, 3), complete=True), [])

    def test_get_values_count(self):
        self.assertEqual(len(self.row.get_values()), 7)

    def test_get_values_coord(self):
        coord = (0, 8)
        self.assertEqual(len(self.row.get_values(coord)), 7)
        coord = "a1:c2"
        self.assertEqual(len(self.row.get_values(coord)), 3)
        coord = "a1:a2"
        self.assertEqual(len(self.row.get_values(coord)), 1)
        coord = "a1:EE2"
        self.assertEqual(len(self.row.get_values(coord)), 7)
        coord = "D1"
        self.assertEqual(len(self.row.get_values(coord)), 0)
        coord = "c5:a1"
        self.assertEqual(len(self.row.get_values(coord)), 0)
        coord = (5, 6)
        self.assertEqual(len(self.row.get_values(coord)), 2)
        coord = (-5, 6)
        self.assertEqual(len(self.row.get_values(coord)), 5)
        coord = (0, -1)
        self.assertEqual(len(self.row.get_values(coord)), 7)
        coord = (0, -2)
        self.assertEqual(len(self.row.get_values(coord)), 6)
        coord = (-1, -1)
        self.assertEqual(len(self.row.get_values(coord)), 1)
        coord = (1, 0)
        self.assertEqual(len(self.row.get_values(coord)), 0)

    def test_get_values_cell_type(self):
        row = self.row.clone
        values = row.get_values(cell_type="all")
        self.assertEqual(len(values), 7)
        values = row.get_values(cell_type="float")
        self.assertEqual(len(values), 7)
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3])
        values = row.get_values(cell_type="percentage")
        self.assertEqual(len(values), 0)
        values = row.get_values(cell_type="string")
        self.assertEqual(len(values), 0)

    def test_get_values_cell_type2(self):
        row = self.row.clone
        row.append_cell(Cell(value="bob"), clone=False)
        row.append_cell(Cell(value=14, cell_type="percentage"))
        row.append_cell(Cell(value="bob2"), clone=False)
        values = row.get_values(cell_type="all")
        self.assertEqual(len(values), 7 + 3)
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3, "bob", 14, "bob2"])
        values = row.get_values(cell_type="float")
        self.assertEqual(len(values), 7)
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3])
        values = row.get_values(cell_type="percentage")
        self.assertEqual(len(values), 1)
        self.assertEqual(values, [14])
        values = row.get_values(cell_type="string")
        self.assertEqual(len(values), 2)
        self.assertEqual(values, ["bob", "bob2"])

    def test_get_values_cell_type2_with_hole(self):
        row = self.row.clone
        row.append_cell(Cell(value="bob"), clone=False)
        row.append_cell(Cell(value=14, cell_type="percentage"))
        row.append_cell(Cell(value="bob2"), clone=False)
        row.set_cell(12, Cell(value="far"), clone=False)
        values = row.get_values(cell_type="all")  # aka all non empty
        self.assertEqual(len(values), 11)
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3, "bob", 14, "bob2", "far"])
        values = row.get_values()  # difference when requestion everything
        self.assertEqual(len(values), 13)
        self.assertEqual(
            values, [1, 1, 1, 2, 3, 3, 3, "bob", 14, "bob2", None, None, "far"]
        )
        values = row.get_values(cell_type="float")
        self.assertEqual(len(values), 7)
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3])
        values = row.get_values(cell_type="percentage")
        self.assertEqual(len(values), 1)
        self.assertEqual(values, [14])
        values = row.get_values(cell_type="string")
        self.assertEqual(len(values), 3)
        self.assertEqual(values, ["bob", "bob2", "far"])
        values = row.get_values(":")  # requesting everything
        self.assertEqual(len(values), 13)
        self.assertEqual(
            values, [1, 1, 1, 2, 3, 3, 3, "bob", 14, "bob2", None, None, "far"]
        )
        values = row.get_values(cell_type="float")
        self.assertEqual(len(values), 7)
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3])
        values = row.get_values(cell_type="percentage")
        self.assertEqual(len(values), 1)
        self.assertEqual(values, [14])
        values = row.get_values(cell_type="string")
        self.assertEqual(len(values), 3)
        self.assertEqual(values, ["bob", "bob2", "far"])
        values = row.get_values(":")  # requesting everything
        self.assertEqual(len(values), 13)
        self.assertEqual(
            values, [1, 1, 1, 2, 3, 3, 3, "bob", 14, "bob2", None, None, "far"]
        )
        values = row.get_values(cell_type="float")
        self.assertEqual(len(values), 7)
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3])
        values = row.get_values(cell_type="percentage")
        self.assertEqual(len(values), 1)
        self.assertEqual(values, [14])
        values = row.get_values(cell_type="string")
        self.assertEqual(len(values), 3)
        self.assertEqual(values, ["bob", "bob2", "far"])
        values = row.get_values("")  # requesting everything 2
        self.assertEqual(len(values), 13)
        self.assertEqual(
            values, [1, 1, 1, 2, 3, 3, 3, "bob", 14, "bob2", None, None, "far"]
        )
        values = row.get_values(cell_type="float")
        self.assertEqual(len(values), 7)
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3])
        values = row.get_values(cell_type="percentage")
        self.assertEqual(len(values), 1)
        self.assertEqual(values, [14])
        values = row.get_values(cell_type="string")
        self.assertEqual(len(values), 3)
        self.assertEqual(values, ["bob", "bob2", "far"])

    def test_get_values_cell_type2_with_hole_and_get_type(self):
        row = self.row.clone
        row.append_cell(Cell(value="bob"), clone=False)
        row.append_cell(Cell(value=14, cell_type="percentage"))
        row.append_cell(Cell(value="bob2"), clone=False)
        row.set_cell(12, Cell(value="far"), clone=False)
        values = row.get_values(cell_type="all", get_type=True)  # aka all non empty
        self.assertEqual(len(values), 11)
        self.assertEqual(
            values,
            [
                (1, "float"),
                (1, "float"),
                (1, "float"),
                (2, "float"),
                (3, "float"),
                (3, "float"),
                (3, "float"),
                ("bob", "string"),
                (14, "percentage"),
                ("bob2", "string"),
                ("far", "string"),
            ],
        )
        values = row.get_values(get_type=True)  # difference when  everything
        self.assertEqual(len(values), 13)
        self.assertEqual(
            values,
            [
                (1, "float"),
                (1, "float"),
                (1, "float"),
                (2, "float"),
                (3, "float"),
                (3, "float"),
                (3, "float"),
                ("bob", "string"),
                (14, "percentage"),
                ("bob2", "string"),
                (None, None),
                (None, None),
                ("far", "string"),
            ],
        )
        values = row.get_values(cell_type="float", get_type=True)
        self.assertEqual(len(values), 7)
        self.assertEqual(
            values,
            [
                (1, "float"),
                (1, "float"),
                (1, "float"),
                (2, "float"),
                (3, "float"),
                (3, "float"),
                (3, "float"),
            ],
        )
        values = row.get_values(cell_type="percentage", get_type=True)
        self.assertEqual(len(values), 1)
        self.assertEqual(values, [(14, "percentage")])
        values = row.get_values(cell_type="string", get_type=True)
        self.assertEqual(len(values), 3)
        self.assertEqual(
            values, [("bob", "string"), ("bob2", "string"), ("far", "string")]
        )

    def test_get_values_cell_type2_complete(self):
        row = self.row.clone
        row.append_cell(Cell(value="bob"), clone=False)
        row.append_cell(Cell(value=14, cell_type="percentage"))
        row.append_cell(Cell(value="bob2"), clone=False)
        row.set_cell(12, Cell(value="far"), clone=False)
        values = row.get_values(cell_type="ALL", complete=True)
        self.assertEqual(len(values), 13)
        self.assertEqual(
            values, [1, 1, 1, 2, 3, 3, 3, "bob", 14, "bob2", None, None, "far"]
        )
        values = row.get_values(cell_type="FLOAT", complete=True)
        self.assertEqual(len(values), 13)
        self.assertEqual(
            values, [1, 1, 1, 2, 3, 3, 3, None, None, None, None, None, None]
        )
        values = row.get_values(cell_type="percentage", complete=True)
        self.assertEqual(len(values), 13)
        self.assertEqual(
            values,
            [
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                14,
                None,
                None,
                None,
                None,
            ],
        )
        values = row.get_values(cell_type="string", complete=True)
        self.assertEqual(len(values), 13)
        self.assertEqual(
            values,
            [
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                "bob",
                None,
                "bob2",
                None,
                None,
                "far",
            ],
        )

    def test_get_values_cell_type_and_coord(self):
        row = self.row.clone
        values = row.get_values(coord=(0, 5), cell_type="all")
        self.assertEqual(len(values), 6)
        values = row.get_values(coord=(0, 5), cell_type="float")
        self.assertEqual(len(values), 6)
        values = row.get_values(coord=(0, 5), cell_type="percentage")
        self.assertEqual(len(values), 0)
        values = row.get_values(coord=(2, 5), cell_type="string")
        self.assertEqual(len(values), 0)

    def test_get_values_cell_type_and_coord_strange(self):
        row = self.row.clone
        values = row.get_values(coord="A:F", cell_type="all")
        self.assertEqual(len(values), 6)
        values = row.get_values(coord="C:", cell_type="all")
        self.assertEqual(len(values), 5)
        values = row.get_values(coord="A : f", cell_type="float")
        self.assertEqual(len(values), 6)
        values = row.get_values(coord="A:F", cell_type="percentage")
        self.assertEqual(len(values), 0)
        values = row.get_values(coord="C:F", cell_type="string")
        self.assertEqual(len(values), 0)

    def test_get_values_cell_type_and_coord_strange_long(self):
        row = self.row.clone
        values = row.get_values(coord="A8:F2", cell_type="all")
        self.assertEqual(len(values), 6)
        values = row.get_values(coord="C5:", cell_type="all")
        self.assertEqual(len(values), 5)
        values = row.get_values(coord="C5:99", cell_type="all")
        self.assertEqual(len(values), 5)
        values = row.get_values(coord="A2 : f", cell_type="float")
        self.assertEqual(len(values), 6)
        values = row.get_values(coord="A:F5", cell_type="percentage")
        self.assertEqual(len(values), 0)
        values = row.get_values(coord="C:F4", cell_type="string")
        self.assertEqual(len(values), 0)

    def test_get_values_cell_type_and_coord_and_get_type(self):
        row = self.row.clone
        values = row.get_values(coord=(0, 5), cell_type="all", get_type=True)
        self.assertEqual(len(values), 6)
        self.assertEqual(
            values,
            [
                (1, "float"),
                (1, "float"),
                (1, "float"),
                (2, "float"),
                (3, "float"),
                (3, "float"),
            ],
        )
        values = row.get_values(coord=(0, 5), cell_type="float", get_type=True)
        self.assertEqual(len(values), 6)
        self.assertEqual(
            values,
            [
                (1, "float"),
                (1, "float"),
                (1, "float"),
                (2, "float"),
                (3, "float"),
                (3, "float"),
            ],
        )
        values = row.get_values(coord=(0, 5), cell_type="percentage", get_type=True)
        self.assertEqual(len(values), 0)
        values = row.get_values(coord=(2, 5), cell_type="string", get_type=True)
        self.assertEqual(len(values), 0)

    def test_get_values_cell_type_and_coord_and_complete(self):
        row = self.row.clone
        values = row.get_values(coord=(0, 5), cell_type="all", complete=True)
        self.assertEqual(len(values), 6)
        self.assertEqual(values, [1, 1, 1, 2, 3, 3])
        values = row.get_values(coord=(0, 5), cell_type="float", complete=True)
        self.assertEqual(len(values), 6)
        self.assertEqual(values, [1, 1, 1, 2, 3, 3])
        values = row.get_values(coord=(0, 5), cell_type="percentage", complete=True)
        self.assertEqual(len(values), 6)
        self.assertEqual(values, [None, None, None, None, None, None])
        values = row.get_values(coord=(2, 5), cell_type="string", complete=True)
        self.assertEqual(len(values), 4)
        self.assertEqual(values, [None, None, None, None])

    def test_get_values_cell_type_and_coord2_and_complete(self):
        row = self.row.clone
        row.append_cell(Cell(value="bob"), clone=False)
        row.append_cell(Cell(value=14, cell_type="percentage"))
        row.append_cell(Cell(value="bob2"), clone=False)
        row.set_cell(12, Cell(value="far"), clone=False)
        values = row.get_values(coord=(2, 20), cell_type="all", complete=True)
        self.assertEqual(len(values), 11)
        self.assertEqual(values, [1, 2, 3, 3, 3, "bob", 14, "bob2", None, None, "far"])
        values = row.get_values(coord=(2, 11), cell_type="all", complete=True)
        self.assertEqual(len(values), 10)
        self.assertEqual(values, [1, 2, 3, 3, 3, "bob", 14, "bob2", None, None])
        values = row.get_values(coord=(3, 12), cell_type="float", complete=True)
        self.assertEqual(len(values), 10)
        self.assertEqual(values, [2, 3, 3, 3, None, None, None, None, None, None])
        values = row.get_values(coord=(0, 5), cell_type="percentage", complete=True)
        self.assertEqual(len(values), 6)
        self.assertEqual(values, [None, None, None, None, None, None])
        values = row.get_values(coord=(0, 5), cell_type="string", complete=True)
        self.assertEqual(len(values), 6)
        self.assertEqual(values, [None, None, None, None, None, None])
        values = row.get_values(coord=(5, 11), cell_type="percentage", complete=True)
        self.assertEqual(len(values), 7)
        self.assertEqual(values, [None, None, None, 14, None, None, None])
        values = row.get_values(coord=(6, 12), cell_type="string", complete=True)
        self.assertEqual(len(values), 7)
        self.assertEqual(values, [None, "bob", None, "bob2", None, None, "far"])
        values = row.get_values(coord=(8, 20), cell_type="string", complete=True)
        self.assertEqual(len(values), 5)
        self.assertEqual(values, [None, "bob2", None, None, "far"])

    def test_get_values_cell_type_and_coord2_and_complete_and_get_type(self):
        row = self.row.clone
        row.append_cell(Cell(value="bob"), clone=False)
        row.append_cell(Cell(value=14, cell_type="percentage"))
        row.append_cell(Cell(value="bob2"), clone=False)
        row.set_cell(12, Cell(value="far"), clone=False)
        values = row.get_values(
            coord=(2, 20), cell_type="all", complete=True, get_type=True
        )
        self.assertEqual(len(values), 11)
        self.assertEqual(
            values,
            [
                (1, "float"),
                (2, "float"),
                (3, "float"),
                (3, "float"),
                (3, "float"),
                ("bob", "string"),
                (14, "percentage"),
                ("bob2", "string"),
                (None, None),
                (None, None),
                ("far", "string"),
            ],
        )
        values = row.get_values(
            coord=(2, 11), cell_type="all", complete=True, get_type=True
        )
        self.assertEqual(len(values), 10)
        self.assertEqual(
            values,
            [
                (1, "float"),
                (2, "float"),
                (3, "float"),
                (3, "float"),
                (3, "float"),
                ("bob", "string"),
                (14, "percentage"),
                ("bob2", "string"),
                (None, None),
                (None, None),
            ],
        )
        values = row.get_values(
            coord=(3, 12), cell_type="float", complete=True, get_type=True
        )
        self.assertEqual(len(values), 10)
        self.assertEqual(
            values,
            [
                (2, "float"),
                (3, "float"),
                (3, "float"),
                (3, "float"),
                (None, None),
                (None, None),
                (None, None),
                (None, None),
                (None, None),
                (None, None),
            ],
        )
        values = row.get_values(
            coord=(0, 5), cell_type="percentage", complete=True, get_type=True
        )
        self.assertEqual(len(values), 6)
        self.assertEqual(
            values,
            [
                (None, None),
                (None, None),
                (None, None),
                (None, None),
                (None, None),
                (None, None),
            ],
        )
        values = row.get_values(
            coord=(0, 5), cell_type="string", complete=True, get_type=True
        )
        self.assertEqual(len(values), 6)
        self.assertEqual(
            values,
            [
                (None, None),
                (None, None),
                (None, None),
                (None, None),
                (None, None),
                (None, None),
            ],
        )
        values = row.get_values(
            coord=(5, 11), cell_type="percentage", complete=True, get_type=True
        )
        self.assertEqual(len(values), 7)
        self.assertEqual(
            values,
            [
                (None, None),
                (None, None),
                (None, None),
                (14, "percentage"),
                (None, None),
                (None, None),
                (None, None),
            ],
        )
        values = row.get_values(
            coord=(6, 12), cell_type="string", complete=True, get_type=True
        )
        self.assertEqual(len(values), 7)
        self.assertEqual(
            values,
            [
                (None, None),
                ("bob", "string"),
                (None, None),
                ("bob2", "string"),
                (None, None),
                (None, None),
                ("far", "string"),
            ],
        )
        values = row.get_values(
            coord=(8, 20), cell_type="string", complete=True, get_type=True
        )
        self.assertEqual(len(values), 5)
        self.assertEqual(
            values,
            [
                (None, None),
                ("bob2", "string"),
                (None, None),
                (None, None),
                ("far", "string"),
            ],
        )

    def test_get_cell_alpha(self):
        row = self.row
        cell_5 = row.get_cell("F")
        self.assertEqual(cell_5.get_value(), 3)
        self.assertEqual(cell_5.text_content, "3")
        self.assertEqual(cell_5.type, "float")
        self.assertEqual(cell_5.style, "ce5")
        self.assertEqual(cell_5.x, 5)
        self.assertEqual(cell_5.y, 1)

    def test_get_cell_int(self):
        row = self.row
        cell_5 = row.get_cell(5)
        self.assertEqual(cell_5.get_value(), 3)
        self.assertEqual(cell_5.text_content, "3")
        self.assertEqual(cell_5.type, "float")
        self.assertEqual(cell_5.style, "ce5")

    def test_get_cell_coord(self):
        row = self.row.clone
        cell = row.get_cell(-1)
        self.assertEqual(cell.get_value(), 3)
        cell = row.get_cell(-3)
        self.assertEqual(cell.get_value(), 3)
        cell = row.get_cell(-4)
        self.assertEqual(cell.get_value(), 2)
        cell = row.get_cell(-5)
        self.assertEqual(cell.get_value(), 1)
        cell = row.get_cell(-1 - 7)
        self.assertEqual(cell.get_value(), 3)
        cell = row.get_cell(-3 - 56)
        self.assertEqual(cell.get_value(), 3)
        cell = row.get_cell(-4 - 560)
        self.assertEqual(cell.get_value(), 2)
        cell = row.get_cell(-5 - 7000)
        self.assertEqual(cell.get_value(), 1)
        cell = row.get_cell(8)
        self.assertEqual(cell.get_value(), None)
        cell = row.get_cell(1000)
        self.assertEqual(cell.get_value(), None)

    def test_get_value_coord(self):
        row = self.row.clone
        row.append_cell(Cell("Appended"))
        value = row.get_value(-1)
        self.assertEqual(value, "Appended")
        value = row.get_value(-3)
        self.assertEqual(value, 3)
        value = row.get_value(-4)
        self.assertEqual(value, 3)
        value = row.get_value(-5)
        self.assertEqual(value, 2)
        value = row.get_value(-1 - 8)
        self.assertEqual(value, "Appended")
        value = row.get_value(7)
        self.assertEqual(value, "Appended")
        value = row.get_value(8)
        self.assertEqual(value, None)
        value = row.get_value(1000)
        self.assertEqual(value, None)

    def test_get_value_coord_with_get_type(self):
        row = self.row.clone
        row.append_cell(Cell("Appended"))
        value = row.get_value(-1, get_type=True)
        self.assertEqual(value, ("Appended", "string"))
        value = row.get_value(-3, get_type=True)
        self.assertEqual(value, (3, "float"))
        value = row.get_value(-4, get_type=True)
        self.assertEqual(value, (3, "float"))
        value = row.get_value(-5, get_type=True)
        self.assertEqual(value, (2, "float"))
        value = row.get_value(-1 - 8, get_type=True)
        self.assertEqual(value, ("Appended", "string"))
        value = row.get_value(7, get_type=True)
        self.assertEqual(value, ("Appended", "string"))
        value = row.get_value(8, get_type=True)
        self.assertEqual(value, (None, None))
        value = row.get_value(1000, get_type=True)
        self.assertEqual(value, (None, None))


class TestColumn(TestCase):
    def setUp(self):
        self.column = Column(default_cell_style="ce5", repeated=7, style="co1")

    def test_get_column_default_cell_style(self):
        self.assertEqual(self.column.get_default_cell_style(), "ce5")

    def test_set_column_default_cell_style(self):
        column = self.column.clone
        column.set_default_cell_style("ce2")
        self.assertEqual(column.get_default_cell_style(), "ce2")
        column.set_default_cell_style(None)
        self.assertEqual(column.get_default_cell_style(), None)

    def test_get_column_repeated(self):
        self.assertEqual(self.column.repeated, 7)

    def test_set_column_repeated(self):
        column = self.column.clone
        column.repeated = 99
        self.assertEqual(column.repeated, 99)
        column.repeated = 1
        self.assertEqual(column.repeated, None)
        column.repeated = 2
        self.assertEqual(column.repeated, 2)
        column.repeated = None
        self.assertEqual(column.repeated, None)

    def test_get_column_style(self):
        self.assertEqual(self.column.style, "co1")

    def test_set_column_style(self):
        column = self.column.clone
        column.style = "co2"
        self.assertEqual(column.style, "co2")
        column.style = None
        self.assertEqual(column.style, None)


class TestTable(TestCase):
    # simpletable :
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1   2	3	4	5	6	7

    def setUp(self):
        document = Document("samples/simple_table.ods")
        self.body = body = document.body
        self.table = body.get_table(name="Example1")

    def test_get_table_list(self):
        body = self.body
        self.assertEqual(len(body.get_tables()), 3)

    def test_get_table_list_style(self):
        body = self.body
        self.assertEqual(len(body.get_tables(style="ta1")), 3)

    def test_get_table_by_name(self):
        body = self.body.clone
        name = "New Table"
        body.append(Table(name))
        table = body.get_table(name=name)
        self.assertEqual(table.name, name)

    def test_get_table_by_position(self):
        body = self.body.clone
        body.append(Table("New Table"))
        table = body.get_table(position=3)
        self.assertEqual(table.name, "New Table")

    def test_get_table_style(self):
        self.assertEqual(self.table.style, "ta1")

    def test_get_table_printable(self):
        self.assertEqual(self.table.printable, False)

    def test_get_table_width(self):
        self.assertEqual(self.table.width, 7)

    def test_get_table_height(self):
        self.assertEqual(self.table.height, 4)

    def test_get_table_size(self):
        self.assertEqual(self.table.size, (7, 4))

    def test_get_table_size_empty(self):
        table = Table("Empty")
        self.assertEqual(table.size, (0, 0))

    def test_get_table_width_after(self):
        table = Table("Empty")
        self.assertEqual(table.width, 0)
        self.assertEqual(table.height, 0)
        # The first row creates the columns
        table.append_row(Row(width=5))
        self.assertEqual(table.width, 5)
        self.assertEqual(table.height, 1)
        # The subsequent ones don't
        table.append_row(Row(width=5))
        self.assertEqual(table.width, 5)
        self.assertEqual(table.height, 2)

    def test_get_values(self):
        self.assertEqual(
            self.table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7],
            ],
        )

    def test_set_table_values_with_clear(self):
        table = self.table.clone
        values = [
            ["a", "b", "c", "d", "e", "f", "g"],
            ["h", "i", "j", "k", "l", "m", "n"],
            ["o", "p", "q", "r", "s", "t", "u"],
            ["v", "w", "x", "y", "z", "aa", "ab"],
        ]
        table.clear()
        table.set_values(values)
        self.assertEqual(table.get_values(), values)

    def test_set_table_values_big(self):
        table = self.table.clone
        values = [
            ["a", "b", "c", "d", "e", "f", "g"],
            ["h", "i", "j", "k", "l", "m", "n"],
            ["o", "p", "q", "r", "s", "t", "u"],
            ["o", "p", "q", "r", "s", "t", "u"],
            ["o", "p", "q", "r", "s", "t", "u"],
            ["o", "p", "q", "r", "s", "t", "u"],
            ["v", "w", "x", "y", "z", "aa", "ab"],
            ["v", "w", "x", "y", "z", "aa", "ab"],
        ]
        table.set_values(values)
        self.assertEqual(table.get_values(), values)
        self.assertEqual(table.size, (7, 8))

    def test_set_table_values_small(self):
        table = self.table.clone
        values = [
            ["a", "b", "c"],
            ["h", "i", "j", "k", "l", "m", "n"],
            ["o", "p", None, None, "s", "t", "u"],
        ]
        table.set_values(values)
        self.assertEqual(table.size, (7, 4))
        self.assertEqual(
            table.get_values(),
            [
                ["a", "b", "c", 2, 3, 3, 3],
                ["h", "i", "j", "k", "l", "m", "n"],
                ["o", "p", None, None, "s", "t", "u"],
                [1, 2, 3, 4, 5, 6, 7],
            ],
        )

    def test_set_table_values_small_coord(self):
        table = self.table.clone
        values = [
            ["a", "b", "c"],
            ["h", "i", "j", "k", "l", "m", "n"],
            ["o", "p", None, None, "s", "t", "u"],
        ]
        table.set_values(values, coord=("c2"))
        self.assertEqual(table.size, (9, 4))
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3, None, None],
                [1, 1, "a", "b", "c", 3, 3, None, None],
                [1, 1, "h", "i", "j", "k", "l", "m", "n"],
                [1, 2, "o", "p", None, None, "s", "t", "u"],
            ],
        )

    def test_set_table_values_small_coord_far(self):
        table = self.table.clone
        values = [["a", "b", "c"], ["h", None], ["o"]]
        table.set_values(values, coord=("J6"))
        self.assertEqual(table.size, (12, 8))
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3, None, None, None, None, None],
                [1, 1, 1, 2, 3, 3, 3, None, None, None, None, None],
                [1, 1, 1, 2, 3, 3, 3, None, None, None, None, None],
                [1, 2, 3, 4, 5, 6, 7, None, None, None, None, None],
                [
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ],
                [None, None, None, None, None, None, None, None, None, "a", "b", "c"],
                [None, None, None, None, None, None, None, None, None, "h", None, None],
                [None, None, None, None, None, None, None, None, None, "o", None, None],
            ],
        )

    def test_set_table_values_small_type(self):
        table = self.table.clone
        values = [[10, None, 30], [None, 40]]
        table.set_values(values, coord=("C4"), cell_type="percentage")
        self.assertEqual(table.size, (7, 5))
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 2, 10, None, 30, 6, 7],
                [None, None, None, 40, None, None, None],
            ],
        )
        self.assertEqual(
            table.get_values(coord="4:", get_type=True),
            [
                [
                    (1, "float"),
                    (2, "float"),
                    (10, "percentage"),
                    (None, None),
                    (30, "percentage"),
                    (6, "float"),
                    (7, "float"),
                ],
                [
                    (None, None),
                    (None, None),
                    (None, None),
                    (40, "percentage"),
                    (None, None),
                    (None, None),
                    (None, None),
                ],
            ],
        )

    def test_rstrip_table(self):
        document = Document("samples/styled_table.ods")
        table = document.body.get_table(name="Feuille1").clone
        table.rstrip()
        self.assertEqual(table.size, (5, 9))

    # simpletable :
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1   2	3	4	5	6	7

    def test_table_transpose(self):
        table = self.table.clone
        table.transpose()
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 1],
                [1, 1, 1, 2],
                [1, 1, 1, 3],
                [2, 2, 2, 4],
                [3, 3, 3, 5],
                [3, 3, 3, 6],
                [3, 3, 3, 7],
            ],
        )

    def test_table_transpose_2(self):
        table = self.table.clone
        table.transpose("A1:G1")
        self.assertEqual(
            table.get_values(),
            [
                [1, None, None, None, None, None, None],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [2, 2, 3, 4, 5, 6, 7],
                [3, None, None, None, None, None, None],
                [3, None, None, None, None, None, None],
                [3, None, None, None, None, None, None],
            ],
        )

    def test_table_transpose_3(self):
        table = self.table.clone
        table.delete_row(3)
        table.delete_row(2)
        table.delete_row(1)
        table.transpose()
        self.assertEqual(table.get_values(), [[1], [1], [1], [2], [3], [3], [3]])

    def test_table_transpose_4(self):
        table = self.table.clone
        table.transpose("F2:F4")
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3, None],
                [1, 1, 1, 2, 3, 3, 3, 6],
                [1, 1, 1, 2, 3, None, 3, None],
                [1, 2, 3, 4, 5, None, 7, None],
            ],
        )


class TestTableCellSpan(TestCase):
    # simpletable :
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1   2	3	4	5	6	7

    def setUp(self):
        document = Document("samples/simple_table.ods")
        self.body = body = document.body
        self.table = body.get_table(name="Example1")
        self.table2 = self.table.clone
        self.table2.set_value("a1", "a")
        self.table2.set_value("b1", "b")
        self.table2.set_value("d1", "d")
        self.table2.set_value("b2", "")
        self.table2.set_value("c2", "C")
        self.table2.set_value("d2", "")

    def test_span_bad1(self):
        table = self.table.clone
        self.assertEqual(table.set_span("a1:a1"), False)

    def test_span_sp1(self):
        table = self.table.clone
        table.set_span("a1:a2")
        # span change only display
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7],
            ],
        )
        for coord in ("a1", "a2"):
            self.assertEqual(table.get_cell(coord)._is_spanned(), True)
        for coord in ("b1", "b2", "a3"):
            self.assertEqual(table.get_cell(coord)._is_spanned(), False)
        self.assertEqual(table.set_span("a1:a2"), False)
        self.assertEqual(table.del_span("a1:a2"), True)
        self.assertEqual(table.del_span("a1:a2"), False)
        for coord in ("a1", "a2"):
            self.assertEqual(table.get_cell(coord)._is_spanned(), False)

    def test_span_sp1_merge(self):
        table = self.table2.clone
        table.set_span("a1:a2", merge=True)
        # span change only display
        self.assertEqual(
            table.get_values(),
            [
                ["a 1", "b", 1, "d", 3, 3, 3],
                [None, "", "C", "", 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7],
            ],
        )
        for coord in ("a1", "a2"):
            self.assertEqual(table.get_cell(coord)._is_spanned(), True)
        for coord in ("b1", "b2", "a3"):
            self.assertEqual(table.get_cell(coord)._is_spanned(), False)
        self.assertEqual(table.set_span("a1:a2"), False)
        self.assertEqual(table.del_span("a1:a2"), True)
        self.assertEqual(table.del_span("a1:a2"), False)
        for coord in ("a1", "a2"):
            self.assertEqual(table.get_cell(coord)._is_spanned(), False)

    def test_span_sp2(self):
        table = self.table.clone
        zone = "a1:b3"
        table.set_span(zone)
        # span change only display
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7],
            ],
        )
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [True, True, False, False, False, False, False],
                [True, True, False, False, False, False, False],
                [True, True, False, False, False, False, False],
                [False, False, False, False, False, False, False],
            ],
        )
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
            ],
        )

    def test_span_sp2_merge(self):
        table = self.table2.clone
        zone = "a1:b3"
        table.set_span(zone, merge=True)
        # span change only display
        self.assertEqual(
            table.get_values(),
            [
                ["a b 1 1 1", None, 1, "d", 3, 3, 3],
                [None, None, "C", "", 3, 3, 3],
                [None, None, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7],
            ],
        )
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [True, True, False, False, False, False, False],
                [True, True, False, False, False, False, False],
                [True, True, False, False, False, False, False],
                [False, False, False, False, False, False, False],
            ],
        )
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
            ],
        )

    def test_span_sp3(self):
        table = self.table.clone
        zone = "c1:c3"
        table.set_span(zone)
        # span change only display
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7],
            ],
        )
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, True, False, False, False, False],
                [False, False, True, False, False, False, False],
                [False, False, True, False, False, False, False],
                [False, False, False, False, False, False, False],
            ],
        )
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
            ],
        )

    # table 2
    # [[u'a', u'b', 1, u'd', 3, 3, 3],
    # [1, u'', u'C', u'', 3, 3, 3],
    # [1, 1, 1, 2, 3, 3, 3],
    # [1, 2, 3, 4, 5, 6, 7]])

    def test_span_sp3_merge(self):
        table = self.table2.clone
        zone = "c1:c3"
        table.set_span(zone, merge=True)
        # span change only display
        self.assertEqual(
            table.get_values(),
            [
                ["a", "b", "1 C 1", "d", 3, 3, 3],
                [1, "", None, "", 3, 3, 3],
                [1, 1, None, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7],
            ],
        )
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, True, False, False, False, False],
                [False, False, True, False, False, False, False],
                [False, False, True, False, False, False, False],
                [False, False, False, False, False, False, False],
            ],
        )
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
            ],
        )

    def test_span_sp4(self):
        table = self.table.clone
        zone = "g1:g4"
        table.set_span(zone)
        # span change only display
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7],
            ],
        )
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, True],
                [False, False, False, False, False, False, True],
                [False, False, False, False, False, False, True],
                [False, False, False, False, False, False, True],
            ],
        )
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
            ],
        )

    def test_span_sp4(self):
        table = self.table2.clone
        zone = "g1:g4"
        table.set_span(zone, merge=True)
        # span change only display
        self.assertEqual(
            table.get_values(),
            [
                ["a", "b", 1, "d", 3, 3, "3 3 3 7"],
                [1, "", "C", "", 3, 3, None],
                [1, 1, 1, 2, 3, 3, None],
                [1, 2, 3, 4, 5, 6, None],
            ],
        )
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, True],
                [False, False, False, False, False, False, True],
                [False, False, False, False, False, False, True],
                [False, False, False, False, False, False, True],
            ],
        )
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
            ],
        )

    def test_span_sp5(self):
        table = self.table.clone
        zone = "a3:c4"
        table.set_span(zone)
        # span change only display
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7],
            ],
        )
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [True, True, True, False, False, False, False],
                [True, True, True, False, False, False, False],
            ],
        )
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
            ],
        )

    def test_span_sp5_merge(self):
        table = self.table2.clone
        zone = "a3:c4"
        table.set_span(zone, merge=True)
        # span change only display
        self.assertEqual(
            table.get_values(),
            [
                ["a", "b", 1, "d", 3, 3, 3],
                [1, "", "C", "", 3, 3, 3],
                ["1 1 1 1 2 3", None, None, 2, 3, 3, 3],
                [None, None, None, 4, 5, 6, 7],
            ],
        )
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [True, True, True, False, False, False, False],
                [True, True, True, False, False, False, False],
            ],
        )
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
            ],
        )

    def test_span_sp6(self):
        table = self.table.clone
        zone = "b3:f3"
        table.set_span(zone)
        # span change only display
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7],
            ],
        )
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, True, True, True, True, True, False],
                [False, False, False, False, False, False, False],
            ],
        )
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
            ],
        )

    def test_span_sp6_2zone(self):
        table = self.table.clone
        zone = "b3:f3"
        table.set_span(zone)
        # span change only display
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7],
            ],
        )
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, True, True, True, True, True, False],
                [False, False, False, False, False, False, False],
            ],
        )
        zone2 = "a2:a4"
        table.set_span(zone2)
        # span change only display
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7],
            ],
        )
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [True, False, False, False, False, False, False],
                [True, True, True, True, True, True, False],
                [True, False, False, False, False, False, False],
            ],
        )
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [True, False, False, False, False, False, False],
                [True, False, False, False, False, False, False],
                [True, False, False, False, False, False, False],
            ],
        )
        self.assertEqual(table.del_span(zone2), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
            ],
        )

    def test_span_bigger(self):
        table = self.table.clone
        zone = "e2:i4"
        table.set_span(zone)
        # span change only display
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3, None, None],
                [1, 1, 1, 2, 3, 3, 3, None, None],
                [1, 1, 1, 2, 3, 3, 3, None, None],
                [1, 2, 3, 4, 5, 6, 7, None, None],
            ],
        )
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [False, False, False, False, True, True, True, True, True],
                [False, False, False, False, True, True, True, True, True],
                [False, False, False, False, True, True, True, True, True],
            ],
        )
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False, False, False],
            ],
        )

    def test_span_bigger_merge(self):
        table = self.table.clone
        zone = "f4:f5"
        table.set_span(zone, merge=True)
        # span change only display
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7],
                [None, None, None, None, None, None, None],
            ],
        )
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, True, False],
                [False, False, False, False, False, True],
            ],
        )
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False],
            ],
        )

    def test_span_bigger_outside(self):
        table = self.table.clone
        zone = "g6:i7"
        table.set_span(zone)
        # span change only display
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3, None, None],
                [1, 1, 1, 2, 3, 3, 3, None, None],
                [1, 1, 1, 2, 3, 3, 3, None, None],
                [1, 2, 3, 4, 5, 6, 7, None, None],
                [None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None],
            ],
        )
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [],
                [False, False, False, False, False, False, True, True, True],
                [False, False, False, False, False, False, True, True, True],
            ],
        )
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [],
                [False, False, False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False, False, False],
            ],
        )

    def test_span_bigger_outside_merge(self):
        table = self.table.clone
        zone = "g6:i7"
        table.set_span(zone, merge=True)
        # span change only display
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3, None, None],
                [1, 1, 1, 2, 3, 3, 3, None, None],
                [1, 1, 1, 2, 3, 3, 3, None, None],
                [1, 2, 3, 4, 5, 6, 7, None, None],
                [None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None],
            ],
        )
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [],
                [False, False, False, False, False, False, True, True, True],
                [False, False, False, False, False, False, True, True, True],
            ],
        )
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(
            res,
            [
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False],
                [],
                [False, False, False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False, False, False],
            ],
        )


class TestTableGetValues(TestCase):

    #    simpletable :
    #      1	1	1	2	3	3	3
    #      1	1	1	2	3	3	3       self.row
    #      1	1	1	2	3	3	3
    #      1    2	3	4	5	6	7

    def setUp(self):
        document = Document("samples/simple_table.ods")
        body = document.body
        self.table = body.get_table(name="Example1").clone
        self.row_repeats = self.table.get_row(0)
        self.row = self.table.get_row(1)

    def test_on_empty_table(self):
        table = Table("Table")
        self.assertEqual(table.get_values(), [])
        self.assertEqual(table.get_values(complete=True), [])
        self.assertEqual(table.get_values(complete=True, get_type=True), [])
        self.assertEqual(table.get_values((0, 10)), [])
        self.assertEqual(table.get_values(cell_type="all"), [])
        self.assertEqual(table.get_values(cell_type="All"), [])
        self.assertEqual(table.get_values((2, 3), complete=True), [])

    def test_get_values_count(self):
        self.assertEqual(len(self.table.get_values()), 4)  # 4 rows
        self.assertEqual(
            len(self.table.get_values(cell_type="All", complete=False)), 4
        )  # same
        self.assertEqual(
            len(self.table.get_values(cell_type="All", complete=True)), 4
        )  # 4 lines result
        self.assertEqual(
            len(self.table.get_values(cell_type="All", flat=True)), 28
        )  # flat
        self.assertEqual(len(self.table.get_values(flat=True)), 28)  # flat

    def test_get_values_coord_1(self):
        table = self.table
        result = [
            [1, 1, 1, 2, 3, 3, 3],
            [1, 1, 1, 2, 3, 3, 3],
            [1, 1, 1, 2, 3, 3, 3],
            [1, 2, 3, 4, 5, 6, 7],
        ]
        self.assertEqual(table.get_values(), result)
        self.assertEqual(table.get_values((0, 0, 6, 3)), result)
        self.assertEqual(table.get_values((0, 3)), result)
        self.assertEqual(table.get_values((0, None, 6, None)), result)
        self.assertEqual(table.get_values((None, None, 6, 20)), result)
        self.assertEqual(table.get_values((0, 0, None, None)), result)
        self.assertEqual(table.get_values((None, 0, 10, None)), result)
        self.assertEqual(table.get_values(""), result)
        self.assertEqual(table.get_values(":"), result)
        self.assertEqual(table.get_values("A1:G4"), result)
        self.assertEqual(table.get_values("A1:"), result)
        self.assertEqual(table.get_values("1:4"), result)
        self.assertEqual(table.get_values("1:4"), result)
        self.assertEqual(table.get_values("1:"), result)
        self.assertEqual(table.get_values("1:10"), result)
        self.assertEqual(table.get_values(":10"), result)
        self.assertEqual(table.get_values("A:"), result)
        self.assertEqual(table.get_values(":G"), result)
        self.assertEqual(table.get_values("1:H"), result)

    def test_get_values_coord_2(self):
        table = self.table
        result = [[1, 1, 1, 2, 3, 3, 3], [1, 2, 3, 4, 5, 6, 7]]
        self.assertEqual(table.get_values((0, 2, 7, 3)), result)
        self.assertEqual(table.get_values((2, 3)), result)
        self.assertEqual(table.get_values((0, 2, 6, None)), result)
        self.assertEqual(table.get_values((None, 2, None, 20)), result)
        self.assertEqual(table.get_values((None, 2, None, None)), result)
        self.assertEqual(table.get_values((None, 2, 10, None)), result)
        self.assertEqual(table.get_values("A3:G4"), result)
        self.assertEqual(table.get_values("A3:"), result)
        self.assertEqual(table.get_values("3:4"), result)
        self.assertEqual(table.get_values("3:"), result)
        self.assertEqual(table.get_values("3:10"), result)
        self.assertEqual(table.get_values("A3:"), result)
        self.assertEqual(table.get_values("3:G"), result)
        self.assertEqual(table.get_values("3:H"), result)

    def test_get_values_coord_3(self):
        table = self.table
        result = [[1, 1], [1, 1]]
        self.assertEqual(table.get_values((0, 0, 1, 1)), result)
        self.assertEqual(table.get_values((None, 0, 1, 1)), result)
        self.assertEqual(table.get_values((None, None, 1, 1)), result)
        self.assertEqual(table.get_values("A1:B2"), result)
        self.assertEqual(table.get_values(":B2"), result)

    def test_get_values_coord_4(self):
        table = self.table
        result = [[3, 3], [6, 7]]
        self.assertEqual(table.get_values("F3:G4"), result)
        self.assertEqual(table.get_values("F3:"), result)
        self.assertEqual(table.get_values("F3:RR555"), result)

    def test_get_values_coord_5(self):
        table = self.table
        result = [[2, 3], [2, 3], [2, 3], [4, 5]]
        self.assertEqual(table.get_values("D1:E4"), result)
        self.assertEqual(table.get_values("D:E"), result)
        self.assertEqual(table.get_values("D1:E555"), result)

    def test_get_values_coord_5_flat(self):
        table = self.table
        result = [2, 3, 2, 3, 2, 3, 4, 5]
        self.assertEqual(table.get_values("D1:E4", flat=True), result)

    def test_get_values_coord_6(self):
        table = self.table
        result = [[5]]
        self.assertEqual(table.get_values("E4"), result)
        self.assertEqual(table.get_values("E4:E4"), result)

    def test_get_values_coord_6_flat(self):
        table = self.table
        result = [5]
        self.assertEqual(table.get_values("E4", flat=True), result)

    def test_get_values_coord_7(self):
        table = self.table
        result = []
        self.assertEqual(table.get_values("E5"), result)
        self.assertEqual(table.get_values("B3:A1"), result)

    def test_get_values_cell_type(self):
        table = self.table
        result = [
            [1, 1, 1, 2, 3, 3, 3],
            [1, 1, 1, 2, 3, 3, 3],
            [1, 1, 1, 2, 3, 3, 3],
            [1, 2, 3, 4, 5, 6, 7],
        ]
        values = table.get_values(cell_type="all")
        self.assertEqual(values, result)
        values = table.get_values(cell_type="float")
        self.assertEqual(values, result)

    def test_get_values_cell_type_no_comp(self):
        table = self.table
        result = [
            1,
            1,
            1,
            2,
            3,
            3,
            3,
            1,
            1,
            1,
            2,
            3,
            3,
            3,
            1,
            1,
            1,
            2,
            3,
            3,
            3,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
        ]
        values = table.get_values(cell_type="all", complete=True, flat=True)
        self.assertEqual(values, result)
        values = table.get_values(cell_type="float", complete=False, flat=True)
        self.assertEqual(values, result)

    def test_get_values_cell_type_1(self):
        table = self.table
        result = [
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
        ]
        values = table.get_values(cell_type="percentage")
        self.assertEqual(values, result)

    def test_get_values_cell_type_1_flat(self):
        table = self.table
        result = [
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ]
        values = table.get_values(cell_type="percentage", flat=True)
        self.assertEqual(values, result)

    def test_get_values_cell_type_1_no_comp_flat(self):
        table = self.table
        result = []
        values = table.get_values(cell_type="percentage", complete=False, flat=True)
        self.assertEqual(values, result)

    def test_get_values_cell_type_1_no_comp(self):
        table = self.table
        result = [[], [], [], []]
        values = table.get_values(cell_type="percentage", complete=False)
        self.assertEqual(values, result)

    def test_get_values_cell_type2_with_hole(self):
        row = self.row.clone
        row.append_cell(Cell(value="bob"), clone=False)
        row.append_cell(Cell(value=14, cell_type="percentage"))
        row.append_cell(Cell(value="bob2"), clone=False)
        row.set_cell(12, Cell(value="far"), clone=False)
        table = self.table.clone
        table.append_row(row)
        result = [
            [1, 1, 1, 2, 3, 3, 3, None, None, None, None, None, None],
            [1, 1, 1, 2, 3, 3, 3, None, None, None, None, None, None],
            [1, 1, 1, 2, 3, 3, 3, None, None, None, None, None, None],
            [1, 2, 3, 4, 5, 6, 7, None, None, None, None, None, None],
            [1, 1, 1, 2, 3, 3, 3, "bob", 14, "bob2", None, None, "far"],
        ]
        self.assertEqual(table.get_values(), result)
        self.assertEqual(table.get_values("A4:z4"), [result[3]])
        self.assertEqual(table.get_values("5:5"), [result[4]])

    def test_get_values_cell_type2_with_hole_no_comp(self):
        row = self.row.clone
        row.append_cell(Cell(value="bob"), clone=False)
        row.append_cell(Cell(value=14, cell_type="percentage"))
        row.append_cell(Cell(value="bob2"), clone=False)
        row.set_cell(12, Cell(value="far"), clone=False)
        table = self.table.clone
        table.append_row(row)
        result = [
            [1, 1, 1, 2, 3, 3, 3],
            [1, 1, 1, 2, 3, 3, 3],
            [1, 1, 1, 2, 3, 3, 3],
            [1, 2, 3, 4, 5, 6, 7],
            [1, 1, 1, 2, 3, 3, 3, "bob", 14, "bob2", None, None, "far"],
        ]
        self.assertEqual(table.get_values(complete=False), result)
        self.assertEqual(table.get_values("A4:z4", complete=False), [result[3]])
        self.assertEqual(table.get_values("5:5", complete=False), [result[4]])

    def test_get_values_cell_type2_with_hole_no_comp_flat(self):
        row = self.row.clone
        row.append_cell(Cell(value="bob"), clone=False)
        row.append_cell(Cell(value=14, cell_type="percentage"))
        row.append_cell(Cell(value="bob2"), clone=False)
        row.set_cell(12, Cell(value="far"), clone=False)
        table = self.table.clone
        table.append_row(row)
        result = [
            1,
            1,
            1,
            2,
            3,
            3,
            3,
            1,
            1,
            1,
            2,
            3,
            3,
            3,
            1,
            1,
            1,
            2,
            3,
            3,
            3,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            1,
            1,
            1,
            2,
            3,
            3,
            3,
            "bob",
            14,
            "bob2",
            None,
            None,
            "far",
        ]
        result2 = [1, 2, 3, 4, 5, 6, 7]
        result3 = [1, 1, 1, 2, 3, 3, 3, "bob", 14, "bob2", None, None, "far"]
        self.assertEqual(
            table.get_values(
                complete=False,
                flat=True,
            ),
            result,
        )
        self.assertEqual(table.get_values("A4:z4", flat=True, complete=False), result2)
        self.assertEqual(table.get_values("5:5", flat=True, complete=False), result3)

    def test_get_values_cell_type2_with_hole_get_type(self):
        row = self.row.clone
        row.append_cell(Cell(value="bob"), clone=False)
        row.append_cell(Cell(value=14, cell_type="percentage"))
        row.append_cell(Cell(value="bob2"), clone=False)
        row.set_cell(12, Cell(value="far"), clone=False)
        table = self.table.clone
        table.append_row(row)
        result1 = [[1, 1, 1, 2, 3, 3, 3, None, None, None, None, None, None]]
        result2 = [
            [
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                "bob",
                None,
                "bob2",
                None,
                None,
                "far",
            ]
        ]

        self.assertEqual(table.get_values("5:5", cell_type="string"), result2)

        self.assertEqual(
            table.get_values("5:5", cell_type="string", complete=False, flat=True),
            ["bob", "bob2", "far"],
        )

        self.assertEqual(
            table.get_values(
                "5:5", cell_type="string", complete=False, flat=True, get_type=True
            ),
            [("bob", "string"), ("bob2", "string"), ("far", "string")],
        )

        self.assertEqual(
            table.get_values(coord="4:5", cell_type="All", get_type=True),
            [
                [
                    (1, "float"),
                    (2, "float"),
                    (3, "float"),
                    (4, "float"),
                    (5, "float"),
                    (6, "float"),
                    (7, "float"),
                    (None, None),
                    (None, None),
                    (None, None),
                    (None, None),
                    (None, None),
                    (None, None),
                ],
                [
                    (1, "float"),
                    (1, "float"),
                    (1, "float"),
                    (2, "float"),
                    (3, "float"),
                    (3, "float"),
                    (3, "float"),
                    ("bob", "string"),
                    (14, "percentage"),
                    ("bob2", "string"),
                    (None, None),
                    (None, None),
                    ("far", "string"),
                ],
            ],
        )

        self.assertEqual(
            table.get_values(
                coord="4:5", cell_type="All", get_type=True, complete=False
            ),
            [
                [
                    (1, "float"),
                    (2, "float"),
                    (3, "float"),
                    (4, "float"),
                    (5, "float"),
                    (6, "float"),
                    (7, "float"),
                ],
                [
                    (1, "float"),
                    (1, "float"),
                    (1, "float"),
                    (2, "float"),
                    (3, "float"),
                    (3, "float"),
                    (3, "float"),
                    ("bob", "string"),
                    (14, "percentage"),
                    ("bob2", "string"),
                    ("far", "string"),
                ],
            ],
        )

        self.assertEqual(
            table.get_values(coord="4:5", cell_type="string", get_type=True),
            [
                [
                    (None, None),
                    (None, None),
                    (None, None),
                    (None, None),
                    (None, None),
                    (None, None),
                    (None, None),
                    (None, None),
                    (None, None),
                    (None, None),
                    (None, None),
                    (None, None),
                    (None, None),
                ],
                [
                    (None, None),
                    (None, None),
                    (None, None),
                    (None, None),
                    (None, None),
                    (None, None),
                    (None, None),
                    ("bob", "string"),
                    (None, None),
                    ("bob2", "string"),
                    (None, None),
                    (None, None),
                    ("far", "string"),
                ],
            ],
        )

        self.assertEqual(
            table.get_values(
                coord="4:5", cell_type="string", get_type=True, complete=False
            ),
            [[], [("bob", "string"), ("bob2", "string"), ("far", "string")]],
        )

        self.assertEqual(
            table.get_values(
                coord="4:J5", cell_type="string", get_type=True, complete=False
            ),
            [
                [],
                [
                    ("bob", "string"),
                    ("bob2", "string"),
                ],
            ],
        )


class TestTableCache(TestCase):
    def setUp(self):
        document = Document("samples/simple_table.ods")
        self.body = body = document.body
        self.table = body.get_table(name="Example1")

    def test_empty_row_repeat(self):
        row = Row(repeated=5)
        table = self.table.clone
        table.insert_row(2, row)
        value = table.get_value((3, 3))
        self.assertEqual(value, None)
        cell = table.get_cell((4, 5))
        self.assertEqual(cell.x, 4)
        self.assertEqual(cell.y, 5)
        values = table.get_row_values(1)
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3])
        values = table.get_row_values(2)
        self.assertEqual(values, [None, None, None, None, None, None, None])
        values = table.get_row_values(6)
        self.assertEqual(values, [None, None, None, None, None, None, None])
        values = table.get_row_values(7)
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3])
        self.assertEqual(table.height, 9)

    def test_row_repeat_twice(self):
        row = Row(repeated=6)
        table = self.table.clone
        table.insert_row(2, row)
        cell = Cell(value=333, repeated=2)
        self.assertEqual(cell.x, None)
        self.assertEqual(cell.y, None)
        row = Row()
        row.insert_cell(4, cell)
        self.assertEqual(row.get_values(), [None, None, None, None, 333, 333])
        self.assertEqual(row.width, 6)
        row.repeated = 3
        table.set_row(4, row)
        self.assertEqual(
            table.height,
            4 + 6 + 3 - 3,  # initial height  # *insert* row with repeated 5
        )  # *set* row with repeated 3
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None],
                [None, None, None, None, 333, 333, None],
                [None, None, None, None, 333, 333, None],
                [None, None, None, None, 333, 333, None],
                [None, None, None, None, None, None, None],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7],
            ],
        )
        row = table.get_row(6)
        self.assertEqual(row.get_values(), [None, None, None, None, 333, 333])
        self.assertEqual(row.width, 6)
        cell = row.get_cell(5)
        self.assertEqual(cell.x, 5)
        self.assertEqual(cell.y, 6)
        self.assertEqual(cell.get_value(), 333)

    def test_cell_repeat(self):
        cell = Cell(value=55, repeated=5)
        table = self.table.clone
        table.insert_cell((2, 2), cell)
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3, None, None, None, None, None],
                [1, 1, 1, 2, 3, 3, 3, None, None, None, None, None],
                [1, 1, 55, 55, 55, 55, 55, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7, None, None, None, None, None],
            ],
        )
        self.assertEqual(table.width, 12)

    def test_clear_cache(self):
        table = self.table.clone
        table.clear()
        self.assertEqual(table.width, 0)
        self.assertEqual(table.height, 0)

    def test_lonely_cell_add_cache(self):
        table = self.table.clone
        table.clear()
        table.set_value((6, 7), 1)
        self.assertEqual(table.width, 7)
        self.assertEqual(table.height, 8)
        cell = table.get_cell((6, 7))
        self.assertEqual(cell.x, 6)
        self.assertEqual(cell.y, 7)
        self.assertEqual(cell.get_value(), 1)

    def test_basic_spreadsheet_case(self):
        table = Table("Table", width=20, height=3)
        for r in range(2):
            table.append_row()
        self.assertEqual(len(table.get_rows()), 5)
        vals = []
        for row in table.get_rows():
            vals.append(len(row.get_cells()))
        self.assertEqual(vals, [20, 20, 20, 0, 0])
        last_row = table.get_row(-1)
        for r in range(3):
            for c in range(10):
                table.set_value((c, r), "cell %s %s" % (c, r))
        for r in range(3, 5):
            for c in range(10):
                table.set_value((c, r), c * 100 + r)
        self.assertEqual(table.size, (20, 5))
        table.rstrip()
        self.assertEqual(table.size, (10, 5))
        self.assertEqual(len(table.get_row(-1).get_cells()), 10)


class TestTableRow(TestCase):
    def setUp(self):
        document = Document("samples/simple_table.ods")
        self.table = document.body.get_table(name="Example1")

    def test_traverse_rows(self):
        self.assertEqual(len(list(self.table.traverse())), 4)

    def test_get_row_values(self):
        self.assertEqual(self.table.get_row_values(3), [1, 2, 3, 4, 5, 6, 7])

    def test_get_row_list(self):
        self.assertEqual(len(list(self.table.get_rows())), 4)
        self.assertEqual(len(list(self.table.get_rows("2:3"))), 2)

    def test_get_row_list_regex(self):
        coordinates = [row.y for row in self.table.get_rows(content=r"4")]
        self.assertEqual(coordinates, [3])

    def test_get_row_list_style(self):
        table = self.table.clone
        # Set a different style manually
        row = table.get_elements("table:table-row")[2]
        row.style = "A Style"
        coordinates = [row.y for row in table.get_rows(style=r"A Style")]
        self.assertEqual(coordinates, [2])

    def test_get_row(self):
        row = self.table.get_row(3)
        self.assertEqual(row.get_values(), [1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(row.y, 3)

    def test_get_row_repeat(self):
        table = self.table.clone
        # Set a repetition manually
        table.get_elements("table:table-row")[1].repeated = 2
        row = table.get_row(4)
        self.assertEqual(row.get_values(), [1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(row.y, 4)

    def test_set_row(self):
        table = self.table.clone
        row = table.get_row(3)
        row.set_value(3, "Changed")
        row_back = table.set_row(1, row)
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3],
                [1, 2, 3, "Changed", 5, 6, 7],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7],
            ],
        )
        # test columns are synchronized
        self.assertEqual(table.width, 7)
        self.assertEqual(row_back.y, 1)

    def test_set_row_repeat(self):
        table = self.table.clone
        # Set a repetition manually
        table.get_elements("table:table-row")[2].repeated = 3
        row = table.get_row(5)
        row.set_value(3, "Changed")
        table.set_row(2, row)
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 2, 3, "Changed", 5, 6, 7],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7],
            ],
        )
        # test columns are synchronized
        self.assertEqual(table.width, 7)

    def test_set_row_smaller(self):
        table = self.table.clone
        table.set_row(0, Row(width=table.width - 1))
        self.assertEqual(table.height, 4)

    def test_set_row_bigger(self):
        table = self.table.clone
        table.set_row(0, Row(width=table.width + 1))
        self.assertEqual(table.height, 4)

    def test_insert(self):
        table = self.table.clone
        row = table.insert_row(2)
        self.assertTrue(type(row) is Row)
        self.assertEqual(row.y, 2)

    def test_insert_row(self):
        table = self.table.clone
        row = table.get_row(3)
        row_back = table.insert_row(2, row)
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7],
            ],
        )
        # test columns are synchronized
        self.assertEqual(table.width, 7)
        self.assertEqual(row_back.y, 2)

    def test_insert_row_repeated(self):
        table = self.table.clone
        # Set a repetition manually
        table.get_elements("table:table-row")[2].repeated = 3
        row = table.get_row(5)
        table.insert_row(2, row)
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7],
            ],
        )
        # test columns are synchronized
        self.assertEqual(table.width, 7)

    def test_insert_row_smaller(self):
        table = self.table.clone
        small_row = Row(width=table.width - 1)
        table.insert_row(0, small_row)
        self.assertEqual(table.height, 5)

    def test_insert_row_bigger(self):
        table = self.table.clone
        big_row = Row(width=table.width + 1)
        table.insert_row(0, big_row)
        self.assertEqual(table.height, 5)

    def test_append(self):
        table = self.table.clone
        row = table.append_row()
        self.assertTrue(type(row) is Row)

    def test_append_row(self):
        table = self.table.clone
        row = table.get_row(0)
        row_back = table.append_row(row)
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7],
                [1, 1, 1, 2, 3, 3, 3],
            ],
        )
        # test columns are synchronized
        self.assertEqual(table.width, 7)
        self.assertEqual(row_back.y, table.height - 1)

    def test_append_row_smaller(self):
        table = self.table.clone
        table.append_row(Row(width=table.width - 1))
        self.assertEqual(table.height, 5)

    def test_append_row_bigger(self):
        table = self.table.clone
        table.append_row(Row(width=table.width + 1))
        self.assertEqual(table.height, 5)

    def test_delete_row(self):
        table = self.table.clone
        table.delete_row(2)
        self.assertEqual(
            table.get_values(),
            [[1, 1, 1, 2, 3, 3, 3], [1, 1, 1, 2, 3, 3, 3], [1, 2, 3, 4, 5, 6, 7]],
        )
        # test columns are synchronized
        self.assertEqual(table.width, 7)

    def test_delete_row_repeat(self):
        table = self.table.clone
        # Set a repetition manually
        table.get_elements("table:table-row")[2].repeated = 3
        table.delete_row(2)
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7],
            ],
        )
        # Test columns are synchronized
        self.assertEqual(table.width, 7)

    def test_is_row_empty(self):
        table = Table("Empty", width=10, height=20)
        for y in range(20):
            self.assertEqual(table.is_row_empty(y), True)

    def test_is_row_empty_no(self):
        table = Table("Not Empty", width=10, height=20)
        table.set_value((4, 9), "Bouh !")
        self.assertEqual(table.is_row_empty(9), False)


class TestTableCell(TestCase):
    def setUp(self):
        document = Document("samples/simple_table.ods")
        body = document.body
        self.table = body.get_table(name="Example1").clone

    def test_get_cell_alpha(self):
        table = self.table
        cell = table.get_cell("D3")
        self.assertEqual(cell.get_value(), 2)
        self.assertEqual(cell.text_content, "2")
        self.assertEqual(cell.type, "float")
        self.assertEqual(cell.style, "ce5")
        self.assertEqual(cell.x, 3)
        self.assertEqual(cell.y, 2)

    def test_get_cell_tuple(self):
        table = self.table
        cell = table.get_cell((3, 2))
        self.assertEqual(cell.get_value(), 2)
        self.assertEqual(cell.text_content, "2")
        self.assertEqual(cell.type, "float")
        self.assertEqual(cell.style, "ce5")
        self.assertEqual(cell.x, 3)
        self.assertEqual(cell.y, 2)

    def test_set_cell_value(self):
        table = self.table.clone
        table.set_value("D3", "Changed")
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, "Changed", 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7],
            ],
        )

    def test_get_cell_list(self):
        self.assertEqual(len(list(self.table.get_cells(flat=True))), 28)

    def test_get_cell_list_regex(self):
        table = self.table
        coordinates = [
            (cell.x, cell.y) for cell in table.get_cells(content=r"3", flat=True)
        ]
        expected = [
            (4, 0),
            (5, 0),
            (6, 0),
            (4, 1),
            (5, 1),
            (6, 1),
            (4, 2),
            (5, 2),
            (6, 2),
            (2, 3),
        ]
        self.assertEqual(coordinates, expected)

    def test_get_cell_list_style(self):
        table = self.table
        coordinates = [
            (cell.x, cell.y) for cell in table.get_cells(style=r"ce5", flat=True)
        ]
        expected = [(1, 1), (5, 1), (3, 2)]
        self.assertEqual(coordinates, expected)

    def test_insert(self):
        table = self.table.clone
        cell = table.insert_cell("B3")
        self.assertTrue(type(cell) is Cell)
        self.assertEqual(cell.x, 1)
        self.assertEqual(cell.y, 2)

    def test_insert_cell(self):
        table = self.table.clone
        cell = table.insert_cell("B3", Cell("Inserted"))
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3, None],
                [1, 1, 1, 2, 3, 3, 3, None],
                [1, "Inserted", 1, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7, None],
            ],
        )
        # Test columns are synchronized
        self.assertEqual(table.width, 8)
        self.assertEqual(cell.x, 1)
        self.assertEqual(cell.y, 2)

    def test_append(self):
        table = self.table.clone
        cell = table.append_cell(1)
        self.assertTrue(type(cell) is Cell)
        self.assertEqual(cell.x, table.width - 1)

    def test_append_cell(self):
        table = self.table.clone
        cell = table.append_cell(1, Cell("Appended"))
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3, None],
                [1, 1, 1, 2, 3, 3, 3, "Appended"],
                [1, 1, 1, 2, 3, 3, 3, None],
                [1, 2, 3, 4, 5, 6, 7, None],
            ],
        )
        # Test columns are synchronized
        self.assertEqual(table.width, 8)
        self.assertEqual(cell.x, table.width - 1)

    def test_delete_cell(self):
        table = self.table.clone
        table.delete_cell("F3")
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, None],
                [1, 2, 3, 4, 5, 6, 7],
            ],
        )
        # Test columns are synchronized
        self.assertEqual(table.width, 7)


class TestTableNamedRange(TestCase):
    def setUp(self):
        document = Document("samples/simple_table.ods")
        document2 = Document("samples/simple_table_named_range.ods")
        self.body = document.body
        # no clones !
        self.table = self.body.get_table(name="Example1")
        self.body2 = document2.body
        self.table2 = self.body2.get_table(name="Example1")

    def test_create_bad_nr(self):
        self.assertRaises(ValueError, NamedRange)

    def test_create_bad_nr_2(self):
        self.assertRaises(ValueError, NamedRange, " ", "A1", "tname")

    def test_create_bad_nr_3(self):
        self.assertRaises(ValueError, NamedRange, "A1", "A1", "tname")

    def test_create_bad_nr_4(self):
        self.assertRaises(ValueError, NamedRange, "a space", "A1", "tname")

    def test_create_bad_nr_5(self):
        self.assertRaises(ValueError, NamedRange, "===", "A1", "tname")

    def test_create_bad_nr_6(self):
        self.assertRaises(ValueError, NamedRange, "ok", "A1", "/ ")

    def test_create_bad_nr_7(self):
        self.assertRaises(ValueError, NamedRange, "ok", "A1", " ")

    def test_create_bad_nr_8(self):
        self.assertRaises(ValueError, NamedRange, "ok", "A1", "\\")

    def test_create_bad_nr_9(self):
        self.assertRaises(ValueError, NamedRange, "ok", "A1", "tname\nsecond line")

    def test_create_bad_nr_10(self):
        self.assertRaises(ValueError, NamedRange, "ok", "A1", 42)

    def test_create_nr(self):
        nr = NamedRange("nr_name_ù", "A1:C2", "table name é", usage="filter")
        result = """<table:named-range table:name="nr_name_ù" table:base-cell-address="$'table name é'.$A$1" table:cell-range-address="$'table name é'.$A$1:.$C$2" table:range-usable-as="filter"/>"""
        self.assertEqual(nr.serialize(), result)

    def test_usage_1(self):
        nr = NamedRange("a123a", "A1:C2", "tablename")
        self.assertEqual(nr.usage, None)
        nr.set_usage("blob")
        self.assertEqual(nr.usage, None)

    def test_usage_2(self):
        nr = NamedRange("nr_name", "A1:C2", "tablename")
        nr.set_usage("filter")
        self.assertEqual(nr.usage, "filter")
        nr.set_usage("blob")
        self.assertEqual(nr.usage, None)

    def test_usage_3(self):
        nr = NamedRange("nr_name", "A1:C2", "tablename")
        nr.set_usage("Print-Range")
        self.assertEqual(nr.usage, "print-range")
        nr.set_usage(None)
        self.assertEqual(nr.usage, None)

    def test_usage_4(self):
        nr = NamedRange("nr_name", "A1:C2", "tablename")
        nr.set_usage("repeat-column")
        self.assertEqual(nr.usage, "repeat-column")

    def test_usage_5(self):
        nr = NamedRange("nr_name", "A1:C2", "tablename")
        nr.set_usage("repeat-row")
        self.assertEqual(nr.usage, "repeat-row")

    def test_name_1(self):
        nr = NamedRange("nr_name", "A1:C2", "tablename")
        self.assertEqual(nr.name, "nr_name")

    def test_name_2(self):
        nr = NamedRange("nr_name", "A1:C2", "tablename")
        nr.name = "  New_Name_ô "
        self.assertEqual(nr.name, "New_Name_ô")

    def test_name_3(self):
        nr = NamedRange("nr_name", "A1:C2", "tablename")
        try:
            nr.name = "   "
            ok = True
        except:
            ok = False
        self.assertEqual(ok, False)

    def test_table_name_1(self):
        nr = NamedRange("nr_name", "A1:C2", "tablename")
        self.assertEqual(nr.table_name, "tablename")

    def test_table_name_2(self):
        nr = NamedRange("nr_name", "A1:C2", "tablename")
        nr.set_table_name("  new name ")
        self.assertEqual(nr.table_name, "new name")

    def test_table_name_3(self):
        nr = NamedRange("nr_name", "A1:C2", "tablename")
        self.assertRaises(ValueError, nr.set_table_name, "   ")

    def test_range_1(self):
        nr = NamedRange("nr_name", "A1:C2", "tablename")
        self.assertRaises(ValueError, nr.set_range, "   ")

    def test_range_2(self):
        nr = NamedRange("nr_name", "A1:C2", "tablename")
        self.assertEqual(nr.crange, (0, 0, 2, 1))
        self.assertEqual(nr.start, (0, 0))
        self.assertEqual(nr.end, (2, 1))

    def test_range_3(self):
        nr = NamedRange("nr_name", "A1", "tablename")
        self.assertEqual(nr.crange, (0, 0, 0, 0))
        self.assertEqual(nr.start, (0, 0))
        self.assertEqual(nr.end, (0, 0))

    def test_range_4(self):
        nr = NamedRange("nr_name", (1, 2, 3, 4), "tablename")
        self.assertEqual(nr.crange, (1, 2, 3, 4))
        self.assertEqual(nr.start, (1, 2))
        self.assertEqual(nr.end, (3, 4))

    def test_range_5(self):
        nr = NamedRange("nr_name", (5, 6), "tablename")
        self.assertEqual(nr.crange, (5, 6, 5, 6))
        self.assertEqual(nr.start, (5, 6))
        self.assertEqual(nr.end, (5, 6))

    def test_range_6(self):
        nr = NamedRange("nr_name", "A1:C2", "tablename")
        nr.set_range("B3")
        self.assertEqual(nr.crange, (1, 2, 1, 2))
        self.assertEqual(nr.start, (1, 2))
        self.assertEqual(nr.end, (1, 2))

    def test_range_7(self):
        nr = NamedRange("nr_name", "A1:C2", "tablename")
        nr.set_range("B3:b10")
        self.assertEqual(nr.crange, (1, 2, 1, 9))
        self.assertEqual(nr.start, (1, 2))
        self.assertEqual(nr.end, (1, 9))

    def test_range_8(self):
        nr = NamedRange("nr_name", "A1:C2", "tablename")
        nr.set_range((1, 5, 0, 9))
        self.assertEqual(nr.crange, (1, 5, 0, 9))
        self.assertEqual(nr.start, (1, 5))
        self.assertEqual(nr.end, (0, 9))

    def test_range_9(self):
        nr = NamedRange("nr_name", "A1:C2", "tablename")
        nr.set_range((0, 9))
        self.assertEqual(nr.crange, (0, 9, 0, 9))
        self.assertEqual(nr.start, (0, 9))
        self.assertEqual(nr.end, (0, 9))

    def test_value_bad_1(self):
        nr = NamedRange("nr_name", "A1:C2", "tablename")
        self.assertRaises(ValueError, nr.get_values)

    def test_value_bad_2(self):
        nr = NamedRange("nr_name", "A1:C2", "tablename")
        self.assertRaises(ValueError, nr.get_value)

    def test_value_bad_3(self):
        nr = NamedRange("nr_name", "A1:C2", "tablename")
        self.assertRaises(ValueError, nr.set_values, [[1, 2]])

    def test_value_bad_4(self):
        nr = NamedRange("nr_name", "A1:C2", "tablename")
        self.assertRaises(ValueError, nr.set_value, 42)

    def test_body_table_get_1(self):
        self.assertEqual(self.table.get_named_ranges(), [])

    def test_body_table_get_2(self):
        result = [nr.name for nr in self.table2.get_named_ranges()]
        self.assertEqual(result, ["nr_1", "nr_6"])

    def test_body_table_get_3(self):
        table2 = self.table2.clone
        self.assertEqual(table2.get_named_ranges(), [])

    def test_body_table_get_4(self):
        table = self.table2
        back_nr = table.get_named_range("nr_1")
        n = back_nr.name
        self.assertEqual(n, "nr_1")

    def test_body_table_get_4_1(self):
        table = self.table2
        back_nr = table.get_named_range("nr_1xxx")
        self.assertEqual(back_nr, None)

    def test_body_table_get_4_2(self):
        table = self.table2
        back_nr = table.get_named_range("nr_6")
        self.assertEqual(back_nr.name, "nr_6")
        self.assertEqual(back_nr.table_name, "Example1")
        self.assertEqual(back_nr.start, (3, 2))
        self.assertEqual(back_nr.end, (5, 3))
        self.assertEqual(back_nr.crange, (3, 2, 5, 3))
        self.assertEqual(back_nr.usage, "print-range")

    def test_body_table_get_5(self):
        table = self.table
        back_nr = table.get_named_range("nr_1")
        self.assertEqual(back_nr, None)

    def test_body_table_set_0(self):
        self.assertRaises(ValueError, self.table2.set_named_range, "   ", "A1:C2")

    def test_body_table_set_1(self):
        self.table2.set_named_range("new", "A1:B1")
        result = [nr.name for nr in self.table2.get_named_ranges()]
        self.assertEqual(result, ["nr_1", "nr_6", "new"])

    def test_body_table_set_3(self):
        self.table2.set_named_range("new", "A1:B1")
        back_nr = self.table2.get_named_range("new")
        self.assertEqual(back_nr.usage, None)
        self.assertEqual(back_nr.crange, (0, 0, 1, 0))
        self.assertEqual(back_nr.start, (0, 0))
        self.assertEqual(back_nr.end, (1, 0))
        self.assertEqual(back_nr.table_name, "Example1")
        # reset
        self.table2.set_named_range("new", "A1:c2")
        result = [nr.name for nr in self.table2.get_named_ranges()]
        self.assertEqual(result, ["nr_1", "nr_6", "new"])
        back_nr = self.table2.get_named_range("new")
        self.assertEqual(back_nr.usage, None)
        self.assertEqual(back_nr.crange, (0, 0, 2, 1))
        self.assertEqual(back_nr.start, (0, 0))
        self.assertEqual(back_nr.end, (2, 1))
        self.assertEqual(back_nr.table_name, "Example1")

    def test_body_table_delete_1(self):
        self.table2.delete_named_range("xxx")
        result = [nr.name for nr in self.table2.get_named_ranges()]
        self.assertEqual(result, ["nr_1", "nr_6"])

    def test_body_table_delete_2(self):
        self.table2.delete_named_range("nr_1")
        result = [nr.name for nr in self.table2.get_named_ranges()]
        self.assertEqual(result, ["nr_6"])

    def test_body_table_delete_3(self):
        self.table2.set_named_range("new", "A1:c2")
        result = [nr.name for nr in self.table2.get_named_ranges()]
        self.assertEqual(result, ["nr_1", "nr_6", "new"])
        self.table2.delete_named_range("nr_1")
        self.table2.delete_named_range("nr_6")
        result = [nr.name for nr in self.table2.get_named_ranges()]
        self.assertEqual(result, ["new"])
        self.table2.delete_named_range("new")
        result = [nr.name for nr in self.table2.get_named_ranges()]
        self.assertEqual(result, [])
        self.table2.delete_named_range("new")
        self.table2.delete_named_range("xxx")
        self.table2.set_named_range("hop", "A1:C2")
        result = [nr.name for nr in self.table2.get_named_ranges()]
        self.assertEqual(result, ["hop"])
        self.table2.set_named_range("hop", "A2:d8")
        result = [nr.name for nr in self.table2.get_named_ranges()]
        self.assertEqual(result, ["hop"])
        nr = self.table2.get_named_range("hop")
        self.assertEqual(nr.crange, (0, 1, 3, 7))

    def test_body_table_get_value_1(self):
        result = self.table2.get_named_range("nr_1").get_value()
        self.assertEqual(result, 1)

    def test_body_table_get_value_2(self):
        result = self.table2.get_named_range("nr_1").get_value(get_type=True)
        self.assertEqual(result, (1, "float"))

    def test_body_table_get_value_3(self):
        result = self.table2.get_named_range("nr_1").get_values()
        self.assertEqual(result, [[1]])

    def test_body_table_get_value_4(self):
        result = self.table2.get_named_range("nr_1").get_values(flat=True)
        self.assertEqual(result, [1])

    def test_body_table_get_value_5(self):
        result = self.table2.get_named_range("nr_6").get_values(flat=True)
        self.assertEqual(result, [2, 3, 3, 4, 5, 6])

    def test_body_table_get_value_6(self):
        result = self.table2.get_named_range("nr_6").get_value()
        self.assertEqual(result, 2)

    def test_body_table_set_value_1(self):
        self.table2.get_named_range("nr_6").set_value("AAA")
        self.assertEqual(self.table2.get_value("D3"), "AAA")
        self.assertEqual(self.table2.get_value("E3"), 3)

    def test_body_table_set_value_2(self):
        self.table2.get_named_range("nr_6").set_values([[10, 11, 12], [13, 14, 15]])
        self.assertEqual(
            self.table2.get_values(),
            [
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 10, 11, 12, 3],
                [1, 2, 3, 13, 14, 15, 7],
            ],
        )

    def test_body_change_name_table(self):
        self.table2.name = "new table"
        result = [nr.name for nr in self.table2.get_named_ranges()]
        self.assertEqual(result, ["nr_1", "nr_6"])
        back_nr = self.table2.get_named_range("nr_6")
        self.assertEqual(back_nr.name, "nr_6")
        self.assertEqual(back_nr.table_name, "new table")
        self.assertEqual(back_nr.start, (3, 2))
        self.assertEqual(back_nr.end, (5, 3))
        self.assertEqual(back_nr.crange, (3, 2, 5, 3))
        self.assertEqual(back_nr.usage, "print-range")


class TestTableColumn(TestCase):
    def setUp(self):
        document = Document("samples/simple_table.ods")
        body = document.body
        self.table = body.get_table(name="Example1").clone

    def test_traverse_columns(self):
        self.assertEqual(len(list(self.table.traverse_columns())), 7)

    def test_get_column_list(self):
        self.assertEqual(len(list(self.table.get_columns())), 7)

    def test_get_column_list_style(self):
        table = self.table
        coordinates = [col.x for col in table.get_columns(style=r"co2")]
        self.assertEqual(coordinates, [2, 3])

    def test_get_column(self):
        table = self.table
        column = table.get_column(3)
        self.assertEqual(column.style, "co2")
        self.assertEqual(column.x, 3)
        column = table.get_column(4)
        self.assertEqual(column.style, "co1")
        self.assertEqual(column.x, 4)

    def test_set_column(self):
        table = self.table.clone
        column = table.get_column(3)
        column_back = table.set_column(4, column)
        self.assertEqual(column_back.x, 4)
        column = table.get_column(4)
        self.assertEqual(column.x, 4)
        self.assertEqual(column.style, "co2")

    def test_insert(self):
        table = self.table.clone
        column = table.insert_column(3)
        self.assertTrue(type(column) is Column)
        self.assertEqual(column.x, 3)

    def test_insert_column(self):
        table = self.table.clone
        column = table.insert_column(3, Column())
        self.assertEqual(table.width, 8)
        self.assertEqual(table.get_row(0).width, 8)
        self.assertEqual(column.x, 3)

    def test_append(self):
        table = self.table.clone
        column = table.append_column()
        self.assertTrue(type(column) is Column)
        self.assertEqual(column.x, table.width - 1)

    def test_append_column(self):
        table = self.table.clone
        column = table.append_column(Column())
        self.assertEqual(table.width, 8)
        self.assertEqual(table.get_row(0).width, 7)
        self.assertEqual(column.x, table.width - 1)
        # The column must be inserted between the columns and the rows
        self.assertTrue(type(table.children[-1]) is not Column)

    def test_delete_column(self):
        table = self.table.clone
        table.delete_column(3)
        self.assertEqual(table.width, 6)
        self.assertEqual(table.get_row(0).width, 6)

    def test_get_column_cell_values(self):
        self.assertEqual(self.table.get_column_values(3), [2, 2, 2, 4])

    def test_set_column_cell_values(self):
        table = self.table.clone
        table.set_column_values(5, ["a", "b", "c", "d"])
        self.assertEqual(
            table.get_values(),
            [
                [1, 1, 1, 2, 3, "a", 3],
                [1, 1, 1, 2, 3, "b", 3],
                [1, 1, 1, 2, 3, "c", 3],
                [1, 2, 3, 4, 5, "d", 7],
            ],
        )

    def test_is_column_empty(self):
        table = Table("Empty", width=10, height=20)
        for x in range(10):
            self.assertEqual(table.is_column_empty(x), True)

    def test_is_column_empty_no(self):
        table = Table("Not Empty", width=10, height=20)
        table.set_value((4, 9), "Bouh !")
        self.assertEqual(table.is_column_empty(4), False)


class TestCSV(TestCase):
    def setUp(self):
        self.table = import_from_csv(StringIO(csv_data), "From CSV")

    def test_import_from_csv(self):
        expected = (
            '<table:table table:name="From CSV">'
            "<table:table-column "
            'table:number-columns-repeated="2"/>'
            "<table:table-row>"
            '<table:table-cell office:value-type="string" '
            'calcext:value-type="string" '
            'office:string-value="A float">'
            "<text:p>A float</text:p>"
            "</table:table-cell>"
            '<table:table-cell office:value-type="float" '
            'calcext:value-type="float" '
            'office:value="3.14" calcext:value="3.14">'
            "<text:p>3.14</text:p>"
            "</table:table-cell>"
            "</table:table-row>"
            "<table:table-row>"
            '<table:table-cell office:value-type="string" '
            'calcext:value-type="string" '
            'office:string-value="A date">'
            "<text:p>A date</text:p>"
            "</table:table-cell>"
            '<table:table-cell office:value-type="date" '
            'calcext:value-type="date" '
            'office:date-value="1975-05-07T00:00:00">'
            "<text:p>1975-05-07T00:00:00</text:p>"
            "</table:table-cell>"
            "</table:table-row>"
            "</table:table>"
        )
        self.assertEqual(self.table.serialize(), expected)

    def test_export_to_csv(self):
        expected = "A float,3.14\r\n" "A date,1975-05-07 00:00:00\r\n"
        self.assertEqual(self.table.to_csv(), expected)


if __name__ == "__main__":
    main()
