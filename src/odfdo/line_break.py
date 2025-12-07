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
"""LineBreak class to "text:line-break" tag."""

from __future__ import annotations

from typing import Any

from .element import Element, register_element_class
from .mixin_md import MDLineBreak


class LineBreak(MDLineBreak, Element):
    """Representation of a line break, "text:line-break"."""

    _tag = "text:line-break"

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the LineBreak element.

        Args:
            **kwargs: Additional keyword arguments for the parent `Element` class.
        """
        super().__init__(**kwargs)

    def __str__(self) -> str:
        return "\n"

    @property
    def text(self) -> str:
        """Get the textual representation of the line break.

        Returns:
            str: Always returns a newline character ("\\n").
        """
        return "\n"

    @text.setter
    def text(self, text: str | None) -> None:
        pass


register_element_class(LineBreak)
