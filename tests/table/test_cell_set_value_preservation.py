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
from datetime import date, datetime, timedelta
from decimal import Decimal

from odfdo.document import Document


def test_cell_value_setter_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell = table.get_cell("E1", clone=False)
    original_style = cell.style
    assert cell.get_attribute("table:number-columns-spanned") == "2"
    assert cell.get_attribute("table:number-rows-spanned") == "2"

    cell.value = "new value"

    cell_after = table.get_cell("E1", clone=False)
    assert cell_after.value == "new value"
    assert cell_after.style == original_style
    assert cell_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_after.get_attribute("table:number-rows-spanned") == "2"


def test_cell_set_value_method_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell = table.get_cell("E1", clone=False)
    original_style = cell.style

    cell.set_value("new value via method")

    cell_after = table.get_cell("E1", clone=False)
    assert cell_after.value == "new value via method"
    assert cell_after.style == original_style
    assert cell_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_after.get_attribute("table:number-rows-spanned") == "2"


def test_cell_string_setter_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell = table.get_cell("E1", clone=False)
    original_style = cell.style

    cell.string = "string content"

    cell_after = table.get_cell("E1", clone=False)
    assert cell_after.string == "string content"
    assert cell_after.type == "string"
    assert cell_after.style == original_style
    assert cell_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_after.get_attribute("table:number-rows-spanned") == "2"


def test_cell_float_setter_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell = table.get_cell("E1", clone=False)
    original_style = cell.style

    cell.float = 42.5

    cell_after = table.get_cell("E1", clone=False)
    assert cell_after.float == 42.5
    assert cell_after.type == "float"
    assert cell_after.style == original_style
    assert cell_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_after.get_attribute("table:number-rows-spanned") == "2"


def test_cell_decimal_setter_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell = table.get_cell("E1", clone=False)
    original_style = cell.style

    cell.decimal = Decimal("99.99")

    cell_after = table.get_cell("E1", clone=False)
    assert cell_after.decimal == Decimal("99.99")
    assert cell_after.type == "float"
    assert cell_after.style == original_style
    assert cell_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_after.get_attribute("table:number-rows-spanned") == "2"


def test_cell_int_setter_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell = table.get_cell("E1", clone=False)
    original_style = cell.style

    cell.int = 100

    cell_after = table.get_cell("E1", clone=False)
    assert cell_after.int == 100
    assert cell_after.type == "float"
    assert cell_after.style == original_style
    assert cell_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_after.get_attribute("table:number-rows-spanned") == "2"


def test_cell_bool_setter_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell = table.get_cell("E1", clone=False)
    original_style = cell.style

    cell.bool = True

    cell_after = table.get_cell("E1", clone=False)
    assert cell_after.bool is True
    assert cell_after.type == "boolean"
    assert cell_after.style == original_style
    assert cell_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_after.get_attribute("table:number-rows-spanned") == "2"


def test_cell_date_setter_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell = table.get_cell("E1", clone=False)
    original_style = cell.style

    target_date = date(2026, 8, 13)
    cell.date = target_date

    cell_after = table.get_cell("E1", clone=False)
    assert cell_after.date == target_date
    assert cell_after.type == "date"
    assert cell_after.style == original_style
    assert cell_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_after.get_attribute("table:number-rows-spanned") == "2"


def test_cell_datetime_setter_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell = table.get_cell("E1", clone=False)
    original_style = cell.style

    target_dt = datetime(2026, 8, 13, 20, 30)
    cell.datetime = target_dt

    cell_after = table.get_cell("E1", clone=False)
    assert cell_after.datetime == target_dt
    assert cell_after.type == "date"
    assert cell_after.style == original_style
    assert cell_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_after.get_attribute("table:number-rows-spanned") == "2"


def test_cell_duration_setter_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell = table.get_cell("E1", clone=False)
    original_style = cell.style

    target_duration = timedelta(hours=3, minutes=15)
    cell.duration = target_duration

    cell_after = table.get_cell("E1", clone=False)
    assert cell_after.duration == target_duration
    assert cell_after.type == "time"
    assert cell_after.style == original_style
    assert cell_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_after.get_attribute("table:number-rows-spanned") == "2"


