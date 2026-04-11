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
from datetime import datetime
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from odfdo.annotation import Annotation, AnnotationEnd
from odfdo.element import Element, EText
from odfdo.mixin_paragraph import (
    _by_offset_wrapper,
    _by_regex_offset,
    _by_regex_wrapper,
)
from odfdo.note import Note
from odfdo.paragraph import Paragraph, Span
from odfdo.reference import (
    ReferenceMark,
    ReferenceMarkEnd,
    ReferenceMarkStart,
)
from odfdo.spacer import Spacer


def _make_span_method(element, *args, **kwargs):
    return Element.from_tag("text:span")


def test_by_offset_wrapper_counted():
    elem = Paragraph("abc")
    span = Span("def")
    elem.append(span)

    res = _by_offset_wrapper(_make_span_method, elem, offset=4, length=1)
    assert len(res) == 1


def test_by_offset_wrapper_no_container_parent():
    elem = Paragraph("abc")

    with patch.object(EText, "parent", new_callable=PropertyMock) as mock_parent:
        mock_parent.return_value = None
        res = _by_offset_wrapper(_make_span_method, elem, offset=0)
        assert res == []


def test_by_offset_wrapper_length_0():
    elem = Paragraph("abc")

    res = _by_offset_wrapper(_make_span_method, elem, offset=1, length=0)
    assert len(res) == 1


def test_by_regex_wrapper_no_regex():
    res = _by_regex_wrapper(lambda: None, Paragraph("test"), "")
    assert res == []


def test_by_regex_offset_wrapper_regex():
    @_by_regex_offset
    def my_method(element, *args, **kwargs):
        return Element.from_tag("text:span")

    elem = Paragraph("hello")
    res = my_method(elem, regex="ll")
    assert len(res) == 1


def test_expand_spaces_not_s():
    elem = Paragraph()
    elem.append("a")
    span = Element.from_tag("text:span")
    span.text = "b"
    elem.append(span)
    res = elem._expand_spaces("c")
    assert len(res) == 3


def test_sub_merge_spaces_complex():
    res = Paragraph._sub_merge_spaces("  a  b  ")
    assert len(res) >= 5


def test_append_plain_text_variants():
    elem = Paragraph()
    elem.append_plain_text(None)
    assert elem.inner_text == ""
    elem.append_plain_text(b"hello")
    assert elem.inner_text == "hello"


def test_append_element_special_tags():
    elem = Paragraph()
    s = Element.from_tag("text:s")
    s.set_attribute("text:c", "2")
    elem.append(s)
    assert elem.inner_text == "  "


def test_append_not_formatted():
    elem = Paragraph()
    elem.append("  a  \n  b  ", formatted=False)
    assert "a b" in elem.get_formatted_text()


def test_insert_note_existing():
    elem = Paragraph("test")
    note = Note("footnote", note_id="id0", citation="*")
    elem.insert_note(
        note,
        note_class="endnote",
        note_id="id1",
        citation="**",
        body="body",
    )
    assert note.note_class == "endnote"
    assert note.note_id == "id1"
    assert note.citation == "**"


def test_insert_note_after_element():
    elem = Paragraph("abc")
    span = Span("s")
    elem.append(span)
    elem.insert_note(after=span, note_id="id1", citation="*")
    assert span.xpath("descendant::text:note")


def test_insert_annotation_existing():
    elem = Paragraph("test")
    ann = Annotation(body="initial", creator="me")
    dt = datetime(2023, 1, 1)
    elem.insert_annotation(
        ann,
        body="new body",
        creator="you",
        date=dt,
    )
    assert ann.note_body == "new body"
    assert ann.creator == "you"
    assert ann.date == dt


def test_insert_annotation_content_element_empty():
    elem = Paragraph()
    inner = Span("")
    elem.append(inner)
    elem.insert_annotation(content=inner, body="ann", creator="me")
    assert inner.xpath("following-sibling::office:annotation")


