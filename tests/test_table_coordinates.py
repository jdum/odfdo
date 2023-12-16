# Copyright 2018-2023 Jérôme Dumonteil
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
#          David Versmisse <david.versmisse@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>

import pytest

from odfdo.table import _alpha_to_digit, _convert_coordinates, _digit_to_alpha


def test_digit_to_alpha_to_digit():
    for i in range(1024):
        assert _alpha_to_digit(_digit_to_alpha(i)) == i


def test_alpha_to_digit_digit():
    assert _alpha_to_digit(730) == 730


def test_alpha_to_digit_digit_alphanum():
    pytest.raises(ValueError, _alpha_to_digit, "730")


def test_digit_to_alpha_digit():
    assert _digit_to_alpha("ABC") == "ABC"


def test_digit_to_alpha_alphanum():
    pytest.raises(TypeError, _digit_to_alpha, "730")


def test_convert_coordinates_tuple():
    x1, y1 = (12, 34)
    x2, y2 = _convert_coordinates((x1, y1))
    assert (x1, y1) == (x2, y2)


def test_convert_coordinates_tuple4():
    coord = (12, 34, 15, 60)
    converted = _convert_coordinates(coord)
    assert converted == coord


def test_convert_coordinates_alphanum():
    x, y = _convert_coordinates("ABC123")
    assert (x, y) == (730, 122)


def test_convert_coordinates_alphanum4():
    converted = _convert_coordinates("F7:ABC123")
    assert converted == (5, 6, 730, 122)


def test_convert_coordinates_alphanum4_2():
    converted = _convert_coordinates("f7:ABc123")
    assert converted == (5, 6, 730, 122)


def test_convert_coordinates_alphanum4_3():
    converted = _convert_coordinates("f7 : ABc 123 ")
    assert converted == (5, 6, 730, 122)


def test_convert_coordinates_alphanum4_4():
    converted = _convert_coordinates("ABC 123: F7 ")
    assert converted == (730, 122, 5, 6)


def test_convert_coordinates_bad():
    pytest.raises(TypeError, _convert_coordinates, None)
    assert _convert_coordinates((None,)) == (None,)
    assert _convert_coordinates((None, None)) == (None, None)
    assert _convert_coordinates((1, "bad")) == (1, "bad")


def test_convert_coordinates_bad_string():
    assert _convert_coordinates("2B") == (None, None)
    assert _convert_coordinates("$$$") == (None, None)
    assert _convert_coordinates("") == (None, None)


def test_convert_coordinates_std():
    assert _convert_coordinates("A1") == (0, 0)
    assert _convert_coordinates(" a 1 ") == (0, 0)
    assert _convert_coordinates(" aa 1 ") == (26, 0)


def test_convert_coordinates_assert():
    pytest.raises(ValueError, _convert_coordinates, "A0")
    pytest.raises(ValueError, _convert_coordinates, "A-5")


def test_convert_coordinates_big():
    assert _convert_coordinates("AAA200001") == (26 * 26 + 26, 200000)


def test_convert_coordinates_partial():
    assert _convert_coordinates("B") == (1, None)
    assert _convert_coordinates("2") == (None, 1)


def test_convert_coordinates_partial_4():
    assert _convert_coordinates("B3:D5") == (1, 2, 3, 4)
    assert _convert_coordinates("B3:") == (1, 2, None, None)
    assert _convert_coordinates(" B  3  :  ") == (1, 2, None, None)
    assert _convert_coordinates(":D5") == (None, None, 3, 4)
    assert _convert_coordinates("  :  D 5  ") == (None, None, 3, 4)
    assert _convert_coordinates("C:D") == (2, None, 3, None)
    assert _convert_coordinates(" : D ") == (None, None, 3, None)
    assert _convert_coordinates(" C :  ") == (2, None, None, None)
    assert _convert_coordinates("2 : 3 ") == (None, 1, None, 2)
    assert _convert_coordinates("2 :  ") == (None, 1, None, None)
    assert _convert_coordinates(" :3  ") == (None, None, None, 2)
    assert _convert_coordinates(" :  ") == (None, None, None, None)


def test_convert_coordinates_partial_bad_4():
    assert _convert_coordinates(" : $$$ ") == (None, None, None, None)
    assert _convert_coordinates(" B 3: $$$ ") == (1, 2, None, None)
