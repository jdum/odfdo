# Copyright 2018-2023 Jérôme Dumonteil
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

from collections.abc import Iterable
from pathlib import Path

import pytest

from odfdo.document import Document
from odfdo.element import Element
from odfdo.paragraph import LineBreak, Paragraph, Spacer, Tab

SAMPLE = Path(__file__).parent / "samples" / "base_text.odt"


@pytest.fixture
def document() -> Iterable[Document]:
    document = Document(SAMPLE)
    yield document


def test_get_paragraph_list(document):
    body = document.body
    paragraphs = body.get_paragraphs()
    assert len(paragraphs) == 7
    second = paragraphs[1]
    text = second.text
    assert text == "This is the second paragraph."


def test_get_paragraph_list_style(document):
    body = document.body
    paragraphs = body.get_paragraphs(style="Hanging_20_indent")
    assert len(paragraphs) == 1
    paragraph = paragraphs[0]
    text = paragraph.text
    assert text == "This is a paragraph with a named style."


def test_get_paragraph_list_context(document):
    body = document.body
    section2 = body.get_section(position=1)
    paragraphs = section2.get_paragraphs()
    assert len(paragraphs) == 2
    paragraph = paragraphs[0]
    text = paragraph.text
    assert text == "First paragraph of the second section."


def test_get_paragraph_by_content(document):
    body = document.body
    regex = r"(first|second|a) paragraph"
    paragraph = body.get_paragraph(content=regex)
    text = paragraph.text
    assert text == "This is the first paragraph."


def test_get_paragraph_by_content_context(document):
    body = document.body
    section2 = body.get_section(position=1)
    regex = r"([Ff]irst|second|a) paragraph"
    paragraph = section2.get_paragraph(content=regex)
    text = paragraph.text
    assert text == "First paragraph of the second section."


def test_odf_paragraph(document):
    body = document.body
    paragraph = body.get_paragraph()
    assert isinstance(paragraph, Paragraph)


def test_get_paragraph(document):
    body = document.body
    paragraph = body.get_paragraph(position=3)
    text = paragraph.text
    expected = "This is the first paragraph of the second title."
    assert text == expected


def test_insert_paragraph(document):
    body = document.body.clone
    paragraph = Paragraph("An inserted test", style="Text_20_body")
    body.append(paragraph)
    last_paragraph = body.get_paragraphs()[-1]
    assert last_paragraph.text == "An inserted test"


def test_get_paragraph_missed(document):
    body = document.body
    paragraph = body.get_paragraph(position=999)
    assert paragraph is None


def test_create_space():
    sp1 = Spacer()
    expected = '<text:s text:c="1"/>'
    assert sp1.serialize() == expected


def test_create_spaces():
    sp5 = Spacer(5)
    expected = '<text:s text:c="5"/>'
    assert sp5.serialize() == expected


def test_create_tabulation():
    tab = Tab()
    expected = "<text:tab/>"
    assert tab.serialize() == expected


def test_create_tabulation_pos():
    tab = Tab(4)
    expected = '<text:tab text:tab-ref="4"/>'
    assert tab.serialize() == expected


def test_create_line_break():
    lb = LineBreak()
    expected = "<text:line-break/>"
    assert lb.serialize() == expected


def test_append_plain_text_unicode():
    txt = "A test,\n   \twith \n\n some é and \t and     5 spaces."
    para = Paragraph()
    para.append_plain_text(txt)
    expected = (
        '<text:p>A test,<text:line-break/> <text:s text:c="2"/>'
        "<text:tab/>with <text:line-break/><text:line-break/> "
        'some é and <text:tab/> and <text:s text:c="4"/>'
        "5 spaces.</text:p>"
    )
    assert para.serialize() == expected


def test_append_plain_text_utf8():
    txt = "A test,\n   \twith \n\n some é and \t and     5 spaces."
    para = Paragraph()
    para.append_plain_text(txt)
    expected = (
        '<text:p>A test,<text:line-break/> <text:s text:c="2"/>'
        "<text:tab/>with <text:line-break/><text:line-break/> "
        'some é and <text:tab/> and <text:s text:c="4"/>'
        "5 spaces.</text:p>"
    )
    assert para.serialize() == expected


def test_append_plain_text_guess_utf8():
    txt = "A test,\n   \twith \n\n some é and \t and     5 spaces."
    para = Paragraph()
    para.append_plain_text(txt)
    expected = (
        '<text:p>A test,<text:line-break/> <text:s text:c="2"/>'
        "<text:tab/>with <text:line-break/><text:line-break/> "
        'some é and <text:tab/> and <text:s text:c="4"/>'
        "5 spaces.</text:p>"
    )
    assert para.serialize() == expected


def test_append_plain_text_guess_iso():
    txt = "A test,\n   \twith \n\n some \xe9 and \t and     5 spaces."
    para = Paragraph()
    para.append_plain_text(txt)
    expected = (
        '<text:p>A test,<text:line-break/> <text:s text:c="2"/>'
        "<text:tab/>with <text:line-break/><text:line-break/> "
        'some é and <text:tab/> and <text:s text:c="4"/>'
        "5 spaces.</text:p>"
    )
    assert para.serialize() == expected


