# Copyright 2018-2026 Jérôme Dumonteil
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

from __future__ import annotations

from textwrap import dedent

from odfdo.utils.json_formater import format_json


def test_format_json_primitive():
    assert format_json(123) == "123"
    assert format_json(3.14) == "3.14"
    assert format_json("hello") == '"hello"'
    assert format_json(True) == "true"
    assert format_json(False) == "false"
    assert format_json(None) == "null"


def test_format_json_empty():
    assert format_json({}) == "{}"
    assert format_json([]) == "[]"


def test_format_json_1d_list():
    res = format_json(["a", 1, True, None])
    assert res == '["a", 1, true, null]'


def test_format_json_2d_list():
    data = [
        ["A", "B"],
        [1, 2],
    ]
    expected = dedent("""\
        [
          ["A", "B"],
          [1, 2]
        ]""")
    assert format_json(data, indent=2) == expected


def test_format_json_dict_matrix():
    data = {
        "Sheet1": [
            ["Name", "Country"],
            ["Alice", "USA"],
            ["Gaël", "France"],
        ]
    }
    expected = dedent("""\
        {
          "Sheet1": [
            ["Name", "Country"],
            ["Alice", "USA"],
            ["Gaël", "France"]
          ]
        }""")
    assert format_json(data, indent=2) == expected


def test_format_json_indent_4():
    data = {
        "Data": [
            [1, 2],
        ]
    }
    expected = dedent("""\
        {
            "Data": [
                [1, 2]
            ]
        }""")
    assert format_json(data, indent=4) == expected


def test_format_json_ensure_ascii():
    data = ["Gaël", "Français"]
    assert format_json(data, ensure_ascii=False) == '["Gaël", "Français"]'
    assert format_json(data, ensure_ascii=True) == '["Ga\\u00ebl", "Fran\\u00e7ais"]'
