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
#          David Versmisse <david.versmisse@itaapy.com>

from unittest import TestCase, main

from lxml.etree import _ElementTree

from odfdo.const import ODF_CONTENT
from odfdo.container import Container
from odfdo.element import Element
from odfdo.xmlpart import XmlPart
from odfdo.content import Content


class XmlPartTestCase(TestCase):
    def setUp(self):
        self.container = Container()
        self.container.open("samples/example.odt")

    def tearDown(self):
        del self.container

    def test_get_element_list(self):
        content_part = XmlPart(ODF_CONTENT, self.container)
        elements = content_part.get_elements("//text:p")
        # The annotation paragraph is counted
        self.assertEqual(len(elements), 8)

    def test_tree(self):
        # Testing a private but important method
        content = XmlPart(ODF_CONTENT, self.container)
        tree = content._XmlPart__get_tree()
        self.assertTrue(isinstance(tree, _ElementTree))
        self.assertNotEqual(content._XmlPart__tree, None)

    def test_root(self):
        content = XmlPart(ODF_CONTENT, self.container)
        root = content.root
        self.assertTrue(isinstance(root, Element))
        self.assertEqual(root.tag, "office:document-content")
        self.assertNotEqual(content._XmlPart__root, None)

    def test_serialize(self):
        container = self.container
        content_bytes = container.get_part(ODF_CONTENT)
        content_part = XmlPart(ODF_CONTENT, container)
        # differences with lxml
        serialized = content_part.serialize().replace(b"'", b"&apos;")
        self.assertEqual(content_bytes, serialized)

    def test_pretty_serialize(self):
        # With pretty = True
        element = Element.from_tag("<root><a>spam</a><b/></root>")
        serialized = element.serialize(pretty=True)
        expected = "<root>\n" "  <a>spam</a>\n" "  <b/>\n" "</root>\n"
        self.assertEqual(serialized, expected)

    def test_clone(self):
        # Testing that the clone works on subclasses too
        container = self.container
        content = Content(ODF_CONTENT, container)
        clone = content.clone
        self.assertEqual(clone.part_name, content.part_name)
        self.assertNotEqual(id(container), id(clone.container))
        self.assertEqual(clone._XmlPart__tree, None)

    def test_delete(self):
        container = self.container
        content = XmlPart(ODF_CONTENT, container)
        paragraphs = content.get_elements("//text:p")
        for paragraph in paragraphs:
            content.delete_element(paragraph)
        serialized = content.serialize()
        self.assertEqual(serialized.count(b"<text:p"), 0)


if __name__ == "__main__":
    main()
