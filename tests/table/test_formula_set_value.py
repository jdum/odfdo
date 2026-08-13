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
from odfdo.document import Document
from odfdo.row import Row
from odfdo.table import Table


def test_row_set_value_with_formula_new_cell():
    row = Row()
    row.set_value(0, 10, formula="of:=SUM([.A1:.A5])")
    cell = row.get_cell(0)
    assert cell.value == 10
    assert cell.formula == "of:=SUM([.A1:.A5])"


def test_row_set_value_with_formula_existing_cell():
    row = Row()
    row.set_value(0, 10)
    row.set_value(0, 20, formula="of:=SUM([.A1:.A10])")
    cell = row.get_cell(0)
    assert cell.value == 20
    assert cell.formula == "of:=SUM([.A1:.A10])"


def test_table_set_value_with_formula_tuple_coord():
    table = Table("TestSheet")
    table.set_value((0, 0), 100, formula="of:=[.B1]+[.C1]")
    cell = table.get_cell((0, 0))
    assert cell.value == 100
    assert cell.formula == "of:=[.B1]+[.C1]"


def test_table_set_value_with_formula_str_coord():
    table = Table("TestSheet")
    table.set_value("A1", 100, formula="of:=[.B1]+[.C1]")
    cell = table.get_cell("A1")
    assert cell.value == 100
    assert cell.formula == "of:=[.B1]+[.C1]"


def test_table_set_value_formula_preserves_span_and_style(samples):
    doc = Document(samples("styled_cell_replace.ods"))
    table = doc.body.tables[0]
    cell_a1 = table.get_cell("A1")

    orig_style = cell_a1.style
    orig_col_span = cell_a1.get_attribute_string("table:number-columns-spanned")
    orig_row_span = cell_a1.get_attribute_string("table:number-rows-spanned")

    formula_val = 'of:=CONCAT("modified", " span")'
    table.set_value("A1", "modified span", formula=formula_val)

    updated_cell = table.get_cell("A1")
    assert updated_cell.value == "modified span"
    assert updated_cell.formula == formula_val
    assert updated_cell.style == orig_style
    assert (
        updated_cell.get_attribute_string("table:number-columns-spanned")
        == orig_col_span
    )
    assert (
        updated_cell.get_attribute_string("table:number-rows-spanned") == orig_row_span
    )


def test_formula_preserved_on_cell_value_change():
    doc = Document("ods")
    table = doc.body.tables[0]
    cell = table.get_cell("A1")
    formula_str = "of:=SUM([.B1:.B5])"
    cell.set_value(10, formula=formula_str)

    cell.value = 20
    assert cell.value == 20
    assert cell.formula == formula_str

    cell.set_value(30)
    assert cell.value == 30
    assert cell.formula == formula_str

    cell.int = 40
    assert cell.value == 40
    assert cell.formula == formula_str

    cell.float = 50.0
    assert cell.value == 50.0
    assert cell.formula == formula_str

    cell.string = "hello"
    assert cell.value == "hello"
    assert cell.formula == formula_str


def test_formula_preserved_on_cell_value_none():
    doc = Document("ods")
    table = doc.body.tables[0]
    cell = table.get_cell("A1")
    formula_str = "of:=SUM([.B1:.B5])"
    cell.set_value(10, formula=formula_str)

    cell.value = None
    assert cell.value is None
    assert cell.formula == formula_str


def test_formula_preserved_on_row_set_value_change():
    row = Row()
    formula_str = "of:=[.B1]*2"
    row.set_value(0, 50, formula=formula_str)
    assert row.get_cell(0).formula == formula_str

    row.set_value(0, 75)
    assert row.get_cell(0).value == 75
    assert row.get_cell(0).formula == formula_str


def test_formula_preserved_on_table_set_value_change():
    table = Table("Sheet1")
    formula_str = "of:=[.B1]+[.C1]"
    table.set_value("A1", 100, formula=formula_str)
    assert table.get_cell("A1").formula == formula_str

    table.set_value("A1", 200)
    assert table.get_cell("A1").value == 200
    assert table.get_cell("A1").formula == formula_str


def test_formula_explicit_mutation_and_clear():
    doc = Document("ods")
    table = doc.body.tables[0]
    cell = table.get_cell("A1")
    formula1 = "of:=SUM([.A1:.A5])"
    formula2 = "of:=SUM([.B1:.B5])"

    cell.set_value(10, formula=formula1)
    assert cell.formula == formula1

    cell.formula = formula2
    assert cell.formula == formula2

    cell.formula = None
    assert cell.formula is None
