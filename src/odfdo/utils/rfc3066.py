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
"""Language tag validation utility based on RFC 3066.

This module provides a function to validate language tags according to the
format defined in RFC 3066, which is commonly used for language identification
in ODF documents.
"""

from __future__ import annotations

from string import ascii_letters, digits


def is_RFC3066(lang: str) -> bool:
    """Checks if a string conforms to the RFC 3066 language tag format.

    Valid formats are "language" or "language-country", where "language" is a
    2 or 3-letter ASCII string, and "country" (and other subtags) are
    alphanumeric.

    Args:
        lang: The language tag string to validate.

    Returns:
        bool: True if the tag is valid, False otherwise.
    """

    def test_part1(part1: str) -> bool:
        if not 2 <= len(part1) <= 3:
            return False
        return all(x in ascii_letters for x in part1)

    def test_part2(part2: str) -> bool:
        return all(x in ascii_letters or x in digits for x in part2)

    if not lang or not isinstance(lang, str):
        return False
    if "-" not in lang:
        return test_part1(lang)
    parts = lang.split("-")
    if len(parts) > 3:
        return False
    if not test_part1(parts[0]):
        return False
    return all(test_part2(p) for p in parts[1:])
