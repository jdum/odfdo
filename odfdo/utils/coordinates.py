# Copyright 2018-2024 Jérôme Dumonteil
# Copyright (c) 2009-2012 Ars Aperta, Itaapy, Pierlis, Talend.
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
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          Romain Gauthier <romain@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
from __future__ import annotations

from .isiterable import isiterable


def translate_from_any(x: str | int, length: int, idx: int) -> int:
    if isinstance(x, str):
        value_int = convert_coordinates(x)[idx]
        if value_int is None:
            raise TypeError(f"Wrong value: {x!r}")
    elif isinstance(x, int):
        value_int = x
    else:
        raise TypeError(f"Wrong value: {x!r}")
    if value_int < 0:
        return increment(value_int, length)
    return value_int


def alpha_to_digit(alpha: str) -> int:
    """Translates A to 0, B to 1, etc. So "AB" is value 27."""
    if isinstance(alpha, int):
        return alpha
    if not alpha.isalpha():
        raise ValueError(f'column name "{alpha}" is malformed')
    column = 0
    for c in alpha.lower():
        v = ord(c) - ord("a") + 1
        column = column * 26 + v
    return column - 1


def digit_to_alpha(digit: int | str) -> str:
    if isinstance(digit, str) and digit.isalpha():
        return digit
    if not isinstance(digit, int):
        raise TypeError(f'column number "{digit}" is invalid')
    digit += 1
    column = ""
    while digit:
        column = chr(65 + ((digit - 1) % 26)) + column
        digit = (digit - 1) // 26
    return column


# def _coordinates_to_alpha_area(coord: str | tuple | list) -> tuple[str, str, str]:
#     # assuming : either (x,y) or (x,y,z,t), with positive values
#     if isinstance(coord, str):
#         # either A1 or A1:B2, returns A1:A1 if needed
#         parts = coord.strip().split(":")
#         if len(parts) == 1:
#             start = end = parts[0]
#         else:
#             start = parts[0]
#             end = parts[1]
#     elif isiterable(coord):
#         if len(coord) == 2:
#             x, y = coord
#             z, t = coord
#         else:
#             # should be 4 int
#             x, y, z, t = coord
#         start = digit_to_alpha(x) + str(y + 1)
#         end = digit_to_alpha(z) + str(t + 1)
#     else:
#         raise ValueError
#     crange = start + ":" + end
#     return (start, end, crange)


def increment(value: int, step: int) -> int:
    while value < 0:
        if step == 0:
            return 0
        value += step
    return value


def convert_coordinates(
    obj: tuple | list | str,
) -> tuple[int | None, ...]:
    """Translates "D3" to (3, 2) or return (1, 2) untouched.
    Translates "A1:B3" to (0,0,1,2)
    """
    # By (1, 2) ?
    if isiterable(obj):
        return tuple(obj)  # type:ignore
    # Or by 'B3' notation ?
    if not isinstance(obj, str):
        raise TypeError(f'Bad coordinates type: "{type(obj)}"')
    coordinates = []
    for coord in [x.strip() for x in obj.split(":", 1)]:
        # First "A"
        alpha = ""
        for c in coord:
            if c.isalpha():
                alpha += c
            else:
                break
        try:
            column = alpha_to_digit(alpha)
        except ValueError:
            # raise ValueError, 'coordinates "%s" malformed' % obj
            # maybe '1:4' table row coordinates
            column = None
        coordinates.append(column)
        # Then "1"
        try:
            line = int(coord[len(alpha) :]) - 1
        except ValueError:
            # raise ValueError, 'coordinates "%s" malformed' % obj
            # maybe 'A:C' row coordinates
            line = None
        if line and line <= 0:
            raise ValueError(f'Coordinates "{obj}" malformed')
        coordinates.append(line)
    return tuple(coordinates)
