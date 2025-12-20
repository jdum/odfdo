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
"""Annotation class for "office:annotation" tag."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Union, cast

from .element import Element, PropDef, register_element_class
from .elements_between import elements_between
from .mixin_dc_creator import DcCreatorMixin
from .mixin_dc_date import DcDateMixin
from .mixin_link import LinkMixin
from .mixin_md import MDTail

if TYPE_CHECKING:
    from .body import Body


class AnnotationMixin(Element):
    """Mixin class for classes containing Annotations.

    Used by the following classes:
        - "table:covered-table-cell"
        - "table:table-cell"
        - "text:a"
        - "text:h"
        - "text:meta"
        - "text:meta-field"
        - "text:p"
        - "text:ruby-base"
        - "text:span"

    and "office:text", "office:spreadsheet" for compatibility with previous
    versions.
    """

    def get_annotations(
        self,
        creator: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        content: str | None = None,
    ) -> list[Annotation]:
        """Return all the annotations that match the criteria.

        Args:
            creator: The creator of the annotation.
            start_date: The start date for filtering.
            end_date: The end date for filtering.
            content: A regex to match in the content.

        Returns:
            list[Annotation]: A list of matching Annotation elements.
        """
        annotations: list[Annotation] = []
        for annotation in cast(
            list[Annotation],
            self._filtered_elements("descendant::office:annotation", content=content),
        ):
            if creator is not None and creator != annotation.dc_creator:
                continue
            date = annotation.date
            # date never None: recreated if missing
            if date is None:  # pragma: no cover
                continue
            if start_date is not None and date < start_date:
                continue
            if end_date is not None and date >= end_date:
                continue
            annotations.append(annotation)
        return annotations

    def get_annotation(
        self,
        position: int = 0,
        creator: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        content: str | None = None,
        name: str | None = None,
    ) -> Annotation | None:
        """Return the annotation that matches the criteria.

        Args:
            position: The position of the annotation to return.
            creator: The creator of the annotation.
            start_date: The start date for filtering.
            end_date: The end date for filtering.
            content: A regex to match in the content.
            name: The name of the annotation.

        Returns:
            Annotation or None: The matching Annotation element, or None if not found.
        """
        if name is not None:
            return cast(
                Union[None, Annotation],
                self._filtered_element(
                    "descendant::office:annotation", 0, office_name=name
                ),
            )
        annotations: list[Annotation] = cast(
            list[Annotation],
            self.get_annotations(
                creator=creator,
                start_date=start_date,
                end_date=end_date,
                content=content,
            ),
        )
        if not annotations:
            return None
        try:
            return annotations[position]
        except IndexError:
            return None

    def get_annotation_ends(self) -> list[AnnotationEnd]:
        """Return all the annotation ends.

        Returns:
            list[AnnotationEnd]: A list of AnnotationEnd elements.
        """
        return cast(
            list[AnnotationEnd],
            self._filtered_elements(
                "descendant::office:annotation-end",
            ),
        )

    def get_annotation_end(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> AnnotationEnd | None:
        """Return the annotation end that matches the criteria.

        Args:
            position: The position of the annotation end to return.
            name: The name of the annotation end.

        Returns:
            AnnotationEnd or None: The matching AnnotationEnd element, or
                None if not found.
        """
        return cast(
            Union[None, AnnotationEnd],
            self._filtered_element(
                "descendant::office:annotation-end", position, office_name=name
            ),
        )


def get_unique_office_name(element: Element | None = None) -> str:
    """Provide an autogenerated unique "office:name" for the document.

    Args:
        element: The element to which the annotation is related.

    Returns:
        str: A unique name.
    """
    if element is not None:
        body = element.document_body
    else:
        body = None
    if body:
        used = set(body.get_office_names())
    else:
        used = set()
    # unplugged current paragraph:
    if element is not None:
        used.update(element.get_office_names())
    indice = 1
    while True:
        name = f"__Fieldmark__lpod_{indice}"
        if name in used:
            indice += 1
            continue
        break
    return name


class Annotation(MDTail, LinkMixin, Element, DcCreatorMixin, DcDateMixin):
    """An annotation (private note), "office:annotation".

    This element contains the content of a comment or annotation, along with
    metadata such as the creator and date.

    Attributes:
        name (str): The unique name of the annotation.
        note_id (str): The ID of the note.
        creator (str): The creator of the annotation.
        date (datetime): The date of the annotation.
        note_body (str or Element): The body content of the annotation.
    """

    _tag = "office:annotation"
    _properties = (
        PropDef("name", "office:name"),
        PropDef("note_id", "text:id"),
    )

    def __init__(
        self,
        text_or_element: Element | str | None = None,
        creator: str | None = None,
        date: datetime | None = None,
        name: str | None = None,
        parent: Element | None = None,
        **kwargs: Any,
    ) -> None:
        """Create an Annotation element.

        An annotation is a private note, represented by "office:annotation".
        This element is credited to a creator and contains text content,
        optionally dated (current date by default).

        If 'name' is not provided and a 'parent' is given, the name will be
        autogenerated to be unique within the document.

        Args:
            text_or_element: The content of the annotation, which can be a
                string or another ODF element.
            creator: The name of the person who created the annotation.
            date: The date and time when the annotation was created. Defaults
                to the current time if not provided.
            name: A unique name for the annotation. If not provided, a unique
                name is generated.
            parent: The parent element to which this annotation will be
                associated for name generation.
        """
        # fixme : use offset
        # TODO allow paragraph and text styles
        super().__init__(**kwargs)

        if self._do_init:
            self.note_body = text_or_element
            if creator:
                self.creator = creator
            if date is None:
                date = datetime.now()
            self.date = date
            if not name:
                name = get_unique_office_name(parent)
            self.name = name

    @property
    def dc_creator(self) -> str | None:
        """Alias for self.creator property."""
        return self.creator

    @dc_creator.setter
    def dc_creator(self, creator: str) -> None:
        self.creator = creator

    @property
    def dc_date(self) -> datetime | None:
        """Alias for self.date property."""
        return self.date

    @dc_date.setter
    def dc_date(self, dtdate: datetime) -> None:
        self.date = dtdate

    @property
    def note_body(self) -> str:
        return self.text_content

    @note_body.setter
    def note_body(self, text_or_element: Element | str | None) -> None:
        if text_or_element is None:
            self.text_content = ""
        elif isinstance(text_or_element, str):
            self.text_content = text_or_element
        elif isinstance(text_or_element, Element):
            self.clear()
            self.append(text_or_element)
        else:
            raise TypeError(f'Unexpected type for body: "{type(text_or_element)}"')

    @property
    def start(self) -> Annotation:
        """Return self."""
        return self

    @property
    def end(self) -> AnnotationEnd | None:
        """Return the corresponding annotation-end tag or None."""
        name = self.name
        parent = self.parent
        if parent is None:  # pragma: nocover
            raise ValueError("Can't find end tag: no parent available")
        body: Body | Element = self.document_body or parent
        if hasattr(body, "get_annotation_end"):
            return cast(Union[None, AnnotationEnd], body.get_annotation_end(name=name))
        return None

    def get_annotated(
        self,
        as_text: bool = False,
        no_header: bool = True,
        clean: bool = True,
    ) -> Element | list | str | None:
        """Returns the annotated content from an annotation.

        If no content exists (e.g., single position annotation or if the
        annotation-end tag is not found), it returns an empty list or an
        empty string if 'as_text' is True.

        Args:
            as_text: If True, returns the text content as a string. Defaults
                to False.
            no_header: If True, converts 'text:h' elements to 'text:p'.
                Defaults to True.
            clean: If True, suppresses unwanted tags such as deletion marks.
                Defaults to True.

        Returns:
            Element | list | str | None: The content of the annotation, which
            can be a single element, a list of elements, a string, or None if
            the end tag is missing.
        """
        end = self.end
        if end is None:
            if as_text:
                return ""
            return None
        body: Body | Element = self.document_body or self.root
        return elements_between(
            body, self, end, as_text=as_text, no_header=no_header, clean=clean
        )

    def delete(self, child: Element | None = None, keep_tail: bool = True) -> None:
        """Delete the element from the XML tree.

        If a child element is provided, it is deleted. If no child is given,
        the annotation itself and its corresponding "annotation-end" tag
        (if it exists) are deleted.

        Args:
            child: The child element to delete. If None,
                the annotation itself is deleted. Defaults to None.
            keep_tail: This argument is not used in this context but is
                kept for compatibility. Defaults to True.
        """
        if child is not None:  # act like normal delete
            super().delete(child)
            return
        end = self.end
        if end:
            end.delete()
        # act like normal delete
        super().delete()

    def check_validity(self) -> None:
        if not self.note_body:
            raise ValueError("Annotation must have a body")
        if not self.dc_creator:
            raise ValueError("Annotation must have a creator")
        if not self.dc_date:
            self.dc_date = datetime.now()

    def __str__(self) -> str:
        return f"{self.note_body}\n{self.dc_creator} {self.dc_date}"


Annotation._define_attribut_property()


class AnnotationEnd(MDTail, Element):
    """End of annotation marker, "office:annotation-end".

    The "office:annotation-end" element is used to define the end of a text
    range that is being annotated, especially when the content spans across
    element boundaries. It must be preceded by an "office:annotation" element
    with the same 'office:name' attribute.

    If an "office:annotation-end" element does not have a matching preceding
    "office:annotation" element, it is ignored.

    Attributes:
        name (str): The name of the annotation this element is closing. This
                    name must match the 'office:name' of a preceding
                    "office:annotation" element.
    """

    _tag = "office:annotation-end"
    _properties = (PropDef("name", "office:name"),)

    def __init__(
        self,
        annotation: Annotation | None = None,
        name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create an AnnotationEnd element.

        This element marks the end of an annotation. It must be associated
        with an existing "office:annotation" element, either by passing the
        annotation object directly or by providing a matching name.

        Args:
            annotation: The "office:annotation" element
                that this "annotation-end" is closing. If provided, the 'name'
                attribute will be taken from this annotation.
            name: The name of the annotation to close. This is
                required if 'annotation' is not provided.
        """
        # fixme : use offset
        # TODO allow paragraph and text styles
        super().__init__(**kwargs)
        if self._do_init:
            if annotation:
                name = annotation.name
            if not name:
                raise ValueError("Annotation-end must have a name")
            self.name = name

    @property
    def start(self) -> Annotation | None:
        """Return the corresponding annotation starting tag or None."""
        name = self.name
        parent = self.parent
        if parent is None:
            raise ValueError(
                "Can't find start tag: no parent available"
            )  # pragma: nocover
        body: Body | Element = self.document_body or parent
        if hasattr(body, "get_annotation"):  # pragma: nocover
            return cast(Union[None, Annotation], body.get_annotation(name=name))
        return None  # pragma: nocover

    @property
    def end(self) -> AnnotationEnd:
        """Return self."""
        return self


AnnotationEnd._define_attribut_property()

register_element_class(Annotation)
register_element_class(AnnotationEnd)
