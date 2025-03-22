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

from odfdo.style import rgb2hex


def test_color_name():
    color = "violet"
    expected = "#EE82EE"
    assert rgb2hex(color) == expected


def test_color_tuple():
    color = (171, 205, 239)
    expected = "#ABCDEF"
    assert rgb2hex(color) == expected


def test_color_bad_name():
    color = "dark white"
    with pytest.raises(KeyError):
        rgb2hex(color)


def test_color_bad_tuple():
    # For alpha channel? ;-)
    color = (171, 205, 238, 128)
    with pytest.raises(ValueError):
        rgb2hex(color)


def test_color_bad_low_channel():
    color = (171, 205, -1)
    with pytest.raises(ValueError):
        rgb2hex(color)


def test_color_bad_high_channel():
    color = (171, 205, 256)
    with pytest.raises(ValueError):
        rgb2hex(color)


def test_color_bad_value():
    color = {}
    with pytest.raises(TypeError):
        rgb2hex(color)