def test_table_values_property_string_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell_a1 = table.get_cell("A1", clone=False)
    cell_e1 = table.get_cell("E1", clone=False)
    original_style = cell_e1.style
    assert cell_a1.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1.get_attribute("table:number-rows-spanned") == "2"

    matrix = table.values
    matrix[0][0] = "new spanned string"
    matrix[0][4] = "new e1 string"
    table.values = matrix

    cell_a1_after = table.get_cell("A1", clone=False)
    cell_e1_after = table.get_cell("E1", clone=False)

    assert cell_a1_after.value == "new spanned string"
    assert cell_a1_after.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1_after.get_attribute("table:number-rows-spanned") == "2"

    assert cell_e1_after.value == "new e1 string"
    assert cell_e1_after.style == original_style
    assert cell_e1_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_e1_after.get_attribute("table:number-rows-spanned") == "2"


def test_table_values_property_float_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell_a1 = table.get_cell("A1", clone=False)
    cell_e1 = table.get_cell("E1", clone=False)
    original_style = cell_e1.style
    assert cell_a1.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1.get_attribute("table:number-rows-spanned") == "2"

    matrix = table.values
    matrix[0][0] = 12.5
    matrix[0][4] = 42.75
    table.values = matrix

    cell_a1_after = table.get_cell("A1", clone=False)
    cell_e1_after = table.get_cell("E1", clone=False)

    assert cell_a1_after.value == Decimal("12.5")
    assert cell_a1_after.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1_after.get_attribute("table:number-rows-spanned") == "2"

    assert cell_e1_after.value == Decimal("42.75")
    assert cell_e1_after.style == original_style
    assert cell_e1_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_e1_after.get_attribute("table:number-rows-spanned") == "2"


def test_table_values_property_decimal_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell_a1 = table.get_cell("A1", clone=False)
    cell_e1 = table.get_cell("E1", clone=False)
    original_style = cell_e1.style
    assert cell_a1.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1.get_attribute("table:number-rows-spanned") == "2"

    matrix = table.values
    matrix[0][0] = Decimal("100.50")
    matrix[0][4] = Decimal("99.99")
    table.values = matrix

    cell_a1_after = table.get_cell("A1", clone=False)
    cell_e1_after = table.get_cell("E1", clone=False)

    assert cell_a1_after.value == Decimal("100.50")
    assert cell_a1_after.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1_after.get_attribute("table:number-rows-spanned") == "2"

    assert cell_e1_after.value == Decimal("99.99")
    assert cell_e1_after.style == original_style
    assert cell_e1_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_e1_after.get_attribute("table:number-rows-spanned") == "2"


def test_table_values_property_int_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell_a1 = table.get_cell("A1", clone=False)
    cell_e1 = table.get_cell("E1", clone=False)
    original_style = cell_e1.style
    assert cell_a1.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1.get_attribute("table:number-rows-spanned") == "2"

    matrix = table.values
    matrix[0][0] = 10
    matrix[0][4] = 200
    table.values = matrix

    cell_a1_after = table.get_cell("A1", clone=False)
    cell_e1_after = table.get_cell("E1", clone=False)

    assert cell_a1_after.value == 10
    assert cell_a1_after.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1_after.get_attribute("table:number-rows-spanned") == "2"

    assert cell_e1_after.value == 200
    assert cell_e1_after.style == original_style
    assert cell_e1_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_e1_after.get_attribute("table:number-rows-spanned") == "2"


def test_table_values_property_bool_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell_a1 = table.get_cell("A1", clone=False)
    cell_e1 = table.get_cell("E1", clone=False)
    original_style = cell_e1.style
    assert cell_a1.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1.get_attribute("table:number-rows-spanned") == "2"

    matrix = table.values
    matrix[0][0] = True
    matrix[0][4] = False
    table.values = matrix

    cell_a1_after = table.get_cell("A1", clone=False)
    cell_e1_after = table.get_cell("E1", clone=False)

    assert cell_a1_after.value is True
    assert cell_a1_after.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1_after.get_attribute("table:number-rows-spanned") == "2"

    assert cell_e1_after.value is False
    assert cell_e1_after.style == original_style
    assert cell_e1_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_e1_after.get_attribute("table:number-rows-spanned") == "2"


