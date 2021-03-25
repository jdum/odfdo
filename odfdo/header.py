# Copyright 2018-2020 Jérôme Dumonteil
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
"""Header class for "text:h"
"""
from re import sub

from .paragraph import Paragraph
from .element import register_element_class


class Header(Paragraph):
    """Specialised paragraph for headings "text:h"."""

    _tag = "text:h"
    _properties = (
        ("level", "text:outline-level"),
        ("restart_numbering", "text:restart-numbering"),
        ("start_value", "text:start-value"),
        ("suppress_numbering", "text:suppress-numbering"),
    )

    def __init__(
        self,
        level=1,
        text=None,
        restart_numbering=False,
        start_value=None,
        suppress_numbering=False,
        style=None,
        **kwargs
    ):
        """Create a header element of the given style and level, containing the
        optional given text.

        Level count begins at 1.

        Arguments:

            level -- int

            text -- str

            restart_numbering -- bool

            start_value -- int

            style -- str

        Return: Header
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.level = int(level)
            if text:
                self.text = text
            if restart_numbering:
                self.restart_numbering = True
            if start_value:
                self.start_value = start_value
            if suppress_numbering:
                self.suppress_numbering = True
            if style:
                self.style = style

    def get_formatted_text(self, context=None, simple=False):
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
