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


from odfdo.cell import Cell
from odfdo.document import Document
from odfdo.frame import DrawTextBox, Frame
from odfdo.header import Header
from odfdo.line_break import LineBreak
from odfdo.link import Link
from odfdo.list import List, ListItem
from odfdo.mixin_md import (
    MD_GLOBAL,
    LIStyle,
    SplitSpace,
    _as_bold,
    _as_bold_italic,
    _as_none,
    _as_strike,
    _copy_global,
    _md_swap_spaces,
    _restore_global,
    _set_global,
)
from odfdo.note import Note
from odfdo.paragraph import Paragraph, Span
from odfdo.table import Table
from odfdo.toc import TOC
from odfdo.tracked_changes import TrackedChanges


def test_md_swap_spaces_empty():
    word = ""
    assert _md_swap_spaces(word) == SplitSpace("", "", "")


def test_set_global():
    doc = "any"
    _set_global(doc)
    assert MD_GLOBAL["document"] == doc
    assert MD_GLOBAL["list_level"] == {}
    assert MD_GLOBAL["footnote"] == []
    assert MD_GLOBAL["endnote"] == []


def test_copy_global():
    doc = "any"
    _set_global(doc)
    glob_copy = _copy_global()
    assert glob_copy["document"] == "any"
    _set_global("other")
    assert glob_copy["document"] == "any"


def test_restore_global():
    data = {"document": "initial"}
    doc = "any"
    _set_global(doc)
    _restore_global(data)
    assert MD_GLOBAL["document"] == "initial"


def test_as_bold_empty():
    text = " "
    assert _as_bold(text) == text


def test_as_bold_italic_empty():
    text = " "
    assert _as_bold_italic(text) == text


def test_as_strike_empty():
    text = " "
    assert _as_strike(text) == text


def test_md_style_no_doc_no_style():
    p = Paragraph()
    _set_global(None)
    assert p._md_is_fixed_paragraph() is False


def test_md_style_no_doc():
    p = Paragraph()
    p.style = "some_style"
    _set_global(None)
    assert p._md_is_fixed_paragraph() is False


def test_md_style_no_style():
    doc = Document()
    _set_global(doc)
    p = Paragraph()
    p.style = "unknown_style"
    assert p._md_is_fixed_paragraph() is False


def test_md_style_styling_1():
    doc = Document()
    _set_global(doc)
    p = Paragraph()
    p.style = "unknown_style"
    result = p._md_styling()
    assert result == _as_none


def test_md_style_styling_no_doc():
    _set_global(None)
    p = Paragraph()
    p.style = "unknown_style"
    result = p._md_styling()
    assert result == _as_none


def test_md_toc_1():
    toc = TOC()
    index_body = toc.get_element("text:index-body")
    index_body.delete()
    result = toc._md_format()
    assert result == ""


def test_md_toc_2():
    toc = TOC()
    index_body = toc.get_element("text:index-body")
    index_body.delete()
    result = toc._md_collect()
    assert result == []


def test_md_note():
    note = Note()
    result = note._md_collect()
    assert result == ["[]\n"]


def test_md_zap():
    tc = TrackedChanges()
    result = tc._md_format()
    assert result == ""


def test_md_lb():
    lb = LineBreak()
    result = lb._md_collect()
    assert result == ["\\\n"]


def test_md_paragraph_tail():
    p = Paragraph("text")
    p.tail = "but paragraph have no tail"
    result = p._md_collect_fixed_text()
    assert result == "```\ntext\n```\nbut paragraph have no tail"


def test_md_paragraph_listyle_no_doc():
    _set_global(None)
    p = Paragraph()
    p.style = "unknown_style"
    result = p._md_collect_list_item_style()
    assert result == LIStyle("", "")


def test_md_paragraph_listyle_no_style():
    doc = Document()
    _set_global(doc)
    p = Paragraph()
    p.style = "unknown_style"
    result = p._md_collect_list_item_style()
    assert result == LIStyle("", "")


