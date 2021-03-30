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
#          Luis Belmar-Letelier <luis@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>

# from io import StringIO, BytesIO
from io import BytesIO

# from ftplib import FTP
from unittest import TestCase, main

# from urllib.request import urlopen
from os.path import join

from odfdo.const import ODF_EXTENSIONS, ODF_CONTENT, ODF_MANIFEST, ODF_META, ODF_STYLES
from odfdo.content import Content
from odfdo.document import Document
from odfdo.paragraph import Paragraph
from odfdo.manifest import Manifest
from odfdo.meta import Meta
from odfdo.styles import Styles


class NewDocumentFromTemplateTestCase(TestCase):
    def test_bad_template(self):
        self.assertRaises(IOError, Document, "../odfdo/templates/notexisting")

    def test_text_template(self):
        path = join("..", "odfdo", "templates", "text.ott")
        self.assertTrue(Document.new(path))

    def test_spreadsheet_template(self):
        path = join("..", "odfdo", "templates", "spreadsheet.ots")
        self.assertTrue(Document.new(path))

    def test_presentation_template(self):
        path = join("..", "odfdo", "templates", "presentation.otp")
        self.assertTrue(Document.new(path))

    def test_drawing_template(self):
        path = join("..", "odfdo", "templates", "drawing.otg")
        self.assertTrue(Document.new(path))

    def test_mimetype(self):
        path = join("..", "odfdo", "templates", "drawing.otg")
        document = Document.new(path)
        mimetype = document.mimetype
        self.assertFalse("template" in mimetype)
        manifest = document.get_part(ODF_MANIFEST)
        media_type = manifest.get_media_type("/")
        self.assertFalse("template" in media_type)


class NewdocumentFromTypeTestCase(TestCase):
    def test_bad_type(self):
        self.assertRaises(IOError, Document.new, "foobar")

    def test_text_type(self):
        document = Document("text")
        self.assertEqual(document.mimetype, ODF_EXTENSIONS["odt"])

    def test_spreadsheet_type(self):
        document = Document.new("spreadsheet")
        self.assertEqual(document.mimetype, ODF_EXTENSIONS["ods"])

    def test_presentation_type(self):
        document = Document("presentation")
        self.assertEqual(document.mimetype, ODF_EXTENSIONS["odp"])

    def test_drawing_type(self):
        document = Document.new("drawing")
        self.assertEqual(document.mimetype, ODF_EXTENSIONS["odg"])


class GetDocumentTestCase(TestCase):
    def test_filesystem(self):
        path = join("samples", "example.odt")
        self.assertTrue(Document(path))

    # def test_odf_xml(self):
    #     path = 'samples/example.xml'
    #     self.assertTrue(Document(path))


# fixme : reactivitate ftp


