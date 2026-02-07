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
"""Collection of utilities."""

from .blob import Blob
from .color import hex2rgb, hexa_color, rgb2hex
from .coordinates import (
    alpha_to_digit,
    convert_coordinates,
    digit_to_alpha,
    increment,
    translate_from_any,
)
from .formula import oooc_to_ooow
from .isiterable import isiterable
from .remove_tree import remove_tree
from .rfc3066 import is_RFC3066
from .str_convert import bytes_to_str, str_to_bytes, to_bytes, to_str
from .style_constants import (
    FALSE_FAMILY_MAP_REVERSE,
    FAMILY_MAPPING,
    FAMILY_ODF_STD,
    STYLES_TO_REGISTER,
    SUBCLASSED_STYLES,
)
from .xpath_query import make_xpath_query

__all__ = [
    "FALSE_FAMILY_MAP_REVERSE",
    "FAMILY_MAPPING",
    "FAMILY_ODF_STD",
    "STYLES_TO_REGISTER",
    "SUBCLASSED_STYLES",
    "Blob",
    "alpha_to_digit",
    "bytes_to_str",
    "convert_coordinates",
    "digit_to_alpha",
    "hex2rgb",
    "hexa_color",
    "increment",
    "is_RFC3066",
    "isiterable",
    "make_xpath_query",
    "oooc_to_ooow",
    "remove_tree",
    "rgb2hex",
    "str_to_bytes",
    "to_bytes",
    "to_str",
    "translate_from_any",
]
