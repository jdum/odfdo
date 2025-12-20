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

from typing import Any, ClassVar, Union, cast

from .annotation import Annotation, AnnotationEnd, get_unique_office_name  # noqa: F401
from .element import Element, PropDef, PropDefBool, register_element_class
from .mixin_link import LinkMixin
from .mixin_md import MDNote
from .mixin_toc import TocMixin
from .section import SectionMixin


class NoteMixin(Element):
    """Mixin class for classes containing Notes.

    Used by the following classes: "text:a", "text:h", "text:meta", "text:meta-field",
    "text:p", "text:ruby-base", "text:span". And with "office:text" for compatibility
    with previous versions.
    """

    def get_notes(
        self,
        note_class: str | None = None,
        content: str | None = None,
    ) -> list[Note]:
        """Retrieve all notes (`text:note`) that match the specified criteria.

        Args:
            note_class: Filter by note class ("footnote" or "endnote").
            content: A regular expression to match against the note's content.

        Returns:
            list[Note]: A list of `Note` instances matching the criteria.
        """
        return cast(
            list[Note],
            self._filtered_elements(
                "descendant::text:note", note_class=note_class, content=content
            ),
        )

    def get_note(
        self,
        position: int = 0,
        note_id: str | None = None,
        note_class: str | None = None,
        content: str | None = None,
    ) -> Note | None:
        """Retrieve a specific note (`text:note`) that matches the specified criteria.

        Args:
            position: The 0-based index of the matching note to retrieve if multiple match
                the other criteria. Defaults to 0.
            note_id: The unique ID of the note.
            note_class: Filter by note class ("footnote" or "endnote").
            content: A regular expression to match against the note's content.

        Returns:
            Note | None: A `Note` instance matching the criteria, or `None` if not found.
        """
        return cast(
            Union[None, Note],
            self._filtered_element(
                "descendant::text:note",
                position,
                text_id=note_id,
                note_class=note_class,
                content=content,
            ),
        )


class NoteBody(TocMixin, LinkMixin, SectionMixin):
    """Container for the content of a note, "text:note-body"."""

    _tag: str = "text:note-body"
    _properties: tuple[PropDef | PropDefBool, ...] = ()


class Note(MDNote, LinkMixin, Element):
    """A note (footnote or endnote), "text:note".

    Either a footnote or a endnote element with the given text, optionally
    referencing it using the given note_id.
    """

    _tag = "text:note"
    _properties: tuple[PropDef | PropDefBool, ...] = (
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
        """Initialize a Note element (footnote or endnote).

        Args:
            note_class: The class of the note ("footnote" or "endnote").
                Defaults to "footnote".
            note_id: A unique ID for the note. If None, one is generated.
            citation: The citation text for the note.
            body: The content of the note body. Can be a string or an `Element`.
            **kwargs: Additional keyword arguments for the parent `Element` class.
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
        """Get the text content of the note citation.

        Returns:
            str: The citation text, or an empty string if not found.
        """
        note_citation = self.get_element("text:note-citation")
        if note_citation:
            return note_citation.text
        return ""

    @citation.setter
    def citation(self, text: str | None) -> None:
        """Set the text content of the note citation.

        Args:
            text: The new citation text.
        """
        note_citation = self.get_element("text:note-citation")
        if note_citation:
            note_citation.text = text

    @property
    def note_body(self) -> str:
        """Get the text content of the note body.

        Returns:
            str: The content of the note body, or an empty string if not found.
        """
        note_body = self.get_element("text:note-body")
        if note_body:
            return note_body.text_content
        return ""

    @note_body.setter
    def note_body(self, text_or_element: Element | str | None) -> None:
        """Set the content of the note body.

        Args:
            text_or_element: The new content for the note body.
                Can be a string, an `Element`, or None to clear the content.
        """
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
        """Check the validity of the note's properties.

        Ensures that `note_class` is valid, and that `note_id` and `citation`
        are not empty.

        Raises:
            ValueError: If `note_class` is invalid, or if `note_id` or `citation` are empty.
        """
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
register_element_class(NoteBody)
