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

from odfdo.const import ODF_CONTENT
from odfdo.container import Container
from odfdo.document import Document
from odfdo.style import Style
from odfdo.style import hex2rgb, rgb2hex
from odfdo.style import make_table_cell_border_string
from odfdo.style import create_table_cell_style
from odfdo.xmlpart import XmlPart


class Hex2RgbTestCase(TestCase):
    def test_color_low(self):
        color = "#012345"
        expected = (1, 35, 69)
        self.assertEqual(hex2rgb(color), expected)

    def test_color_high(self):
        color = "#ABCDEF"
        expected = (171, 205, 239)
        self.assertEqual(hex2rgb(color), expected)

    def test_color_lowercase(self):
        color = "#abcdef"
        expected = (171, 205, 239)
        self.assertEqual(hex2rgb(color), expected)

    def test_color_bad_size(self):
        color = "#fff"
        self.assertRaises(ValueError, hex2rgb, color)

    def test_color_bad_format(self):
        color = "978EAE"
        self.assertRaises(ValueError, hex2rgb, color)

    def test_color_bad_hex(self):
        color = "#978EAZ"
        self.assertRaises(ValueError, hex2rgb, color)


class Rgb2HexTestCase(TestCase):
    def test_color_name(self):
        color = "violet"
        expected = "#EE82EE"
        self.assertEqual(rgb2hex(color), expected)

    def test_color_tuple(self):
        color = (171, 205, 239)
        expected = "#ABCDEF"
        self.assertEqual(rgb2hex(color), expected)

    def test_color_bad_name(self):
        color = "dark white"
        self.assertRaises(KeyError, rgb2hex, color)

    def test_color_bad_tuple(self):
        # For alpha channel? ;-)
        color = (171, 205, 238, 128)
        self.assertRaises(ValueError, rgb2hex, color)

    def test_color_bad_low_channel(self):
        color = (171, 205, -1)
        self.assertRaises(ValueError, rgb2hex, color)

    def test_color_bad_high_channel(self):
        color = (171, 205, 256)
        self.assertRaises(ValueError, rgb2hex, color)

    def test_color_bad_value(self):
        color = {}
        self.assertRaises(TypeError, rgb2hex, color)


class Test_make_table_cell_border_string(TestCase):
    def test_default_border(self):
        expected = "0.06pt solid #000000"
        self.assertEqual(make_table_cell_border_string(), expected)

    def test_border_bold(self):
        expected = "0.30pt solid #000000"
        self.assertEqual(make_table_cell_border_string(thick=0.3), expected)

    def test_border_bold2(self):
        expected = "0.30pt solid #000000"
        self.assertEqual(make_table_cell_border_string(thick="0.30pt"), expected)

    def test_border_int(self):
        expected = "0.06pt solid #000000"
        self.assertEqual(make_table_cell_border_string(thick=6), expected)

    def test_border_custom(self):
        expected = "0.1cm dotted #FF0000"
        self.assertEqual(
            make_table_cell_border_string(
                thick="0.1cm ", line=" dotted", color="#FF0000 "
            ),
            expected,
        )

    def test_border_color_raise(self):
        arg = (None, None, "bug")
        self.assertRaises(ValueError, make_table_cell_border_string, arg)

    def test_border_color_name(self):
        expected = "0.06pt solid #D3D3D3"
        self.assertEqual(make_table_cell_border_string(color="lightgrey"), expected)

    def test_border_color_tuple(self):
        expected = "0.06pt solid #808080"
        self.assertEqual(make_table_cell_border_string(color=(128, 128, 128)), expected)


