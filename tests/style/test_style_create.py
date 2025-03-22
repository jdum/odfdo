# Copyright 2018-2025 Jérôme Dumonteil
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

from odfdo.style import Style


def test_create_style_paragraph():
    style = Style("paragraph", "style1")
    # expected = ()
    assert style.serialize() in (
        ('<style:style style:family="paragraph" style:name="style1"/>'),
        ('<style:style style:name="style1" style:family="paragraph"/>'),
    )


def test_create_style_text():
    style = Style("text")
    expected = '<style:style style:family="text"/>'
    assert style.serialize() == expected


def test_create_style_graphic():
    style = Style("graphic")
    expected = '<style:style style:family="graphic"/>'
    assert style.serialize() == expected


def test_create_style_table():
    style = Style("table")
    expected = '<style:style style:family="table"/>'
    assert style.serialize() == expected


def test_create_style_table_column():
    style = Style("table-column")
    expected = '<style:style style:family="table-column"/>'
    assert style.serialize() == expected


def test_create_style_table_row():
    style = Style("table-row")
    expected = '<style:style style:family="table-row"/>'
    assert style.serialize() == expected


def test_create_style_table_cell():
    style = Style("table-cell")
    expected = '<style:style style:family="table-cell"/>'
    assert style.serialize() == expected


def test_create_style_section():
    style = Style("section")
    expected = '<style:style style:family="section"/>'
    assert style.serialize() == expected


def test_create_style_list():
    style = Style("list")
    expected = "<text:list-style/>"
    assert style.serialize() == expected


def test_create_style_outline():
    style = Style("outline")
    expected = "<text:outline-style/>"
    assert style.serialize() == expected


def test_create_style_page_layout():
    style = Style("page-layout")
    expected = "<style:page-layout/>"
    assert style.serialize() == expected


def test_create_style_master_page():
    style = Style("master-page")
    expected = "<style:master-page/>"
    assert style.serialize() == expected


def test_create_style_display_name():
    style = Style("paragraph", display_name="Heading 1")
    expected = '<style:style style:family="paragraph" style:display-name="Heading 1"/>'
    assert style.serialize() == expected


def test_create_style_parent():
    style = Style("paragraph", parent_style="Heading 1")
    expected = (
        '<style:style style:family="paragraph" style:parent-style-name="Heading 1"/>'
    )
    assert style.serialize() == expected


def test_create_style_properties():
    style = Style("paragraph", **{"fo:margin-top": "0cm"})
    expected = (
        '<style:style style:family="paragraph">'
        '<style:paragraph-properties fo:margin-top="0cm"/>'
        "</style:style>"
    )
    assert style.serialize() == expected


def test_create_style_properties_shorcut():
    style = Style("paragraph", area="text", color="#ff0000")
    expected = (
        '<style:style style:family="paragraph">'
        '<style:text-properties fo:color="#ff0000"/>'
        "</style:style>"
    )
    # <style:style style:family="paragraph"/>
    assert style.serialize() == expected
