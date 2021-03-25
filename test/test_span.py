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
from odfdo.paragraph import Span


class TestSpan(TestCase):
    def setUp(self):
        self.document = document = Document("samples/span_style.odt")
        self.body = document.body

    def test_create_span(self):
        span = Span("my text", style="my_style")
        expected = '<text:span text:style-name="my_style">' "my text" "</text:span>"
        self.assertEqual(span.serialize(), expected)

    def test_get_span_list(self):
        body = self.body
        result = body.get_spans()
        self.assertEqual(len(result), 2)
        element = result[0]
        expected = '<text:span text:style-name="T1">' "moustache" "</text:span>"
        self.assertEqual(element.serialize(), expected)

    def test_get_span_list_style(self):
        body = self.body
        result = body.get_spans(style="T2")
        self.assertEqual(len(result), 1)
        element = result[0]
        expected = '<text:span text:style-name="T2">' "rouge" "</text:span>"
        self.assertEqual(element.serialize(), expected)

    def test_get_span(self):
        body = self.body
        span = body.get_span(position=1)
        expected = '<text:span text:style-name="T2">' "rouge" "</text:span>"
        self.assertEqual(span.serialize(), expected)

    def test_insert_span(self):
        body = self.body.clone
        span = Span("my_style", "my text")
        paragraph = body.get_paragraph(position=0)
        paragraph.append(span)


if __name__ == "__main__":
    main()
