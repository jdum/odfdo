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

from .element import Element, PropDef, PropDefBool, register_element_class
from .paragraph import Paragraph
from .section import SectionMixin


class IndexBody(SectionMixin):
    """Represents the "text:index-body" element, which contains the content of an index.

    This element is used for all types of indexes within an ODF document and
    holds the generated index content.
    """

    _tag: str = "text:index-body"
    _properties: tuple[PropDef | PropDefBool, ...] = ()


class IndexTitle(SectionMixin):
    """Represents the title of an index, "text:index-title".

    This element contains the title for an index, and its properties define
    how the title is displayed and protected.

    Attributes:
        name (str): The name of the index title.
        style (str): The style name applied to the index title.
        xml_id (str): A unique XML identifier.
        protected (bool): Indicates if the index title is protected.
        protection_key (str): The protection key if the title is protected.
        protection_key_digest_algorithm (str): The algorithm used for the protection key.
    """

    _tag = "text:index-title"
    _properties: tuple[PropDef | PropDefBool, ...] = (
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
        """Create an IndexTitle element.

        Args:
            name (str, optional): The name of the index title.
            style (str, optional): The style name for the index title.
            title_text (str, optional): The actual text content of the title.
            title_text_style (str, optional): The style name for the title text.
            xml_id (str, optional): A unique XML identifier for the title.
            **kwargs: Arbitrary keyword arguments for the Element base class.
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
        """Set the actual text content of the index title.

        Args:
            title_text (str): The text content to set for the title.
            title_text_style (str, optional): The style name for the title text.
        """
        title = Paragraph(title_text, style=title_text_style)
        self.append(title)


IndexTitle._define_attribut_property()


class IndexTitleTemplate(Element):
    """Represents a template style for an index title, "text:index-title-template".

    This element defines the styling for index titles within an ODF document.
    """

    _tag = "text:index-title-template"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("style", "text:style-name"),
    )

    def __init__(self, style: str | None = None, **kwargs: Any) -> None:
        """Create an IndexTitleTemplate element.

        Args:
            style (str, optional): The style name for the template.
            **kwargs: Arbitrary keyword arguments for the Element base class.
        """
        super().__init__(**kwargs)
        if self._do_init and style:
            self.style = style


IndexTitleTemplate._define_attribut_property()

register_element_class(IndexBody)
register_element_class(IndexTitle)
register_element_class(IndexTitleTemplate)
