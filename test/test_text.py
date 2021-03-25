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

from odfdo.element import Text, Element


class TextTestCase(TestCase):
    def setUp(self):
        element = Element.from_tag("<text:p>text<text:span/>tail</text:p>")
        self.results = element.xpath("descendant::text()")

    def test_nodes(self):
        self.assertEqual(len(self.results), 2)

    def test_type(self):
        self.assertTrue(type(self.results[0]) is Text)

    def test_text(self):
        text = self.results[0]
        self.assertEqual(text, "text")
        self.assertTrue(text.is_text() is True)
        self.assertTrue(text.is_tail() is False)

    def test_tail(self):
        tail = self.results[1]
        self.assertEqual(tail, "tail")
        self.assertTrue(tail.is_text() is False)
        self.assertTrue(tail.is_tail() is True)


class ParentTestCase(TestCase):
    def setUp(self):
        element = Element.from_tag("<text:p>text<text:span/>tail</text:p>")
        self.results = element.xpath("descendant::text()")

    def test_text(self):
        text = self.results[0]
        self.assertEqual(text.parent.tag, "text:p")

    def test_tail(self):
        tail = self.results[1]
        self.assertEqual(tail.parent.tag, "text:span")


if __name__ == "__main__":
    main()
