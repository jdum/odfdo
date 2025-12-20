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

from .annotation import Annotation, AnnotationEnd, AnnotationMixin
from .bookmark import Bookmark, BookmarkEnd, BookmarkMixin, BookmarkStart
from .element import (
    FIRST_CHILD,
    NEXT_SIBLING,
    Element,
    EText,
)
from .element_strip import strip_elements, strip_tags
from .line_break import LineBreak
from .link import Link
from .note import Note
from .reference import (
    Reference,
    ReferenceMark,
    ReferenceMarkEnd,
    ReferenceMarkStart,
    ReferenceMixin,
)
from .spacer import Spacer
from .tab import Tab

if TYPE_CHECKING:
    from .body import Body
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
) -> list[Span | Link]:
    """Helper for inserting elements by character offset.

    This function wraps a method that creates a new element (like Span or Link)
    and inserts it into the XML tree at a specific character offset within
    the text content of the `element`.

    Args:
        method: The function that creates the new element.
        element: The parent element whose text content is being modified.
        offset: The character offset at which to perform the insertion.
        *args: Positional arguments to pass to the wrapped method.
        **kwargs: Keyword arguments to pass to the wrapped method,
            including 'length' for the matched string length.

    Returns:
        list[Span | Link]: A list of the newly created elements.
    """
    result: list[Span | Link] = []
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
        match_string = text_str[start:end]
        tail = text_str[end:]
        target = method(element, *args, match_string=match_string, **kwargs)
        target.tail = tail
        if is_text:
            container.text = before
            # Insert as first child
            container.insert(target, position=0)
        else:
            container.tail = before
            # Insert as next sibling
            if upper:
                index = upper.index(container)
                upper.insert(target, position=index + 1)
        result.append(target)
    return result


def _by_regex_wrapper(
    method: Callable,
    element: Element,
    regex: str,
    *args: Any,
    **kwargs: Any,
) -> list[Span | Link]:
    """Helper for inserting elements by regular expression match.

    This function wraps a method that creates a new element (like Span or Link)
    and inserts it into the XML tree at positions matching a given regular
    expression within the text content of the `element`.

    Args:
        method: The function that creates the new element.
        element: The parent element whose text content is being modified.
        regex: The regular expression pattern to match.
        *args: Positional arguments to pass to the wrapped method.
        **kwargs: Keyword arguments to pass to the wrapped method.

    Returns:
        list[Span | Link]: A list of the newly created elements.
    """
    result: list[Span | Link] = []
    if not regex:
        return result
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
        for group in reversed(list(pattern.finditer(str(text)))):
            start, end = group.span()
            # Do not use the text node as it changes at each loop
            if is_text:
                text_str = container.text or ""
            else:
                text_str = container.tail or ""
            before = text_str[:start]
            match_string = text_str[start:end]
            tail = text_str[end:]
            target = method(element, *args, match_string=match_string, **kwargs)
            target.tail = tail
            if is_text:
                container.text = before
                # Insert as first child
                container.insert(target, position=0)
            else:
                container.tail = before
                # Insert as next sibling
                if upper:
                    index = upper.index(container)
                    upper.insert(target, position=index + 1)
            result.append(target)
    return result


def _by_regex_offset(method: Callable) -> Callable:
    """Decorator to enable element insertion by regex or offset.

    This decorator wraps a method that creates a new element. The wrapped method
    will then accept either a `regex` pattern or an `offset` and `length` to
    specify where the new element should be inserted within the text content.

    Args:
        method: The function that creates the new element. It will
            receive `element`, `*args`, and `match_string` as keyword argument.

    Returns:
        Callable: The decorated wrapper function.
    """

    @wraps(method)
    def wrapper(element: Element, *args: Any, **kwargs: Any) -> list[Span | Link]:
        offset = kwargs.pop("offset", None)
        regex = kwargs.pop("regex", "")
        if offset is not None:
            return _by_offset_wrapper(
                method,
                element,
                int(offset),
                *args,
                **kwargs,
            )
        else:
            return _by_regex_wrapper(
                method,
                element,
                str(regex),
                *args,
                **kwargs,
            )

    return wrapper