def test_insert_annotation_position_tuple():
    elem = Paragraph("hello world")
    elem.insert_annotation(position=(1, 5), body="ann", creator="me")
    assert len(elem.xpath("//office:annotation")) == 1
    assert len(elem.xpath("//office:annotation-end")) == 1


def test_insert_annotation_bad_args():
    elem = Paragraph("test")
    with pytest.raises(ValueError, match="Annotation must have a creator"):
        elem.insert_annotation(content="regex", position=(1, 2), body="ann")


def test_insert_annotation_end_invalid():
    elem = Paragraph("test")
    with pytest.raises(ValueError):
        elem.insert_annotation_end(None)
    with pytest.raises(TypeError):
        elem.insert_annotation_end(Paragraph())


def test_set_reference_mark_content_element_empty():
    elem = Paragraph()
    inner = Span("")
    elem.append(inner)
    elem.set_reference_mark("ref1", content=inner)
    assert inner.xpath("following-sibling::text:reference-mark")


def test_set_reference_mark_position_tuple():
    elem = Paragraph("hello")
    elem.set_reference_mark("ref1", position=(1, 3))
    assert len(elem.xpath("//text:reference-mark-start")) == 1
    assert len(elem.xpath("//text:reference-mark-end")) == 1


def test_set_reference_mark_bad_args():
    elem = Paragraph("test")
    with pytest.raises(ValueError, match="bad arguments"):
        elem.set_reference_mark("ref1", content="regex", position=(1, 2))


def test_set_reference_mark_end_from_mark():
    elem = Paragraph("abc")
    mark = ReferenceMark("ref1")
    elem.append(mark)
    elem.set_reference_mark_end(mark, position=1)
    assert mark.tag == "text:reference-mark-start"
    assert len(elem.xpath("//text:reference-mark-end")) == 1


def test_remove_spans_no_keep():
    elem = Paragraph()
    span = Span("text")
    elem.append(span)
    res = elem.remove_spans(keep_heading=False)
    assert len(res.xpath("//text:span")) == 0


def test_insert_reference_no_display_no_body():
    elem = Paragraph("test")
    elem.insert_reference("ref1", ref_format="text")
    ref = elem.get_element("//text:reference-ref")
    assert ref.text == " "


def test_set_bookmark_content_int_position():
    elem = Paragraph("abc")
    elem.text = "abc"
    elem.set_bookmark("bm1", content="b", position=0)
    assert len(elem.xpath("//text:bookmark-start")) == 1
    assert len(elem.xpath("//text:bookmark-end")) == 1


def test_set_bookmark_position_tuple():
    elem = Paragraph("abc")
    elem.text = "abc"
    elem.set_bookmark("bm1", position=(1, 2))
    assert len(elem.xpath("//text:bookmark-start")) == 1
    assert len(elem.xpath("//text:bookmark-end")) == 1


def test_set_bookmark_role_start():
    elem = Paragraph("abc")
    elem.text = "abc"
    elem.set_bookmark("bm1", role="start", position=1)
    assert len(elem.xpath("//text:bookmark-start")) == 1


def test_set_bookmark_role_end():
    elem = Paragraph("abc")
    elem.text = "abc"
    elem.set_bookmark("bm1", role="end", position=1)
    assert len(elem.xpath("//text:bookmark-end")) == 1


def test_set_bookmark_bad_args():
    elem = Paragraph("test")
    with pytest.raises(ValueError, match="bad arguments"):
        elem.set_bookmark("bm1", content="regex", position=(1, 2))
    with pytest.raises(ValueError, match="bad arguments"):
        elem.set_bookmark("bm1", role="invalid")


def test_by_regex_wrapper_container_no_parent():
    elem = Paragraph("abc")

    def method(element, *args, **kwargs):
        return Element.from_tag("text:span")

    with patch.object(
        EText,
        "parent",
        new_callable=PropertyMock,
    ) as mock_parent:
        mock_parent.return_value = None
        res = _by_regex_wrapper(method, elem, regex="a")
        assert res == []


