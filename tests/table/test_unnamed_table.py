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

import pytest

from odfdo.document import Document
from odfdo.named_range import NamedRange
from odfdo.table import Table


def test_unnamed_table_creation_default():
    table = Table()
    assert table.name is None
    assert table.get_attribute("table:name") is None
    assert table._canonicalize() == "<table:table></table:table>"


def test_unnamed_table_creation_none():
    table = Table(name=None)
    assert table.name is None
    assert table.get_attribute("table:name") is None
    assert table._canonicalize() == "<table:table></table:table>"


def test_unnamed_table_with_dimensions():
    table = Table(width=2, height=2)
    assert table.name is None
    assert table.get_attribute("table:name") is None
    expected = (
        "<table:table>"
        '<table:table-column table:number-columns-repeated="2">'
        "</table:table-column>"
        "<table:table-row>"
        "<table:table-cell></table:table-cell>"
        "<table:table-cell></table:table-cell>"
        "</table:table-row>"
        "<table:table-row>"
        "<table:table-cell></table:table-cell>"
        "<table:table-cell></table:table-cell>"
        "</table:table-row>"
        "</table:table>"
    )
    assert table._canonicalize() == expected


def test_unnamed_table_set_name_later():
    table = Table()
    assert table.name is None
    table.name = "Sheet1"
    assert table.name == "Sheet1"
    assert table.get_attribute("table:name") == "Sheet1"
    assert table._canonicalize() == '<table:table table:name="Sheet1"></table:table>'


def test_named_table_set_name_to_none():
    table = Table("Sheet1")
    assert table.name == "Sheet1"
    table.name = None
    assert table.name is None
    assert table.get_attribute("table:name") is None
    assert table._canonicalize() == "<table:table></table:table>"


def test_named_table_set_name_to_none_keeps_named_range_pending():
    doc = Document("spreadsheet")
    body = doc.body
    table = body.get_table(position=0)
    assert table is not None
    table.name = "Sheet1"
    table.set_named_range("My_Range", "A1:B2")

    # Set table name to None
    table.name = None
    assert table.name is None

    # The existing named range remains pending with table_name="Sheet1"
    nr = body.get_named_range("My_Range")
    assert nr is not None
    assert nr.table_name == "Sheet1"


def test_unnamed_table_in_document():
    doc = Document("text")
    body = doc.body
    unnamed = Table()
    body.append(unnamed)

    all_tables = body.tables
    assert len(all_tables) >= 1
    pos = len(all_tables) - 1
    fetched = body.get_table(position=pos)
    assert fetched is not None
    assert fetched.name is None
    assert fetched._canonicalize() == "<table:table></table:table>"


def test_unnamed_table_get_table_by_name():
    doc = Document("text")
    body = doc.body
    unnamed = Table()
    body.append(unnamed)

    assert body.get_table_by_name("") is None
    assert body.get_table_by_name("Sheet1") is None


def test_unnamed_table_named_ranges_fail():
    table = Table()
    # Attempting to create named range with table.name=None raises TypeError
    with pytest.raises(TypeError):
        NamedRange(name="My_Range", crange="A1:B2", table_name=table.name)  # type: ignore[arg-type]

    # Attempting set_named_range on unnamed table raises TypeError
    with pytest.raises(TypeError):
        table.set_named_range("My_Range", "A1:B2", global_scope=False)


def test_unnamed_table_named_ranges_queries():
    table = Table()
    assert table.get_named_ranges(global_scope=False) == []
    assert table.get_named_range("My_Range", global_scope=False) is None


def test_unnamed_table_setting_name_does_not_corrupt_other_named_ranges():
    doc = Document("spreadsheet")
    body = doc.body

    # Set name and a named range on the first table
    table1 = body.get_table(position=0)
    assert table1 is not None
    table1.name = "Sheet1"
    table1.set_named_range("My_Range", "A1:B2")

    # Add an unnamed table
    table2 = Table()
    body.append(table2)

    # Naming table2 should NOT rename My_Range on Sheet1
    table2.name = "Sheet2"

    nr = body.get_named_range("My_Range")
    assert nr is not None
    assert nr.table_name == "Sheet1"


def test_unnamed_table_clone():
    table = Table(width=1, height=1)
    table.set_value("A1", "Test")
    clone = table.clone
    assert clone.name is None
    assert clone.get_value("A1") == "Test"
    assert clone.get_attribute("table:name") is None


def test_unnamed_table_cell_operations():
    table = Table()
    table.set_value("A1", 123)
    table.set_value("B2", "Hello")
    assert table.get_value("A1") == 123
    assert table.get_value("B2") == "Hello"


def test_unnamed_table_row_and_column_operations():
    table = Table()
    row = table.get_row(0)
    assert row is not None
    table.set_value((0, 0), "Value")
    assert table.get_value((0, 0)) == "Value"
    assert table.name is None
