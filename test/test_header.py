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
from odfdo.header import Header


class TestHeader(TestCase):
    def setUp(self):
        self.document = document = Document("samples/base_text.odt")
        self.body = document.body

    def test_get_header_list(self):
        body = self.body
        headings = body.get_headers()
        self.assertEqual(len(headings), 3)
        second = headings[1]
        text = second.text
        self.assertEqual(text, "Level 2 Title")

    def test_get_header_list_style(self):
        body = self.body
        headings = body.get_headers(style="Heading_20_2")
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.text
        self.assertEqual(text, "Level 2 Title")

    def test_get_header_list_level(self):
        body = self.body
        headings = body.get_headers(outline_level=2)
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.text
        self.assertEqual(text, "Level 2 Title")

    def test_get_header_list_style_level(self):
        body = self.body
        headings = body.get_headers(style="Heading_20_2", outline_level=2)
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.text
        self.assertEqual(text, "Level 2 Title")

    def test_get_header_list_context(self):
        body = self.body
        section2 = body.get_section(position=1)
        headings = section2.get_headers()
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.text
        self.assertEqual(text, "First Title of the Second Section")

    def test_odf_heading(self):
        body = self.body
        heading = body.get_header()
        self.assertTrue(isinstance(heading, Header))

    def test_get_header(self):
        body = self.body
        heading = body.get_header(position=1)
        text = heading.text
        self.assertEqual(text, "Level 2 Title")

    def test_get_header_level(self):
        body = self.body
        heading = body.get_header(outline_level=2)
        text = heading.text
        self.assertEqual(text, "Level 2 Title")

    def test_insert_heading(self):
        body = self.body.clone
        heading = Header(2, "An inserted heading", style="Heading_20_2")
        body.append(heading)
        last_heading = body.get_headers()[-1]
        self.assertEqual(last_heading.text, "An inserted heading")


if __name__ == "__main__":
    main()
