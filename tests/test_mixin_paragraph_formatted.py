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
from unittest.mock import MagicMock, patch

from odfdo.annotation import Annotation
from odfdo.element import Element
from odfdo.header import Header
from odfdo.mixin_paragraph_formatted import (
    ParaFormattedTextMixin,
    _add_object_text,
    _add_object_text_annotation,
    _add_object_text_line_break,
    _add_object_text_note,
    _add_object_text_note_end,
    _add_object_text_note_foot,
    _add_object_text_span,
    _bold_styled,
    _formatted_text,
    _italic_styled,
    _post,
    _pre,
)
from odfdo.note import Note


class DummyElement(Element, ParaFormattedTextMixin):
    pass


def test_pre_no_match():
    # Patch the regex objects themselves
    with patch("odfdo.mixin_paragraph_formatted.RE_SP_PRE") as mock_re:
        mock_re.match.return_value = None
        assert _pre("abc") == ""
    assert _pre("  abc") == "  "


def test_post_no_match():
    with patch("odfdo.mixin_paragraph_formatted.RE_SP_POST") as mock_re:
        mock_re.search.return_value = None
        assert _post("abc") == ""
    assert _post("abc  ") == "  "


def test_bold_styled():
    assert _bold_styled("  abc  ") == "  **abc**  "


def test_italic_styled():
    assert _italic_styled("  abc  ") == "  *abc*  "


def test_get_formatted_text_simple_false():
    elem = DummyElement.from_tag("text:p")
    elem.text = "hello"
    assert elem.get_formatted_text() == "hello\n\n"


def test_add_object_text_span_no_rst():
    obj = Element.from_tag("text:span")
    obj.text = "bold"
    context = {"rst_mode": False}
    result = []
    _add_object_text(obj, context, result)
    assert result == ["bold"]


def test_add_object_text_span_empty_text():
    obj = Element.from_tag("text:span")
    obj.text = "  "
    context = {"rst_mode": True}
    result = []
    _add_object_text_span(obj, context, result)
    assert result == ["  "]


def test_add_object_text_span_no_style_name():
    obj = Element.from_tag("text:span")
    obj.text = "text"
    context = {"rst_mode": True}
    result = []
    _add_object_text_span(obj, context, result)
    assert result == ["text"]


def test_add_object_text_span_empty_style_name_2():
    obj = Element.from_tag("text:span")
    obj.text = "text"
    obj.set_attribute("text:style-name", "")
    context = {"rst_mode": True}
    result = []
    _add_object_text_span(obj, context, result)
    assert result == ["text"]


def test_add_object_text_note_foot_no_citation():
    note = Note("footnote", citation=None, body="body")
    context = {"footnotes": [], "rst_mode": False}
    result = []
    _add_object_text(note, context, result)
    assert context["footnotes"] == [(0, "body")]
    assert result == ["[0]"]


def test_add_object_text_note_foot_rst():
    note = Note("footnote", citation="1", body="body")
    context = {"footnotes": [], "rst_mode": True}
    result = []
    _add_object_text_note_foot(note, context, result)
    assert result == [" [#]_ "]


def test_add_object_text_note_end_no_citation():
    note = Note("endnote", citation=None, body="body")
    context = {"endnotes": [], "rst_mode": False}
    result = []
    _add_object_text_note_end(note, context, result)
    assert context["endnotes"] == [(0, "body")]
    assert result == ["(0)"]


def test_add_object_text_note_end_rst():
    note = Note("endnote", citation="1", body="body")
    context = {"endnotes": [], "rst_mode": True}
    result = []
    _add_object_text_note_end(note, context, result)
    assert result == [" [*]_ "]


def test_add_object_text_span_rst_bold():
    obj = Element.from_tag("text:span")
    obj.text = "bold"
    obj.set_attribute("text:style-name", "bold_style")

    mock_doc = MagicMock()
    mock_style = MagicMock()
    mock_style.get_properties.return_value = {"fo:font-weight": "bold"}
    mock_doc.get_style.return_value = mock_style

    context = {"rst_mode": True, "document": mock_doc}
    result = []
    _add_object_text_span(obj, context, result)
    assert result == ["**bold**"]


def test_add_object_text_span_rst_italic():
    obj = Element.from_tag("text:span")
    obj.text = "italic"
    obj.set_attribute("text:style-name", "italic_style")

    mock_doc = MagicMock()
    mock_style = MagicMock()
    mock_style.get_properties.return_value = {"fo:font-style": "italic"}
    mock_doc.get_style.return_value = mock_style

    context = {"rst_mode": True, "document": mock_doc}
    result = []
    _add_object_text_span(obj, context, result)
    assert result == ["*italic*"]


