# Copyright 2018-2024 Jérôme Dumonteil
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

from pathlib import Path

from odfdo.document import Document
from odfdo.table import Table

SAMPLES = Path(__file__).parent / "samples"
FILE_HIDDEN_ODS = SAMPLES / "minimal_hidden.ods"


def test_display_default():
    table = Table("A Table")
    expected = '<table:table table:name="A Table"/>'
    assert table.serialize() == expected


def test_table_style_get_table_name():
    doc = Document("spreadsheet")
    body = doc.body
    body.clear()
    table = Table("Table0")
    body.append(table)
    table = doc._get_table("Table0")
    assert table.name == "Table0"


def test_table_style_table_display_default():
    doc = Document("spreadsheet")
    doc.body.clear()
    doc.body.append(Table("Table0"))
    assert doc.get_table_displayed("Table0")


def test_table_style_table_display_default_idx():
    doc = Document("spreadsheet")
    doc.body.clear()
    doc.body.append(Table("Table0"))
    assert doc.get_table_displayed(0)


def test_table_style_table_display_change1():
    name0 = "Table0"
    name1 = "Table1"
    doc = Document("spreadsheet")
    doc.body.clear()
    doc.body.append(Table(name0))
    doc.body.append(Table(name1))
    doc.set_table_displayed(name0, True)
    assert doc.get_table_displayed(name0)
    assert doc.get_table_displayed(name1)


def test_table_style_table_display_change2():
    name0 = "Table0"
    name1 = "Table1"
    doc = Document("spreadsheet")
    doc.body.clear()
    doc.body.append(Table(name0))
    doc.body.append(Table(name1))
    doc.set_table_displayed(name0, False)
    assert not doc.get_table_displayed(name0)
    assert doc.get_table_displayed(name1)


def test_table_style_table_display_change3():
    name0 = "Table0"
    name1 = "Table1"
    doc = Document("spreadsheet")
    doc.body.clear()
    doc.body.append(Table(name0))
    doc.body.append(Table(name1))
    doc.set_table_displayed(name0, True)
    doc.set_table_displayed(name1, False)
    assert doc.get_table_displayed(name0)
    assert not doc.get_table_displayed(name1)


def test_table_style_table_display_change1_idx():
    name0 = "Table0"
    name1 = "Table1"
    doc = Document("spreadsheet")
    doc.body.clear()
    doc.body.append(Table(name0))
    doc.body.append(Table(name1))
    doc.set_table_displayed(0, True)
    assert doc.get_table_displayed(0)
    assert doc.get_table_displayed(1)


def test_table_style_table_display_change2_idx():
    name0 = "Table0"
    name1 = "Table1"
    doc = Document("spreadsheet")
    doc.body.clear()
    doc.body.append(Table(name0))
    doc.body.append(Table(name1))
    doc.set_table_displayed(0, False)
    assert not doc.get_table_displayed(0)
    assert doc.get_table_displayed(1)


def test_table_style_table_display_change3_idx():
    name0 = "Table0"
    name1 = "Table1"
    doc = Document("spreadsheet")
    doc.body.clear()
    doc.body.append(Table(name0))
    doc.body.append(Table(name1))
    doc.set_table_displayed(0, True)
    doc.set_table_displayed(1, False)
    assert doc.get_table_displayed(0)
    assert not doc.get_table_displayed(1)


def test_table_style_get_table_name_file():
    doc = Document(FILE_HIDDEN_ODS)
    table = doc._get_table("Tab 1")
    assert table.name == "Tab 1"


def test_table_style_table_display_file1():
    doc = Document(FILE_HIDDEN_ODS)
    assert doc.get_table_displayed("Tab 1")


def test_table_style_table_display_file2():
    doc = Document(FILE_HIDDEN_ODS)
    assert not doc.get_table_displayed("Tab 2")


def test_table_style_table_display_3_idx_file():
    doc = Document(FILE_HIDDEN_ODS)
    doc.body.append(Table("Table 3"))
    assert doc.get_table_displayed(2)


def test_table_style_table_display_change1_file():
    doc = Document(FILE_HIDDEN_ODS)
    doc.set_table_displayed("Tab 1", True)
    assert doc.get_table_displayed("Tab 1")
    assert not doc.get_table_displayed("Tab 2")


def test_table_style_table_display_change2_file():
    doc = Document(FILE_HIDDEN_ODS)
    doc.set_table_displayed("Tab 1", False)
    assert not doc.get_table_displayed("Tab 1")
    assert not doc.get_table_displayed("Tab 2")


def test_table_style_table_display_change3_file():
    doc = Document(FILE_HIDDEN_ODS)
    doc.set_table_displayed("Tab 1", False)
    doc.set_table_displayed("Tab 2", True)
    assert not doc.get_table_displayed("Tab 1")
    assert doc.get_table_displayed("Tab 2")


def test_table_style_table_display_change1_idx_file():
    doc = Document(FILE_HIDDEN_ODS)
    doc.set_table_displayed(0, True)
    assert doc.get_table_displayed(0)
    assert not doc.get_table_displayed(1)


def test_table_style_table_display_change2_idx_file():
    doc = Document(FILE_HIDDEN_ODS)
    doc.set_table_displayed(0, False)
    assert not doc.get_table_displayed(0)
    assert not doc.get_table_displayed(1)


def test_table_style_table_display_change3_idx_file():
    doc = Document(FILE_HIDDEN_ODS)
    doc.set_table_displayed(0, False)
    doc.set_table_displayed(1, True)
    assert not doc.get_table_displayed(0)
    assert doc.get_table_displayed(1)