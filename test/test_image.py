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
from odfdo.element import NEXT_SIBLING
from odfdo.frame import Frame
from odfdo.image import DrawImage


class TestImage(TestCase):
    def setUp(self):
        self.document = document = Document("samples/frame_image.odp")
        self.body = document.body
        self.path = "Pictures/100002010000012C00000042188DCB81589D2C10.png"

    def test_create_image(self):
        image = DrawImage(self.path)
        expected = (
            '<draw:image xlink:href="%s" xlink:type="simple" '
            'xlink:show="embed" xlink:actuate="onLoad"/>' % self.path
        )
        self.assertEqual(image.serialize(), expected)

    def test_get_image_list(self):
        body = self.body
        result = body.get_images()
        self.assertEqual(len(result), 1)
        element = result[0]
        self.assertEqual(element.url, self.path)

    def test_get_image_by_name(self):
        body = self.body
        element = body.get_image(name="odfdo")
        self.assertEqual(element.url, self.path)

    def test_get_image_by_position(self):
        body = self.body
        element = body.get_image(position=0)
        self.assertEqual(element.url, self.path)

    def test_get_image_by_path(self):
        body = self.body
        element = body.get_image(url=".png")
        self.assertEqual(element.url, self.path)

    def test_insert_image(self):
        body = self.body.clone
        path = "a/path"
        image = DrawImage(path)
        frame = Frame("Image Frame", size=("0cm", "0cm"), style="Graphics")
        frame.append(image)
        body.get_frame().parent.insert(frame, NEXT_SIBLING)
        element = body.get_image(name="Image Frame")
        self.assertEqual(element.url, path)
        element = body.get_image(position=1)
        self.document.save(packaging="folder")
        self.assertEqual(element.url, path)


if __name__ == "__main__":
    main()