def test_by_offset_wrapper_upper_tail():
    para = Paragraph("a")
    span = Span("b")
    para.append(span)
    span.tail = "c"
    # offset 2 is in tail of span
    res = _by_offset_wrapper(_make_span_method, para, offset=2, length=1)
    assert len(res) == 1


def test_by_regex_wrapper_upper_tail():
    para = Paragraph("a")
    span = Span("b")
    para.append(span)
    span.tail = "c"
    res = _by_regex_wrapper(_make_span_method, para, regex="c")
    assert len(res) == 1


def test_expand_spaces_s_tag():
    elem = Paragraph()
    s = Element.from_tag("text:s")
    s.text = "  "
    elem.append(s)
    res = elem._expand_spaces("x")
    assert "  x" in "".join([str(x) for x in res])


def test_sub_merge_spaces_only_spaces():
    res = Paragraph._sub_merge_spaces("   ")
    assert len(res) == 1
    assert isinstance(res[0], Spacer)


def test_replace_tabs_lb():
    elem = Paragraph()
    res = elem._replace_tabs_lb(["a\tb\nc", Element.from_tag("text:s")])
    assert len(res) == 6


def test_insert_annotation_content_element_not_empty():
    elem = Paragraph()
    inner = Span("text")
    elem.append(inner)
    elem.insert_annotation(content=inner, body="ann", creator="me")
    assert inner.children[0].tag == "office:annotation"
    assert inner.children[-1].tag == "office:annotation-end"


def test_insert_annotation_end_exists():
    elem = Paragraph("abc")
    ann = Annotation(body="ann", creator="me", name="ann1")
    elem.append(ann)
    end1 = AnnotationEnd(ann)
    elem.append(end1)
    elem.insert_annotation_end(ann, position=1)
    assert len(elem.xpath("//office:annotation-end")) == 1


def test_set_reference_mark_content_element_not_empty():
    elem = Paragraph()
    inner = Span("text")
    elem.append(inner)
    elem.set_reference_mark("ref1", content=inner)
    assert inner.children[0].tag == "text:reference-mark-start"
    assert inner.children[-1].tag == "text:reference-mark-end"


def test_set_reference_mark_end_exists():
    elem = Paragraph("abc")
    mark = ReferenceMarkStart("ref1")
    elem.append(mark)
    end1 = ReferenceMarkEnd("ref1")
    elem.append(end1)
    elem.set_reference_mark_end(mark, position=1)
    assert len(elem.xpath("//text:reference-mark-end")) == 1


def test_insert_variable():
    elem = Paragraph("abc")
    var = Element.from_tag("text:variable-set")
    elem.insert_variable(var, after="a")
    assert elem.xpath("//text:variable-set")


def test_remove_span_list():
    elem = Paragraph("abc")
    span1 = elem.set_span("s1", regex="a")[0]
    span2 = elem.set_span("s2", regex="b")[0]
    res = elem.remove_span([span1, span2])
    assert len(res.xpath("//text:span")) == 0


def test_remove_links():
    elem = Paragraph("abc")
    elem.set_link("http://a", regex="a")
    res = elem.remove_links()
    assert len(res.xpath("//text:a")) == 0


def test_remove_link():
    elem = Paragraph("abc")
    link = elem.set_link("http://a", regex="a")[0]
    res = elem.remove_link(link)
    assert len(res.xpath("//text:a")) == 0


def test_insert_reference_with_mark():
    mark = ReferenceMarkStart("ref1")
    mark.set_attribute("text:name", "ref1")
    with patch.object(
        ReferenceMarkStart, "referenced_text", return_value="referenced text"
    ):
        doc = MagicMock()
        doc.get_reference_mark.return_value = mark
        para = Paragraph("ref here: ")
        with patch.object(
            Element, "document_body", new_callable=PropertyMock
        ) as mock_body:
            mock_body.return_value = doc
            para.insert_reference("ref1", ref_format="text")
    ref = para.get_element("//text:reference-ref")
    assert ref.text == "referenced text"


