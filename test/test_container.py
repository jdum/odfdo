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
#          Luis Belmar-Letelier <luis@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>

# import os
from os.path import join, isfile

# from io import StringIO, BytesIO
# from ftplib import FTP
from os import mkdir
from shutil import rmtree
from unittest import TestCase, main

# from urllib.request import urlopen

from odfdo.utils import to_bytes
from odfdo.const import ODF_EXTENSIONS, ODF_CONTENT
from odfdo.container import Container


class NewContainerFromTemplateTestCase(TestCase):
    def test_bad_template(self):
        self.assertRaises(OSError, Container.new, "../odfdo/templates/notexisting")

    def test_text_template(self):
        path = join("..", "odfdo", "templates", "text.ott")
        container = Container.new(path)
        mimetype = container.get_part("mimetype")
        umimetype = container.mimetype
        self.assertEqual(mimetype, to_bytes(ODF_EXTENSIONS["odt"]))
        self.assertEqual(umimetype, ODF_EXTENSIONS["odt"])

    def test_spreadsheet_template(self):
        path = join("..", "odfdo", "templates", "spreadsheet.ots")
        container = Container.new(path)
        mimetype = container.get_part("mimetype")
        umimetype = container.mimetype
        self.assertEqual(mimetype, to_bytes(ODF_EXTENSIONS["ods"]))
        self.assertEqual(umimetype, ODF_EXTENSIONS["ods"])

    def test_presentation_template(self):
        path = join("..", "odfdo", "templates", "presentation.otp")
        container = Container.new(path)
        mimetype = container.get_part("mimetype")
        umimetype = container.mimetype
        self.assertEqual(mimetype, to_bytes(ODF_EXTENSIONS["odp"]))
        self.assertEqual(umimetype, ODF_EXTENSIONS["odp"])

    def test_drawing_template(self):
        path = join("..", "odfdo", "templates", "drawing.otg")
        container = Container.new(path)
        mimetype = container.get_part("mimetype")
        umimetype = container.mimetype
        self.assertEqual(mimetype, to_bytes(ODF_EXTENSIONS["odg"]))
        self.assertEqual(umimetype, ODF_EXTENSIONS["odg"])


class NewContainerFromTypeTestCase(TestCase):
    def test_bad_type(self):
        self.assertRaises(IOError, Container.new, "foobar")

    def test_text_type(self):
        container = Container.new("text")
        mimetype = container.get_part("mimetype")
        umimetype = container.mimetype
        self.assertEqual(mimetype, to_bytes(ODF_EXTENSIONS["odt"]))
        self.assertEqual(umimetype, ODF_EXTENSIONS["odt"])

    def test_spreadsheet_type(self):
        container = Container.new("spreadsheet")
        mimetype = container.get_part("mimetype")
        umimetype = container.mimetype
        self.assertEqual(mimetype, to_bytes(ODF_EXTENSIONS["ods"]))
        self.assertEqual(umimetype, ODF_EXTENSIONS["ods"])

    def test_presentation_type(self):
        container = Container.new("presentation")
        mimetype = container.get_part("mimetype")
        umimetype = container.mimetype
        self.assertEqual(mimetype, to_bytes(ODF_EXTENSIONS["odp"]))
        self.assertEqual(umimetype, ODF_EXTENSIONS["odp"])

    def test_drawing_type(self):
        container = Container.new("drawing")
        mimetype = container.get_part("mimetype")
        umimetype = container.mimetype
        self.assertEqual(mimetype, to_bytes(ODF_EXTENSIONS["odg"]))
        self.assertEqual(umimetype, ODF_EXTENSIONS["odg"])


class GetContainerTestCase(TestCase):
    def test_filesystem(self):
        path = join("samples", "example.odt")
        container = Container()
        container.open(path)
        mimetype = container.get_part("mimetype")
        umimetype = container.mimetype
        self.assertEqual(mimetype, to_bytes(ODF_EXTENSIONS["odt"]))
        self.assertEqual(umimetype, ODF_EXTENSIONS["odt"])

    # def test_odf_xml(self):
    #     path = 'samples/example.xml'
    #     container = odf_get_container(path)
    #     mimetype = container.get_part('mimetype')
    #     self.assertEqual(mimetype, ODF_EXTENSIONS['odt'])


