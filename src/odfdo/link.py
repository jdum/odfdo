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
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
"""Link class for "text:a" tag."""

from __future__ import annotations

from typing import Any

from .element import Element, PropDef, register_element_class
from .mixin_md import MDLink
from .mixin_paragraph_formatted import ParaFormattedTextMixin


class Link(MDLink, ParaFormattedTextMixin, Element):
    """Representation of a link (URL), "text:a"."""

    _tag = "text:a"
    _properties: tuple[PropDef, ...] = (
        PropDef("url", "xlink:href"),
        PropDef("name", "office:name"),
        PropDef("title", "office:title"),
        PropDef("target_frame", "office:target-frame-name"),
        PropDef("show", "xlink:show"),
        PropDef("visited_style", "text:visited-style-name"),
        PropDef("style", "text:style-name"),
    )

    def __init__(
        self,
        url: str | None = "",
        name: str | None = None,
        title: str | None = None,
        text: str | None = None,
        target_frame: str | None = None,
        style: str | None = None,
        visited_style: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Representation of a link (URL), "text:a".

        Arguments:

            url -- str

            name -- str

            title -- str

            text -- str

            target_frame -- '_self', '_blank', '_parent', '_top'

            style -- str

            visited_style -- str
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.url = url
            if name is not None:
                self.name = name
            if title is not None:
                self.title = title
            if text is not None:
                self.text = text
            if target_frame is not None:
                self.target_frame = target_frame
                # show can be: 'new' or 'replace'"
                if target_frame == "_blank":
                    self.show = "new"
                else:
                    self.show = "replace"
            if style is not None:
                self.style = style
            if visited_style is not None:
                self.visited_style = visited_style

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} tag={self.tag} link={self.url}>"

    def __str__(self) -> str:
        text = self.inner_text.strip()
        if text:
            return f"[{text}]({self.url})"
        return f"({self.url})"


Link._define_attribut_property()

register_element_class(Link)
