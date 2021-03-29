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

from odfdo.const import ODF_STYLES
from odfdo.document import Document
from odfdo.style import Style


class TestStyle(TestCase):
    def setUp(self):
        self.document = document = Document("samples/example.odt")
        self.styles = document.get_part(ODF_STYLES)

    def tearDown(self):
        del self.styles
        del self.document

    def test_create_style(self):
        style = Style("paragraph", "style1")
        self.assertIn(
            style.serialize(),
            (
                ('<style:style style:name="style1" ' 'style:family="paragraph"/>'),
                ('<style:style style:family="paragraph" ' 'style:name="style1"/>'),
            ),
        )

    def test_get_styles(self):
        style_list = self.styles.get_styles()
        self.assertEqual(len(style_list), 20)

    def test_get_styles_paragraph(self):
        style_list = self.styles.get_styles(family="paragraph")
        self.assertEqual(len(style_list), 10)

    def test_get_styles_master_page(self):
        style_list = self.styles.get_styles(family="master-page")
        self.assertEqual(len(style_list), 1)

    def test_get_style_automatic(self):
        style = self.styles.get_style("page-layout", "Mpm1")
        self.assertNotEqual(style, None)

    def test_get_style_named(self):
        style = self.styles.get_style("paragraph", "Heading_20_1")
        self.assertEqual(style.display_name, "Heading 1")

    def test_get_style_display_name(self):
        style = self.styles.get_style("paragraph", display_name="Text body")
        self.assertEqual(style.name, "Text_20_body")

    def test_insert_style(self):
        styles = self.styles.clone
        style = Style(
            "paragraph",
            name="style1",
            area="text",
            **{"fo:color": "#0000ff", "fo:background-color": "#ff0000"}
        )
        context = styles.get_element("//office:styles")
        context.append(style)
        get1 = styles.get_style("paragraph", "style1")
        self.assertIn(
            get1.serialize(),
            (
                (
                    '<style:style style:name="style1" '
                    'style:family="paragraph">'
                    '<style:text-properties fo:background-color="#ff0000" '
                    'fo:color="#0000ff"/>'
                    "</style:style>"
                ),
                '<style:style style:family="paragraph" '
                'style:name="style1">'
                "<style:text-properties "
                'fo:background-color="#ff0000" '
                'fo:color="#0000ff"/>'
                "</style:style>",
            ),
        )


class TestInsertStyleCase(TestCase):
    def setUp(self):
        self.doc = Document("samples/example.odt")

    def test_insert_common_style(self):
        doc = self.doc

        style = Style("paragraph", "MyStyle")
        doc.insert_style(style)
        inserted_style = doc.get_style("paragraph", "MyStyle")

        self.assertEqual(style.serialize(), inserted_style.serialize())

    def test_insert_default_style(self):
        doc = self.doc

        style = Style("paragraph", "MyStyle")
        doc.insert_style(style, default=True)

        inserted_style = doc.get_style("paragraph")
        expected = '<style:default-style style:family="paragraph"/>'

        self.assertEqual(inserted_style.serialize(), expected)

    def test_insert_automatic_style(self):
        doc = self.doc

        style = Style("paragraph")
        doc.insert_style(style, automatic=True)
        self.assertNotEqual(style.name, None)

    def test_insert_style_name_as_argument(self):
        doc = self.doc

        style = Style("paragraph")
        arg_name = "some_name"
        returned_name = doc.insert_style(style, name=arg_name, automatic=True)
        self.assertNotEqual(style.name, None)
        self.assertEqual(returned_name, arg_name)

    def test_insert_style_from_string(self):
        doc = self.doc
        style_str = (
            '<style:style style:name="style_as_str" '
            'style:family="paragraph">'
            "<style:text-properties "
            'fo:background-color="#ff0000" '
            'fo:color="#0000ff"/>'
            "</style:style>"
        )
        returned_name = doc.insert_style(style_str, automatic=True)
        self.assertEqual(returned_name, "style_as_str")
        get1 = doc.get_style("paragraph", "style_as_str")
        self.assertIn(
            get1.serialize(),
            (
                (
                    '<style:style style:name="style_as_str" '
                    'style:family="paragraph">'
                    "<style:text-properties "
                    'fo:background-color="#ff0000" '
                    'fo:color="#0000ff"/>'
                    "</style:style>"
                ),
                (
                    '<style:style style:name="style_as_str" '
                    'style:family="paragraph">'
                    '<style:text-properties fo:color="#0000ff" '
                    'fo:background-color="#ff0000"/>'
                    "</style:style>"
                ),
                (
                    '<style:style style:family="paragraph" '
                    'style:name="style_as_str">'
                    "<style:text-properties "
                    'fo:background-color="#ff0000" '
                    'fo:color="#0000ff"/>'
                    "</style:style>"
                ),
            ),
        )

    def test_insert_with_error(self):
        doc = self.doc

        style = Style("paragraph", "MyStyle")
        self.assertRaises(
            AttributeError, doc.insert_style, style=style, automatic=True, default=True
        )

    def test_insert_master_page_style(self):
        doc = self.doc

        style = Style("master-page", "MyPageStyle")
        doc.insert_style(style)

        inserted_style = doc.get_style("master-page", "MyPageStyle")
        self.assertEqual(style.serialize(), inserted_style.serialize())


if __name__ == "__main__":
    main()
