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
from __future__ import annotations

from collections.abc import Iterable
from io import StringIO

import pytest

from odfdo.document import Document
from odfdo.mixin_md import MD_GLOBAL
from odfdo.note import Note
from odfdo.table import Table, import_from_csv

CSV_DATA = '"A float","3.14"\n"A date","1975-05-07"\n'


@pytest.fixture
def table() -> Iterable[Table]:
    table = import_from_csv(StringIO(CSV_DATA), "From CSV")
    yield table


def test_export_to_markdown(table):
    md = table.to_markdown()
    expected = (
        "| A float | 3.14                  |\n"
        "|---------|-----------------------|\n"
        "| A date  | 1975\\-05\\-07T00:00:00 |\n"
    )
    assert md == expected


def test_export_to_markdown_empty():
    table = Table("Empty")
    assert table.to_markdown() == ""


def test_export_to_markdown_from_doc(samples):
    doc = Document(samples("table.odt"))
    table = doc.body.tables[0]
    md = table.to_markdown()
    assert "Some bar" in md
    assert "Log or" in md


def test_export_to_markdown_not_initialized():
    table = Table("Uninit")
    table.set_value("A1", "val")
    MD_GLOBAL.pop("document", None)
    md = table.to_markdown()
    assert "val" in md


def test_export_to_markdown_with_notes():
    table = Table("Notes")
    table.set_value("A1", "Cell with note")
    cell = table.get_row(0).get_cell(0)
    fn = Note("footnote", note_id="fn1", citation="1", body="Footnote in table")
    en = Note("endnote", note_id="en1", citation="A", body="Endnote in table")
    p = cell.get_element("text:p")
    p.append(fn)
    p.append(en)
    md = table.to_markdown()
    assert "Cell with note" in md


def test_export_to_markdown_empty_md_global():
    table = Table("EmptyGlobal")
    table.set_value("A1", "val")
    MD_GLOBAL.clear()
    md = table._md_format()
    assert "val" in md
