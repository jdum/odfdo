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
"""Utility function to check for iterability.

This module provides a helper function to determine if an object is iterable,
with special handling for string and byte types.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def isiterable(instance: Any) -> bool:
    """Checks if an object is iterable, excluding strings and bytes.

    This function considers strings and bytes objects as non-iterable, which is
    often the desired behavior when handling collections of items that might
    also include simple text.

    Args:
        instance: The object to check.

    Returns:
        bool: True if the object is iterable (and not a string/bytes),
            False otherwise.
    """
    if isinstance(instance, (str, bytes)):
        return False
    return isinstance(instance, Iterable)