def test_table_values_property_date_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell_a1 = table.get_cell("A1", clone=False)
    cell_e1 = table.get_cell("E1", clone=False)
    original_style = cell_e1.style
    assert cell_a1.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1.get_attribute("table:number-rows-spanned") == "2"

    target_date1 = date(2026, 1, 1)
    target_date2 = date(2026, 8, 13)

    matrix = table.values
    matrix[0][0] = target_date1
    matrix[0][4] = target_date2
    table.values = matrix

    cell_a1_after = table.get_cell("A1", clone=False)
    cell_e1_after = table.get_cell("E1", clone=False)

    assert cell_a1_after.date == target_date1
    assert cell_a1_after.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1_after.get_attribute("table:number-rows-spanned") == "2"

    assert cell_e1_after.date == target_date2
    assert cell_e1_after.style == original_style
    assert cell_e1_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_e1_after.get_attribute("table:number-rows-spanned") == "2"


def test_table_values_property_datetime_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell_a1 = table.get_cell("A1", clone=False)
    cell_e1 = table.get_cell("E1", clone=False)
    original_style = cell_e1.style
    assert cell_a1.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1.get_attribute("table:number-rows-spanned") == "2"

    target_dt1 = datetime(2026, 1, 1, 10, 0)
    target_dt2 = datetime(2026, 8, 13, 20, 30)

    matrix = table.values
    matrix[0][0] = target_dt1
    matrix[0][4] = target_dt2
    table.values = matrix

    cell_a1_after = table.get_cell("A1", clone=False)
    cell_e1_after = table.get_cell("E1", clone=False)

    assert cell_a1_after.datetime == target_dt1
    assert cell_a1_after.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1_after.get_attribute("table:number-rows-spanned") == "2"

    assert cell_e1_after.datetime == target_dt2
    assert cell_e1_after.style == original_style
    assert cell_e1_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_e1_after.get_attribute("table:number-rows-spanned") == "2"


def test_table_values_property_duration_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell_a1 = table.get_cell("A1", clone=False)
    cell_e1 = table.get_cell("E1", clone=False)
    original_style = cell_e1.style
    assert cell_a1.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1.get_attribute("table:number-rows-spanned") == "2"

    target_dur1 = timedelta(hours=1)
    target_dur2 = timedelta(hours=3, minutes=15)

    matrix = table.values
    matrix[0][0] = target_dur1
    matrix[0][4] = target_dur2
    table.values = matrix

    cell_a1_after = table.get_cell("A1", clone=False)
    cell_e1_after = table.get_cell("E1", clone=False)

    assert cell_a1_after.duration == target_dur1
    assert cell_a1_after.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1_after.get_attribute("table:number-rows-spanned") == "2"

    assert cell_e1_after.duration == target_dur2
    assert cell_e1_after.style == original_style
    assert cell_e1_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_e1_after.get_attribute("table:number-rows-spanned") == "2"


def test_table_set_value_string_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell_e1 = table.get_cell("E1", clone=False)
    original_style = cell_e1.style

    table.set_value("A1", "new spanned string")
    table.set_value("E1", "new e1 string")

    cell_a1_after = table.get_cell("A1", clone=False)
    cell_e1_after = table.get_cell("E1", clone=False)

    assert cell_a1_after.value == "new spanned string"
    assert cell_a1_after.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1_after.get_attribute("table:number-rows-spanned") == "2"

    assert cell_e1_after.value == "new e1 string"
    assert cell_e1_after.style == original_style
    assert cell_e1_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_e1_after.get_attribute("table:number-rows-spanned") == "2"


def test_table_set_value_float_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell_e1 = table.get_cell("E1", clone=False)
    original_style = cell_e1.style

    table.set_value("A1", 12.5)
    table.set_value("E1", 42.75)

    cell_a1_after = table.get_cell("A1", clone=False)
    cell_e1_after = table.get_cell("E1", clone=False)

    assert cell_a1_after.value == Decimal("12.5")
    assert cell_a1_after.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1_after.get_attribute("table:number-rows-spanned") == "2"

    assert cell_e1_after.value == Decimal("42.75")
    assert cell_e1_after.style == original_style
    assert cell_e1_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_e1_after.get_attribute("table:number-rows-spanned") == "2"


def test_table_set_value_decimal_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell_e1 = table.get_cell("E1", clone=False)
    original_style = cell_e1.style

    table.set_value("A1", Decimal("100.50"))
    table.set_value("E1", Decimal("99.99"))

    cell_a1_after = table.get_cell("A1", clone=False)
    cell_e1_after = table.get_cell("E1", clone=False)

    assert cell_a1_after.value == Decimal("100.50")
    assert cell_a1_after.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1_after.get_attribute("table:number-rows-spanned") == "2"

    assert cell_e1_after.value == Decimal("99.99")
    assert cell_e1_after.style == original_style
    assert cell_e1_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_e1_after.get_attribute("table:number-rows-spanned") == "2"


