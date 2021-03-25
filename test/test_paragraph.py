#!/usr/bin/env python
# Copyright 2018 Jérôme Dumonteil
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

from unittest import TestCase, main

from odfdo.element import Element
from odfdo.document import Document
from odfdo.paragraph import Paragraph, Spacer, Tab, LineBreak


class TestParagraph(TestCase):
    def setUp(self):
        self.document = document = Document("samples/base_text.odt")
        self.body = document.body

    def test_get_paragraph_list(self):
        body = self.body
        paragraphs = body.get_paragraphs()
        self.assertEqual(len(paragraphs), 7)
        second = paragraphs[1]
        text = second.text
        self.assertEqual(text, "This is the second paragraph.")

    def test_get_paragraph_list_style(self):
        body = self.body
        paragraphs = body.get_paragraphs(style="Hanging_20_indent")
        self.assertEqual(len(paragraphs), 1)
        paragraph = paragraphs[0]
        text = paragraph.text
        self.assertEqual(text, "This is a paragraph with a named style.")

    def test_get_paragraph_list_context(self):
        body = self.body
        section2 = body.get_section(position=1)
        paragraphs = section2.get_paragraphs()
        self.assertEqual(len(paragraphs), 2)
        paragraph = paragraphs[0]
        text = paragraph.text
        self.assertEqual(text, "First paragraph of the second section.")

    def test_get_paragraph_by_content(self):
        body = self.body
        regex = r"(first|second|a) paragraph"
        paragraph = body.get_paragraph(content=regex)
        text = paragraph.text
        self.assertEqual(text, "This is the first paragraph.")

    def test_get_paragraph_by_content_context(self):
        body = self.body
        section2 = body.get_section(position=1)
        regex = r"([Ff]irst|second|a) paragraph"
        paragraph = section2.get_paragraph(content=regex)
        text = paragraph.text
        self.assertEqual(text, "First paragraph of the second section.")

    def test_odf_paragraph(self):
        body = self.body
        paragraph = body.get_paragraph()
        self.assertTrue(isinstance(paragraph, Paragraph))

    def test_get_paragraph(self):
        body = self.body
        paragraph = body.get_paragraph(position=3)
        text = paragraph.text
        expected = "This is the first paragraph of the second title."
        self.assertEqual(text, expected)

    def test_insert_paragraph(self):
        body = self.body.clone
        paragraph = Paragraph("An inserted test", style="Text_20_body")
        body.append(paragraph)
        last_paragraph = body.get_paragraphs()[-1]
        self.assertEqual(last_paragraph.text, "An inserted test")

    def test_get_paragraph_missed(self):
        body = self.body
        paragraph = body.get_paragraph(position=999)
        self.assertEqual(paragraph, None)


class TestParagraphElements(TestCase):
    def test_create_space(self):
        sp1 = Spacer()
        expected = '<text:s text:c="1"/>'
        self.assertEqual(sp1.serialize(), expected)

    def test_create_spaces(self):
        sp5 = Spacer(5)
        expected = '<text:s text:c="5"/>'
        self.assertEqual(sp5.serialize(), expected)

    def test_create_tabulation(self):
        tab = Tab()
        expected = "<text:tab/>"
        self.assertEqual(tab.serialize(), expected)

    def test_create_tabulation_pos(self):
        tab = Tab(4)
        expected = '<text:tab text:tab-ref="4"/>'
        self.assertEqual(tab.serialize(), expected)

    def test_create_line_break(self):
        lb = LineBreak()
        expected = "<text:line-break/>"
        self.assertEqual(lb.serialize(), expected)

    def test_append_plain_text_unicode(self):
        txt = "A test,\n   \twith \n\n some é and \t and     5 spaces."
        para = Paragraph()
        para.append_plain_text(txt)
        expected = (
            '<text:p>A test,<text:line-break/> <text:s text:c="2"/>'
            "<text:tab/>with <text:line-break/><text:line-break/> "
            'some é and <text:tab/> and <text:s text:c="4"/>'
            "5 spaces.</text:p>"
        )
        self.assertEqual(para.serialize(), expected)

    def test_append_plain_text_utf8(self):
        txt = "A test,\n   \twith \n\n some é and \t and     5 spaces."
        para = Paragraph()
        para.append_plain_text(txt)
        expected = (
            '<text:p>A test,<text:line-break/> <text:s text:c="2"/>'
            "<text:tab/>with <text:line-break/><text:line-break/> "
            'some é and <text:tab/> and <text:s text:c="4"/>'
            "5 spaces.</text:p>"
        )
        self.assertEqual(para.serialize(), expected)

    def test_append_plain_text_guess_utf8(self):
        txt = "A test,\n   \twith \n\n some é and \t and     5 spaces."
        para = Paragraph()
        para.append_plain_text(txt)
        expected = (
            '<text:p>A test,<text:line-break/> <text:s text:c="2"/>'
            "<text:tab/>with <text:line-break/><text:line-break/> "
            'some é and <text:tab/> and <text:s text:c="4"/>'
            "5 spaces.</text:p>"
        )
        self.assertEqual(para.serialize(), expected)

    def test_append_plain_text_guess_iso(self):
        txt = "A test,\n   \twith \n\n some \xe9 and \t and     5 spaces."
        para = Paragraph()
        para.append_plain_text(txt)
        expected = (
            '<text:p>A test,<text:line-break/> <text:s text:c="2"/>'
            "<text:tab/>with <text:line-break/><text:line-break/> "
            'some é and <text:tab/> and <text:s text:c="4"/>'
            "5 spaces.</text:p>"
        )
        self.assertEqual(para.serialize(), expected)


