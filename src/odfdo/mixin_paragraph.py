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
"""Mixin class for Paragraph methods."""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import TYPE_CHECKING, Any

from .annotation import Annotation, AnnotationEnd
from .bookmark import Bookmark, BookmarkEnd, BookmarkStart
from .element import (
    FIRST_CHILD,
    NEXT_SIBLING,
    Element,
    EText,
)
from .line_break import LineBreak
from .link import Link
from .note import Note
from .reference import Reference, ReferenceMark, ReferenceMarkEnd, ReferenceMarkStart
from .spacer import Spacer
from .tab import Tab

if TYPE_CHECKING:
    from .paragraph import Span

_re_splitter = re.compile(r"(\n|\t)")
_re_sub_splitter = re.compile(r"[ \t\n]+")
_re_spaces_split = re.compile(r"( +)")
_re_only_spaces = re.compile(r"^ +$")


def _by_offset_wrapper(
    method: Callable,
    element: Element,
    offset: int,
    *args: Any,
    **kwargs: Any,
) -> None:
    length = int(kwargs.get("length", 0))
    counted = 0
    for text in element.xpath("descendant::text()"):
        if len(text) + counted <= offset:  # type: ignore
            counted += len(text)  # type: ignore
            continue
        if length > 0:
            length = min(length, len(text))  # type: ignore
        else:
            length = len(text)  # type: ignore
        # Static information about the text node
        container = text.parent
        if container is None:
            continue
        upper = container.parent
        is_text = text.is_text()  # type: ignore
        start = offset - counted
        end = start + length
        # Do not use the text node as it changes at each loop
        if is_text:
            text_str = container.text or ""
        else:
            text_str = container.tail or ""
        before = text_str[:start]
        match = text_str[start:end]
        tail = text_str[end:]
        result = method(element, match, tail, *args, **kwargs)
        if is_text:
            container.text = before
            # Insert as first child
            container.insert(result, position=0)
        else:
            container.tail = before
            # Insert as next sibling
            if upper:
                index = upper.index(container)
                upper.insert(result, position=index + 1)


def _by_regex_wrapper(
    method: Callable,
    element: Element,
    regex: str,
    *args: Any,
    **kwargs: Any,
) -> None:
    pattern = re.compile(regex)
    for text in element.xpath("descendant::text()"):
        # Static information about the text node
        container = text.parent
        if container is None:
            continue
        upper = container.parent
        is_text = text.is_text()  # type: ignore
        # Group positions are calculated and static, so apply in
        # reverse order to preserve positions
        for group in reversed(list(pattern.finditer(text))):
            start, end = group.span()
            # Do not use the text node as it changes at each loop
            if is_text:
                text_str = container.text or ""
            else:
                text_str = container.tail or ""
            before = text_str[:start]
            match = text_str[start:end]
            tail = text_str[end:]
            result = method(element, match, tail, *args, **kwargs)
            if is_text:
                container.text = before
                # Insert as first child
                container.insert(result, position=0)
            else:
                container.tail = before
                # Insert as next sibling
                if upper:
                    index = upper.index(container)
                    upper.insert(result, position=index + 1)


def _by_regex_offset(method: Callable) -> Callable:
    @wraps(method)
    def wrapper(element: Element, *args: Any, **kwargs: Any) -> None:
        """Insert the result of method(element, ...) at the place matching the
        regex OR the positional arguments offset and length.

        Arguments:

            method -- wrapped method

            element -- self

            regex -- str, regular expression

            offset -- int

            length -- int
        """
        offset = kwargs.pop("offset", None)
        regex = kwargs.pop("regex", None)
        if offset is not None:
            return _by_offset_wrapper(
                method,
                element,
                int(offset),
                *args,
                **kwargs,
            )
        if regex:
            return _by_regex_wrapper(
                method,
                element,
                str(regex),
                *args,
                **kwargs,
            )

    return wrapper


