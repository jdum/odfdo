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
"""Color conversion utilities for ODF documents.

This module provides helper functions to convert between different color
representations commonly used in ODF files, such as hexadecimal, RGB tuples,
and CSS color names.
"""

from __future__ import annotations

from .css3_colormap import CSS3_COLORMAP


def hex2rgb(color: str) -> tuple[int, int, int]:
    """Convert a "#RRGGBB" hexadecimal color to an (R, G, B) tuple.

    Args:
        color: The hexadecimal color string (e.g., "#FF0000").

    Returns:
        tuple[int, int, int]: A tuple representing the RGB values.

    Raises:
        ValueError: If the input string is not a valid hexadecimal color.
    """
    code = color[1:]
    if not (len(color) == 7 and color[0] == "#" and code.isalnum()):
        raise ValueError(f'"{color}" is not a valid color')
    red = int(code[:2], 16)
    green = int(code[2:4], 16)
    blue = int(code[4:6], 16)
    return (red, green, blue)


def rgb2hex(color: str | tuple[int, int, int]) -> str:
    """Convert a color name or (R, G, B) tuple to a "#RRGGBB" hexadecimal string.

    Args:
        color: The color as a standard CSS color name (e.g., "yellow") or an
            RGB tuple (e.g., (238, 130, 238)).

    Returns:
        str: The hexadecimal representation of the color (e.g., "#FFFF00").

    Raises:
        KeyError: If the color name is unknown.
        ValueError: If the color tuple is invalid.
        TypeError: If the color argument is of an unsupported type.

    Examples:
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
    """Safely convert a color from a tuple or string to its hexadecimal representation.

    - An empty string is converted to black ("#000000").
    - None is returned as None.
    - A color name is converted to its hex value.
    - A hex value is returned as is.

    Args:
        color: The color representation to convert. Can be a color name, an
            RGB tuple, a hex string, or None.

    Returns:
        str | None: The hexadecimal color string, or None if the input was None.

    Raises:
        TypeError: If the color argument is of an unsupported type.
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
