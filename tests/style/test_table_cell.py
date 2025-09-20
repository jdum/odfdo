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

from odfdo.style import create_table_cell_style, make_table_cell_border_string


def test_odf_create_table_cell_style():
    border = make_table_cell_border_string()
    style = create_table_cell_style(border=border)
    assert style.serialize() == (
        "<style:style "
        'style:family="table-cell"><style:table-cell-properties '
        'fo:border="0.06pt solid #000000"/></style:style>'
    )


def test_odf_create_table_cell_style_top():
    border = make_table_cell_border_string()
    style = create_table_cell_style(border_top=border)
    assert style.serialize() in (
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
    )


def test_odf_create_table_cell_style_bg():
    border = make_table_cell_border_string(color="blue")
    style = create_table_cell_style(border=border, background_color="green")
    assert style.serialize() in (
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
    )


def test_odf_create_table_cell_style_color():
    border = make_table_cell_border_string(color="blue")
    style = create_table_cell_style(border=border, color="yellow")
    assert style.serialize() == (
        "<style:style "
        'style:family="table-cell"><style:table-cell-properties '
        'fo:border="0.06pt solid #0000FF"/><style:text-properties '
        'fo:color="#FFFF00"/></style:style>'
    )


def test_odf_create_table_cell_style_all():
    border_left = make_table_cell_border_string(color="blue")
    border_right = make_table_cell_border_string(thick=60)
    style = create_table_cell_style(
        background_color="yellow",
        color=(128, 64, 32),
        border_left=border_left,
        border_right=border_right,
        padding_right="0.05pt",
    )
    assert style.serialize() in (
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
    )


def test_odf_create_table_cell_style_default_border():
    style = create_table_cell_style(border="default")
    assert style.serialize() == (
        "<style:style "
        'style:family="table-cell"><style:table-cell-properties '
        'fo:border="0.06pt solid #000000"/>'
        "</style:style>"
    )


def test_odf_create_table_cell_style_none_border():
    style = create_table_cell_style()
    assert style.serialize() == (
        "<style:style "
        'style:family="table-cell"><style:table-cell-properties '
        'fo:border="none"/>'
        "</style:style>"
    )


def test_odf_create_table_cell_style_padding():
    style = create_table_cell_style(padding="0.5mm")
    assert style.serialize() == (
        "<style:style "
        'style:family="table-cell"><style:table-cell-properties '
        'fo:border="none" fo:padding="0.5mm"/>'
        "</style:style>"
    )


def test_odf_create_table_cell_style_padding_some():
    style = create_table_cell_style(padding_top="0.6mm", padding_bottom="0.7mm")
    assert style.serialize() in (
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
    )
