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
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>

from collections.abc import Iterable

import pytest

from odfdo.document import Document
from odfdo.element import Element
from odfdo.header import Header
from odfdo.line_break import LineBreak
from odfdo.paragraph import Paragraph
from odfdo.spacer import Spacer
from odfdo.tab import Tab


@pytest.fixture
def document(samples) -> Iterable[Document]:
    document = Document(samples("base_text.odt"))
    yield document


def test_get_paragraph_list(document):
    body = document.body
    paragraphs = body.get_paragraphs()
    assert len(paragraphs) == 7
    second = paragraphs[1]
    text = second.text
    assert text == "This is the second paragraph."


def test_empty_str(document):
    paragraph = Paragraph()
    assert (str(paragraph)) == "\n"


def test_get_paragraph_list_str(document):
    body = document.body
    paragraphs = body.get_paragraphs()
    second = paragraphs[1]
    assert (str(second)) == "This is the second paragraph.\n"


def test_get_paragraph_list_property(document):
    body = document.body
    paragraphs = body.paragraphs
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


def test_get_paragraph_list_context_property(document):
    body = document.body
    section2 = body.get_section(position=1)
    paragraphs = section2.paragraphs
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
    paragraph = Paragraph("An inserted text", style="Text_20_body")
    body.append(paragraph)
    last_paragraph = body.get_paragraphs()[-1]
    assert last_paragraph.text == "An inserted text"


def test_insert_paragraph_property(document):
    body = document.body.clone
    paragraph = Paragraph("An inserted text", style="Text_20_body")
    body.append(paragraph)
    last_paragraph = body.paragraphs[-1]
    assert last_paragraph.text == "An inserted text"


def test_get_paragraph_missed(document):
    body = document.body
    paragraph = body.get_paragraph(position=999)
    assert paragraph is None


def test_read_spacer_empty():
    element = Element.from_tag("<text:s />")
    assert isinstance(element, Spacer)
    assert element.length == 1


def test_read_spacer_empty_str():
    element = Element.from_tag("<text:s />")
    assert str(element) == " "


def test_read_spacer_1():
    element = Element.from_tag('<text:s text:c="1" />')
    assert isinstance(element, Spacer)
    assert element.length == 1


def test_read_spacer_1_str():
    element = Element.from_tag('<text:s text:c="1" />')
    assert str(element) == " "


def test_read_spacer_2():
    element = Element.from_tag('<text:s text:c="2" />')
    assert isinstance(element, Spacer)
    assert element.length == 2


def test_read_spacer_2_str():
    element = Element.from_tag('<text:s text:c="2" />')
    assert str(element) == "  "


def test_create_space_1_base():
    sp1 = Spacer()
    expected = "<text:s/>"
    assert sp1.serialize() == expected


def test_create_space_1_number():
    sp1 = Spacer()
    assert sp1.number in (None, "1")


def test_create_space_1_length():
    sp1 = Spacer()
    assert sp1.length == 1


def test_create_space_1_length_mod_serialize():
    sp1 = Spacer()
    sp1.length = 3
    expected = '<text:s text:c="3"/>'
    assert sp1.serialize() == expected


def test_create_space_1_length_mod_number():
    sp1 = Spacer()
    sp1.length = 3
    assert sp1.number == "3"


def test_create_space_1_length_mod_length():
    sp1 = Spacer()
    sp1.length = 3
    assert sp1.length == 3


def test_create_space_5_base():
    sp1 = Spacer(5)
    expected = '<text:s text:c="5"/>'
    assert sp1.serialize() == expected


def test_create_space_5_number():
    sp1 = Spacer(5)
    assert sp1.number == "5"


def test_create_space_5_length():
    sp1 = Spacer(5)
    assert sp1.length == 5


def test_create_spaces():
    sp5 = Spacer(5)
    expected = '<text:s text:c="5"/>'
    assert sp5.serialize() == expected


