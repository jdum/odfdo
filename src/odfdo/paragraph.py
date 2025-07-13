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
"""Paragraph class for "text:p" tag and PageBreak()."""

from __future__ import annotations

from typing import Any

from .element import (
    Element,
    PropDef,
    register_element_class,
)
from .line_break import LineBreak
from .mixin_md import MDParagraph
from .mixin_paragraph import ParaMixin
from .mixin_paragraph_formatted import ParaFormattedTextMixin
from .spacer import Spacer
from .span import Span
from .tab import Tab

__all__ = [
    "LineBreak",
    "PageBreak",
    "Paragraph",
    "Spacer",
    "Span",
    "Tab",
]


class Paragraph(MDParagraph, ParaFormattedTextMixin, ParaMixin, Element):
    """An ODF paragraph, "text:p".

    The "text:p" element represents a paragraph, which is
    the basic unit of text in an OpenDocument file.
    """

    _tag = "text:p"
    _properties: tuple[PropDef, ...] = (PropDef("style", "text:style-name"),)

    def __init__(
        self,
        text_or_element: str | bytes | Element | None = None,
        style: str | None = None,
        formatted: bool = True,
        **kwargs: Any,
    ):
        """
        Create a paragraph element "text:p" of the given style containing the
        pptional given text.

        If "formatted" is True (the default), the given text is appended with <CR>,
        <TAB> and multiple spaces replaced by ODF corresponding tags.

        Arguments:

            text -- str, bytes or Element

            style -- str

            formatted -- bool
        """
        super().__init__(**kwargs)
        if self._do_init:
            if isinstance(text_or_element, Element):
                self.append(text_or_element)
            else:
                self.text = ""
                if formatted:
                    self.append_plain_text(text_or_element)
                else:
                    self.append_plain_text(self._unformatted(text_or_element))
            if style is not None:
                self.style = style

    def __str__(self) -> str:
        # '\n' at the end slightly breaks compatibility, but is clearly better
        return self.inner_text + "\n"


Paragraph._define_attribut_property()


def PageBreak() -> Paragraph:
    """Return an empty paragraph with a manual page break.

    Using this function requires to register the page break style with:
        document.add_page_break_style()
    """
    return Paragraph("", style="odfdopagebreak")


register_element_class(Paragraph)