class TestCreateStyle(TestCase):
    def test_create_style_paragraph(self):
        style = Style("paragraph", "style1")
        expected = ()
        self.assertIn(
            style.serialize(),
            (
                ('<style:style style:family="paragraph" ' 'style:name="style1"/>'),
                ('<style:style style:name="style1" ' 'style:family="paragraph"/>'),
            ),
        )

    def test_create_style_text(self):
        style = Style("text")
        expected = '<style:style style:family="text"/>'
        self.assertEqual(style.serialize(), expected)

    def test_create_style_graphic(self):
        style = Style("graphic")
        expected = '<style:style style:family="graphic"/>'
        self.assertEqual(style.serialize(), expected)

    def test_create_style_table(self):
        style = Style("table")
        expected = '<style:style style:family="table"/>'
        self.assertEqual(style.serialize(), expected)

    def test_create_style_table_column(self):
        style = Style("table-column")
        expected = '<style:style style:family="table-column"/>'
        self.assertEqual(style.serialize(), expected)

    def test_create_style_table_row(self):
        style = Style("table-row")
        expected = '<style:style style:family="table-row"/>'
        self.assertEqual(style.serialize(), expected)

    def test_create_style_table_cell(self):
        style = Style("table-cell")
        expected = '<style:style style:family="table-cell"/>'
        self.assertEqual(style.serialize(), expected)

    def test_create_style_section(self):
        style = Style("section")
        expected = '<style:style style:family="section"/>'
        self.assertEqual(style.serialize(), expected)

    def test_create_style_list(self):
        style = Style("list")
        expected = "<text:list-style/>"
        self.assertEqual(style.serialize(), expected)

    def test_create_style_outline(self):
        style = Style("outline")
        expected = "<text:outline-style/>"
        self.assertEqual(style.serialize(), expected)

    def test_create_style_page_layout(self):
        style = Style("page-layout")
        expected = "<style:page-layout/>"
        self.assertEqual(style.serialize(), expected)

    def test_create_style_master_page(self):
        style = Style("master-page")
        expected = "<style:master-page/>"
        self.assertEqual(style.serialize(), expected)

    def test_create_style_display_name(self):
        style = Style("paragraph", display_name="Heading 1")
        expected = (
            '<style:style style:family="paragraph" ' 'style:display-name="Heading 1"/>'
        )
        self.assertEqual(style.serialize(), expected)

    def test_create_style_parent(self):
        style = Style("paragraph", parent_style="Heading 1")
        expected = (
            '<style:style style:family="paragraph" '
            'style:parent-style-name="Heading 1"/>'
        )
        self.assertEqual(style.serialize(), expected)

    def test_create_style_properties(self):
        style = Style("paragraph", **{"fo:margin-top": "0cm"})
        expected = (
            '<style:style style:family="paragraph">'
            '<style:paragraph-properties fo:margin-top="0cm"/>'
            "</style:style>"
        )
        self.assertEqual(style.serialize(), expected)

    def test_create_style_properties_shorcut(self):
        style = Style("paragraph", area="text", color="#ff0000")
        expected = (
            '<style:style style:family="paragraph">'
            '<style:text-properties fo:color="#ff0000"/>'
            "</style:style>"
        )
        # <style:style style:family="paragraph"/>
        self.assertEqual(style.serialize(), expected)


class TestStyle(TestCase):
    def setUp(self):
        self.document = document = Document("samples/span_style.odt")
        self.content = document.get_part(ODF_CONTENT)

    def test_get_styles(self):
        content = self.content
        styles = content.get_styles()
        self.assertEqual(len(styles), 7)

    def test_get_styles_family(self):
        content = self.content
        styles = content.get_styles(family="paragraph")
        self.assertEqual(len(styles), 2)

    def test_get_style_automatic(self):
        content = self.content
        style = content.get_style("paragraph", "P1")
        self.assertNotEqual(style, None)

    def test_insert_style(self):
        content = self.content.clone
        style = Style(
            "paragraph",
            "style1",
            area="text",
            **{"fo:color": "#0000ff", "fo:background-color": "#ff0000"}
        )
        auto_styles = content.get_element("//office:automatic-styles")
        auto_styles.append(style)
        get1 = content.get_style("paragraph", "style1")
        self.assertIn(
            get1.serialize(),
            (
                (
                    '<style:style style:name="style1" '
                    'style:family="paragraph">'
                    "<style:text-properties "
                    'fo:background-color="#ff0000" '
                    'fo:color="#0000ff"/>'
                    "</style:style>"
                ),
                (
                    '<style:style style:name="style1" '
                    'style:family="paragraph">'
                    '<style:text-properties fo:color="#0000ff" '
                    'fo:background-color="#ff0000"/>'
                    "</style:style>"
                ),
                (
                    '<style:style style:family="paragraph" '
                    'style:name="style1">'
                    "<style:text-properties "
                    'fo:background-color="#ff0000" '
                    'fo:color="#0000ff"/>'
                    "</style:style>"
                ),
            ),
        )


