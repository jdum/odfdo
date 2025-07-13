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

import contextlib
from typing import Any

from .element import Element, PropDef, _get_lxml_tag, register_element_class
from .mixin_md import MDSpacer


class Spacer(MDSpacer, Element):
    """Representation of several spaces, "text:s".

    This element shall be used to represent the second and all following “ “
    (U+0020, SPACE) characters in a sequence of “ “ (U+0020, SPACE) characters.
    Note: It is not an error if the character preceding the element is not a
    white space character, but it is good practice to use this element only for
    the second and all following SPACE characters in a sequence.
    """

    _tag = "text:s"
    _properties: tuple[PropDef, ...] = (PropDef("number", "text:c"),)

    def __init__(self, number: int | None = 1, **kwargs: Any):
        """Representation of several spaces, "text:s".

        Arguments:

            number -- int
        """
        super().__init__(**kwargs)
        if self._do_init:
            if number and number >= 2:
                self.number = str(number)
            else:
                self.number = None

    def __str__(self) -> str:
        return self.text

    @property
    def text(self) -> str:
        """Get / set the text content of the element."""
        return " " * self.length

    @text.setter
    def text(self, text: str | None) -> None:
        if text is None:
            text = ""
        self.length = len(text)

    @property
    def length(self) -> int:
        name = _get_lxml_tag("text:c")
        value = self._Element__element.get(name)
        if value is None:
            return 1  # minimum 1 space
        return int(value)

    @length.setter
    def length(self, value: int | None) -> None:
        name = _get_lxml_tag("text:c")
        if value is None or value < 2:
            with contextlib.suppress(KeyError):
                del self._Element__element.attrib[name]
            return
        self._Element__element.set(name, str(value))


Spacer._define_attribut_property()

register_element_class(Spacer)
