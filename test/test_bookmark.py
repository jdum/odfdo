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
# Authors: Hervé Cauwelier <herve@itaapy.com>

from unittest import TestCase, main

from odfdo.document import Document
from odfdo.bookmark import Bookmark, BookmarkStart, BookmarkEnd
from odfdo.paragraph import Paragraph

ZOE = "你好 Zoé"


class BookmarkTest(TestCase):
    def setUp(self):
        document = Document("samples/bookmark.odt")
        self.body = document.body

    def test_create_bookmark(self):
        bookmark = Bookmark(ZOE)
        expected = '<text:bookmark text:name="%s"/>' % ZOE
        self.assertEqual(bookmark.serialize(), expected)

    def test_create_bookmark_start(self):
        bookmark_start = BookmarkStart(ZOE)
        expected = '<text:bookmark-start text:name="%s"/>' % ZOE
        self.assertEqual(bookmark_start.serialize(), expected)

    def test_create_bookmark_end(self):
        bookmark_end = BookmarkEnd(ZOE)
        expected = '<text:bookmark-end text:name="%s"/>' % ZOE
        self.assertEqual(bookmark_end.serialize(), expected)

    def test_get_bookmark(self):
        body = self.body
        para = self.body.get_paragraph()
        bookmark = Bookmark(ZOE)
        para.append(bookmark)
        get = body.get_bookmark(name=ZOE)
        expected = '<text:bookmark text:name="%s"/>' % ZOE
        self.assertEqual(get.serialize(), expected)

    def test_get_bookmark_list(self):
        body = self.body
        result = self.body.get_bookmarks()
        self.assertEqual(len(result), 1)
        element = result[0]
        expected = '<text:bookmark text:name="Repère de texte"/>'
        self.assertEqual(element.serialize(), expected)

    def test_get_bookmark_start(self):
        body = self.body
        para = self.body.get_paragraph()
        bookmark_start = BookmarkStart(ZOE)
        para.append(bookmark_start)
        get = body.get_bookmark_start(name=ZOE)
        expected = '<text:bookmark-start text:name="%s"/>' % ZOE
        self.assertEqual(get.serialize(), expected)

    def test_get_bookmark_start_list(self):
        bookmark_start = BookmarkStart(ZOE)
        para = self.body.get_paragraph()
        para.append(bookmark_start)
        get = self.body.get_bookmark_starts()[0]
        expected = '<text:bookmark-start text:name="%s"/>' % ZOE
        self.assertEqual(get.serialize(), expected)

    def test_get_bookmark_end(self):
        body = self.body
        para = self.body.get_paragraph()
        bookmark_end = BookmarkEnd(ZOE)
        para.append(bookmark_end)
        get = body.get_bookmark_end(name=ZOE)
        expected = '<text:bookmark-end text:name="%s"/>' % ZOE
        self.assertEqual(get.serialize(), expected)

    def test_get_bookmark_end_list(self):
        body = self.body
        bookmark_end = BookmarkEnd(ZOE)
        para = self.body.get_paragraph()
        para.append(bookmark_end)
        get = body.get_bookmark_ends()[0]
        expected = '<text:bookmark-end text:name="%s"/>' % ZOE
        self.assertEqual(get.serialize(), expected)

    def test_set_bookmark_simple(self):
        body = self.body
        paragraph = body.get_paragraph(position=-1)
        paragraph.set_bookmark("A bookmark")
        bookmark = paragraph.get_bookmark(name="A bookmark")
        self.assertNotEqual(bookmark, None)

    def test_set_bookmark_with_after_without_position(self):
        paragraph = Paragraph("aa bb aa aa cc aa dd")
        paragraph.set_span(style="style", regex="bb aa aa")
        paragraph.set_span(style="style", regex="dd")
        paragraph.set_bookmark("bookmark", after="aa")
        expected = (
            '<text:p>aa<text:bookmark text:name="bookmark"/> '
            '<text:span text:style-name="style">bb aa aa'
            "</text:span>"
            ' cc aa <text:span text:style-name="style">dd</text:span>'
            "</text:p>"
        )
        self.assertEqual(paragraph.serialize(), expected)

    def test_set_bookmark_with_before(self):
        paragraph = Paragraph("aa bb aa aa cc aa dd")
        paragraph.set_span(style="style", regex="bb aa aa")
        paragraph.set_span(style="style", regex="dd")
        paragraph.set_bookmark("bookmark", before="aa", position=1)
        expected = (
            "<text:p>aa "
            '<text:span text:style-name="style">bb '
            '<text:bookmark text:name="bookmark"/>aa aa'
            "</text:span>"
            ' cc aa <text:span text:style-name="style">dd</text:span>'
            "</text:p>"
        )
        self.assertEqual(paragraph.serialize(), expected)

    def test_set_bookmark_with_after(self):
        paragraph = Paragraph("aa bb aa aa cc aa dd")
        paragraph.set_span(style="style", regex="bb aa aa")
        paragraph.set_span(style="style", regex="dd")
        paragraph.set_bookmark("bookmark", after="aa", position=1)
        expected = (
            "<text:p>aa "
            '<text:span text:style-name="style">bb '
            'aa<text:bookmark text:name="bookmark"/> aa'
            "</text:span>"
            ' cc aa <text:span text:style-name="style">dd</text:span>'
            "</text:p>"
        )
        self.assertEqual(paragraph.serialize(), expected)

    def test_set_bookmark_with_position(self):
        paragraph = Paragraph("aa bb aa aa cc aa dd")
        paragraph.set_span(style="style", regex="bb aa aa")
        paragraph.set_span(style="style", regex="dd")
        paragraph.set_bookmark("bookmark1", position=0)
        paragraph.set_bookmark("bookmark2", position=2)
        paragraph.set_bookmark("bookmark3", position=len("aa bb aa aa cc aa dd"))
        expected = (
            '<text:p><text:bookmark text:name="bookmark1"/>aa'
            '<text:bookmark text:name="bookmark2"/> '
            '<text:span text:style-name="style">bb aa aa</text:span>'
            ' cc aa <text:span text:style-name="style">dd'
            '<text:bookmark text:name="bookmark3"/></text:span>'
            "</text:p>"
        )
        self.assertEqual(paragraph.serialize(), expected)

    def test_set_bookmark_with_end(self):
        paragraph = Paragraph("aa bb aa aa cc aa dd")
        paragraph.set_span(style="style", regex="bb aa aa")
        paragraph.set_span(style="style", regex="dd")
        paragraph.set_bookmark("bookmark1", after="cc", position=-1)
        paragraph.set_bookmark("bookmark2", position=-1)
        expected = (
            "<text:p>aa "
            '<text:span text:style-name="style">'
            "bb aa aa"
            "</text:span>"
            ' cc<text:bookmark text:name="bookmark1"/> aa '
            '<text:span text:style-name="style">dd</text:span>'
            '<text:bookmark text:name="bookmark2"/>'
            "</text:p>"
        )
        self.assertEqual(paragraph.serialize(), expected)

    def test_set_bookmark_with_role(self):
        paragraph = Paragraph("aa")
        paragraph.set_bookmark("bookmark", role="start")
        paragraph.set_bookmark("bookmark", role="end", position=-1)
        expected = (
            "<text:p>"
            '<text:bookmark-start text:name="bookmark"/>'
            "aa"
            '<text:bookmark-end text:name="bookmark"/>'
            "</text:p>"
        )
        self.assertEqual(paragraph.serialize(), expected)

    def test_set_bookmark_with_content(self):
        paragraph = Paragraph("aa bb bb aa")
        paragraph.set_bookmark("bookmark", content="bb", position=1)
        expected = (
            "<text:p>aa bb "
            '<text:bookmark-start text:name="bookmark"/>'
            "bb"
            '<text:bookmark-end text:name="bookmark"/>'
            " aa"
            "</text:p>"
        )
        self.assertEqual(paragraph.serialize(), expected)

    def test_set_bookmark_with_limits(self):
        paragraph = Paragraph("aa bb bb aa")
        paragraph.set_bookmark("bookmark", position=(6, 8))
        expected = (
            "<text:p>aa bb "
            '<text:bookmark-start text:name="bookmark"/>'
            "bb"
            '<text:bookmark-end text:name="bookmark"/>'
            " aa"
            "</text:p>"
        )
        self.assertEqual(paragraph.serialize(), expected)


if __name__ == "__main__":
    main()