class StylePropertiesTestCase(TestCase):
    def setUp(self):
        self.container = container = Container("samples/example.odt")
        self.content_part = content_part = XmlPart(ODF_CONTENT, container)
        self.paragraph_element = content_part.get_element("//text:p[1]")
        query = '//style:style[@style:family="paragraph"][1]'
        self.style_element = content_part.get_element(query)

    def test_odf_style(self):
        style = self.style_element
        self.assertTrue(isinstance(style, Style))

    def test_get_style_properties(self):
        style = self.style_element
        properties = style.get_properties()
        self.assertTrue(isinstance(properties, dict))
        self.assertEqual(len(properties), 12)
        self.assertEqual(properties["fo:margin-left"], "0cm")

    def test_get_style_properties_area(self):
        style = self.style_element
        properties = style.get_properties(area="text")
        self.assertTrue(isinstance(properties, dict))
        self.assertEqual(len(properties), 1)
        self.assertEqual(properties["fo:hyphenate"], "false")

    def test_get_style_properties_bad_element(self):
        element = self.paragraph_element
        self.assertRaises(AttributeError, element.__getattribute__, "get_properties")

    def test_get_style_properties_bad_area(self):
        style = self.style_element
        properties = style.get_properties(area="toto")
        self.assertEqual(properties, None)

    def test_set_style_properties(self):
        style = self.style_element.clone
        style.set_properties({"fo:color": "#f00"})
        properties = style.get_properties()
        self.assertEqual(len(properties), 13)
        self.assertEqual(properties["fo:color"], "#f00")

    def test_set_style_properties_area(self):
        style = self.style_element.clone
        style.set_properties({"fo:color": "#f00"}, area="text")
        properties = style.get_properties(area="text")
        self.assertEqual(len(properties), 2)
        self.assertEqual(properties["fo:color"], "#f00")

    def test_set_style_properties_new_area(self):
        style = self.style_element.clone
        properties = style.get_properties(area="chart")
        self.assertEqual(properties, None)
        style.set_properties({"fo:color": "#f00"}, area="chart")
        properties = style.get_properties(area="chart")
        self.assertEqual(len(properties), 1)
        self.assertEqual(properties["fo:color"], "#f00")

    def test_del_style_properties(self):
        style = self.style_element.clone
        style.del_properties(["fo:margin-left"])
        properties = style.get_properties()
        self.assertEqual(len(properties), 11)
        self.assertRaises(KeyError, properties.__getitem__, "fo:margin-left")

    def test_del_style_properties_bad_area(self):
        style = self.style_element
        self.assertRaises(ValueError, style.del_properties, area="toto")


class StyleBackgroundTestCase(TestCase):
    def setUp(self):
        self.style = Style("paragraph")

    def test_bad_family(self):
        style = Style("master-page")
        self.assertRaises(TypeError, style.set_background)

    def test_color(self):
        style = self.style.clone
        style.set_background(color="#abcdef")
        expected = (
            '<style:style style:family="paragraph">'
            "<style:paragraph-properties "
            'fo:background-color="#abcdef"/>'
            "</style:style>"
        )
        self.assertEqual(style.serialize(), expected)

    def test_image(self):
        style = self.style.clone
        style.set_background(url="Pictures/toto")
        expected = (
            '<style:style style:family="paragraph">'
            "<style:paragraph-properties "
            'fo:background-color="transparent">'
            "<style:background-image "
            'xlink:href="Pictures/toto" '
            'style:position="center"/>'
            "</style:paragraph-properties>"
            "</style:style>"
        )
        self.assertEqual(style.serialize(), expected)

    def test_image_full(self):
        style = self.style.clone
        style.set_background(
            url="Pictures/toto",
            position="top left",
            repeat="no-repeat",
            opacity=50,
            filter="myfilter",
        )
        expected = (
            '<style:style style:family="paragraph">'
            "<style:paragraph-properties "
            'fo:background-color="transparent">'
            "<style:background-image "
            'xlink:href="Pictures/toto" '
            'style:position="top left" '
            'style:repeat="no-repeat" '
            'draw:opacity="50" '
            'style:filter-name="myfilter"/>'
            "</style:paragraph-properties>"
            "</style:style>"
        )
        self.assertEqual(style.serialize(), expected)