class ParaMixin(ReferenceMixin, BookmarkMixin, AnnotationMixin):
    """Mixin for Paragraph methods."""

    def _expand_spaces(self, added_string: str) -> list[Element | str]:
        """Expand spaces within the element's content.

        This function processes text and `<text:s>` (space) elements,
        merging consecutive text nodes and converting `<text:s>` into strings.

        Args:
            added_string: A string to append at the end of the expansion.

        Returns:
            list[Element | str]: A list of elements and strings with spaces expanded.
        """
        result: list[Element | str] = []

        def _merge_text(txt: str) -> None:
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
        """Merge multiple consecutive spaces into `<text:s>` elements where appropriate.

        Args:
            content: A list of elements and strings to process.

        Returns:
            list[Element | str]: A new list with consecutive spaces merged into `<text:s>` elements.
        """
        result: list[Element | str] = []
        for item in content:
            if isinstance(item, str):
                result.extend(self._sub_merge_spaces(item))
            else:
                result.append(item)
        return result

    @staticmethod
    def _sub_merge_spaces(text: str) -> list[Element | str]:
        """Internal helper to merge spaces within a string into `Spacer` elements.

        Args:
            text: The string to process.

        Returns:
            list[Element | str]: A list of elements and strings, with spaces
                converted into `Spacer` objects where appropriate.
        """
        result: list[Element | str] = []
        content = [x for x in _re_spaces_split.split(text) if x]

        def _merge_text(txt: str) -> None:
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
        """Replace tab and line break characters within a list of content with ODF elements.

        Args:
            content: A list of elements and strings to process.

        Returns:
            list[Element | str]: A new list with tabs and line breaks replaced by `Tab` and `LineBreak` elements.
        """
        result: list[Element | str] = []
        for item in content:
            if isinstance(item, str):
                result.extend(self._sub_replace_tabs_lb(item))
            else:
                result.append(item)
        return result

    @staticmethod
    def _sub_replace_tabs_lb(text: str) -> list[Element | str]:
        """Internal helper to replace tab and line break characters in a string with ODF elements.

        Args:
            text: The string to process.

        Returns:
            list[Element | str]: A list of elements and strings, with tab and
                line break characters replaced by `Tab` and `LineBreak` objects.
        """
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
        """Append plain text to the paragraph, converting special characters to ODF tags.

        This method processes the input `text`, replacing carriage returns, tabs,
        and multiple spaces with their corresponding ODF tags (`<text:line-break>`,
        `<text:tab>`, `<text:s>`). Existing content of the paragraph is cleared.

        Args:
            text: The plain text to append.
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
            self._Element__append(element)  # type: ignore[attr-defined]

    @staticmethod
    def _unformatted(text: str | bytes | None) -> str:
        """Remove extra whitespace and newlines, replacing them with single spaces.

        Args:
            text: The input text.

        Returns:
            str: The unformatted text.
        """
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
        """Append a string or an element to the paragraph.

        Args:
            str_or_element: The content to append.
            formatted: If True (default), special characters like
                newlines, tabs, and multiple spaces in strings are converted
                to their ODF tag equivalents. If False, the string content
                is inserted unformatted (only extra whitespace is removed).
        """
        if isinstance(str_or_element, Element):
            if str_or_element.tag in {"text:p", "text:h", "text:s"}:
                # minimal compliancy or spacer summation
                self.append_plain_text(str(str_or_element))
                self.append_plain_text(str_or_element.tail)
            else:
                self._Element__append(str_or_element)  # type: ignore[attr-defined]
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
        """Insert a note (footnote or endnote) into the paragraph.

        A new `Note` element can be created using the provided parameters,
        or an existing `Note` element can be inserted.

        Args:
            note_element: An existing `Note` element to insert.
                If None, a new one is created.
            after: A regular expression (str) or an
                `Element` after which to insert the note.
            note_class: The class of the note ("footnote" or "endnote").
            note_id: A unique ID for the note.
            citation: The citation text for the note.
            body: The content of the note body.
        """
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
            self._insert(note_element, after=after)
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
        """Insert an annotation into the paragraph.

        The insertion point can be defined by a regular expression (`before`, `after`, `content`)
        or by positional arguments (`position`).

        - If `content` is provided, the annotation will cover the entire content matching the regex.
          If `content` is an `Element`, the annotation will cover its full inner content.
          In this case, `AnnotationStart` and `AnnotationEnd` tags are automatically inserted.
        - Otherwise, the annotation is positioned either `before` or `after` a regex match,
          or at a specific `position`.

        If `before`, `after`, or `content` are regular expressions that return multiple matches,
        the `position` argument can be used to select which match to use.

        Args:
            annotation_element: An optional pre-existing `Annotation` element.
                If None, a new `Annotation` is created using `body`, `creator`, and `date`.
            before: A regular expression. The annotation is inserted before text matching this regex.
            after: A regular expression or an `Element`.
                The annotation is inserted after text matching this regex or as the first child of the `Element`.
            position: An integer for character offset, or a 2-tuple `(start, end)`
                for a range. Used when `before`, `after`, and `content` are not specified.
            content: A regular expression or an `Element`. If provided,
                the annotation spans the matching content.
            body: The content of the annotation.
            creator: The creator of the annotation.
            date: The creation date of the annotation. Defaults to current date if None.

        Returns:
            Annotation: The inserted annotation element.

        Raises:
            ValueError: If an invalid combination of arguments is provided.
        """

        if annotation_element is None:
            annotation_element = Annotation(
                text_or_element=body,
                creator=creator,
                date=date,
                parent=self,
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
            self._insert(annotation_element, before=content, position=position)
            # End tag
            annotation_end = AnnotationEnd(annotation_element)
            self._insert(annotation_end, after=content, position=position)
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
            self._insert(annotation_element, position=position[0])
            # End
            annotation_end = AnnotationEnd(annotation_element)
            self._insert(annotation_end, position=position[1])
            return annotation_element

        # Without "content" nor "position"
        if content is not None or not isinstance(position, int):
            raise ValueError("Bad arguments")

        # Insert
        self._insert(annotation_element, before=before, after=after, position=position)
        return annotation_element

    def insert_annotation_end(
        self,
        annotation_element: Annotation,
        before: str | None = None,
        after: str | None = None,
        position: int = 0,
    ) -> AnnotationEnd:
        """Insert an annotation end tag for an existing annotation.

        If an end tag for the given `annotation_element` already exists, it is
        replaced. The end tag is positioned based on a regex match (`before` or `after`)
        or a numerical `position`.

        Args:
            annotation_element: The `Annotation` element for which
                to create the end tag.
            before: A regular expression. The end tag is inserted
                before text matching this regex.
            after: A regular expression. The end tag is inserted
                after text matching this regex.
            position: An integer character offset for insertion.

        Returns:
            AnnotationEnd: The inserted `AnnotationEnd` element.

        Raises:
            ValueError: If `annotation_element` is None.
            TypeError: If `annotation_element` is not an `Annotation` instance.
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
        self._insert(end_tag, before=before, after=after, position=position)
        return end_tag

    def set_reference_mark(
        self,
        name: str,
        before: str | None = None,
        after: str | None = None,
        position: int = 0,
        content: str | Element | None = None,
    ) -> Element:
        """Insert a reference mark (`ReferenceMark`, `ReferenceMarkStart`, or `ReferenceMarkEnd`) into the paragraph.

        The insertion point can be defined by a regular expression (`before`, `after`, `content`)
        or by positional arguments (`position`).

        - If `content` is provided (regex or `Element`), a pair of `ReferenceMarkStart`
          and `ReferenceMarkEnd` tags are inserted to cover the specified content.
        - Otherwise, a single `ReferenceMark` tag is positioned either `before` or `after`
          a regex match, or at a specific `position`.

        The `name` is mandatory and should be unique within the document for the reference mark.

        Args:
            name: The name of the reference mark.
            before: A regular expression. The mark is inserted before text matching this regex.
            after: A regular expression. The mark is inserted after text matching this regex.
            position: An integer for character offset, or a 2-tuple `(start, end)`
                for a range.
            content: A regular expression or an `Element`. If provided,
                the reference mark spans the matching content.

        Returns:
            Element: The created `ReferenceMark` or `ReferenceMarkStart` element.

        Raises:
            ValueError: If an invalid combination of arguments is provided.
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
            self._insert(reference_start, before=content, position=position)
            # End tag
            reference_end = ReferenceMarkEnd(name)
            self._insert(reference_end, after=content, position=position)
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
            self._insert(reference_start, position=position[0])
            # End
            reference_end = ReferenceMarkEnd(name)
            self._insert(reference_end, position=position[1])
            return reference_start

        # Without "content" nor "position"
        if content is not None or not isinstance(position, int):
            raise ValueError("bad arguments")

        # Insert a positional reference mark
        reference = ReferenceMark(name)
        self._insert(reference, before=before, after=after, position=position)
        return reference

    def set_reference_mark_end(
        self,
        reference_mark: Element,
        before: str | None = None,
        after: str | None = None,
        position: int = 0,
    ) -> ReferenceMarkEnd:
        """Insert or move a `ReferenceMarkEnd` for an existing reference mark.

        If an end tag for the given `reference_mark` already exists, it is
        replaced. The end tag is positioned based on a regex match (`before` or `after`)
        or a numerical `position`.

        Args:
            reference_mark: The `ReferenceMark` or `ReferenceMarkStart`
                element for which to create the end tag.
            before: A regular expression. The end tag is inserted
                before text matching this regex.
            after: A regular expression. The end tag is inserted
                after text matching this regex.
            position: An integer character offset for insertion.

        Returns:
            ReferenceMarkEnd: The inserted `ReferenceMarkEnd` element.

        Raises:
            TypeError: If `reference_mark` is not a `ReferenceMark` or `ReferenceMarkStart` instance.
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
        self._insert(end_tag, before=before, after=after, position=position)
        return end_tag

    def insert_variable(self, variable_element: Element, after: str | None) -> None:
        """Insert a variable element into the paragraph.

        Args:
            variable_element: The variable element to insert.
            after: A regular expression after which to insert the variable.
        """
        self._insert(variable_element, after=after)

    @_by_regex_offset
    def set_span(
        self,
        style: str,
        regex: str | None = None,
        offset: int | None = None,
        length: int = 0,
        **kwargs: Any,
    ) -> list[Span]:
        """Apply a text style to content within the paragraph using a `text:span` element.

        The target content can be specified either by a regular expression (`regex`)
        or by an `offset` and `length`.

        Args:
            style: The name of the text style to apply.
            regex: A regular expression to match the text content.
            offset: The starting character offset in the paragraph's text content.
            length: The length of the text content to apply the style to,
                starting from `offset`.

        Returns:
            list[Span]: A list of generated `Span` instances, each representing
                a styled portion of text.
        """
        span: Span = Element.from_tag("text:span")  # type: ignore[assignment]
        span.text = ""
        span.append_plain_text(kwargs["match_string"])
        span.style = style
        return span  # type: ignore[return-value]

    def remove_spans(self, keep_heading: bool = True) -> Element:
        """Remove all `text:span` elements from a copy of the paragraph.

        Args:
            keep_heading: If True, `text:h` (heading) elements are
                protected from stripping. Defaults to True.

        Returns:
            Element: A new `Element` instance representing the paragraph
                without `text:span` elements.
        """
        strip = ("text:span",)
        if keep_heading:
            protect = ("text:h",)
        else:
            protect = None
        return strip_tags(self, strip=strip, protect=protect)  # type: ignore [return-value]

    def remove_span(self, spans: Element | list[Element]) -> Element:
        """Remove specific `text:span` elements from a copy of the paragraph.

        Args:
            spans: The `Span` element(s) to remove.

        Returns:
            Element: A new `Element` instance representing the paragraph
                with the specified `text:span` elements removed.
        """
        return strip_elements(self, spans)  # type: ignore [return-value]

    @_by_regex_offset
    def set_link(
        self,
        url: str,
        regex: str | None = None,
        offset: int | None = None,
        length: int = 0,
        **kwargs: Any,
    ) -> list[Link]:
        """Create a hyperlink from text content within the paragraph.

        The text content can be identified either by a regular expression (`regex`)
        or by an `offset` and `length`.

        Args:
            url: The URL that the hyperlink points to.
            regex: A regular expression to match the text content.
            offset: The starting character offset in the paragraph's text content.
            length: The length of the text content to convert into a link,
                starting from `offset`.

        Returns:
            list[Link]: A list of generated `Link` instances, each representing
                a hyperlink.
        """

        return Link(url, text=kwargs["match_string"])  # type: ignore[return-value]

    def remove_links(self) -> Element:
        """Remove all `text:a` (hyperlink) elements from a copy of the paragraph.

        Returns:
            Element: A new `Element` instance representing the paragraph
                without hyperlink elements.
        """
        strip = (Link._tag,)
        return strip_tags(self, strip=strip)  # type: ignore [return-value]

    def remove_link(self, links: Link | list[Link]) -> Element:
        """Remove specific `text:a` (hyperlink) elements from a copy of the paragraph.

        Args:
            links: The `Link` element(s) to remove.

        Returns:
            Element: A new `Element` instance representing the paragraph
                with the specified hyperlink elements removed.
        """
        return strip_elements(self, links)  # type: ignore [return-value]

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
        mark. The Reference element ("text:reference-ref") represents a field
        that references a "text:reference-mark-start" or "text:reference-mark"
        element. Its "text:reference-format" attribute specifies what is
        displayed from the referenced element. Default is 'page'. Actual
        content is not automatically updated except for the 'text' format.

        name is mandatory and should represent an existing reference mark of the
        document.

        ref_format is the argument for format reference (default is 'page').

        The reference is inserted the position defined by the regex (before /
        after), or by positional argument (position). If 'display' is provided,
        it will be used as the text value for the reference.

        If after is an ODF Element, the reference is inserted as first child of
        this element.

        Args:
            name: The name of the reference mark.
            ref_format: The format for the reference, one of 'chapter',
                'direction', 'page', 'text', 'caption', 'category-and-value',
                'value', 'number', 'number-all-superior',
                'number-no-superior'.
            before: A regular expression before which to insert the reference.
            after: A regular expression or an ODF element after which to insert the reference.
            position: The insertion position.
            display: The text value for the reference, if provided.
        """
        reference = Reference(name, ref_format)
        if display is None and ref_format == "text":
            # get reference content
            body: Body | Element = self.document_body or self.root
            if hasattr(body, "get_reference_mark"):
                mark = body.get_reference_mark(name=name)
            else:
                mark = None
            if isinstance(mark, ReferenceMarkStart):
                display = mark.referenced_text()
        if not display:
            display = " "
        reference.text = display
        if isinstance(after, Element):
            after.insert(reference, FIRST_CHILD)
        else:
            self._insert(reference, before=before, after=after, position=position)

    def set_bookmark(
        self,
        name: str,
        before: str | None = None,
        after: str | None = None,
        position: int | tuple = 0,
        role: str | None = None,
        content: str | None = None,
    ) -> Element | tuple[Element, Element]:
        """Insert a bookmark (`Bookmark`, `BookmarkStart`, or `BookmarkEnd`) into the paragraph.

        The insertion point can be defined by a regular expression (`before`, `after`, `content`)
        or by positional arguments (`position`).

        - If `content` is provided, a pair of `BookmarkStart` and `BookmarkEnd`
          tags are automatically inserted to span the content.
        - If `position` is a 2-tuple `(start, end)`, `BookmarkStart` and `BookmarkEnd`
          tags are inserted at the specified offsets.
        - Otherwise, a single `Bookmark` (if `role` is None), `BookmarkStart` (if `role="start"`),
          or `BookmarkEnd` (if `role="end"`) is inserted based on `before`, `after`, or `position`.

        Args:
            name: The name of the bookmark.
            before: A regular expression. The bookmark is inserted before text matching this regex.
            after: A regular expression. The bookmark is inserted after text matching this regex.
            position: An integer for a character offset, or a 2-tuple `(start, end)` for a range.
            role: Specifies the type of bookmark to insert: "start", "end", or None for a regular bookmark.
            content: A regular expression. If provided, the bookmark spans the matching content.

        Returns:
            Element | tuple[Element, Element]: The created bookmark element(s).
                Returns a tuple `(BookmarkStart, BookmarkEnd)` if `content` or a 2-tuple `position` is used.

        Raises:
            ValueError: If an invalid combination of arguments is provided.
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
            self._insert(start, before=content, position=position)
            # End
            end = BookmarkEnd(name)
            self._insert(end, after=content, position=position)
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
            self._insert(start, position=position[0])
            # End
            end = BookmarkEnd(name)
            self._insert(end, position=position[1])
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
        self._insert(bookmark, before=before, after=after, position=position)

        return bookmark
