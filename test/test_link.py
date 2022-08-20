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

from odfdo.document import Document
from odfdo.element import Element
from odfdo.link import Link


class TestLinks(TestCase):
    def setUp(self):
        document = Document("samples/base_text.odt")
        self.body = body = document.body.clone
        self.paragraph = body.get_paragraph()

    def test_create_link1(self):
        link = Link("http://example.com/")
        expected = '<text:a xlink:href="http://example.com/"/>'
        self.assertEqual(link.serialize(), expected)

    def test_create_link2(self):
        link = Link(
            "http://example.com/",
            name="link2",
            target_frame="_blank",
            style="style1",
            visited_style="style2",
        )
        expected = (
            '<text:a xlink:href="http://example.com/" '
            'office:name="link2" office:target-frame-name="_blank" '
            'xlink:show="new" text:style-name="style1" '
            'text:visited-style-name="style2"/>'
        )
        self.assertEqual(link.serialize(), expected)

    def test_get_link(self):
        link1 = Link("http://example.com/", name="link1")
        link2 = Link("http://example.com/", name="link2")
        paragraph = self.paragraph
        paragraph.append(link1)
        paragraph.append(link2)
        element = self.body.get_link(name="link2")
        expected = '<text:a xlink:href="http://example.com/" ' 'office:name="link2"/>'
        self.assertEqual(element.serialize(), expected)

    def test_get_link_list(self):
        link1 = Link("http://example.com/", name="link1")
        link2 = Link("http://example.com/", name="link2")
        paragraph = self.paragraph
        paragraph.append(link1)
        paragraph.append(link2)
        element = self.body.get_links()[1]
        expected = '<text:a xlink:href="http://example.com/" ' 'office:name="link2"/>'
        self.assertEqual(element.serialize(), expected)

    def test_get_link_list_name(self):
        link1 = Link("http://example.com/", name="link1", title="title1")
        link2 = Link("http://example.com/", name="link2", title="title2")
        paragraph = self.paragraph
        paragraph.append(link1)
        paragraph.append(link2)
        # name
        element = self.body.get_links(name="link1")[0]
        expected = (
            '<text:a xlink:href="http://example.com/" '
            'office:name="link1" office:title="title1"/>'
        )
        self.assertEqual(element.serialize(), expected)

    def test_get_link_list_title(self):
        link1 = Link("http://example.com/", name="link1", title="title1")
        link2 = Link("http://example.com/", name="link2", title="title2")
        paragraph = self.paragraph
        paragraph.append(link1)
        paragraph.append(link2)
        # title
        element = self.body.get_links(title="title2")[0]
        expected = (
            '<text:a xlink:href="http://example.com/" '
            'office:name="link2" office:title="title2"/>'
        )
        self.assertEqual(element.serialize(), expected)

    def test_get_link_list_href(self):
        link1 = Link("http://example.com/", name="link1", title="title1")
        link2 = Link("http://example.com/", name="link2", title="title2")
        paragraph = self.paragraph
        paragraph.append(link1)
        paragraph.append(link2)
        # url
        elements = self.body.get_links(url=r"\.com")
        self.assertEqual(len(elements), 2)

    def test_href_from_existing_document(self):
        body = self.body
        links = body.get_links(url=r"lpod")
        self.assertEqual(len(links), 1)

    def test_get_link_list_name_and_title(self):
        link1 = Link("http://example.com/", name="link1", title="title1")
        link2 = Link("http://example.com/", name="link2", title="title2")
        paragraph = self.paragraph
        paragraph.append(link1)
        paragraph.append(link2)
        # name and title
        element = self.body.get_links(name="link1", title="title1")[0]
        expected = (
            '<text:a xlink:href="http://example.com/" '
            'office:name="link1" office:title="title1"/>'
        )
        self.assertEqual(element.serialize(), expected)

    def test_get_link_by_href(self):
        body = self.body
        link = body.get_link(url=r"lpod")
        url = link.get_attribute("xlink:href")
        self.assertEqual(url, "http://lpod-project.net/")

    def test_get_link_by_path_context(self):
        body = self.body
        section2 = body.get_section(position=1)
        link = section2.get_link(url=r"\.net")
        url = link.url
        self.assertEqual(url, "http://lpod-project.net/")

    def test_get_link_list_not_found(self):
        link1 = Link("http://example.com/", name="link1", title="title1")
        link2 = Link("http://example.com/", name="link2", title="title2")
        paragraph = self.paragraph
        paragraph.append(link1)
        paragraph.append(link2)
        # Not found
        element = self.body.get_links(name="link1", title="title2")
        self.assertEqual(element, [])


class TestInsertLink(TestCase):
    def test_insert_link_simple(self):
        paragraph = Element.from_tag("<text:p>toto tata titi</text:p>")
        paragraph.set_link("http://example.com", regex="tata")
        expected = (
            "<text:p>toto "
            '<text:a xlink:href="http://example.com">tata</text:a> '
            "titi</text:p>"
        )
        self.assertEqual(paragraph.serialize(), expected)

    def test_insert_link_medium(self):
        paragraph = Element.from_tag(
            "<text:p><text:span>toto</text:span> tata titi</text:p>"
        )
        paragraph.set_link("http://example.com", regex="tata")
        expected = (
            "<text:p><text:span>toto</text:span> "
            '<text:a xlink:href="http://example.com">tata</text:a> '
            "titi</text:p>"
        )
        self.assertEqual(paragraph.serialize(), expected)

    def test_insert_link_complex(self):
        paragraph = Element.from_tag(
            "<text:p>toto <text:span> tata </text:span> titi</text:p>"
        )
        paragraph.set_link("http://example.com", regex="tata")
        expected = (
            "<text:p>toto <text:span> "
            '<text:a xlink:href="http://example.com">'
            "tata</text:a> </text:span> titi"
            "</text:p>"
        )
        self.assertEqual(paragraph.serialize(), expected)


if __name__ == "__main__":
    main()