class ParaMixin:
    """Mixin for Paragraph methods."""

    def _expand_spaces(self, added_string: str) -> list[Element | str]:
        result: list[Element | str] = []

        def _merge_text(txt: str):
            nonlocal result
            if result and isinstance(result[-1], str):
                result[-1] += txt
            else:
                result.append(txt)

        for obj in self.xpath("*|text()"):
            if isinstance(obj, EText):
                _merge_text(str(obj))
                continue
            obj.tail = ""
            if obj.tag != "text:s":
                result.append(obj)
                continue
            _merge_text(obj.text)
        _merge_text(added_string)
        return result

    def _merge_spaces(self, content: list[Element | str]) -> list[Element | str]:
        result: list[Element | str] = []
        for item in content:
            if isinstance(item, str):
                result.extend(self._sub_merge_spaces(item))
            else:
                result.append(item)
        return result

    @staticmethod
    def _sub_merge_spaces(text: str) -> list[Element | str]:
        result: list[Element | str] = []
        content = [x for x in _re_spaces_split.split(text) if x]

        def _merge_text(txt: str):
            nonlocal result
            if result and isinstance(result[-1], str):
                result[-1] += txt
            else:
                result.append(txt)

        if content:
            item0 = content[0]
            if isinstance(item0, str) and _re_only_spaces.match(item0):
                spacer = Spacer(len(item0))
                result.append(spacer)
            else:
                result.append(item0)
        for item in content[1:-1]:
            if isinstance(item, str):
                if len(item) > 1 and _re_only_spaces.match(item):
                    spacer = Spacer(len(item) - 1)
                    _merge_text(" ")
                    result.append(spacer)
                else:
                    _merge_text(item)
            else:
                result.append(item)
        if len(content) > 1:
            last_item = content[-1]
            if isinstance(last_item, str):
                if _re_only_spaces.match(last_item):
                    spacer = Spacer(len(last_item))
                    result.append(spacer)
                else:
                    _merge_text(last_item)
            else:
                result.append(last_item)
        return result

    def _replace_tabs_lb(self, content: list[Element | str]) -> list[Element | str]:
        result: list[Element | str] = []
        for item in content:
            if isinstance(item, str):
                result.extend(self._sub_replace_tabs_lb(item))
            else:
                result.append(item)
        return result

    @staticmethod
    def _sub_replace_tabs_lb(text: str) -> list[Element | str]:
        if not text:
            return []
        blocs = _re_splitter.split(text)
        result: list[Element | str] = []
        for bloc in blocs:
            if not bloc:
                continue
            if bloc == "\n":
                result.append(LineBreak())
                continue
            if bloc == "\t":
                result.append(Tab())
                continue
            result.append(bloc)
        return result

    def append_plain_text(self, text: str | bytes | None = "") -> None:
        """Append plain text to the paragraph, replacing <CR>, <TAB>
        and multiple spaces by ODF corresponding tags.
        """
        if text is None:
            stext = ""
        elif isinstance(text, bytes):
            stext = text.decode("utf-8")
        else:
            stext = str(text)
        content = self._expand_spaces(stext)
        content = self._merge_spaces(content)
        content = self._replace_tabs_lb(content)
        for child in self.children:
            self.delete(child, keep_tail=False)
        self.text = None
        for element in content:
            self._Element__append(element)

    @staticmethod
    def _unformatted(text: str | bytes | None) -> str:
        if not text:
            return ""
        if isinstance(text, bytes):
            stext = text.decode("utf-8")
        else:
            stext = str(text)
        return _re_sub_splitter.sub(" ", stext)

    def append(
        self,
        str_or_element: str | bytes | Element,
        formatted: bool = True,
    ) -> None:
        if isinstance(str_or_element, Element):
            if str_or_element.tag in {"text:p", "text:h", "text:s"}:
                # minimal compliancy or spacer summation
                self.append_plain_text(str(str_or_element))
                self.append_plain_text(str_or_element.tail)
            else:
                self._Element__append(str_or_element)
        elif formatted:
            self.append_plain_text(str_or_element)
        else:
            # self._Element__append(self._unformatted(str_or_element))
            # The added text is first "unformatted", but result needs
            # to be compliant
            self.append_plain_text(self._unformatted(str_or_element))

    def insert_note(
        self,
        note_element: Note | None = None,
        after: str | Element | None = None,
        note_class: str = "footnote",
        note_id: str | None = None,
        citation: str | None = None,
        body: str | None = None,
    ) -> None:
        if note_element is None:
            note_element = Note(
                note_class=note_class, note_id=note_id, citation=citation, body=body
            )
        else:
            # XXX clone or modify the argument?
            if note_class:
                note_element.note_class = note_class
            if note_id:
                note_element.note_id = note_id
            if citation:
                note_element.citation = citation
            if body:
                note_element.note_body = body
        note_element.check_validity()
        if isinstance(after, str):
            self._insert(note_element, after=after, main_text=True)
        elif isinstance(after, Element):
            after.insert(note_element, FIRST_CHILD)
        else:
            self.insert(note_element, FIRST_CHILD)

    def insert_annotation(
        self,
        annotation_element: Annotation | None = None,
        before: str | None = None,
        after: str | Element | None = None,
        position: int | tuple = 0,
        content: str | Element | None = None,
        body: str | None = None,
        creator: str | None = None,
        date: datetime | None = None,
    ) -> Annotation:
        """Insert an annotation, at the position defined by the regex (before,
        after, content) or by positionnal argument (position). If content is
        provided, the annotation covers the full content regex. Else, the
        annotation is positionned either 'before' or 'after' provided regex.

        If content is an odf element (ie: paragraph, span, ...), the full inner
        content is covered by the annotation (of the position just after if
        content is a single empty tag).

        If content/before or after exists (regex) and return a group of matching
        positions, the position value is the index of matching place to use.

        annotation_element can contain a previously created annotation, else
        the annotation is created from the body, creator and optional date
        (current date by default).

        Arguments:

            annotation_element -- Annotation or None

            before -- str regular expression or None

            after -- str regular expression or Element or None

            content -- str regular expression or None, or Element

            position -- int or tuple of int

            body -- str or Element

            creator -- str

            date -- datetime
        """

        if annotation_element is None:
            annotation_element = Annotation(
                text_or_element=body, creator=creator, date=date, parent=self
            )
        else:
            # XXX clone or modify the argument?
            if body:
                annotation_element.note_body = body
            if creator:
                annotation_element.creator = creator
            if date:
                annotation_element.date = date
        annotation_element.check_validity()

        # special case: content is an odf element (ie: a paragraph)
        if isinstance(content, Element):
            if content.is_empty():
                content.insert(annotation_element, xmlposition=NEXT_SIBLING)
                return annotation_element
            content.insert(annotation_element, start=True)
            annotation_end = AnnotationEnd(annotation_element)
            content.append(annotation_end)
            return annotation_element

        # special case
        if isinstance(after, Element):
            after.insert(annotation_element, FIRST_CHILD)
            return annotation_element

        # With "content" => automatically insert a "start" and an "end"
        # bookmark
        if (
            before is None
            and after is None
            and content is not None
            and isinstance(position, int)
        ):
            # Start tag
            self._insert(
                annotation_element, before=content, position=position, main_text=True
            )
            # End tag
            annotation_end = AnnotationEnd(annotation_element)
            self._insert(
                annotation_end, after=content, position=position, main_text=True
            )
            return annotation_element

        # With "(int, int)" =>  automatically insert a "start" and an "end"
        # bookmark
        if (
            before is None
            and after is None
            and content is None
            and isinstance(position, tuple)
        ):
            # Start
            self._insert(annotation_element, position=position[0], main_text=True)
            # End
            annotation_end = AnnotationEnd(annotation_element)
            self._insert(annotation_end, position=position[1], main_text=True)
            return annotation_element

        # Without "content" nor "position"
        if content is not None or not isinstance(position, int):
            raise ValueError("Bad arguments")

        # Insert
        self._insert(
            annotation_element,
            before=before,
            after=after,
            position=position,
            main_text=True,
        )
        return annotation_element

    def insert_annotation_end(
        self,
        annotation_element: Annotation,
        before: str | None = None,
        after: str | None = None,
        position: int = 0,
    ) -> AnnotationEnd:
        """Insert an annotation end tag for an existing annotation. If some end
        tag already exists, replace it. Annotation end tag is set at the
        position defined by the regex (before or after).

        If content/before or after (regex) returns a group of matching
        positions, the position value is the index of matching place to use.

        Arguments:

            annotation_element -- Annotation (mandatory)

            before -- str regular expression or None

            after -- str regular expression or None

            position -- int
        """

        if annotation_element is None:
            raise ValueError
        if not isinstance(annotation_element, Annotation):
            raise TypeError("Not a <office:annotation> Annotation")

        # remove existing end tag
        name = annotation_element.name
        existing_end_tag = self.get_annotation_end(name=name)
        if existing_end_tag:
            existing_end_tag.delete()

        # create the end tag
        end_tag = AnnotationEnd(annotation_element)

        # Insert
        self._insert(
            end_tag, before=before, after=after, position=position, main_text=True
        )
        return end_tag

    def set_reference_mark(
        self,
        name: str,
        before: str | None = None,
        after: str | None = None,
        position: int = 0,
        content: str | Element | None = None,
    ) -> Element:
        """Insert a reference mark, at the position defined by the regex
        (before, after, content) or by positionnal argument (position). If
        content is provided, the annotation covers the full range content regex
        (instances of ReferenceMarkStart and ReferenceMarkEnd are
        created). Else, an instance of ReferenceMark is positionned either
        'before' or 'after' provided regex.

        If content is an ODF Element (ie: Paragraph, Span, ...), the full inner
        content is referenced (of the position just after if content is a single
        empty tag).

        If content/before or after exists (regex) and return a group of matching
        positions, the position value is the index of matching place to use.

        Name is mandatory and shall be unique in the document for the preference
        mark range.

        Arguments:

            name -- str

            before -- str regular expression or None

            after -- str regular expression or None,

            content -- str regular expression or None, or Element

            position -- int or tuple of int

        Return: the created ReferenceMark or ReferenceMarkStart
        """
        # special case: content is an odf element (ie: a paragraph)
        if isinstance(content, Element):
            if content.is_empty():
                reference = ReferenceMark(name)
                content.insert(reference, xmlposition=NEXT_SIBLING)
                return reference
            reference_start = ReferenceMarkStart(name)
            content.insert(reference_start, start=True)
            reference_end = ReferenceMarkEnd(name)
            content.append(reference_end)
            return reference_start

        # With "content" => automatically insert a "start" and an "end"
        # reference
        if (
            before is None
            and after is None
            and content is not None
            and isinstance(position, int)
        ):
            # Start tag
            reference_start = ReferenceMarkStart(name)
            self._insert(
                reference_start, before=content, position=position, main_text=True
            )
            # End tag
            reference_end = ReferenceMarkEnd(name)
            self._insert(
                reference_end, after=content, position=position, main_text=True
            )
            return reference_start

        # With "(int, int)" =>  automatically insert a "start" and an "end"
        if (
            before is None
            and after is None
            and content is None
            and isinstance(position, tuple)
        ):
            # Start
            reference_start = ReferenceMarkStart(name)
            self._insert(reference_start, position=position[0], main_text=True)
            # End
            reference_end = ReferenceMarkEnd(name)
            self._insert(reference_end, position=position[1], main_text=True)
            return reference_start

        # Without "content" nor "position"
        if content is not None or not isinstance(position, int):
            raise ValueError("bad arguments")

        # Insert a positional reference mark
        reference = ReferenceMark(name)
        self._insert(
            reference,
            before=before,
            after=after,
            position=position,
            main_text=True,
        )
        return reference

    def set_reference_mark_end(
        self,
        reference_mark: Element,
        before: str | None = None,
        after: str | None = None,
        position: int = 0,
    ) -> ReferenceMarkEnd:
        """Insert/move a ReferenceMarkEnd for an existing reference mark. If
        some end tag already exists, replace it. Reference tag is set at the
        position defined by the regex (before or after).

        If content/before or after (regex) returns a group of matching
        positions, the position value is the index of matching place to use.

        Arguments:

            reference_mark -- ReferenceMark or ReferenceMarkStart (mandatory)

            before -- str regular expression or None

            after -- str regular expression or None

            position -- int
        """
        if not isinstance(reference_mark, (ReferenceMark, ReferenceMarkStart)):
            raise TypeError("Not a ReferenceMark or ReferenceMarkStart")
        name = reference_mark.name
        if isinstance(reference_mark, ReferenceMark):
            # change it to a range reference:
            reference_mark.tag = ReferenceMarkStart._tag

        existing_end_tag = self.get_reference_mark_end(name=name)
        if existing_end_tag:
            existing_end_tag.delete()

        # create the end tag
        end_tag = ReferenceMarkEnd(name)

        # Insert
        self._insert(
            end_tag, before=before, after=after, position=position, main_text=True
        )
        return end_tag

    def insert_variable(self, variable_element: Element, after: str | None) -> None:
        self._insert(variable_element, after=after, main_text=True)

    @_by_regex_offset
    def set_span(
        self,
        match: str,
        tail: str,
        style: str,
        regex: str | None = None,
        offset: int | None = None,
        length: int = 0,
    ) -> Span:
        """
        set_span(style, regex=None, offset=None, length=0)
        Apply the given style to text content matching the regex OR the
        positional arguments offset and length.

        (match, tail: provided by regex decorator)

        Arguments:

            style -- str

            regex -- str regular expression

            offset -- int

            length -- int
        """
        # span = Span(match, style=style)
        # span.tail = tail
        span: Span = Element.from_tag("text:span")
        span.text = ""
        span.append_plain_text(match)
        span.tail = tail
        span.style = style

        return span

    def remove_spans(self, keep_heading: bool = True) -> Element | list:
        """Send back a copy of the element, without span styles.
        If keep_heading is True (default), the first level heading style is left
        unchanged.
        """
        strip = ("text:span",)
        if keep_heading:
            protect = ("text:h",)
        else:
            protect = None
        return self.strip_tags(strip=strip, protect=protect)

    def remove_span(self, spans: Element | list[Element]) -> Element | list:
        """Send back a copy of the element, the spans (not a clone) removed.

        Arguments:

            spans -- Element or list of Element
        """
        return self.strip_elements(spans)

    @_by_regex_offset
    def set_link(
        self,
        match: str,
        tail: str,
        url: str,
        regex: str | None = None,
        offset: int | None = None,
        length: int = 0,
    ) -> Element:
        """
        set_link(url, regex=None, offset=None, length=0)
        Make a link to the provided url from text content matching the regex
        OR the positional arguments offset and length.

        (match, tail: provided by regex decorator)

        Arguments:

            url -- str

            regex -- str regular expression

            offset -- int

            length -- int
        """
        link = Link(url, text=match)
        link.tail = tail
        return link

    def remove_links(self) -> Element | list:
        """Send back a copy of the element, without links tags."""
        strip = (Link._tag,)
        return self.strip_tags(strip=strip)

    def remove_link(self, links: Link | list[Link]) -> Element | list:
        """Send back a copy of the element (not a clone), with the sub links
           removed.

        Arguments:

            links -- Link or list of Link
        """
        return self.strip_elements(links)

    def insert_reference(
        self,
        name: str,
        ref_format: str = "",
        before: str | None = None,
        after: str | Element | None = None,
        position: int = 0,
        display: str | None = None,
    ) -> None:
        """Create and insert a reference to a content marked by a reference
        mark. The Reference element ("text:reference-ref") represents a
        field that references a "text:reference-mark-start" or
        "text:reference-mark" element. Its "text:reference-format" attribute
        specifies what is displayed from the referenced element. Default is
        'page'. Actual content is not automatically updated except for the 'text'
        format.

        name is mandatory and should represent an existing reference mark of the
        document.

        ref_format is the argument for format reference (default is 'page').

        The reference is inserted the position defined by the regex (before /
        after), or by positionnal argument (position). If 'display' is provided,
        it will be used as the text value for the reference.

        If after is an ODF Element, the reference is inserted as first child of
        this element.

        Arguments:

            name -- str

            ref_format -- one of : 'chapter', 'direction', 'page', 'text',
                                    'caption', 'category-and-value', 'value',
                                    'number', 'number-all-superior',
                                    'number-no-superior'

            before -- str regular expression or None

            after -- str regular expression or odf element or None

            position -- int

            display -- str or None
        """
        reference = Reference(name, ref_format)
        if display is None and ref_format == "text":
            # get reference content
            body = self.document_body
            if not body:
                body = self.root
            mark = body.get_reference_mark(name=name)
            if mark:
                display = mark.referenced_text  # type: ignore
        if not display:
            display = " "
        reference.text = display
        if isinstance(after, Element):
            after.insert(reference, FIRST_CHILD)
        else:
            self._insert(
                reference, before=before, after=after, position=position, main_text=True
            )

    def set_bookmark(
        self,
        name: str,
        before: str | None = None,
        after: str | None = None,
        position: int | tuple = 0,
        role: str | None = None,
        content: str | None = None,
    ) -> Element | tuple[Element, Element]:
        """Insert a bookmark before or after the characters in the text which
        match the regex before/after. When the regex matches more of one part
        of the text, position can be set to choose which part must be used.
        If before and after are None, we use only position that is the number
        of characters.

        So, by default, this function inserts a bookmark before the first
        character of the content. Role can be None, "start" or "end", we
        insert respectively a position bookmark a bookmark-start or a
        bookmark-end.

        If content is not None these 2 calls are equivalent:

          paragraph.set_bookmark("bookmark", content="xyz")

        and:

          paragraph.set_bookmark("bookmark", before="xyz", role="start")
          paragraph.set_bookmark("bookmark", after="xyz", role="end")


        If position is a 2-tuple, these 2 calls are equivalent:

          paragraph.set_bookmark("bookmark", position=(10, 20))

        and:

          paragraph.set_bookmark("bookmark", position=10, role="start")
          paragraph.set_bookmark("bookmark", position=20, role="end")


        Arguments:

            name -- str

            before -- str regex

            after -- str regex

            position -- int or (int, int)

            role -- None, "start" or "end"

            content -- str regex
        """
        # With "content" => automatically insert a "start" and an "end"
        # bookmark
        if (
            before is None
            and after is None
            and role is None
            and content is not None
            and isinstance(position, int)
        ):
            # Start
            start = BookmarkStart(name)
            self._insert(start, before=content, position=position, main_text=True)
            # End
            end = BookmarkEnd(name)
            self._insert(end, after=content, position=position, main_text=True)
            return start, end

        # With "(int, int)" =>  automatically insert a "start" and an "end"
        # bookmark
        if (
            before is None
            and after is None
            and role is None
            and content is None
            and isinstance(position, tuple)
        ):
            # Start
            start = BookmarkStart(name)
            self._insert(start, position=position[0], main_text=True)
            # End
            end = BookmarkEnd(name)
            self._insert(end, position=position[1], main_text=True)
            return start, end

        # Without "content" nor "position"
        if content is not None or not isinstance(position, int):
            raise ValueError("bad arguments")

        # Role
        if role is None:
            bookmark: Element = Bookmark(name)
        elif role == "start":
            bookmark = BookmarkStart(name)
        elif role == "end":
            bookmark = BookmarkEnd(name)
        else:
            raise ValueError("bad arguments")

        # Insert
        self._insert(
            bookmark, before=before, after=after, position=position, main_text=True
        )

        return bookmark
