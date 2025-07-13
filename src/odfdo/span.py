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
"""Span class for "text:span" tag."""

from __future__ import annotations

from typing import Any

from .element import (
    Element,
    PropDef,
    register_element_class,
)
from .mixin_md import MDParagraph, MDSpan
from .mixin_paragraph import ParaMixin
from .mixin_paragraph_formatted import ParaFormattedTextMixin


class Span(MDSpan, MDParagraph, ParaFormattedTextMixin, ParaMixin, Element):
    """A span tag (syled text in paragraph), "text:span"."""

    _tag = "text:span"
    _properties = (
        PropDef("style", "text:style-name"),
        PropDef("class_names", "text:class-names"),
    )

    def __init__(
        self,
        text: str | None = None,
        style: str | None = None,
        formatted: bool = True,
        **kwargs: Any,
    ) -> None:
        """Create a span element "text:span" of the given style containing the optional
        given text.

        If "formatted" is True (the default), the given text is appended with <CR>,
        <TAB> and multiple spaces replaced by ODF corresponding tags.

        Arguments:

            text -- str

            style -- str

            formatted -- bool
        """
        super().__init__(**kwargs)
        if self._do_init:
            if text:
                if formatted:
                    self.text = ""
                    self.append_plain_text(text)
                else:
                    self.text = self._unformatted(text)
            if style:
                self.style = style

    def __str__(self) -> str:
        return self.inner_text


Span._define_attribut_property()

register_element_class(Span)