class LevelStyleTestCase(TestCase):
    def setUp(self):
        self.style = Style("list")

    def test_get_level_style(self):
        level_style = self.style.get_level_style(1)
        self.assertTrue(level_style is None)

    def test_set_level_style(self):
        self.style.set_level_style(1, num_format="1")
        level_style = self.style.get_level_style(1)
        self.assertTrue(level_style is not None)

    def test_set_level_style_number_missing_format(self):
        self.assertRaises(ValueError, self.style.set_level_style, 1)

    def test_set_level_style_number(self):
        level_style = self.style.set_level_style(1, num_format="1")
        self.assertTrue(isinstance(level_style, Style))
        expected = "<text:list-level-style-number " 'text:level="1" fo:num-format="1"/>'
        self.assertEqual(level_style.serialize(), expected)

    def test_set_level_style_bullet(self):
        level_style = self.style.set_level_style(2, bullet_char="·")
        self.assertTrue(isinstance(level_style, Style))
        expected = (
            "<text:list-level-style-bullet " 'text:level="2" text:bullet-char="·"/>'
        )
        self.assertEqual(level_style.serialize(), expected)

    def test_set_level_style_image(self):
        level_style = self.style.set_level_style(3, url="bullet.png")
        self.assertTrue(isinstance(level_style, Style))
        expected = (
            "<text:list-level-style-image " 'text:level="3" xlink:href="bullet.png"/>'
        )
        self.assertEqual(level_style.serialize(), expected)

    def test_set_level_style_full(self):
        level_style = self.style.set_level_style(
            3,
            num_format="1",
            prefix=" ",
            suffix=".",
            display_levels=3,
            start_value=2,
            style="MyList",
        )
        expected = (
            "<text:list-level-style-number "
            'text:level="3" fo:num-format="1" '
            'style:num-prefix=" " style:num-suffix="." '
            'text:display-levels="3" text:start-value="2" '
            'text:style-name="MyList"/>'
        )
        self.assertEqual(level_style.serialize(), expected)

    def test_set_level_style_clone(self):
        level_1 = self.style.set_level_style(1, num_format="1")
        level_2 = self.style.set_level_style(2, display_levels=2, clone=level_1)
        expected = (
            "<text:list-level-style-number "
            'text:level="2" fo:num-format="1" '
            'text:display-levels="2"/>'
        )
        self.assertEqual(level_2.serialize(), expected)


