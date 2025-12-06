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
# Authors: Hervé Cauwelier <herve@itaapy.com>
"""Header class for "text:h" tag."""

from __future__ import annotations

from re import sub
from typing import Any

from .element import PropDef, register_element_class
from .mixin_md import MDHeader
from .paragraph import Paragraph


class Header(Paragraph, MDHeader):
    """A title, a specialized paragraph, "text:h".

    Attributes:
        level (int): The outline level of the header. Level count begins at 1.
        text (str or None): The content of the header.
        restart_numbering (bool): If True, numbering restarts at this header level.
        start_value (int or None): The value at which to start numbering.
        suppress_numbering (bool): If True, no numbering for this header.
        style (str or None): The style name of the header.
    """

    _tag = "text:h"
    _properties = (
        PropDef("level", "text:outline-level"),
        PropDef("restart_numbering", "text:restart-numbering"),
        PropDef("start_value", "text:start-value"),
        PropDef("suppress_numbering", "text:suppress-numbering"),
    )

    def __init__(
        self,
        level: int = 1,
        text: str | None = None,
        restart_numbering: bool = False,
        start_value: int | None = None,
        suppress_numbering: bool = False,
        style: str | None = None,
        formatted: bool = True,
        **kwargs: Any,
    ) -> None:
        """Create a header element "text:h" of the given style and level, containing the
        optional given text.

        If "formatted" is True (the default), the given text is appended with <CR>,
        <TAB> and multiple spaces replaced by ODF corresponding tags.

        Args:
            level: The outline level of the header (starts at 1).
            text: The initial text content of the header.
            restart_numbering: If True, restart numbering at this level.
            start_value: The value at which to start numbering.
            suppress_numbering: If True, suppresses numbering for this header.
            style: The style name for the header.
            formatted: If True, replace special characters in `text` with ODF tags.
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.level = int(level)
            if text:
                if formatted:
                    self.text = ""
                    self.append_plain_text(text)
                else:
                    self.text = self._unformatted(text)
            if restart_numbering:
                self.restart_numbering = True
            if start_value is not None:
                self.start_value = start_value
            if suppress_numbering:
                self.suppress_numbering = True
            # if style:
            #     self.style = style

    def get_formatted_text(
        self,
        context: dict | None = None,
        simple: bool = False,
    ) -> str:
        if not context:
            context = {
                "document": None,
                "footnotes": [],
                "endnotes": [],
                "annotations": [],
                "rst_mode": False,
                "img_counter": 0,
                "images": [],
                "no_img_level": 0,
            }
        context["no_img_level"] += 1
        title = super().get_formatted_text(context)
        context["no_img_level"] -= 1
        title = title.strip()
        title = sub(r"\s+", " ", title)

        # No rst_mode ?
        if not context["rst_mode"]:
            return title
        # If here in rst_mode!

        # Get the level, max 5!
        LEVEL_STYLES = "#=-~`+^°'."
        level = int(self.level)
        if level > len(LEVEL_STYLES):
            raise ValueError("Too many levels of heading")

        # And return the result
        result = ["\n", title, "\n", LEVEL_STYLES[level - 1] * len(title), "\n"]
        return "".join(result)


Header._define_attribut_property()

register_element_class(Header)