def test_add_object_text_span_rst_no_props():
    obj = Element.from_tag("text:span")
    obj.text = "normal"
    obj.set_attribute("text:style-name", "normal_style")

    mock_doc = MagicMock()
    mock_style = MagicMock()
    mock_style.get_properties.return_value = {}
    mock_doc.get_style.return_value = mock_style

    context = {"rst_mode": True, "document": mock_doc}
    result = []
    _add_object_text_span(obj, context, result)
    assert result == ["normal"]


def test_add_object_text_span_rst_no_doc():
    obj = Element.from_tag("text:span")
    obj.text = "normal"
    obj.set_attribute("text:style-name", "normal_style")

    context = {"rst_mode": True, "document": None}
    result = []
    _add_object_text_span(obj, context, result)
    assert result == ["normal"]


def test_add_object_text_annotation():
    obj = Annotation(body="note")
    obj.note_body = "note"
    context = {"annotations": [], "rst_mode": False}
    result = []
    _add_object_text(obj, context, result)
    assert context["annotations"] == ["note"]
    assert result == ["[*]"]


def test_add_object_text_annotation_rst():
    obj = Annotation(body="note")
    obj.note_body = "note"
    context = {"annotations": [], "rst_mode": True}
    result = []
    _add_object_text_annotation(obj, context, result)
    assert result == [" [#]_ "]


def test_add_object_text_tab():
    obj = Element.from_tag("text:tab")
    result = []
    _add_object_text(obj, {}, result)
    assert result == ["\t"]


def test_add_object_text_line_break():
    obj = Element.from_tag("text:line-break")
    result = []
    _add_object_text(obj, {"rst_mode": False}, result)
    assert result == ["\n"]


def test_add_object_text_line_break_rst():
    obj = Element.from_tag("text:line-break")
    result = []
    _add_object_text_line_break(obj, {"rst_mode": True}, result)
    assert result == ["\n|"]


def test_add_object_text_paragraph_tag():
    obj = Element.from_tag("text:p")
    obj.text = "text"
    result = []
    _add_object_text(obj, {}, result)
    assert result == ["text"]


def test_add_object_text_link_tag():
    obj = Element.from_tag("text:a")
    obj.text = "link"
    result = []
    _add_object_text(obj, {}, result)
    assert result == ["link"]


def test_add_object_text_other_tag():
    obj = Header(1, "title")
    result = []
    _add_object_text(obj, {}, result)
    assert result == ["title"]


def test_add_object_text_note_end_dispatch():
    note = Note("endnote", citation="1", body="body")
    context = {"endnotes": [], "rst_mode": False}
    result = []
    _add_object_text_note(note, context, result)
    assert result == ["(1)"]


def test_get_formatted_text_default_context():
    elem = DummyElement.from_tag("text:p")
    elem.text = "test"
    assert elem.get_formatted_text() == "test\n\n"
    assert elem.get_formatted_text(simple=True) == "test"


def test_formatted_text_etext():
    elem = Element.from_tag("text:p")
    elem.append("hello")
    res = _formatted_text(elem, {})
    assert res == "hello"


def test_get_formatted_text_with_context():
    elem = DummyElement.from_tag("text:p")
    elem.text = "test"
    context = {"rst_mode": True, "img_counter": 0, "images": []}
    assert elem.get_formatted_text(context=context, simple=True) == "test"


def test_add_object_text_span_hasattr_branches():
    context = {"rst_mode": True}
    result = []
    obj1 = Element.from_tag("text:span")
    obj1.set_attribute("text:style-name", "S1")
    _add_object_text_span(obj1, context, result)
    assert result == [""]  # text is empty

    class NoStyleElement:
        tag = "text:span"

        def xpath(self, query):
            return ["content"]

    obj2 = NoStyleElement()
    with patch(
        "odfdo.mixin_paragraph_formatted._formatted_text",
        return_value="text",
    ):
        _add_object_text_span(obj2, context, result)
    assert result[1] == "text"


def test_formatted_text_full_recursive():
    elem = Element.from_tag("text:p")
    span = Element.from_tag("text:span")
    span.text = "inner"
    elem.append(span)
    res = _formatted_text(elem, {})
    assert res == "inner"


def test_add_object_text_span_italic_else_branch():
    obj = Element.from_tag("text:span")
    obj.text = "text"
    obj.set_attribute("text:style-name", "style")

    mock_doc = MagicMock()
    mock_style = MagicMock()
    # Properties exists, but neither bold nor italic
    mock_style.get_properties.return_value = {"fo:color": "red"}
    mock_doc.get_style.return_value = mock_style

    context = {"rst_mode": True, "document": mock_doc}
    result = []
    _add_object_text_span(obj, context, result)
    assert result == ["text"]
