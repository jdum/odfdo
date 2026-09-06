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
"""Generate unique name series."""

from __future__ import annotations

DEFAULT_TABLE_NAME = "Sheet"


class NameUnifyer:
    """Class for enforcing a unique name series.

    Tracks already seen names and generates unique variations by appending
    a numeric suffix.
    """

    def __init__(self, base_name: str = DEFAULT_TABLE_NAME) -> None:
        """Initialize the NameUnifyer generator.

        Args:
            base_name: Default fallback name used when an empty name is
                provided.
        """
        self.seen: set[str] = set()
        self.base_name = base_name

    def unique(self, name: str = "") -> str:
        """Return a unique name based on the input name.

        If the name has already been registered or is empty, a unique name
        is generated and recorded in the seen set.

        Args:
            name: The candidate name to make unique.

        Returns:
            A unique name that has not been registered yet.
        """
        if name and name not in self.seen:
            self.seen.add(name)
            return name
        if not name:
            name = self.base_name
        if name in self.seen:
            counter = 2
        else:
            counter = 1
        new_name = f"{name}{counter}"
        while new_name in self.seen:
            counter += 1
            new_name = f"{name}{counter}"
        self.seen.add(new_name)
        return new_name