class ContainerTestCase(TestCase):
    def test_clone(self):
        container = Container.new("text")
        clone = container.clone
        self.assertEqual(clone.path, None)

    def test_get_part_xml(self):
        container = Container()
        container.open(join("samples", "example.odt"))
        content = container.get_part(ODF_CONTENT)
        self.assertIn(b"<office:document-content", content)

    def test_get_part_mimetype(self):
        container = Container()
        container.open(join("samples", "example.odt"))
        mimetype = container.get_part("mimetype")
        umimetype = container.mimetype
        self.assertEqual(mimetype, to_bytes(ODF_EXTENSIONS["odt"]))
        self.assertEqual(umimetype, ODF_EXTENSIONS["odt"])

    def test_mimetype_setter(self):
        container = Container()
        container.open(join("samples", "example.odt"))
        container.mimetype = ODF_EXTENSIONS["odt"]
        self.assertEqual(container.mimetype, ODF_EXTENSIONS["odt"])

    # def test_odf_xml_bad_part(self):
    #     container = odf_get_container('samples/example.xml')
    #     self.assertRaises(ValueError, container.get_part, 'Pictures/a.jpg')

    # def test_odf_xml_part_xml(self):
    #     container = odf_get_container('samples/example.xml')
    #     meta = container.get_part('meta')
    #     self.assertTrue(meta.startswith('<office:document-meta>'))

    def test_set_part(self):
        container = Container()
        container.open(join("samples", "example.odt"))
        path = join("Pictures", "a.jpg")
        data = to_bytes("JFIFIThinéééékImAnImage")
        container.set_part(path, data)
        self.assertEqual(container.get_part(path), data)

    def test_del_part(self):
        container = Container()
        container.open(join("samples", "example.odt"))
        # Not a realistic test
        path = "content"
        container.del_part(path)
        self.assertRaises(ValueError, container.get_part, path)


class ContainerSaveTestCase(TestCase):
    def setUp(self):
        mkdir("trash")

    def tearDown(self):
        rmtree("trash")

    def test_save_zip(self):
        """TODO: 2 cases
        1. from "zip" to "zip"
        2. from "flat" to "zip"
        """
        container = Container()
        container.open(join("samples", "example.odt"))
        container.save(join("trash", "example.odt"))
        new_container = Container()
        new_container.open(join("trash", "example.odt"))
        mimetype = new_container.get_part("mimetype")
        self.assertEqual(mimetype, to_bytes(ODF_EXTENSIONS["odt"]))

    def test_save_folder(self):
        container = Container()
        container.open(join("samples", "example.odt"))
        container.save(join("trash", "example.odt"), packaging="folder")
        path = join("trash", "example.odt" + ".folder", "mimetype")
        self.assertEqual(isfile(path), True)
        path = join("trash", "example.odt" + ".folder", "content.xml")
        self.assertEqual(isfile(path), True)
        path = join("trash", "example.odt" + ".folder", "meta.xml")
        self.assertEqual(isfile(path), True)
        path = join("trash", "example.odt" + ".folder", "styles.xml")
        self.assertEqual(isfile(path), True)
        path = join("trash", "example.odt" + ".folder", "settings.xml")
        self.assertEqual(isfile(path), True)

    def test_save_folder_to_zip(self):
        container = Container()
        container.open(join("samples", "example.odt"))
        container.save(join("trash", "example.odt"), packaging="folder")
        path = join("trash", "example.odt" + ".folder", "mimetype")
        self.assertEqual(isfile(path), True)
        new_container = Container()
        new_container.open(join("trash", "example.odt.folder"))
        new_container.save(join("trash", "example_bis.odt"), packaging="zip")
        new_container_zip = Container()
        new_container_zip.open(join("trash", "example_bis.odt"))
        mimetype = new_container_zip.get_part("mimetype")
        self.assertEqual(mimetype, to_bytes(ODF_EXTENSIONS["odt"]))

    def test_load_folder(self):
        container = Container()
        container.open(join("samples", "example.odt"))
        container.save(join("trash", "example_f.odt"), packaging="folder")
        new_container = Container()
        new_container.open(join("trash", "example_f.odt.folder"))
        content = new_container.get_part(ODF_CONTENT)
        self.assertIn(b"<office:document-content", content)
        mimetype = new_container.get_part("mimetype")
        self.assertEqual(mimetype, to_bytes(ODF_EXTENSIONS["odt"]))
        path = join("Pictures", "a.jpg")
        data = to_bytes("JFIFIThiééénkImA §ççànImage")
        new_container.set_part(path, data)
        self.assertEqual(new_container.get_part(path), to_bytes(data))
        # Not a realistic test
        path = "content"
        new_container.del_part(path)
        self.assertRaises(ValueError, new_container.get_part, path)

    # XXX We must implement the flat xml part
    # def xtest_save_flat(self):
    #     """TODO: 2 cases
    #        1. from "zip" to "flat"
    #        2. from "flat" to "flat"
    #     """
    #     raise NotImplementedError


if __name__ == "__main__":
    main()