def test_by_offset_wrapper_tail_no_upper():
    para = Paragraph("abc")
    mock_text = MagicMock(spec=EText)
    mock_text.is_text.return_value = False
    mock_text.__len__.return_value = 3
    container = MagicMock(spec=Element)
    container.parent = None
    container.tail = "tail"
    mock_text.parent = container

    with patch.object(Element, "xpath", return_value=[mock_text]):
        res = _by_offset_wrapper(_make_span_method, para, offset=0, length=1)
        assert len(res) == 1


def test_by_regex_wrapper_tail_no_upper():
    para = Paragraph("abc")
    mock_text = MagicMock(spec=EText)
    mock_text.is_text.return_value = False
    mock_text.__str__.return_value = "tail"
    container = MagicMock(spec=Element)
    container.parent = None
    container.tail = "tail"
    mock_text.parent = container

    with patch.object(Element, "xpath", return_value=[mock_text]):
        res = _by_regex_wrapper(_make_span_method, para, regex="tail")
        assert len(res) == 1


def test_by_regex_offset_with_offset():
    @_by_regex_offset
    def method(element, *args, **kwargs):
        return Element.from_tag("text:span")

    para = Paragraph("abc")
    res = method(para, offset=1, length=1)
    assert len(res) == 1


def test_merge_spaces_with_element():
    para = Paragraph()
    span = Span("test")
    res = para._merge_spaces([span])
    assert res == [span]


def test_sub_merge_spaces_with_non_str():
    para = Paragraph()
    span = Span("test")
    # Patch the whole pattern object
    with patch("odfdo.mixin_paragraph._re_spaces_split") as mock_re:
        mock_re.split.return_value = [" ", span, " "]
        res = para._sub_merge_spaces("anything")
        assert span in res
        assert any(isinstance(x, Spacer) for x in res)

    with patch("odfdo.mixin_paragraph._re_spaces_split") as mock_re:
        mock_re.split.return_value = ["a", span]
        res = para._sub_merge_spaces("anything")
        assert res[1] == span


def test_replace_tabs_lb_empty_text():
    para = Paragraph()
    assert para._sub_replace_tabs_lb("") == []


def test_replace_tabs_lb_text_continue():
    para = Paragraph()
    res = para._sub_replace_tabs_lb("a\n\nb")
    assert len(res) == 4


def test_unformatted_variants():
    para = Paragraph()
    assert para._unformatted("") == ""
    assert para._unformatted(b"abc") == "abc"


def test_insert_note_existing_modify():
    para = Paragraph("test")
    # Use orphan Note
    note = Note("footnote", note_id="id1", citation="1", body="body1")
    # All True
    para.insert_note(
        note,
        note_class="endnote",
        note_id="id2",
        citation="2",
        body="body2",
    )
    assert note.note_class == "endnote"

    # All False
    note2 = Note("footnote", note_id="id3", citation="3", body="body3")
    para.insert_note(
        note2,
        note_class=None,
        note_id=None,
        citation=None,
        body=None,
    )


def test_insert_note_after_str():
    para = Paragraph("abc")
    para.insert_note(after="b", note_id="id1", citation="1", body="body")
    assert len(para.xpath("//text:note")) == 1


def test_insert_annotation_existing_modify():
    para = Paragraph("test")
    # Use orphan Annotation
    ann = Annotation("b1", creator="c1")
    dt = datetime(2023, 1, 1)
    # All True
    para.insert_annotation(ann, body="b2", creator="c2", date=dt)
    assert ann.note_body == "b2"

    # All False
    ann2 = Annotation("b3", creator="c3")
    para.insert_annotation(ann2, body=None, creator=None, date=None)


