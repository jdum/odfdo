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

from odfdo.style import hex2rgb


def test_color_low():
    color = "#012345"
    expected = (1, 35, 69)
    assert hex2rgb(color) == expected


def test_color_high():
    color = "#ABCDEF"
    expected = (171, 205, 239)
    assert hex2rgb(color) == expected


def test_color_lowercase():
    color = "#abcdef"
    expected = (171, 205, 239)
    assert hex2rgb(color) == expected


def test_color_bad_size():
    color = "#fff"
    with pytest.raises(ValueError):
        hex2rgb(color)


def test_color_bad_format():
    color = "978EAE"
    with pytest.raises(ValueError):
        hex2rgb(color)


def test_color_bad_hex():
    color = "#978EAZ"
    with pytest.raises(ValueError):
        hex2rgb(color)