def test_table_set_value_int_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell_e1 = table.get_cell("E1", clone=False)
    original_style = cell_e1.style

    table.set_value("A1", 10)
    table.set_value("E1", 200)

    cell_a1_after = table.get_cell("A1", clone=False)
    cell_e1_after = table.get_cell("E1", clone=False)

    assert cell_a1_after.value == 10
    assert cell_a1_after.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1_after.get_attribute("table:number-rows-spanned") == "2"

    assert cell_e1_after.value == 200
    assert cell_e1_after.style == original_style
    assert cell_e1_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_e1_after.get_attribute("table:number-rows-spanned") == "2"


def test_table_set_value_bool_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell_e1 = table.get_cell("E1", clone=False)
    original_style = cell_e1.style

    table.set_value("A1", True)
    table.set_value("E1", False)

    cell_a1_after = table.get_cell("A1", clone=False)
    cell_e1_after = table.get_cell("E1", clone=False)

    assert cell_a1_after.value is True
    assert cell_a1_after.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1_after.get_attribute("table:number-rows-spanned") == "2"

    assert cell_e1_after.value is False
    assert cell_e1_after.style == original_style
    assert cell_e1_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_e1_after.get_attribute("table:number-rows-spanned") == "2"


def test_table_set_value_date_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell_e1 = table.get_cell("E1", clone=False)
    original_style = cell_e1.style

    target_date1 = date(2026, 1, 1)
    target_date2 = date(2026, 8, 13)

    table.set_value("A1", target_date1)
    table.set_value("E1", target_date2)

    cell_a1_after = table.get_cell("A1", clone=False)
    cell_e1_after = table.get_cell("E1", clone=False)

    assert cell_a1_after.date == target_date1
    assert cell_a1_after.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1_after.get_attribute("table:number-rows-spanned") == "2"

    assert cell_e1_after.date == target_date2
    assert cell_e1_after.style == original_style
    assert cell_e1_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_e1_after.get_attribute("table:number-rows-spanned") == "2"


def test_table_set_value_datetime_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell_e1 = table.get_cell("E1", clone=False)
    original_style = cell_e1.style

    target_dt1 = datetime(2026, 1, 1, 10, 0)
    target_dt2 = datetime(2026, 8, 13, 20, 30)

    table.set_value("A1", target_dt1)
    table.set_value("E1", target_dt2)

    cell_a1_after = table.get_cell("A1", clone=False)
    cell_e1_after = table.get_cell("E1", clone=False)

    assert cell_a1_after.datetime == target_dt1
    assert cell_a1_after.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1_after.get_attribute("table:number-rows-spanned") == "2"

    assert cell_e1_after.datetime == target_dt2
    assert cell_e1_after.style == original_style
    assert cell_e1_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_e1_after.get_attribute("table:number-rows-spanned") == "2"


def test_table_set_value_duration_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell_e1 = table.get_cell("E1", clone=False)
    original_style = cell_e1.style

    target_dur1 = timedelta(hours=1)
    target_dur2 = timedelta(hours=3, minutes=15)

    table.set_value("A1", target_dur1)
    table.set_value("E1", target_dur2)

    cell_a1_after = table.get_cell("A1", clone=False)
    cell_e1_after = table.get_cell("E1", clone=False)

    assert cell_a1_after.duration == target_dur1
    assert cell_a1_after.get_attribute("table:number-columns-spanned") == "3"
    assert cell_a1_after.get_attribute("table:number-rows-spanned") == "2"

    assert cell_e1_after.duration == target_dur2
    assert cell_e1_after.style == original_style
    assert cell_e1_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_e1_after.get_attribute("table:number-rows-spanned") == "2"


def test_table_set_value_override_style_preserves_span(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]

    table.set_value("E1", "new value", style="custom_style")

    cell_e1_after = table.get_cell("E1", clone=False)
    assert cell_e1_after.value == "new value"
    assert cell_e1_after.style == "custom_style"
    assert cell_e1_after.get_attribute("table:number-columns-spanned") == "2"
    assert cell_e1_after.get_attribute("table:number-rows-spanned") == "2"