def test_create_tabulation():
    tab = Tab()
    expected = "<text:tab/>"
    assert tab.serialize() == expected


def test_create_tabulation_str():
    tab = Tab()
    assert str(tab) == "\t"


def test_create_tabulation_pos():
    tab = Tab(4)
    expected = '<text:tab text:tab-ref="4"/>'
    assert tab.serialize() == expected


def test_create_line_break():
    lb = LineBreak()
    expected = "<text:line-break/>"
    assert lb.serialize() == expected


def test_create_line_break_str():
    lb = LineBreak()
    assert str(lb) == "\n"


def test_create_naive_spaces():
    para = Paragraph("   ")
    # old rules
    # expected = '<text:p> <text:s text:c="2"/></text:p>'
    expected = '<text:p><text:s text:c="3"/></text:p>'
    assert para.serialize() == expected


def test_create_naive_spaces_no_format():
    para = Paragraph("   ", formatted=False)
    expected = "<text:p><text:s/></text:p>"
    assert para.serialize() == expected


def test_create_naive_cr():
    para = Paragraph("\n")
    expected = "<text:p><text:line-break/></text:p>"
    assert para.serialize() == expected


def test_create_naive_cr_no_format():
    para = Paragraph("\n", formatted=False)
    expected = "<text:p><text:s/></text:p>"
    assert para.serialize() == expected


def test_plain_text_splitted_length():
    txt = "A test,\n   \twith \n\n some é and \t and     5 spaces."
    para = Paragraph()
    content = para._expand_spaces(txt)
    content = para._merge_spaces(content)
    content = para._replace_tabs_lb(content)
    assert len(content) == 13


def test_plain_text_splitted_elements():
    txt = "A test,\n   \twith \n\n some é and \t and     5 spaces."
    para = Paragraph()
    content = para._expand_spaces(txt)
    content = para._merge_spaces(content)
    content = para._replace_tabs_lb(content)
    assert content[0] == "A test,"
    assert isinstance(content[1], LineBreak)
    assert isinstance(content[3], Spacer)
    assert isinstance(content[4], Tab)
    assert isinstance(content[6], LineBreak)


def test_plain_text_splitted_empty():
    para = Paragraph()
    content = para._expand_spaces("")
    content = para._merge_spaces(content)
    content = para._replace_tabs_lb(content)
    assert content == []


def test_append_plain_text_guess_utf8():
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


def test_append_plain_text_guess_utf8_2():
    txt = "A test,\n   \twith \n\n some \xe9 and \t and     5 spaces."
    para = Paragraph()
    para.append(txt)
    expected = (
        '<text:p>A test,<text:line-break/> <text:s text:c="2"/>'
        "<text:tab/>with <text:line-break/><text:line-break/> "
        'some é and <text:tab/> and <text:s text:c="4"/>'
        "5 spaces.</text:p>"
    )
    assert para.serialize() == expected


def test_append_plain_text_guess_utf8_2_no_format():
    txt = "A test,\n   \twith \n\n some \xe9 and \t and     5 spaces."
    para = Paragraph()
    para.append(txt, formatted=False)
    expected = "<text:p>A test, with some é and and 5 spaces.</text:p>"
    assert para.serialize() == expected


def test_append_plain_text_guess_utf8_3_no_format():
    txt = " A test,\n   \twith \n\n some \xe9 and \t and     5 spaces. "
    para = Paragraph()
    para.append(txt, formatted=False)
    # old rule
    # expected = "<text:p> A test, with some é and and 5 spaces. </text:p>"
    # new rule, the result must comply with standard
    expected = (
        "<text:p><text:s/>A test, with some é and and 5 spaces.<text:s/></text:p>"
    )
    assert para.serialize() == expected


def test_paragraph_1_space():
    para = Paragraph(" ")
    # new rule
    expected = "<text:p><text:s/></text:p>"
    assert para.serialize() == expected


