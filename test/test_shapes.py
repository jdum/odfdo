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

from odfdo.const import ODF_CONTENT
from odfdo.document import Document
from odfdo.draw_page import DrawPage
from odfdo.paragraph import Paragraph
from odfdo.shapes import EllipseShape, ConnectorShape
from odfdo.shapes import LineShape, RectangleShape


class TestShapes(TestCase):
    def setUp(self):
        self.document = document = Document("samples/base_shapes.odg")
        self.content = document.get_part(ODF_CONTENT)

    def tearDown(self):
        del self.content
        del self.document

    def test_create_line(self):
        page = DrawPage("Page1")
        line = LineShape(p1=("2cm", "2cm"), p2=("1cm", "1cm"))
        page.append(line)
        expected = (
            '<draw:page draw:id="Page1">\n'
            '  <draw:line svg:x1="2cm" svg:y1="2cm" svg:x2="1cm" '
            'svg:y2="1cm"/>\n'
            "</draw:page>\n"
        )
        self.assertEqual(page.serialize(pretty=True), expected)

    def test_create_rectangle(self):
        page = DrawPage("Page1")
        rectangle = RectangleShape(size=("2cm", "1cm"), position=("3cm", "4cm"))
        page.append(rectangle)
        self.assertIn(
            page.serialize(),
            (
                (
                    '<draw:page draw:id="Page1">'
                    '<draw:rect svg:x="3cm" svg:y="4cm" '
                    'svg:width="2cm" svg:height="1cm"/>'
                    "</draw:page>"
                ),
                (
                    '<draw:page draw:id="Page1">'
                    '<draw:rect svg:width="2cm" '
                    'svg:height="1cm" svg:x="3cm"'
                    ' svg:y="4cm"/>'
                    "</draw:page>"
                ),
            ),
        )

    def test_create_ellipse(self):
        page = DrawPage("Page1")
        svg_attrs = {
            "svg:width": "2cm",
            "svg:height": "2cm",
            "svg:x": "2cm",
            "svg:y": "2cm",
        }
        ellipse = EllipseShape(size=("2cm", "1cm"), position=("3cm", "4cm"))
        page.append(ellipse)
        expected = (
            '<draw:page draw:id="Page1">'
            "<draw:ellipse "
            'svg:x="3cm" svg:y="4cm" '
            'svg:width="2cm" svg:height="1cm"/>'
            "</draw:page>"
        )
        self.assertEqual(page.serialize(), expected)

    def test_create_connector(self):
        page = DrawPage("Page1")
        rectangle = RectangleShape(
            size=("2cm", "1cm"), position=("3cm", "4cm"), draw_id="rectangle"
        )
        ellipse = EllipseShape(
            size=("2cm", "1cm"), position=("3cm", "4cm"), draw_id="ellipse"
        )
        connector = ConnectorShape(
            connected_shapes=(rectangle, ellipse), glue_points=(1, 2)
        )
        page.append(rectangle)
        page.append(ellipse)
        page.append(connector)
        expected = (
            '<draw:page draw:id="Page1">'
            '<draw:rect draw:id="rectangle" '
            'svg:x="3cm" svg:y="4cm" '
            'svg:width="2cm" svg:height="1cm"/>'
            '<draw:ellipse draw:id="ellipse" '
            'svg:x="3cm" svg:y="4cm" '
            'svg:width="2cm" svg:height="1cm"/>'
            '<draw:connector draw:start-shape="rectangle" '
            'draw:end-shape="ellipse" '
            'draw:start-glue-point="1" '
            'draw:end-glue-point="2"/>'
            "</draw:page>"
        )
        self.assertEqual(page.serialize(), expected)

    # Lines

    def test_get_draw_line_list(self):
        body = self.content.body
        page = body.get_draw_page()
        lines = page.get_draw_lines()
        self.assertEqual(len(lines), 2)

    def test_get_draw_line_list_regex(self):
        body = self.content.body
        page = body.get_draw_page()
        lines = page.get_draw_lines(content="èche*")
        self.assertEqual(len(lines), 1)

    def test_get_draw_line_list_draw_style(self):
        body = self.content.body
        page = body.get_draw_page()
        lines = page.get_draw_lines(draw_style="gr2")
        self.assertEqual(len(lines), 1)

    def test_get_draw_line_list_draw_text_style(self):
        body = self.content.body
        page = body.get_draw_page()
        lines = page.get_draw_lines(draw_text_style="P1")
        self.assertEqual(len(lines), 2)

    def test_get_draw_line_by_content(self):
        body = self.content.body
        page = body.get_draw_page()
        line = page.get_draw_line(content="Ligne")
        expected = (
            '<draw:line draw:style-name="gr1" '
            'draw:text-style-name="P1" draw:layer="layout" '
            'svg:x1="3.5cm" svg:y1="2.5cm" svg:x2="10.5cm" '
            'svg:y2="12cm">\n'
            '  <text:p text:style-name="P1">Ligne</text:p>\n'
            "</draw:line>\n"
        )
        self.assertEqual(line.serialize(pretty=True), expected)

    def test_get_draw_line_by_id(self):
        body = self.content.body
        page = body.get_draw_page()
        line = LineShape(draw_id="an id")
        page.append(line)
        line = page.get_draw_line(id="an id")
        expected = '<draw:line draw:id="an id"/>\n'
        self.assertEqual(line.serialize(pretty=True), expected)

    # Rectangles

    def test_get_draw_rectangle_list(self):
        body = self.content.body
        page = body.get_draw_page()
        rectangles = page.get_draw_rectangles()
        self.assertEqual(len(rectangles), 1)

    def test_get_draw_rectangle_list_regex(self):
        body = self.content.body
        page = body.get_draw_page()
        rectangles = page.get_draw_rectangles(content="angle")
        self.assertEqual(len(rectangles), 1)

    def test_get_draw_rectangle_list_draw_style(self):
        body = self.content.body
        page = body.get_draw_page()
        rectangles = page.get_draw_rectangles(draw_style="gr1")
        self.assertEqual(len(rectangles), 1)

    def test_get_draw_rectangle_list_draw_text_style(self):
        body = self.content.body
        page = body.get_draw_page()
        rectangles = page.get_draw_rectangles(draw_text_style="P1")
        self.assertEqual(len(rectangles), 1)

    def test_get_draw_rectangle_by_content(self):
        body = self.content.body
        page = body.get_draw_page()
        rectangle = page.get_draw_rectangle(content="Rect")
        expected = (
            '<draw:rect draw:style-name="gr1" '
            'draw:text-style-name="P1" xml:id="id1" draw:id="id1" '
            'draw:layer="layout" svg:width="6cm" svg:height="7cm" '
            'svg:x="5cm" svg:y="4.5cm">\n'
            '  <text:p text:style-name="P1">Rectangle</text:p>\n'
            "</draw:rect>\n"
        )
        self.assertEqual(rectangle.serialize(pretty=True), expected)

    def test_get_draw_rectangle_by_id(self):
        body = self.content.body
        page = body.get_draw_page()
        rectangle = RectangleShape(draw_id="an id")
        page.append(rectangle)
        rectangle = page.get_draw_rectangle(id="an id")
        expected = '<draw:rect draw:id="an id"/>'
        self.assertEqual(rectangle.serialize(), expected)

    # Ellipses

    def test_get_draw_ellipse_list(self):
        body = self.content.body
        page = body.get_draw_page()
        ellipses = page.get_draw_ellipses()
        self.assertEqual(len(ellipses), 1)

    def test_get_draw_ellipse_list_regex(self):
        body = self.content.body
        page = body.get_draw_page()
        ellipses = page.get_draw_ellipses(content="rcle")
        self.assertEqual(len(ellipses), 1)

    def test_get_draw_ellipse_list_draw_style(self):
        body = self.content.body
        page = body.get_draw_page()
        ellipses = page.get_draw_ellipses(draw_style="gr1")
        self.assertEqual(len(ellipses), 1)

    def test_get_draw_ellipse_list_draw_text_style(self):
        body = self.content.body
        page = body.get_draw_page()
        ellipses = page.get_draw_ellipses(draw_text_style="P1")
        self.assertEqual(len(ellipses), 1)

    def test_get_draw_ellipse_by_content(self):
        body = self.content.body
        page = body.get_draw_page()
        ellipse = page.get_draw_ellipse(content="Cerc")
        expected = (
            '<draw:ellipse draw:style-name="gr1" '
            'draw:text-style-name="P1" xml:id="id2" draw:id="id2" '
            'draw:layer="layout" svg:width="4cm" svg:height="3.5cm" '
            'svg:x="13.5cm" svg:y="5cm">\n'
            '  <text:p text:style-name="P1">Cercle</text:p>\n'
            "</draw:ellipse>\n"
        )
        self.assertEqual(ellipse.serialize(pretty=True), expected)

    def test_get_draw_ellipse_by_id(self):
        body = self.content.body
        page = body.get_draw_page()
        ellipse = EllipseShape(draw_id="an id")
        page.append(ellipse)
        ellipse = page.get_draw_ellipse(id="an id")
        expected = '<draw:ellipse draw:id="an id"/>'
        self.assertEqual(ellipse.serialize(), expected)

    # Connectors

    def test_get_draw_connector_list(self):
        body = self.content.body
        page = body.get_draw_page()
        connectors = page.get_draw_connectors()
        self.assertEqual(len(connectors), 1)

    def test_get_draw_connector_list_regex(self):
        body = self.content.body
        page = body.get_draw_page()
        connectors = page.get_draw_connectors(content="Con")
        self.assertEqual(len(connectors), 1)

    def test_get_draw_connector_list_draw_style(self):
        body = self.content.body
        page = body.get_draw_page()
        connectors = page.get_draw_connectors(draw_style="gr4")
        self.assertEqual(len(connectors), 0)

    def test_get_draw_connector_list_draw_text_style(self):
        body = self.content.body
        page = body.get_draw_page()
        connectors = page.get_draw_connectors(draw_text_style="P1")
        self.assertEqual(len(connectors), 1)

    def test_get_draw_connector_by_content(self):
        body = self.content.body
        page = body.get_draw_page()
        connector = page.get_draw_connector(content="ecteur")
        expected = (
            '<draw:connector draw:style-name="gr1" '
            'draw:text-style-name="P1" draw:layer="layout" '
            'svg:x1="11cm" svg:y1="8cm" svg:x2="15.5cm" svg:y2="8.5cm" '
            'draw:start-shape="id1" draw:start-glue-point="1" '
            'draw:end-shape="id2" draw:end-glue-point="2" '
            'svg:d="M11000 8000h1250v1001h3250v-501" '
            'svg:viewBox="0 0 4501 1002">\n'
            '  <text:p text:style-name="P1">Connecteur</text:p>\n'
            "</draw:connector>\n"
        )
        self.assertEqual(connector.serialize(pretty=True), expected)

    def test_get_draw_connector_by_id(self):
        body = self.content.body
        page = body.get_draw_page()
        connector = ConnectorShape(draw_id="an id")
        page.append(connector)
        connector = page.get_draw_connector(id="an id")
        expected = '<draw:connector draw:id="an id"/>\n'
        self.assertEqual(connector.serialize(pretty=True), expected)

    def test_get_draw_orphans_connector(self):
        body = self.content.body
        page = body.get_draw_page()
        orphan_connector = ConnectorShape()
        orphan_connector.append(Paragraph("Orphan c"))
        body.append(orphan_connector)
        connectors = body.get_orphan_draw_connectors()
        self.assertEqual(len(connectors), 1)


if __name__ == "__main__":
    main()
