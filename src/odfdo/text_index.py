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
"""Classes IndexBody and IndexTitle, mostly used in TOC."""

from __future__ import annotations

from typing import Any

from .element import Element, PropDef, register_element_class
from .paragraph import Paragraph


class IndexBody(Element):
    """The "text:index-body" element contains an index.

    The "text:index-body" element is used for all types of indexes. It contains the index content generated to form the index."""

    _tag: str = "text:index-body"
    _properties: tuple[PropDef, ...] = ()


class IndexTitle(Element):
    """The title of an index, "text:index-title".

    The element has the following attributes:
    text:name, text:protected, text:protection-key,
    text:protection-key-digest-algorithm, text:style-name, xml:id.

    The actual title is stored in a child element
    """

    _tag = "text:index-title"
    _properties = (
        PropDef("name", "text:name"),
        PropDef("style", "text:style-name"),
        PropDef("xml_id", "xml:id"),
        PropDef("protected", "text:protected"),
        PropDef("protection_key", "text:protection-key"),
        PropDef(
            "protection_key_digest_algorithm", "text:protection-key-digest-algorithm"
        ),
    )

    def __init__(
        self,
        name: str | None = None,
        style: str | None = None,
        title_text: str | None = None,
        title_text_style: str | None = None,
        xml_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create title of an index "text:index-title".

        The element has the following attributes:
        text:name, text:protected, text:protection-key,
        text:protection-key-digest-algorithm, text:style-name, xml:id.

        The actual title is stored in a child element
        """
        super().__init__(**kwargs)
        if self._do_init:
            if name:
                self.name = name
            if style:
                self.style = style
            if xml_id:
                self.xml_id = xml_id
            if title_text:
                self.set_title_text(title_text, title_text_style)

    def set_title_text(
        self,
        title_text: str,
        title_text_style: str | None = None,
    ) -> None:
        title = Paragraph(title_text, style=title_text_style)
        self.append(title)


IndexTitle._define_attribut_property()


register_element_class(IndexTitle)
register_element_class(IndexBody)
