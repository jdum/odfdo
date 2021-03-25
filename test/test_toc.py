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
# Authors: David Versmisse <david.versmisse@itaapy.com>

from unittest import TestCase, main

from odfdo.document import Document
from odfdo.toc import TOC


def get_toc_lines(toc):
    return [paragraph.text for paragraph in toc.get_paragraphs()]


class TOCTest(TestCase):
    def setUp(self):
        self.document = Document("samples/toc.odt")
        self.expected = [
            "Table des matières",
            "1. Level 1 title 1",
            "1.1. Level 2 title 1",
            "2. Level 1 title 2",
            "2.1.1. Level 3 title 1",
            "2.2. Level 2 title 2",
            "3. Level 1 title 3",
            "3.1. Level 2 title 1",
            "3.1.1. Level 3 title 1",
            "3.1.2. Level 3 title 2",
            "3.2. Level 2 title 2",
            "3.2.1. Level 3 title 1",
            "3.2.2. Level 3 title 2",
        ]

    def test_toc_fill_unattached(self):
        toc = TOC("Table des matières")
        self.assertRaises(ValueError, toc.fill)

    def test_toc_fill_unattached_document(self):
        toc = TOC("Table des matières")
        toc.fill(self.document)
        toc_lines = get_toc_lines(toc)
        self.assertEqual(toc_lines, self.expected)

    def test_toc_fill_attached(self):
        document = self.document.clone
        toc = TOC("Table des matières")
        document.body.append(toc)
        toc.fill()
        toc_lines = get_toc_lines(toc)
        self.assertEqual(toc_lines, self.expected)


if __name__ == "__main__":
    main()