class TableStyleTestCase(TestCase):
    def test_table_cell_border(self):
        style = Style("table-cell", border="0.002cm")
        self.assertEqual(
            style.serialize(),
            (
                "<style:style "
                'style:family="table-cell"><style:table-cell-properties '
                'fo:border="0.002cm"/></style:style>'
            ),
        )

    def test_table_cell_border_border_left(self):
        style = Style("table-cell", border="0.002cm", border_left="0.002cm")
        self.assertEqual(
            style.serialize(),
            (
                "<style:style "
                'style:family="table-cell"><style:table-cell-properties '
                'fo:border="0.002cm"/></style:style>'
            ),
        )

    def test_table_cell_border_top(self):
        style = Style("table-cell", border_top="0.002cm")
        self.assertIn(
            style.serialize(),
            (
                (
                    "<style:style "
                    'style:family="table-cell"><style:table-cell-properties '
                    'fo:border-bottom="none" fo:border-left="none" '
                    'fo:border-right="none" fo:border-top="0.002cm"/>'
                    "</style:style>"
                ),
                (
                    "<style:style "
                    'style:family="table-cell"><style:table-cell-properties '
                    'fo:border-top="0.002cm" fo:border-right="none" '
                    'fo:border-bottom="none" fo:border-left="none"/>'
                    "</style:style>"
                ),
                (
                    "<style:style "
                    'style:family="table-cell"><style:table-cell-properties '
                    'fo:border-top="0.002cm" fo:border-left="none" '
                    'fo:border-right="none" fo:border-bottom="none"/>'
                    "</style:style>"
                ),
            ),
        )

    def test_table_cell_border_all(self):
        style = Style(
            "table-cell",
            border_top="0.001cm",
            border_right="0.002cm",
            border_bottom="0.003cm",
            border_left="0.004cm",
        )

        self.assertIn(
            style.serialize(),
            (
                (
                    "<style:style "
                    'style:family="table-cell"><style:table-cell-properties '
                    'fo:border-top="0.001cm" fo:border-right="0.002cm" '
                    'fo:border-bottom="0.003cm" fo:border-left="0.004cm"/>'
                    "</style:style>"
                ),
                (
                    "<style:style "
                    'style:family="table-cell"><style:table-cell-properties '
                    'fo:border-bottom="0.003cm" fo:border-left="0.004cm" '
                    'fo:border-right="0.002cm" fo:border-top="0.001cm"/>'
                    "</style:style>"
                ),
            ),
        )

    def test_table_cell_shadow(self):
        style = Style("table-cell", shadow="#808080 0.176cm 0.176cm")
        self.assertEqual(
            style.serialize(),
            (
                "<style:style "
                'style:family="table-cell"><style:table-cell-properties '
                'style:shadow="#808080 0.176cm 0.176cm"/></style:style>'
            ),
        )

    def test_table_row_height(self):
        style = Style("table-row", height="5cm")
        self.assertEqual(
            style.serialize(),
            (
                "<style:style "
                'style:family="table-row"><style:table-row-properties '
                'style:row-height="5cm"/></style:style>'
            ),
        )

    def test_table_column_width(self):
        style = Style("table-column", width="5cm")
        self.assertEqual(
            style.serialize(),
            (
                "<style:style "
                'style:family="table-column"><style:table-column-properties '
                'style:column-width="5cm"/></style:style>'
            ),
        )


