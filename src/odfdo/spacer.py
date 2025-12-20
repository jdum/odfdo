# Copyright 2018-2025 Jérôme Dumonteil
# Copyright (c) 2009-2013 Ars Aperta, Itaapy, Pierlis, Talend.
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
"""Spacer class for "text:s" tag."""

from __future__ import annotations

from typing import Any

from .element import Element, PropDef, PropDefBool, register_element_class
from .mixin_md import MDSpacer


class Spacer(MDSpacer, Element):
    """Representation of several spaces, "text:s".

    This element shall be used to represent the second and all following " "
    (U+0020, SPACE) characters in a sequence of " " (U+0020, SPACE) characters.
    It's good practice to use this element only for the second and all
    following SPACE characters in a sequence, though it's not an error if
    the preceding character is not a white space.
    """

    _tag = "text:s"
    _properties: tuple[PropDef | PropDefBool, ...] = (PropDef("number", "text:c"),)

    def __init__(self, number: int | None = 1, **kwargs: Any) -> None:
        """Create a Spacer element, "text:s", representing several spaces.

        Args:
            number: The number of spaces. Defaults to 1.
        """
        super().__init__(**kwargs)
        if self._do_init:
            if number and number >= 2:
                self.number: str | None = str(number)
            else:
                self.number = None

    def __str__(self) -> str:
        return self.text

    @property
    def text(self) -> str:
        """Get the string representation of the spacer.

        Returns:
            str: A string composed of spaces, e.g., "   ".
        """
        return " " * self.length

    @text.setter
    def text(self, text: str | None) -> None:
        """Set the string value of the spacer, which updates its length.

        Args:
            text: The string to set.
        """
        if text is None:
            text = ""
        self.length = len(text)

    @property
    def length(self) -> int:
        """Get the number of spaces represented by the spacer.

        Returns:
            int: The number of spaces.
        """
        value = self._base_attrib_getter("text:c")
        if value is None:
            return 1  # minimum 1 space
        return int(value)

    @length.setter
    def length(self, value: int | None) -> None:
        """Set the number of spaces represented by the spacer.

        Args:
            value: The number of spaces to set. If None or less
                than 2, the `text:c` attribute is removed, defaulting to 1 space.
        """
        if value is None or int(value) < 2:
            self._base_attrib_setter("text:c", None)
        else:
            self._base_attrib_setter("text:c", int(value))


Spacer._define_attribut_property()

register_element_class(Spacer)
