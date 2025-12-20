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
"""Tab class for "text:tab" tag."""

from __future__ import annotations

from typing import Any

from .element import Element, PropDef, PropDefBool, register_element_class
from .mixin_md import MDTab


class Tab(MDTab, Element):
    """Representation of a tabulation, "text:tab".

    This element represents the [UNICODE] tab character (HORIZONTAL TABULATION,
    U+0009). The position attribute indicates the number of the tab-stop to
    which a tab character refers, where position 0 marks the start margin of
    a paragraph. Layout-oriented consumers should determine tab positions based
    on style information.
    """

    _tag = "text:tab"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("position", "text:tab-ref"),
    )

    def __init__(self, position: int | None = None, **kwargs: Any) -> None:
        """Create a tabulation element "text:tab".

        Args:
            position: The position of the tab-stop. If provided,
                must be a non-negative integer.
        """
        super().__init__(**kwargs)
        if self._do_init and position is not None and position >= 0:
            self.position = str(position)

    def __str__(self) -> str:
        return "\t"

    @property
    def text(self) -> str:
        """Get the text content, which is always a tab character.

        Returns:
            str: The tab character ("\t").
        """
        return "\t"

    @text.setter
    def text(self, text: str | None) -> None:
        """Setting text for a tab is a no-op as it always represents a tab character."""
        pass


Tab._define_attribut_property()

register_element_class(Tab)