def test_text():
    text = "Le Père Noël a une moustache rouge."
    paragraph = Paragraph(text)
    paragraph.set_span("highlight", regex="rouge")
    expected = (
        "<text:p>Le Père Noël a une moustache "
        "<text:span "
        'text:style-name="highlight">rouge</text:span>.'
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_tail():
    data = (
        "<text:p>Le Père Noël a une " "<text:span>moustache</text:span> rouge.</text:p>"
    )
    paragraph = Element.from_tag(data)
    paragraph.set_span("highlight", regex="rouge")
    expected = (
        "<text:p>Le Père Noël a une "
        "<text:span>moustache</text:span> "
        "<text:span "
        'text:style-name="highlight">rouge</text:span>.'
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_text_several():
    text = "Le Père rouge a une moustache rouge."
    paragraph = Paragraph(text)
    paragraph.set_span("highlight", regex="rouge")
    expected = (
        "<text:p>Le Père "
        "<text:span "
        'text:style-name="highlight">rouge</text:span> '
        "a une moustache "
        "<text:span "
        'text:style-name="highlight">rouge</text:span>.'
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_tail_several():
    data = (
        "<text:p>Le <text:span>Père</text:span> rouge a une "
        "moustache rouge.</text:p>"
    )
    paragraph = Element.from_tag(data)
    paragraph.set_span("highlight", regex="rouge")
    expected = (
        "<text:p>Le <text:span>Père</text:span> "
        "<text:span "
        'text:style-name="highlight">rouge</text:span> '
        "a une moustache "
        "<text:span "
        'text:style-name="highlight">rouge</text:span>.'
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_offset():
    text = "Le Père Noël a une moustache rouge."
    paragraph = Paragraph(text)
    paragraph.set_span("highlight", offset=text.index("moustache"))
    expected = (
        "<text:p>Le Père Noël a une "
        '<text:span text:style-name="highlight">moustache '
        "rouge.</text:span>"
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_offset_length():
    text = "Le Père Noël a une moustache rouge."
    paragraph = Paragraph(text)
    paragraph.set_span(
        "highlight", offset=text.index("moustache"), length=len("moustache")
    )
    expected = (
        "<text:p>Le Père Noël a une "
        '<text:span text:style-name="highlight">moustache'
        "</text:span> rouge."
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_set_reference_mark_single(document):
    body = document.body
    para = body.get_paragraph()
    para.set_reference_mark("one", position=0)
    expected = (
        '<text:p text:style-name="Text_20_body">'
        '<text:reference-mark text:name="one"/>'
        "This is the first paragraph.</text:p>"
    )
    assert para.serialize() == expected


def test_set_reference_mark_single_2(document):
    body = document.body
    para = body.get_paragraph()
    para.set_reference_mark("one", position=2)
    expected = (
        '<text:p text:style-name="Text_20_body">'
        "Th"
        '<text:reference-mark text:name="one"/>'
        "is is the first paragraph.</text:p>"
    )
    assert para.serialize() == expected


def test_set_reference_mark_content(document):
    body = document.body
    para = body.get_paragraph()
    para.set_reference_mark("one", content=para)
    expected = (
        '<text:p text:style-name="Text_20_body">'
        '<text:reference-mark-start text:name="one"/>'
        "This is the first paragraph."
        '<text:reference-mark-end text:name="one"/>'
        "</text:p>"
    )
    assert para.serialize() == expected


def test_set_reference_mark_content_pos(document):
    body = document.body
    para = body.get_paragraph()
    para.set_reference_mark("one", position=(2, 4))
    expected = (
        '<text:p text:style-name="Text_20_body">'
        "Th"
        '<text:reference-mark-start text:name="one"/>'
        "is"
        '<text:reference-mark-end text:name="one"/>'
        " is the first paragraph."
        "</text:p>"
    )
    assert para.serialize() == expected


def test_set_reference_mark_content_2(document):
    body = document.body
    para = body.get_paragraph()
    para.set_reference_mark("one", content="first paragraph.")
    expected = (
        '<text:p text:style-name="Text_20_body">'
        "This is the "
        '<text:reference-mark-start text:name="one"/>'
        "first paragraph."
        '<text:reference-mark-end text:name="one"/>'
        "</text:p>"
    )
    assert para.serialize() == expected


def test_set_reference_mark_after(document):
    body = document.body
    para = body.get_paragraph()
    para.set_reference_mark("one", after="first")
    expected = (
        '<text:p text:style-name="Text_20_body">'
        "This is the first"
        '<text:reference-mark text:name="one"/>'
        " paragraph."
        "</text:p>"
    )
    assert para.serialize() == expected


def test_set_reference_mark_before(document):
    body = document.body
    para = body.get_paragraph()
    para.set_reference_mark("one", before="first")
    expected = (
        '<text:p text:style-name="Text_20_body">'
        "This is the "
        '<text:reference-mark text:name="one"/>'
        "first paragraph."
        "</text:p>"
    )
    assert para.serialize() == expected
