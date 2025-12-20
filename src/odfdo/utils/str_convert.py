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
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          Romain Gauthier <romain@itaapy.com>
"""String and byte conversion utilities.

This module provides simple helper functions for encoding strings to bytes
(UTF-8) and decoding bytes to strings.
"""

from __future__ import annotations

from typing import Any


def to_bytes(value: Any) -> Any:
    """Encodes a string to UTF-8 bytes if the input is a string.

    Args:
        value: The value to convert.

    Returns:
        Any: The encoded bytes if the input was a string, otherwise the
            original value.
    """
    if isinstance(value, str):
        return value.encode("utf-8")
    return value


def to_str(value: Any) -> Any:
    """Decodes a UTF-8 byte string to a string if the input is bytes.

    Args:
        value: The value to convert.

    Returns:
        Any: The decoded string if the input was bytes, otherwise the
            original value.
    """
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value


def str_to_bytes(text: str) -> bytes:
    """Encodes a string to UTF-8 bytes, replacing errors.

    Args:
        text: The string to encode.

    Returns:
        bytes: The resulting UTF-8 encoded bytes.
    """
    return text.encode("utf-8", "replace")


def bytes_to_str(text: bytes) -> str:
    """Decodes a UTF-8 byte string to a string, ignoring errors.

    Args:
        text: The byte string to decode.

    Returns:
        str: The resulting decoded string.
    """
    return text.decode("utf-8", "ignore")