def test_paragraph_2_spaces():
    para = Paragraph("  ")
    # new rule
    expected = '<text:p><text:s text:c="2"/></text:p>'
    assert para.serialize() == expected


def test_paragraph_1_space_no_format():
    para = Paragraph(" ", formatted=False)
    expected = "<text:p><text:s/></text:p>"
    assert para.serialize() == expected


def test_paragraph_2_spaces_no_format():
    para = Paragraph("  ", formatted=False)
    # new rule
    expected = "<text:p><text:s/></text:p>"
    assert para.serialize() == expected


def test_paragraph_any_spaces_no_format():
    para = Paragraph("  \n\t ", formatted=False)
    # new rule
    expected = "<text:p><text:s/></text:p>"
    assert para.serialize() == expected


def test_append_plain_text_guess_utf8_4_no_format():
    txt = " A test,\n   \twith \n\n some \xe9 and \t and     5 spaces."
    para = Paragraph(" ")  # -> text:s text:c="1"/>
    para.append(txt, formatted=False)
    # old rule
    # expected = "<text:p> A test, with some é and and 5 spaces.</text:p>"
    expected = (
        '<text:p><text:s text:c="2"/>A test, with some é and and 5 spaces.</text:p>'
    )
    assert para.serialize() == expected


def test_append_plain_text_guess_utf8_5():
    txt = " A test,\n   \twith \n\n some \xe9 and \t and     5 spaces."
    para = Paragraph(" ")
    para.append(txt)
    expected = (
        '<text:p><text:s text:c="2"/>'
        'A test,<text:line-break/> <text:s text:c="2"/>'
        "<text:tab/>with <text:line-break/><text:line-break/> "
        'some é and <text:tab/> and <text:s text:c="4"/>'
        "5 spaces.</text:p>"
    )
    assert para.serialize() == expected


def test_space_plus_space():
    para = Paragraph(" ")
    para.append(" ")
    expected = '<text:p><text:s text:c="2"/></text:p>'
    assert para.serialize() == expected


def test_space_plus_space_no_format():
    para = Paragraph(" ")
    para.append(" ", formatted=False)
    expected = '<text:p><text:s text:c="2"/></text:p>'
    assert para.serialize() == expected


def test_append_simple():
    para = Paragraph("first")
    para.append(" second")
    assert para.text == "first second"


def test_append_simple_end_space():
    para = Paragraph("first ")
    para.append(" second")
    expected = "<text:p>first <text:s/>second</text:p>"
    assert para.serialize() == expected


def test_append_simple_end_2_space():
    para = Paragraph("first ")
    para.append("  second")
    expected = '<text:p>first <text:s text:c="2"/>second</text:p>'
    assert para.serialize() == expected


def test_append_simple_end_space_no_second():
    para = Paragraph("first ")
    para.append("second")
    assert para.text == "first second"


def test_append_multiline_text():
    para = Paragraph("first")
    para.append(" second\n third")
    assert para.text == "first second"
    assert para.inner_text == "first second\n third"


def test_append_multiline():
    para = Paragraph("first")
    para.append(" second\n third")
    expected = "<text:p>first second<text:line-break/> third</text:p>"
    assert para.serialize() == expected


def test_append_multiline_no_format():
    para = Paragraph("first")
    para.append(" second\n third", formatted=False)
    assert para.text == "first second third"


def test_append_plain_text_bytes_utf8():
    txt = "A test,\n   \twith \n\n some é and \t and     5 spaces."
    btxt: bytes = txt.encode("utf-8")
    para = Paragraph()
    para.append_plain_text(btxt)
    expected = (
        '<text:p>A test,<text:line-break/> <text:s text:c="2"/>'
        "<text:tab/>with <text:line-break/><text:line-break/> "
        'some é and <text:tab/> and <text:s text:c="4"/>'
        "5 spaces.</text:p>"
    )
    assert para.serialize() == expected