class TestSetSpan(TestCase):
    def test_text(self):
        text = "Le Père Noël a une moustache rouge."
        paragraph = Paragraph(text)
        paragraph.set_span("highlight", regex="rouge")
        expected = (
            "<text:p>Le Père Noël a une moustache "
            "<text:span "
            'text:style-name="highlight">rouge</text:span>.'
            "</text:p>"
        )
        self.assertEqual(paragraph.serialize(), expected)

    def test_tail(self):
        data = (
            "<text:p>Le Père Noël a une "
            "<text:span>moustache</text:span> rouge.</text:p>"
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
        self.assertEqual(paragraph.serialize(), expected)

    def test_text_several(self):
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
        self.assertEqual(paragraph.serialize(), expected)

    def test_tail_several(self):
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
        self.assertEqual(paragraph.serialize(), expected)

    def test_offset(self):
        text = "Le Père Noël a une moustache rouge."
        paragraph = Paragraph(text)
        paragraph.set_span("highlight", offset=text.index("moustache"))
        expected = (
            "<text:p>Le Père Noël a une "
            '<text:span text:style-name="highlight">moustache '
            "rouge.</text:span>"
            "</text:p>"
        )
        self.assertEqual(paragraph.serialize(), expected)

    def test_offset_length(self):
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
        self.assertEqual(paragraph.serialize(), expected)


class TestPraragraphReferences(TestCase):
    def setUp(self):
        document = Document("samples/base_text.odt").clone
        self.body = document.body

    def test_set_reference_mark_single(self):
        body = self.body
        para = body.get_paragraph()
        para.set_reference_mark("one", position=0)
        expected = (
            '<text:p text:style-name="Text_20_body">'
            '<text:reference-mark text:name="one"/>'
            "This is the first paragraph.</text:p>"
        )
        self.assertEqual(para.serialize(), expected)

    def test_set_reference_mark_single_2(self):
        body = self.body
        para = body.get_paragraph()
        para.set_reference_mark("one", position=2)
        expected = (
            '<text:p text:style-name="Text_20_body">'
            "Th"
            '<text:reference-mark text:name="one"/>'
            "is is the first paragraph.</text:p>"
        )
        self.assertEqual(para.serialize(), expected)

    def test_set_reference_mark_content(self):
        body = self.body
        para = body.get_paragraph()
        para.set_reference_mark("one", content=para)
        expected = (
            '<text:p text:style-name="Text_20_body">'
            '<text:reference-mark-start text:name="one"/>'
            "This is the first paragraph."
            '<text:reference-mark-end text:name="one"/>'
            "</text:p>"
        )
        self.assertEqual(para.serialize(), expected)

    def test_set_reference_mark_content_pos(self):
        body = self.body
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
        self.assertEqual(para.serialize(), expected)

    def test_set_reference_mark_content_2(self):
        body = self.body
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
        self.assertEqual(para.serialize(), expected)

    def test_set_reference_mark_after(self):
        body = self.body
        para = body.get_paragraph()
        para.set_reference_mark("one", after="first")
        expected = (
            '<text:p text:style-name="Text_20_body">'
            "This is the first"
            '<text:reference-mark text:name="one"/>'
            " paragraph."
            "</text:p>"
        )
        self.assertEqual(para.serialize(), expected)

    def test_set_reference_mark_before(self):
        body = self.body
        para = body.get_paragraph()
        para.set_reference_mark("one", before="first")
        expected = (
            '<text:p text:style-name="Text_20_body">'
            "This is the "
            '<text:reference-mark text:name="one"/>'
            "first paragraph."
            "</text:p>"
        )
        self.assertEqual(para.serialize(), expected)


if __name__ == "__main__":
    main()
