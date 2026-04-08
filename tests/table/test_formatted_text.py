# Copyright 2018-2026 Jérôme Dumonteil
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
from __future__ import annotations

from unittest.mock import patch

from odfdo.cell import Cell
from odfdo.table import Table


def test_get_formatted_text_rst_empty_col_size_0():
    table = Table("Test")
    table.set_value("A1", "v1")
    table.set_value("B1", "")
    table.set_value("C1", "v3")
    # Manually clear B1
    row = table.get_row(0, clone=False)
    cell = row.get_cell(1, clone=False)
    cell.clear()
    txt = table.get_formatted_text(
        context={
            "rst_mode": True,
            "no_img_level": 0,
        }
    )
    assert "v1" in txt and "v3" in txt


def test_get_formatted_text_rst_min_size():
    table = Table("Test")
    # We need real_size > free_size.
    table.set_value("A1", "w" * 500)
    table.set_value("B1", "w" * 20)
    txt = table.get_formatted_text(
        context={
            "rst_mode": True,
            "no_img_level": 0,
        }
    )
    assert "word" in txt or "w" in txt


def test_get_formatted_text_empty_col():
    table = Table("TestTable")
    table.set_value("B1", "content")
    txt = table.get_formatted_text(
        context={
            "rst_mode": True,
            "no_img_level": 0,
        }
    )
    assert ".." in txt


def test_get_formatted_text_resize():
    table = Table("TestTable")
    long_content = "word" * 100
    table.set_value("A1", long_content)
    table.set_value("B1", "small")
    txt = table.get_formatted_text(
        context={
            "rst_mode": True,
            "no_img_level": 0,
        }
    )
    assert "word" in txt


def test_get_formatted_text_indent_list():
    table = Table("TestTable")
    table.set_value("A1", "- list item")
    table.set_value("B1", ".. another item")
    txt = table.get_formatted_text(
        context={
            "rst_mode": True,
            "no_img_level": 0,
        }
    )
    assert "- list item" in txt
    assert ".. another item" in txt


def test_get_formatted_text_rst_empty_col_size_0_final():
    table = Table("T")
    # A1 has value, B1 is empty, C1 has value
    table.set_value("A1", "v")
    table.set_value("C1", "v")
    # B1 is a real cell but empty
    table.set_cell("B1", Cell())
    txt = table.get_formatted_text(context={"rst_mode": True, "no_img_level": 0})
    assert "v" in txt


def test_get_formatted_text_edge_case():
    original_max = max

    def mock_max(*args, **kwargs):
        if len(args) == 2 and args[0] == 2 and args[1] == 0:
            return 0
        return original_max(*args, **kwargs)

    table = Table("T")
    table.set_value("A1", "v")
    table.set_value("B1", "")  # len 0
    # C1 to keep B1 column
    table.set_value("C1", "v")

    with patch("odfdo.table.max", side_effect=mock_max):
        txt = table.get_formatted_text(
            context={
                "rst_mode": True,
                "no_img_level": 0,
            }
        )
        assert "v" in txt
