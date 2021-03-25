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
#          David Versmisse <david.versmisse@itaapy.com>

from unittest import TestCase, main

from odfdo.const import ODF_CONTENT
from odfdo.content import Content
from odfdo.document import Document


class ContentTestCase(TestCase):
    def setUp(self):
        self.document = document = Document("samples/base_text.odt")
        self.content = document.get_part(ODF_CONTENT)

    def test_get_content(self):
        self.assertTrue(type(self.content) is Content)

    def test_get_body(self):
        body = self.content.body
        self.assertEqual(body.tag, "office:text")

    def test_get_styles(self):
        result = self.content.get_styles()
        self.assertEqual(len(result), 5)

    def test_get_styles_family(self):
        result = self.content.get_styles("font-face")
        self.assertEqual(len(result), 3)

    def test_get_style(self):
        style = self.content.get_style("section", "Sect1")
        self.assertEqual(style.name, "Sect1")
        self.assertEqual(style.family, "section")


if __name__ == "__main__":
    main()