def test_insert_annotation_after_element():
    para = Paragraph("abc")
    span = Span("s")
    para.append(span)
    para.insert_annotation(after=span, body="ann", creator="me")
    assert span.xpath("office:annotation")


def test_insert_annotation_content_regex():
    para = Paragraph("hello world")
    para.insert_annotation(content="world", body="ann", creator="me")
    assert len(para.xpath("//office:annotation")) == 1
    assert len(para.xpath("//office:annotation-end")) == 1


def test_insert_annotation_bad_args_coverage():
    para = Paragraph("abc")
    with pytest.raises(ValueError, match="Bad arguments"):
        para.insert_annotation(
            content="a",
            position=(0, 1),
            body="ann",
            creator="me",
        )


def test_insert_annotation_end_replace():
    para = Paragraph("abc")
    ann = Annotation("ann", creator="me", name="ann1")
    para.append(ann)
    # Mock get_annotation_end to return an element
    end1 = AnnotationEnd(ann)
    # Force the True branch of line 649
    with patch.object(Paragraph, "get_annotation_end", return_value=end1):
        para.insert_annotation_end(ann, position=1)
    # Force the False branch of line 649
    with patch.object(Paragraph, "get_annotation_end", return_value=None):
        para.insert_annotation_end(ann, position=1)


def test_set_reference_mark_content_regex():
    para = Paragraph("hello world")
    para.set_reference_mark("ref1", content="world")
    assert len(para.xpath("//text:reference-mark-start")) == 1
    assert len(para.xpath("//text:reference-mark-end")) == 1


def test_set_reference_mark_positional():
    para = Paragraph("abc")
    para.set_reference_mark("ref1", position=1)
    assert len(para.xpath("//text:reference-mark")) == 1


def test_set_reference_mark_end_type_error():
    para = Paragraph("abc")
    with pytest.raises(TypeError, match="Not a ReferenceMark"):
        para.set_reference_mark_end(Element.from_tag("text:p"))


def test_set_reference_mark_end_replace():
    para = Paragraph("abc")
    mark = ReferenceMarkStart("ref1")
    para.append(mark)
    end1 = ReferenceMarkEnd("ref1")
    with patch.object(
        Paragraph,
        "get_reference_mark_end",
        return_value=end1,
    ):
        para.set_reference_mark_end(mark, position=1)
    with patch.object(
        Paragraph,
        "get_reference_mark_end",
        return_value=None,
    ):
        para.set_reference_mark_end(mark, position=1)


def test_remove_spans_variants():
    para = Paragraph("abc")
    para.remove_spans(keep_heading=False)
    para.remove_spans(keep_heading=True)


def test_insert_reference_after_element():
    para = Paragraph("abc")
    span = Span("s")
    para.append(span)
    para.insert_reference("ref1", after=span)
    assert span.xpath("text:reference-ref")


def test_insert_reference_text_format():
    para = Paragraph("abc")
    mark = ReferenceMarkStart("ref1")
    mark.set_attribute("text:name", "ref1")
    with patch.object(
        ReferenceMarkStart,
        "referenced_text",
        return_value="ref_text",
    ):
        doc = MagicMock()
        doc.get_reference_mark.return_value = mark
        with patch.object(
            Element, "document_body", new_callable=PropertyMock
        ) as mock_body:
            mock_body.return_value = doc
            para.insert_reference("ref1", ref_format="text")

    # Branch where get_reference_mark is not there
    with patch.object(
        Element,
        "document_body",
        new_callable=PropertyMock,
    ) as mock_body:
        mock_body.return_value = Element.from_tag("office:body")
        para.insert_reference("ref1", ref_format="text")


def test_set_bookmark_role_none():
    para = Paragraph("abc")
    para.set_bookmark("bm1", role=None, position=1)
    assert para.xpath("//text:bookmark")
