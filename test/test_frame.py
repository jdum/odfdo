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
from odfdo.frame import Frame, default_frame_position_style
from odfdo.header import Header

ZOE = "你好 Zoé"


class TestFrame(TestCase):
    def setUp(self):
        document = Document("samples/frame_image.odp")
        self.body = document.body

    def test_create_frame(self):
        frame = Frame("A Frame", size=("10cm", "10cm"), style="Graphics")
        expected = (
            '<draw:frame svg:width="10cm" svg:height="10cm" '
            'draw:z-index="0" draw:name="A Frame" '
            'draw:style-name="Graphics"/>'
        )
        self.assertEqual(frame.serialize(), expected)

    def test_create_frame_page(self):
        frame = Frame(
            "Another Frame",
            size=("10cm", "10cm"),
            anchor_type="page",
            anchor_page=1,
            position=("10mm", "10mm"),
            style="Graphics",
        )
        self.assertIn(
            frame.serialize(),
            (
                (
                    '<draw:frame svg:width="10cm" svg:height="10cm" '
                    'draw:z-index="0" draw:name="Another Frame" '
                    'draw:style-name="Graphics" '
                    'svg:x="10mm" svg:y="10mm" '
                    'text:anchor-type="page" '
                    'text:anchor-page-number="1"/>'
                ),
                (
                    '<draw:frame svg:width="10cm" svg:height="10cm" '
                    'draw:z-index="0" draw:name="Another Frame" '
                    'text:anchor-type="page" text:anchor-page-number="1" '
                    'svg:x="10mm" svg:y="10mm" '
                    'draw:style-name="Graphics"/>'
                ),
            ),
        )

    def test_get_frame_list(self):
        body = self.body
        result = body.get_frames()
        self.assertEqual(len(result), 4)

    def test_get_frame_list_title(self):
        body = self.body
        result = body.get_frames(title="Intitulé")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].tag, "draw:frame")

    def test_get_frame_by_name(self):
        body = self.body
        frame = body.get_frame(name="odfdo")
        self.assertEqual(frame.tag, "draw:frame")

    def test_get_frame_by_position(self):
        body = self.body
        frame = body.get_frame(position=3)
        self.assertEqual(frame.presentation_class, "notes")

    def test_get_frame_by_description(self):
        body = self.body
        frame = body.get_frame(description="描述")
        self.assertEqual(frame.tag, "draw:frame")

    def test_insert_frame(self):
        body = self.body.clone
        frame1 = Frame("frame1", size=("10cm", "10cm"), style="Graphics")
        frame2 = Frame(
            "frame2",
            size=("10cm", "10cm"),
            anchor_page=1,
            position=("10mm", "10mm"),
            style="Graphics",
        )
        body.append(frame1)
        body.append(frame2)
        result = body.get_frames(style="Graphics")
        self.assertEqual(len(result), 2)
        element = body.get_frame(name="frame1")
        self.assertEqual(element.tag, "draw:frame")
        element = body.get_frame(name="frame2")
        self.assertEqual(element.tag, "draw:frame")


class TestImageFrame(TestCase):
    def test_create_image_frame(self):
        frame = Frame.image_frame("Pictures/zoe.jpg")
        self.assertIn(
            frame.serialize(),
            (
                (
                    '<draw:frame svg:width="1cm" svg:height="1cm" '
                    'draw:z-index="0">'
                    '<draw:image xlink:href="Pictures/zoe.jpg" '
                    'xlink:type="simple" xlink:show="embed" '
                    'xlink:actuate="onLoad"/>'
                    "</draw:frame>"
                ),
            ),
        )

    def test_create_image_frame_text(self):
        frame = Frame.image_frame("Pictures/zoe.jpg", text=ZOE)
        expected = (
            '<draw:frame svg:width="1cm" svg:height="1cm" '
            'draw:z-index="0">'
            '<draw:image xlink:href="Pictures/zoe.jpg" '
            'xlink:type="simple" xlink:show="embed" '
            'xlink:actuate="onLoad">'
            "<text:p>%s</text:p>"
            "</draw:image>"
            "</draw:frame>"
        ) % ZOE
        self.assertEqual(frame.serialize(), expected)


class TestTextFrame(TestCase):
    def test_create_text_frame(self):
        frame = Frame.text_frame(ZOE)
        expected = (
            '<draw:frame svg:width="1cm" svg:height="1cm" '
            'draw:z-index="0">'
            "<draw:text-box>"
            "<text:p>%s</text:p>"
            "</draw:text-box>"
            "</draw:frame>"
        ) % ZOE
        self.assertEqual(frame.serialize(), expected)

    def test_create_text_frame_element(self):
        heading = Header(1, ZOE)
        frame = Frame.text_frame(heading)
        expected = (
            '<draw:frame svg:width="1cm" svg:height="1cm" '
            'draw:z-index="0">'
            "<draw:text-box>"
            '<text:h text:outline-level="1">%s</text:h>'
            "</draw:text-box>"
            "</draw:frame>"
        ) % ZOE
        self.assertEqual(frame.serialize(), expected)


class TestOdfFrame(TestCase):
    def setUp(self):
        document = Document("samples/frame_image.odp")
        self.body = document.body
        self.size = size = ("1cm", "2mm")
        self.position = position = ("3in", "4pt")
        self.frame = Frame(size=size, position=position, anchor_type="paragraph")

    def test_get_frame(self):
        body = self.body
        frame = body.get_frame()
        self.assertTrue(isinstance(frame, Frame))

    def test_get_frame_size(self):
        self.assertEqual(self.frame.size, self.size)

    def test_set_size(self):
        frame = self.frame.clone
        frame.size = self.position
        self.assertEqual(frame.size, self.position)

    def test_get_frame_position(self):
        self.assertEqual(self.frame.position, self.position)

    def test_set_frame_position(self):
        frame = self.frame.clone
        frame.position = self.size
        self.assertEqual(frame.position, self.size)

    def test_get_frame_anchor_type(self):
        self.assertEqual(self.frame.anchor_type, "paragraph")

    def test_set_frame_anchor_type(self):
        frame = self.frame.clone
        self.assertEqual(frame.anchor_page, None)
        frame.anchor_type = "page"
        frame.anchor_page = 3
        self.assertEqual(frame.anchor_type, "page")
        self.assertEqual(frame.anchor_page, 3)


if __name__ == "__main__":
    main()