def test_append_plain_text_bytes_utf8_2():
    txt = "A test,\n   \twith \n\n some é and \t and     5 spaces."
    btxt: bytes = txt.encode("utf-8")
    para = Paragraph()
    para.append(btxt)
    expected = (
        '<text:p>A test,<text:line-break/> <text:s text:c="2"/>'
        "<text:tab/>with <text:line-break/><text:line-break/> "
        'some é and <text:tab/> and <text:s text:c="4"/>'
        "5 spaces.</text:p>"
    )
    assert para.serialize() == expected


def test_create_plain_text_utf8():
    txt = "A test,\n   \twith \n\n some é and \t and     5 spaces."
    para = Paragraph(txt)
    expected = (
        '<text:p>A test,<text:line-break/> <text:s text:c="2"/>'
        "<text:tab/>with <text:line-break/><text:line-break/> "
        'some é and <text:tab/> and <text:s text:c="4"/>'
        "5 spaces.</text:p>"
    )
    assert para.serialize() == expected


def test_create_no_plain_text_utf8():
    txt = "A test,\n   \twith \n\n some é and \t and     5 spaces."
    para = Paragraph(txt, formatted=False)
    result = para.serialize()
    assert "line-break" not in result
    assert "text:s" not in result
    assert "text:tab" not in result


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


def test_text_setter_1():
    text = "Le Père Noël a une moustache rouge."
    paragraph = Paragraph(text)
    paragraph.text = None
    expected1 = "<text:p></text:p>"
    expected2 = "<text:p/>"
    assert paragraph.serialize() in (expected1, expected2)


def test_text_setter_2():
    text = "Le Père Noël a une moustache rouge."
    paragraph = Paragraph(text)
    paragraph.text = "new text"
    expected = "<text:p>new text</text:p>"
    assert paragraph.serialize() == expected


