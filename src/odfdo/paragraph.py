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
    PropDefBool,
    register_element_class,
)
from .line_break import LineBreak
from .mixin_link import LinkMixin
from .mixin_md import MDParagraph
from .mixin_paragraph import ParaMixin
from .mixin_paragraph_formatted import ParaFormattedTextMixin
from .note import NoteMixin
from .spacer import Spacer
from .span import Span
from .tab import Tab
from .user_field import UserDefinedMixin

__all__ = [
    "LineBreak",
    "PageBreak",
    "Paragraph",
    "Spacer",
    "Span",
    "Tab",
]


class Paragraph(
    MDParagraph,
    UserDefinedMixin,
    LinkMixin,
    ParaFormattedTextMixin,
    ParaMixin,
    NoteMixin,
    Element,
):
    """An ODF paragraph, "text:p".

    The "text:p" element represents a paragraph, which is the basic unit of
    text in an OpenDocument file.
    """

    _tag = "text:p"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("style", "text:style-name"),
    )

    def __init__(
        self,
        text_or_element: str | bytes | Element | None = None,
        style: str | None = None,
        formatted: bool = True,
        **kwargs: Any,
    ):
        """Initialize a Paragraph element (`text:p`).

        Args:
            text_or_element: Initial content for the paragraph.
                If a string/bytes, it's treated as plain text. If an `Element`, it's appended.
            style: The name of the style to apply to the paragraph.
            formatted: If True (default), special characters (`\\n`, `\\t`, multiple spaces)
                in `text_or_element` are converted to their ODF tag equivalents.
                If False, only extra whitespace is removed.
            **kwargs: Additional keyword arguments for the parent `Element` class.
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
        return self.inner_text + "\n"


Paragraph._define_attribut_property()


def PageBreak() -> Paragraph:
    """Create an empty paragraph configured for a manual page break.

    To properly render this page break, the document must have the
    "odfdopagebreak" style registered using `document.add_page_break_style()`.

    Returns:
        Paragraph: An empty `Paragraph` element with the "odfdopagebreak" style.
    """
    return Paragraph("", style="odfdopagebreak")


register_element_class(Paragraph)
