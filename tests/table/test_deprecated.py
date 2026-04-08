# Copyright 2018-2026 Jérôme Dumonteil
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

from unittest.mock import PropertyMock, patch

import pytest

from odfdo.cell import Cell
from odfdo.document import Document
from odfdo.element import Element
from odfdo.frame import Frame
from odfdo.image import DrawImage
from odfdo.table import Table


def test_set_cell_image_malformed():
    table = Table("T")
    img = DrawImage("test.png")
    frame = Frame.image_frame(img)
    with pytest.warns(DeprecationWarning):
        with pytest.raises(ValueError):
            table.set_cell_image("1", frame, doc_type="spreadsheet")
    with pytest.warns(DeprecationWarning):
        with pytest.raises(ValueError):
            table.set_cell_image("A", frame, doc_type="spreadsheet")


def test_set_cell_image_paragraph_error():
    table = Table("T")
    img = DrawImage("test.png")
    frame = Frame.image_frame(img)

    with patch.object(Cell, "get_element", return_value=None):
        with pytest.warns(DeprecationWarning):
            with pytest.raises(ValueError):
                table.set_cell_image("A1", frame, doc_type="text")


def test_set_cell_image_no_body_internal():
    table = Table("T")
    img = DrawImage("test.png")
    frame = Frame.image_frame(img)
    with patch.object(Table, "document_body", new_callable=PropertyMock) as mock_body:
        mock_body.return_value = None
        with pytest.warns(DeprecationWarning):
            with pytest.raises(ValueError, match="document type not found"):
                table.set_cell_image("A1", frame)


def test_set_cell_image_unsupported_body_internal():
    table = Table("T")
    doc = Document("ods")
    table = doc.body.get_table(0)
    img = DrawImage("test.png")
    frame = Frame.image_frame(img)
    # We mock body.tag to return something not in dict
    with patch.object(Table, "document_body", new_callable=PropertyMock) as mock_body:
        body = doc.body
        with patch.object(Element, "tag", new_callable=PropertyMock) as mock_tag:
            mock_tag.return_value = "office:other"
            mock_body.return_value = body
            with pytest.warns(DeprecationWarning):
                with pytest.raises(
                    ValueError, match="document type not supported for images"
                ):
                    table.set_cell_image("A1", frame)


def test_set_cell_image_doc_type_text_branch():
    table = Table("T")
    img = DrawImage("test.png")
    frame = Frame.image_frame(img)
    with pytest.warns(DeprecationWarning):
        table.set_cell_image("A1", frame, doc_type="text")
    cell = table.get_cell("A1")
    assert cell.get_element("text:p/draw:frame") is not None


def test_set_cell_image_spreadsheet_branch():
    table = Table("T")
    img = DrawImage("test.png")

    frame = Frame.image_frame(img)
    with pytest.warns(DeprecationWarning):
        table.set_cell_image("A1", frame, doc_type="spreadsheet")
    cell = table.get_cell("A1")
    assert cell.get_element("draw:frame") is not None


def test_set_cell_image_text_branch_hit():
    table = Table("T")
    img = DrawImage("test.png")

    frame = Frame.image_frame(img)
    with pytest.warns(DeprecationWarning):
        table.set_cell_image("A1", frame, doc_type="text")
    cell = table.get_cell("A1")
    assert cell.get_element("text:p/draw:frame") is not None


def test_set_cell_image_spreadsheet_branch_hit():
    table = Table("T")
    img = DrawImage("test.png")

    frame = Frame.image_frame(img)
    with pytest.warns(DeprecationWarning):
        table.set_cell_image("A1", frame, doc_type="spreadsheet")
    cell = table.get_cell("A1")
    assert cell.get_element("draw:frame") is not None


def test_set_cell_image_auto_text_branch_hit():
    doc = Document("odt")
    table = Table("T")
    doc.body.append(table)
    img = DrawImage("test.png")

    frame = Frame.image_frame(img)
    # Trigger 1791 branch part (True) via auto doc_type="text"
    with pytest.warns(DeprecationWarning):
        table.set_cell_image("A1", frame)
    cell = table.get_cell("A1")
    assert cell.get_element("text:p/draw:frame") is not None


def test_set_cell_image_auto_spreadsheet_branch_hit():
    doc = Document("ods")
    table = doc.body.get_table(0)
    img = DrawImage("test.png")

    frame = Frame.image_frame(img)
    # Trigger 1791 branch part (False) via auto doc_type="spreadsheet"
    with pytest.warns(DeprecationWarning):
        table.set_cell_image("A1", frame)
    cell = table.get_cell("A1")
    assert cell.get_element("draw:frame") is not None


def test_set_cell_image_skip_both_branches():
    table = Table("T")
    img = DrawImage("test.png")

    frame = Frame.image_frame(img)
    with pytest.warns(DeprecationWarning):
        table.set_cell_image("A1", frame, doc_type="other")
    cell = table.get_cell("A1")
    assert cell.get_element("draw:frame") is None


def test_set_cell_image_spreadsheet():
    doc = Document("ods")
    table = doc.body.get_table(0)
    img = DrawImage("test.png")
    frame = Frame.image_frame(img)
    with pytest.warns(DeprecationWarning):
        table.set_cell_image("A1", frame, doc_type="spreadsheet")
    cell = table.get_cell("A1")
    assert cell.get_element("draw:frame") is not None


def test_set_cell_image_text():
    doc = Document("odt")
    table = Table("Test")
    doc.body.append(table)
    img = DrawImage("test.png")
    frame = Frame.image_frame(img)
    table.set_value("A1", "")
    with pytest.warns(DeprecationWarning):
        table.set_cell_image("A1", frame, doc_type="text")
    cell = table.get_cell("A1")
    assert cell.get_element("text:p/draw:frame") is not None


def test_set_cell_image_no_doctype():
    doc = Document("ods")
    table = doc.body.get_table(0)
    img = DrawImage("test.png")
    frame = Frame.image_frame(img)
    with pytest.warns(DeprecationWarning):
        table.set_cell_image("A1", frame)
    cell = table.get_cell("A1")
    assert cell.get_element("draw:frame") is not None
