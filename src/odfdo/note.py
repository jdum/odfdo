# Copyright 2018-2025 Jérôme Dumonteil
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
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
#          Romain Gauthier <romain@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
"""Note class for "text:note" tag."""

from __future__ import annotations

from typing import Any, ClassVar

from .annotation import Annotation, AnnotationEnd, get_unique_office_name  # noqa: F401
from .element import Element, PropDef, register_element_class
from .mixin_md import MDNote


class Note(MDNote, Element):
    """A note (footnote or endnote), "text:note".

    Either a footnote or a endnote element with the given text,
    optionally referencing it using the given note_id.
    """

    _tag = "text:note"
    _properties = (
        PropDef("note_class", "text:note-class"),
        PropDef("note_id", "text:id"),
    )
    NOTE_CLASS: ClassVar = {"footnote", "endnote"}

    def __init__(
        self,
        note_class: str = "footnote",
        note_id: str | None = None,
        citation: str | None = None,
        body: str | None = None,
        **kwargs: Any,
    ) -> None:
        """A note (footnote or endnote), "text:note".

        Arguments:

            note_class -- 'footnote' or 'endnote'

            note_id -- str

            citation -- str

            body -- str or Element
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.insert(Element.from_tag("text:note-body"), position=0)
            self.insert(Element.from_tag("text:note-citation"), position=0)
            self.note_class = note_class
            if note_id is not None:
                self.note_id = note_id
            if citation is not None:
                self.citation = citation
            if body is not None:
                self.note_body = body

    @property
    def citation(self) -> str:
        note_citation = self.get_element("text:note-citation")
        if note_citation:
            return note_citation.text
        return ""

    @citation.setter
    def citation(self, text: str | None) -> None:
        note_citation = self.get_element("text:note-citation")
        if note_citation:
            note_citation.text = text

    @property
    def note_body(self) -> str:
        note_body = self.get_element("text:note-body")
        if note_body:
            return note_body.text_content
        return ""

    @note_body.setter
    def note_body(self, text_or_element: Element | str | None) -> None:
        note_body = self.get_element("text:note-body")
        if not note_body:
            return None
        if text_or_element is None:
            note_body.text_content = ""
        elif isinstance(text_or_element, str):
            note_body.text_content = text_or_element
        elif isinstance(text_or_element, Element):
            note_body.clear()
            note_body.append(text_or_element)
        else:
            raise TypeError(f'Unexpected type for body: "{type(text_or_element)}"')

    def check_validity(self) -> None:
        if not self.note_class or self.note_class not in self.NOTE_CLASS:
            raise ValueError('Note class must be "footnote" or "endnote"')
        if not self.note_id:
            raise ValueError("Note must have an id")
        if not self.citation:
            raise ValueError("Note must have a citation")
        if not self.note_body:
            pass

    def __str__(self) -> str:
        if self.citation:
            return f"{self.citation}. {self.note_body}"
        return self.note_body


Note._define_attribut_property()

register_element_class(Note)