class Table_cell_style_test(TestCase):
    def test_odf_create_table_cell_style(self):
        border = make_table_cell_border_string()
        style = create_table_cell_style(border=border)
        self.assertEqual(
            style.serialize(),
            (
                "<style:style "
                'style:family="table-cell"><style:table-cell-properties '
                'fo:border="0.06pt solid #000000"/></style:style>'
            ),
        )

    def test_odf_create_table_cell_style_top(self):
        border = make_table_cell_border_string()
        style = create_table_cell_style(border_top=border)
        self.assertIn(
            style.serialize(),
            (
                (
                    "<style:style "
                    'style:family="table-cell"><style:table-cell-properties '
                    'fo:border-bottom="none" fo:border-left="none" '
                    'fo:border-right="none" '
                    'fo:border-top="0.06pt solid #000000"/>'
                    "</style:style>"
                ),
                (
                    "<style:style "
                    'style:family="table-cell"><style:table-cell-properties '
                    'fo:border-top="0.06pt solid #000000" '
                    'fo:border-left="none" '
                    'fo:border-right="none" fo:border-bottom="none"/>'
                    "</style:style>"
                ),
            ),
        )

    def test_odf_create_table_cell_style_bg(self):
        border = make_table_cell_border_string(color="blue")
        style = create_table_cell_style(border=border, background_color="green")
        self.assertIn(
            style.serialize(),
            (
                (
                    "<style:style "
                    'style:family="table-cell"><style:table-cell-properties '
                    'fo:background-color="#008000" '
                    'fo:border="0.06pt solid #0000FF"/>'
                    "</style:style>"
                ),
                (
                    "<style:style "
                    'style:family="table-cell"><style:table-cell-properties '
                    'fo:border="0.06pt solid #0000FF" fo:background-color="#008000"/>'
                    "</style:style>"
                ),
            ),
        )

    def test_odf_create_table_cell_style_color(self):
        border = make_table_cell_border_string(color="blue")
        style = create_table_cell_style(border=border, color="yellow")
        self.assertEqual(
            style.serialize(),
            (
                "<style:style "
                'style:family="table-cell"><style:table-cell-properties '
                'fo:border="0.06pt solid #0000FF"/><style:text-properties '
                'fo:color="#FFFF00"/></style:style>'
            ),
        )

    def test_odf_create_table_cell_style_all(self):
        border_left = make_table_cell_border_string(color="blue")
        border_right = make_table_cell_border_string(thick=60)
        style = create_table_cell_style(
            background_color="yellow",
            color=(128, 64, 32),
            border_left=border_left,
            border_right=border_right,
            padding_right="0.05pt",
        )
        self.assertIn(
            style.serialize(),
            (
                (
                    "<style:style "
                    'style:family="table-cell"><style:table-cell-properties '
                    'fo:background-color="#FFFF00" fo:border-bottom="none" '
                    'fo:border-left="0.06pt solid #0000FF" '
                    'fo:border-right="0.60pt solid #000000" '
                    'fo:border-top="none" fo:padding-bottom="none" '
                    'fo:padding-left="none" fo:padding-right="0.05pt" '
                    'fo:padding-top="none"/>'
                    '<style:text-properties fo:color="#804020"/>'
                    "</style:style>"
                ),
                (
                    "<style:style "
                    'style:family="table-cell"><style:table-cell-properties '
                    'fo:border-top="none" fo:border-right="0.60pt solid #000000" '
                    'fo:border-bottom="none" '
                    'fo:border-left="0.06pt solid #0000FF" '
                    'fo:padding-top="none" fo:padding-right="0.05pt" '
                    'fo:padding-bottom="none" fo:padding-left="none" '
                    'fo:background-color="#FFFF00"/>'
                    '<style:text-properties fo:color="#804020"/>'
                    "</style:style>"
                ),
            ),
        )

    def test_odf_create_table_cell_style_default_border(self):
        style = create_table_cell_style(border="default")
        self.assertEqual(
            style.serialize(),
            (
                "<style:style "
                'style:family="table-cell"><style:table-cell-properties '
                'fo:border="0.06pt solid #000000"/>'
                "</style:style>"
            ),
        )

    def test_odf_create_table_cell_style_none_border(self):
        style = create_table_cell_style()
        self.assertEqual(
            style.serialize(),
            (
                "<style:style "
                'style:family="table-cell"><style:table-cell-properties '
                'fo:border="none"/>'
                "</style:style>"
            ),
        )

    def test_odf_create_table_cell_style_padding(self):
        style = create_table_cell_style(padding="0.5mm")
        self.assertEqual(
            style.serialize(),
            (
                "<style:style "
                'style:family="table-cell"><style:table-cell-properties '
                'fo:border="none" fo:padding="0.5mm"/>'
                "</style:style>"
            ),
        )

    def test_odf_create_table_cell_style_padding_some(self):
        style = create_table_cell_style(padding_top="0.6mm", padding_bottom="0.7mm")
        self.assertIn(
            style.serialize(),
            (
                (
                    "<style:style "
                    'style:family="table-cell"><style:table-cell-properties '
                    'fo:padding-top="0.6mm" fo:padding-left="none" fo:border="none" '
                    'fo:padding-right="none" fo:padding-bottom="0.7mm"/>'
                    "</style:style>"
                ),
                (
                    "<style:style "
                    'style:family="table-cell"><style:table-cell-properties '
                    'fo:border="none" fo:padding-bottom="0.7mm" '
                    'fo:padding-left="none" fo:padding-right="none" '
                    'fo:padding-top="0.6mm"/>'
                    "</style:style>"
                ),
            ),
        )


if __name__ == "__main__":
    main()