def test_md_paragraph_listyle_no_list_style():
    doc = Document()
    _set_global(doc)
    p = Paragraph()
    p.style = "Standard"
    result = p._md_collect_list_item_style()
    assert result == LIStyle("", "")


def test_md_header_level0():
    h = Header(0, "title")
    result = h._md_format()
    assert result == "title"


def test_md_list_item():
    item = ListItem(Header(1, "B"))
    result = item._md_format()
    assert result == " -  # B"


def test_md_list_buggy():
    li = List(["A", "B"])
    li.insert(Paragraph("this never happens"), position=1)
    result = li._md_format()
    assert result == " -  A\n -  B"


def test_md_list_empty():
    li = List()
    result = li._md_format()
    assert result == ""


def test_md_list_empty_collect():
    li = List()
    result = li._md_collect()
    assert result == []


def test_md_span_empty_collect():
    s = Span()
    result = s._md_collect()
    assert result == []


def test_md_span_text_collect():
    s = Span("text")
    result = s._md_collect()
    assert result == ["text"]


def test_md_link_text():
    url = Link("http://example.com", text="example")
    result = url._md_collect()
    assert result == ["[example](http://example.com)"]


def test_md_link_no_text():
    url = Link("http://example.com")
    result = url._md_collect()
    assert result == ["(http://example.com)"]


def test_md_link_empty():
    url = Link()
    result = url._md_collect()
    assert result == ["()"]


def test_md_draw_text_box_empty():
    dtb = DrawTextBox()
    result = dtb._md_collect()
    assert result == []


def test_md_draw_text_something():
    dtb = DrawTextBox()
    dtb.append(Paragraph("strange"))
    result = dtb._md_collect()
    assert result == ["strange"]


def test_md_frame_empty():
    frame = Frame()
    # frame.append(Paragraph("strange"))
    result = frame._md_collect()
    assert result == []


def test_md_frame_something():
    frame = Frame()
    frame.append(Paragraph("strange"))
    result = frame._md_collect()
    assert result == ["strange"]


def test_md_table_empty_collect():
    table = Table("sheet")
    result = table._md_collect()
    assert result == []


def test_md_table_mini_format_1():
    table = Table("sheet")
    table.set_cell((0, 0), Cell(1))
    result = table._md_format()
    assert result == "| 1 |\n|---|\n"


def test_md_table_mini_format_1_none():
    table = Table("sheet")
    table.set_cell((0, 0), Cell(None))
    result = table._md_format()
    assert result == "|   |\n|---|\n"


def test_md_table_mini_format_1_lg():
    table = Table("sheet")
    table.set_cell((0, 0), Cell("abcdef"))
    result = table._md_format()
    assert result == "| abcdef |\n|--------|\n"


def test_md_table_mini_format_2_2():
    table = Table("sheet")
    table.set_cell((0, 0), Cell(1))
    table.set_cell((1, 0), Cell(2))
    table.set_cell((0, 1), Cell(3))
    table.set_cell((1, 1), Cell(4))
    result = table._md_format()
    assert result == "| 1 | 2 |\n|---|---|\n| 3 | 4 |\n"


def test_md_table_mini_format_3_1():
    table = Table("sheet")
    table.set_cell((0, 0), Cell(1))
    table.set_cell((1, 0), Cell(2))
    table.set_cell((2, 0), Cell(3))
    result = table._md_format()
    assert result == "| 1 | 2 | 3 |\n|---|---|---|\n"


def test_md_table_mini_format_3_1_none_6():
    table = Table("sheet")
    table.set_cell((0, 0), Cell(1))
    table.set_cell((1, 0), Cell(None))
    table.set_cell((2, 0), Cell("abcdef"))
    result = table._md_format()
    assert result == "| 1 |   | abcdef |\n|---|---|--------|\n"


def test_md_table_mini_format_1_3_none_6():
    table = Table("sheet")
    table.set_cell((0, 0), Cell(1))
    table.set_cell((0, 1), Cell(None))
    table.set_cell((0, 2), Cell("abcdef"))
    result = table._md_format()
    assert result == "| 1      |\n|--------|\n|        |\n| abcdef |\n"