class DocumentTestCase(TestCase):
    def setUp(self):
        self.document = Document.new(join("samples", "example.odt"))

    def test_get_mimetype(self):
        mimetype = self.document.mimetype
        self.assertEqual(mimetype, ODF_EXTENSIONS["odt"])

    def test_get_content(self):
        content = self.document.get_part(ODF_CONTENT)
        self.assertTrue(isinstance(content, Content))

    def test_get_meta(self):
        meta = self.document.get_part(ODF_META)
        self.assertTrue(isinstance(meta, Meta))

    def test_get_styles(self):
        styles = self.document.get_part(ODF_STYLES)
        self.assertTrue(isinstance(styles, Styles))

    def test_get_manifest(self):
        manifest = self.document.get_part(ODF_MANIFEST)
        self.assertTrue(isinstance(manifest, Manifest))

    def test_get_body(self):
        body = self.document.body
        self.assertEqual(body.tag, "office:text")

    def test_clone_body_none(self):
        document = self.document
        dummy = document.body
        clone = document.clone
        # new body cache should be empty
        self.assertEqual(clone._Document__body, None)

    def test_clone_xmlparts_empty(self):
        document = self.document
        content = self.document.get_part(ODF_CONTENT)
        clone = document.clone
        # new xmlparts cache should be empty
        self.assertEqual(clone._Document__xmlparts, {})

    def test_clone_same_content(self):
        document = self.document
        s_orig = document.body.serialize()
        c = document.clone
        s_clone = c.body.serialize()
        self.assertEqual(s_clone, s_orig)

    def test_clone_different_changes_1(self):
        document = self.document
        s_orig = document.body.serialize()
        c = document.clone
        c.body.append(Paragraph("some text"))
        s_clone = c.body.serialize()
        self.assertNotEqual(s_clone, s_orig)

    def test_clone_different_unchanged_1(self):
        document = self.document
        s_orig = document.body.serialize()
        c = document.clone
        c.body.append(Paragraph("some text"))
        s_after = document.body.serialize()
        self.assertEqual(s_after, s_orig)

    def test_clone_different_unchanged_2(self):
        document = self.document
        s_orig = document.body.serialize()
        c = document.clone
        c.body.append(Paragraph("some text"))
        s_clone1 = c.body.serialize()
        document.body.append(Paragraph("new text"))
        s_clone2 = c.body.serialize()
        self.assertEqual(s_clone1, s_clone2)

    def test_save_nogenerator(self):
        document = self.document
        temp = BytesIO()
        document.save(temp)
        temp.seek(0)
        new = Document(temp)
        generator = new.get_part(ODF_META).get_generator()
        self.assertTrue(generator.startswith("odfdo"))

    def test_save_generator(self):
        document = self.document.clone
        document.get_part(ODF_META).set_generator("toto")
        temp = BytesIO()
        document.save(temp)
        temp.seek(0)
        new = Document(temp)
        generator = new.get_part(ODF_META).get_generator()
        self.assertEqual(generator, "toto")


class TestStyle(TestCase):
    def setUp(self):
        self.document = Document.new(
            join("..", "odfdo", "templates", "lpod_styles.odt")
        )

    def test_get_styles(self):
        document = self.document
        styles = document.get_styles()
        self.assertEqual(len(styles), 75)

    def test_get_styles_family_paragraph(self):
        document = self.document
        styles = document.get_styles(family="paragraph")
        self.assertEqual(len(styles), 33)

    def test_get_styles_family_paragraph_bytes(self):
        document = self.document
        styles = document.get_styles(family="paragraph")
        self.assertEqual(len(styles), 33)

    def test_get_styles_family_text(self):
        document = self.document
        styles = document.get_styles(family="text")
        self.assertEqual(len(styles), 4)

    def test_get_styles_family_graphic(self):
        document = self.document
        styles = document.get_styles(family="graphic")
        self.assertEqual(len(styles), 1)

    def test_get_styles_family_page_layout_automatic(self):
        document = self.document
        styles = document.get_styles(family="page-layout", automatic=True)
        self.assertEqual(len(styles), 2)

    def test_get_styles_family_page_layout_no_automatic(self):
        document = self.document
        styles = document.get_styles(family="page-layout")
        self.assertEqual(len(styles), 2)

    def test_get_styles_family_master_page(self):
        document = self.document
        styles = document.get_styles(family="master-page")
        self.assertEqual(len(styles), 2)

    def test_get_style_automatic(self):
        document = self.document
        style = document.get_style("paragraph", "P1")
        self.assertNotEqual(style, None)

    def test_get_style_named(self):
        document = self.document
        style = document.get_style("paragraph", "Heading_20_1")
        self.assertNotEqual(style, None)

    def test_show_styles(self):
        # XXX hard to unit test
        document = self.document
        all_styles = document.show_styles()
        self.assertTrue("auto   used:" in all_styles)
        self.assertTrue("common used:" in all_styles)
        common_styles = document.show_styles(automatic=False)
        self.assertTrue("auto   used:" not in common_styles)
        self.assertTrue("common used:" in common_styles)
        automatic_styles = document.show_styles(common=False)
        self.assertTrue("auto   used:" in automatic_styles)
        self.assertTrue("common used:" not in automatic_styles)
        no_styles = document.show_styles(automatic=False, common=False)
        self.assertEqual(no_styles, "")


if __name__ == "__main__":
    main()
