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
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>

import pytest

from odfdo.utils import (
    alpha_to_digit,
    convert_coordinates,
    digit_to_alpha,
    translate_from_any,
)


def test_digit_toalpha_to_digit():
    for i in range(1024):
        assert alpha_to_digit(digit_to_alpha(i)) == i


def testalpha_to_digit_digit():
    assert alpha_to_digit(730) == 730


def testalpha_to_digit_digit_alphanum():
    pytest.raises(ValueError, alpha_to_digit, "730")


def testdigit_to_alpha_digit():
    assert digit_to_alpha("ABC") == "ABC"


def testdigit_to_alpha_alphanum():
    pytest.raises(TypeError, digit_to_alpha, "730")


def testconvert_coordinates_tuple():
    x1, y1 = (12, 34)
    x2, y2 = convert_coordinates((x1, y1))
    assert (x1, y1) == (x2, y2)


def testconvert_coordinates_tuple4():
    coord = (12, 34, 15, 60)
    converted = convert_coordinates(coord)
    assert converted == coord


def testconvert_coordinates_alphanum():
    x, y = convert_coordinates("ABC123")
    assert (x, y) == (730, 122)


def testconvert_coordinates_alphanum4():
    converted = convert_coordinates("F7:ABC123")
    assert converted == (5, 6, 730, 122)


def testconvert_coordinates_alphanum4_2():
    converted = convert_coordinates("f7:ABc123")
    assert converted == (5, 6, 730, 122)


def testconvert_coordinates_alphanum4_3():
    converted = convert_coordinates("f7 : ABc 123 ")
    assert converted == (5, 6, 730, 122)


def testconvert_coordinates_alphanum4_4():
    converted = convert_coordinates("ABC 123: F7 ")
    assert converted == (730, 122, 5, 6)


def testconvert_coordinates_bad():
    pytest.raises(TypeError, convert_coordinates, None)
    assert convert_coordinates((None,)) == (None,)
    assert convert_coordinates((None, None)) == (None, None)
    assert convert_coordinates((1, "bad")) == (1, "bad")


def testconvert_coordinates_bad_string():
    assert convert_coordinates("2B") == (None, None)
    assert convert_coordinates("$$$") == (None, None)
    assert convert_coordinates("") == (None, None)


def testconvert_coordinates_std():
    assert convert_coordinates("A1") == (0, 0)
    assert convert_coordinates(" a 1 ") == (0, 0)
    assert convert_coordinates(" aa 1 ") == (26, 0)


def testconvert_coordinates_assert():
    pytest.raises(ValueError, convert_coordinates, "A0")
    pytest.raises(ValueError, convert_coordinates, "A-5")


def testconvert_coordinates_big():
    assert convert_coordinates("AAA200001") == (26 * 26 + 26, 200000)


def testconvert_coordinates_partial():
    assert convert_coordinates("B") == (1, None)
    assert convert_coordinates("2") == (None, 1)


def testconvert_coordinates_partial_4():
    assert convert_coordinates("B3:D5") == (1, 2, 3, 4)
    assert convert_coordinates("B3:") == (1, 2, None, None)
    assert convert_coordinates(" B  3  :  ") == (1, 2, None, None)
    assert convert_coordinates(":D5") == (None, None, 3, 4)
    assert convert_coordinates("  :  D 5  ") == (None, None, 3, 4)
    assert convert_coordinates("C:D") == (2, None, 3, None)
    assert convert_coordinates(" : D ") == (None, None, 3, None)
    assert convert_coordinates(" C :  ") == (2, None, None, None)
    assert convert_coordinates("2 : 3 ") == (None, 1, None, 2)
    assert convert_coordinates("2 :  ") == (None, 1, None, None)
    assert convert_coordinates(" :3  ") == (None, None, None, 2)
    assert convert_coordinates(" :  ") == (None, None, None, None)


def testconvert_coordinates_partial_bad_4():
    assert convert_coordinates(" : $$$ ") == (None, None, None, None)
    assert convert_coordinates(" B 3: $$$ ") == (1, 2, None, None)


def test_translate_from_any_1():
    result = translate_from_any(42, 0, 0)
    assert result == 42


def test_translate_from_any_2():
    result = translate_from_any("42", 0, 1)
    assert result == 41


def test_translate_from_any_3():
    with pytest.raises(TypeError):
        translate_from_any("//42", 0, 1)


def test_translate_from_any_4():
    with pytest.raises(TypeError):
        translate_from_any([], 0, 1)
