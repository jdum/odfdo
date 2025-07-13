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
from __future__ import annotations

from .css3_colormap import CSS3_COLORMAP


def hex2rgb(color: str) -> tuple[int, int, int]:
    """Convert "#RRGGBB" hexadecimal representation into (R, G, B) tuple.

    Arguments:

        color -- str

    Return: tuple
    """
    code = color[1:]
    if not (len(color) == 7 and color[0] == "#" and code.isalnum()):
        raise ValueError(f'"{color}" is not a valid color')
    red = int(code[:2], 16)
    green = int(code[2:4], 16)
    blue = int(code[4:6], 16)
    return (red, green, blue)


def rgb2hex(color: str | tuple[int, int, int]) -> str:
    """Convert color name or (R, G, B) tuple into "#RRGGBB" hexadecimal.

    Arguments:

        color -- str or tuple

    Return: str

    Examples::

        >>> rgb2hex('yellow')
        '#FFFF00'
        >>> rgb2hex((238, 130, 238))
        '#EE82EE'
    """
    if isinstance(color, str):
        try:
            code = CSS3_COLORMAP[color.lower()]
        except KeyError as e:
            raise KeyError(f'Color "{color}" is unknown in CSS color list') from e
    elif isinstance(color, tuple):
        if len(color) != 3:
            raise ValueError("Color must be a 3-tuple")
        code = color
    else:
        raise TypeError(f'Invalid color "{color}"')
    for channel in code:
        if not 0 <= channel <= 255:
            raise ValueError(
                f'Invalid color "{color}", channel must be between 0 and 255'
            )
    return f"#{code[0]:02X}{code[1]:02X}{code[2]:02X}"


def hexa_color(color: str | tuple[int, int, int] | None = None) -> str | None:
    """Safe conversion from color tuple or string to hexadecimal representation.

    Empty string is converted to black.
    None is converted to None.

    Arguments:

        color -- str or tuple or None

    Return: str or None
    """
    if color is None:
        return None
    if isinstance(color, tuple):
        return rgb2hex(color)
    if not isinstance(color, str):
        raise TypeError(f'Invalid color argument "{color!r}"')
    color = color.strip()
    if not color:
        return "#000000"
    if color.startswith("#"):
        return color
    return rgb2hex(color)
