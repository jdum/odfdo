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

import pytest

from odfdo.style import Style


def test_table_cell_border():
    style = Style("table-cell", border="0.002cm")
    assert style.serialize() == (
        "<style:style "
        'style:family="table-cell"><style:table-cell-properties '
        'fo:border="0.002cm"/></style:style>'
    )


def test_table_cell_border_border_left():
    style = Style("table-cell", border="0.002cm", border_left="0.002cm")
    assert style.serialize() == (
        "<style:style "
        'style:family="table-cell"><style:table-cell-properties '
        'fo:border="0.002cm"/></style:style>'
    )


def test_table_cell_border_top():
    style = Style("table-cell", border_top="0.002cm")
    assert style.serialize() in (
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
    )


def test_table_cell_border_all():
    style = Style(
        "table-cell",
        border_top="0.001cm",
        border_right="0.002cm",
        border_bottom="0.003cm",
        border_left="0.004cm",
    )

    assert style.serialize() in (
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
    )


def test_table_cell_shadow():
    style = Style("table-cell", shadow="#808080 0.176cm 0.176cm")
    assert style.serialize() == (
        "<style:style "
        'style:family="table-cell"><style:table-cell-properties '
        'style:shadow="#808080 0.176cm 0.176cm"/></style:style>'
    )


def test_table_row_height():
    style = Style("table-row", height="5cm")
    assert style.serialize() == (
        "<style:style "
        'style:family="table-row"><style:table-row-properties '
        'style:row-height="5cm"/></style:style>'
    )


def test_table_column_width():
    style = Style("table-column", width="5cm")
    assert style.serialize() == (
        "<style:style "
        'style:family="table-column"><style:table-column-properties '
        'style:column-width="5cm"/></style:style>'
    )


def test_table_width():
    style = Style("table", "tab1", width="5cm")
    assert style.serialize() == (
        "<style:style "
        'style:family="table" '
        'style:name="tab1">'
        "<style:table-properties "
        'style:width="5cm"/>'
        "</style:style>"
    )


def test_table_width_align_left():
    style = Style("table", "tab1", width="5cm", align="left")
    assert style.serialize() == (
        "<style:style "
        'style:family="table" '
        'style:name="tab1">'
        "<style:table-properties "
        'style:width="5cm" '
        'table:align="left"/>'
        "</style:style>"
    )


def test_table_width_align_left_marge():
    style = Style("table", "tab1", width="5cm", align="left", margin_left="2cm")
    assert style.serialize() == (
        "<style:style "
        'style:family="table" '
        'style:name="tab1">'
        "<style:table-properties "
        'fo:margin-left="2cm" '
        'style:width="5cm" '
        'table:align="left"/>'
        "</style:style>"
    )


def test_table_align_wrong():
    with pytest.raises(ValueError):
        Style("table", "tab1", align="wrong")
