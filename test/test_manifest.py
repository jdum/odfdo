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

from odfdo.const import ODF_PRESENTATION, ODF_MANIFEST
from odfdo.document import Document
from odfdo.manifest import Manifest


class ManifestTestCase(TestCase):
    def setUp(self):
        self.document = Document("samples/frame_image.odp")
        self.manifest = self.document.get_part(ODF_MANIFEST)
        self.image_path = "Pictures/100002010000012C00000042188DCB81589D2C10.png"

    def test_get_manifest(self):
        self.assertTrue(type(self.manifest) is Manifest)

    def test_get_path_list(self):
        results = self.manifest.get_paths()
        self.assertEqual(len(results), 9)

    def test_get_path_media_list(self):
        results = self.manifest.get_path_medias()
        self.assertEqual(len(results), 9)
        root = results[0]
        self.assertEqual(root, ("/", ODF_PRESENTATION))

    def test_get_media_type_root(self):
        self.assertEqual(self.manifest.get_media_type("/"), ODF_PRESENTATION)

    def test_get_media_type_directory(self):
        self.assertEqual(self.manifest.get_media_type("Pictures/"), None)

    def test_get_media_type_other(self):
        path = self.image_path
        self.assertEqual(self.manifest.get_media_type(path), "image/png")

    def test_get_media_type_missing(self):
        self.assertTrue(self.manifest.get_media_type("LpOD") is None)

    def test_set_media_type(self):
        manifest = self.manifest.clone
        path = self.image_path
        self.assertEqual(manifest.get_media_type(path), "image/png")
        manifest.set_media_type(path, "image/jpeg")
        self.assertEqual(manifest.get_media_type(path), "image/jpeg")

    def test_set_media_type_missing(self):
        manifest = self.manifest.clone
        self.assertRaises(KeyError, manifest.set_media_type, "LpOD", "")

    def test_add_full_path(self):
        manifest = self.manifest.clone
        self.assertTrue(manifest.get_media_type("LpOD") is None)
        manifest.add_full_path("LpOD", "")
        self.assertEqual(manifest.get_media_type("LpOD"), "")

    def test_add_full_path_existing(self):
        manifest = self.manifest.clone
        path = self.image_path
        self.assertEqual(manifest.get_media_type(path), "image/png")
        manifest.add_full_path(path, "image/jpeg")
        self.assertEqual(manifest.get_media_type(path), "image/jpeg")

    def test_del_full_path(self):
        manifest = self.manifest.clone
        path = self.image_path
        self.assertEqual(manifest.get_media_type(path), "image/png")
        manifest.del_full_path(path)
        self.assertTrue(manifest.get_media_type(path) is None)


if __name__ == "__main__":
    main()