def test_text_spaces_s1():
    text = " Le Père Noël a une moustache rouge."
    paragraph = Paragraph(text)
    paragraph.set_span("highlight", regex="rouge")
    expected = (
        "<text:p><text:s/>Le Père Noël a une moustache "
        "<text:span "
        'text:style-name="highlight">rouge</text:span>.'
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_text_spaces_s1_no_format():
    text = " Le Père Noël a une moustache rouge."
    paragraph = Paragraph(text, formatted=False)
    paragraph.set_span("highlight", regex="rouge")
    expected = (
        "<text:p><text:s/>Le Père Noël a une moustache "
        "<text:span "
        'text:style-name="highlight">rouge</text:span>.'
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_text_spaces_s2():
    text = "  Le Père Noël a une moustache rouge."
    paragraph = Paragraph(text)
    paragraph.set_span("highlight", regex="rouge")
    expected = (
        '<text:p><text:s text:c="2"/>Le Père Noël a une moustache '
        "<text:span "
        'text:style-name="highlight">rouge</text:span>.'
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_text_spaces_s2_no_format():
    text = "  Le Père Noël a une moustache rouge."
    paragraph = Paragraph(text, formatted=False)
    paragraph.set_span("highlight", regex="rouge")
    expected = (
        "<text:p><text:s/>Le Père Noël a une moustache "
        "<text:span "
        'text:style-name="highlight">rouge</text:span>.'
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_text_spaces_s3():
    text = " \n Le Père Noël a une moustache rouge."
    paragraph = Paragraph(text)
    paragraph.set_span("highlight", regex="rouge")
    expected = (
        "<text:p><text:s/><text:line-break/> Le Père Noël a une moustache "
        "<text:span "
        'text:style-name="highlight">rouge</text:span>.'
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_text_spaces_s3_no_format():
    text = " \n Le Père Noël a une moustache rouge."
    paragraph = Paragraph(text, formatted=False)
    paragraph.set_span("highlight", regex="rouge")
    expected = (
        "<text:p><text:s/>Le Père Noël a une moustache "
        "<text:span "
        'text:style-name="highlight">rouge</text:span>.'
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_text_spaces_s4():
    text = " \n\t Le Père Noël a une moustache rouge."
    paragraph = Paragraph(text)
    paragraph.set_span("highlight", regex="rouge")
    expected = (
        "<text:p><text:s/><text:line-break/><text:tab/> "
        "Le Père Noël a une moustache "
        "<text:span "
        'text:style-name="highlight">rouge</text:span>.'
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_text_spaces_s4_no_format():
    text = "<text:s/>\n\t Le Père Noël a une moustache rouge."
    paragraph = Paragraph(text, formatted=False)
    paragraph.set_span("highlight", regex="rouge")
    expected = (
        "<text:p>&lt;text:s/&gt; Le Père Noël a une moustache "
        "<text:span "
        'text:style-name="highlight">rouge</text:span>.'
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_text_spaces_e1():
    text = "Le Père Noël a une moustache rouge. "
    paragraph = Paragraph(text)
    paragraph.set_span("highlight", regex="rouge")
    expected = (
        "<text:p>Le Père Noël a une moustache "
        "<text:span "
        'text:style-name="highlight">rouge</text:span>.'
        "<text:s/></text:p>"
    )
    assert paragraph.serialize() == expected


def test_text_spaces_e1_no_format():
    text = "Le Père Noël a une moustache rouge. "
    paragraph = Paragraph(text, formatted=False)
    paragraph.set_span("highlight", regex="rouge")
    expected = (
        "<text:p>Le Père Noël a une moustache "
        "<text:span "
        'text:style-name="highlight">rouge</text:span>.'
        "<text:s/></text:p>"
    )
    assert paragraph.serialize() == expected


def test_text_spaces_e2():
    text = "Le Père Noël a une moustache rouge.  "
    paragraph = Paragraph(text)
    paragraph.set_span("highlight", regex="rouge")
    expected = (
        "<text:p>Le Père Noël a une moustache "
        "<text:span "
        'text:style-name="highlight">rouge</text:span>.'
        '<text:s text:c="2"/>'
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_text_spaces_e2_no_format():
    text = "Le Père Noël a une moustache rouge.  "
    paragraph = Paragraph(text, formatted=False)
    paragraph.set_span("highlight", regex="rouge")
    expected = (
        "<text:p>Le Père Noël a une moustache "
        "<text:span "
        'text:style-name="highlight">rouge</text:span>.'
        "<text:s/></text:p>"
    )
    assert paragraph.serialize() == expected


def test_text_spaces_e3():
    text = "Le Père Noël a une moustache rouge. \n "
    paragraph = Paragraph(text)
    paragraph.set_span("highlight", regex="rouge")
    expected = (
        "<text:p>Le Père Noël a une moustache "
        "<text:span "
        'text:style-name="highlight">rouge</text:span>.'
        " <text:line-break/><text:s/>"
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_text_spaces_e3_no_format():
    text = "Le Père Noël a une moustache rouge. \n "
    paragraph = Paragraph(text, formatted=False)
    paragraph.set_span("highlight", regex="rouge")
    expected = (
        "<text:p>Le Père Noël a une moustache "
        "<text:span "
        'text:style-name="highlight">rouge</text:span>.'
        "<text:s/></text:p>"
    )
    assert paragraph.serialize() == expected


def test_multiple_append_1():
    paragraph = Paragraph("a")
    paragraph.append("b")
    paragraph.append("\n")
    paragraph.append("c")
    paragraph.append("d")
    paragraph.append(" ")
    expected = "<text:p>ab<text:line-break/>cd<text:s/></text:p>"
    assert paragraph.serialize() == expected


def test_multiple_append_2():
    paragraph = Paragraph("a")
    paragraph.append("b")
    paragraph.append("\n")
    paragraph.append("c")
    paragraph.append("d")
    paragraph.append(" ")
    paragraph.append(" ")
    expected = '<text:p>ab<text:line-break/>cd<text:s text:c="2"/></text:p>'
    assert paragraph.serialize() == expected


def test_init_append_element_paragraph():
    elem = Paragraph("a")
    paragraph = Paragraph(elem)
    expected = "<text:p>a<text:line-break/></text:p>"
    assert paragraph.serialize() == expected


def test_init_append_element_header():
    elem = Header(1, "header")
    paragraph = Paragraph(elem)
    expected = "<text:p>header<text:line-break/></text:p>"
    assert paragraph.serialize() == expected


def test_init_append_element_other():
    elem = Tab()
    paragraph = Paragraph(elem)
    expected = "<text:p><text:tab/></text:p>"
    assert paragraph.serialize() == expected


def test_text_spaces_se4():
    text = " \n Le Père Noël a une moustache rouge. \n\t "
    paragraph = Paragraph(text)
    paragraph.set_span("highlight", regex="rouge")
    expected = (
        "<text:p><text:s/><text:line-break/> "
        "Le Père Noël a une moustache "
        "<text:span "
        'text:style-name="highlight">rouge</text:span>.'
        " <text:line-break/><text:tab/>"
        "<text:s/></text:p>"
    )
    assert paragraph.serialize() == expected


def test_text_spaces_se4_no_format():
    text = " \n Le Père Noël a une moustache rouge. \n\t "
    paragraph = Paragraph(text, formatted=False)
    paragraph.set_span("highlight", regex="rouge")
    expected = (
        "<text:p><text:s/>Le Père Noël a une moustache "
        "<text:span "
        'text:style-name="highlight">rouge</text:span>.'
        "<text:s/></text:p>"
    )
    assert paragraph.serialize() == expected


def test_tail():
    data = "<text:p>Le Père Noël a une <text:span>moustache</text:span> rouge.</text:p>"
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
        "<text:p>Le <text:span>Père</text:span> rouge a une moustache rouge.</text:p>"
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


def test_spacer_setter_0():
    spacer = Spacer()
    spacer.text = None
    expected = "<text:s/>"
    assert spacer.serialize() == expected


def test_spacer_setter_1():
    spacer = Spacer()
    spacer.text = ""
    expected = "<text:s/>"
    assert spacer.serialize() == expected


def test_spacer_setter_2():
    spacer = Spacer()
    spacer.text = "x"
    expected = "<text:s/>"
    assert spacer.serialize() == expected


def test_spacer_setter_3():
    spacer = Spacer()
    spacer.text = "xx"
    expected = '<text:s text:c="2"/>'
    assert spacer.serialize() == expected


def test_spacer_setter_4():
    spacer = Spacer()
    spacer.text = "xxx"
    expected = '<text:s text:c="3"/>'
    assert spacer.serialize() == expected


def test_tab_getter_0():
    tab = Tab()
    expected = "<text:tab/>"
    assert tab.serialize() == expected


def test_tab_getter_1():
    tab = Tab()
    assert tab.text == "\t"


def test_line_break_getter_0():
    lb = LineBreak()
    expected = "<text:line-break/>"
    assert lb.serialize() == expected


def test_line_break_getter_1():
    lb = LineBreak()
    assert lb.text == "\n"


def test_paragraph_formatted():
    p = Paragraph()
    p.text = "content"
    assert p.get_formatted_text() == "content\n\n"


def test_paragraph_formatted_simple():
    p = Paragraph()
    p.text = "content"
    assert p.get_formatted_text(simple=True) == "content"


def test_paragraph_formatted_context_simple():
    p = Paragraph()
    p.text = "content"
    context = {
        "document": None,
        "footnotes": [],
        "endnotes": [],
        "annotations": [],
        "rst_mode": False,
        "img_counter": 0,
        "images": [],
        "no_img_level": 0,
    }
    assert p.get_formatted_text(context, simple=True) == "content"
