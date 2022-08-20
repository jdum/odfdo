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
from odfdo.section import Section


class TestSection(TestCase):
    def setUp(self):
        self.document = document = Document("samples/base_text.odt")
        self.body = document.body

    def test_create_simple_section(self):
        """The idea is to test only with the mandatory arguments (none
        in this case), not to test odf_create_element which is done in
        test_xmlpart.
        """
        element = Section()
        expected = "<text:section/>"
        self.assertEqual(element.serialize(), expected)

    def test_create_complex_section(self):
        """The idea is to test with all possible arguments. If some arguments
        are contradictory or trigger different behaviours, test all those
        combinations separately.
        """
        element = Section(style="Standard")
        expected = '<text:section text:style-name="Standard"/>'
        self.assertEqual(element.serialize(), expected)

    def test_create_complex_section_with_name(self):
        """Test the name argument."""
        element = Section(name="SomeName")
        expected = '<text:section text:name="SomeName"/>'
        self.assertEqual(element.serialize(), expected)

    def test_get_section_list(self):
        body = self.body
        sections = body.get_sections()
        self.assertEqual(len(sections), 2)
        second = sections[1]
        name = second.name
        self.assertEqual(name, "Section2")

    def test_get_section_list_style(self):
        body = self.body
        sections = body.get_sections(style="Sect1")
        self.assertEqual(len(sections), 2)
        section = sections[0]
        name = section.name
        self.assertEqual(name, "Section1")

    def test_get_section(self):
        body = self.body
        section = body.get_section(position=1)
        name = section.name
        self.assertEqual(name, "Section2")


if __name__ == "__main__":
    main()
