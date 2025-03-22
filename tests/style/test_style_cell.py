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

from odfdo.style import make_table_cell_border_string


def test_default_border():
    expected = "0.06pt solid #000000"
    assert make_table_cell_border_string() == expected


def test_border_bold():
    expected = "0.30pt solid #000000"
    assert make_table_cell_border_string(thick=0.3) == expected


def test_border_bold2():
    expected = "0.30pt solid #000000"
    assert make_table_cell_border_string(thick="0.30pt") == expected


def test_border_int():
    expected = "0.06pt solid #000000"
    assert make_table_cell_border_string(thick=6) == expected


def test_border_custom():
    expected = "0.1cm dotted #FF0000"
    result = make_table_cell_border_string(
        thick="0.1cm ",
        line=" dotted",
        color="#FF0000 ",
    )
    assert result == expected


def test_border_color_raise():
    arg = (None, None, "bug")
    pytest.raises(ValueError, make_table_cell_border_string, arg)


def test_border_color_name():
    expected = "0.06pt solid #D3D3D3"
    assert make_table_cell_border_string(color="lightgrey") == expected


def test_border_color_tuple():
    expected = "0.06pt solid #808080"
    assert make_table_cell_border_string(color=(128, 128, 128)) == expected
