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
#          Romain Gauthier <romain@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
"""TrackedChanges class for "text:tracked-changes" and related classes
(ChangeInfo, TextInsertion, TextChange...).
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Union, cast

from .element import FIRST_CHILD, LAST_CHILD, Element, register_element_class
from .elements_between import elements_between
from .mixin_dc_creator import DcCreatorMixin
from .mixin_dc_date import DcDateMixin
from .mixin_md import MDZap
from .mixin_toc import TocMixin
from .paragraph import Paragraph
from .section import SectionMixin

if TYPE_CHECKING:
    from .body import Body, Text


class TrackedChangesMixin(Element):
    """Mixin class for classes containing TrackedChanges.

    Used by the following classes:  "office:text", "style:footer",
    "style:footer-first", "style:footer-left", "style:header",
    "style:header-first" and "style:header-left".
    """

    def get_tracked_changes(self) -> TrackedChanges | None:
        """Return the tracked-changes part in the text body.

        Returns:
            TrackedChanges or None: The tracked changes element, or None if
                not found.
        """
        return cast(
            Union[None, TrackedChanges], self.get_element("//text:tracked-changes")
        )

    @property
    def tracked_changes(self) -> TrackedChanges | None:
        """The 'text:tracked-changes' element in the body.

        This property provides access to the main container for tracked
        changes within the element's scope.
        """
        return self.get_tracked_changes()


class ChangeInfo(Element, DcCreatorMixin, DcDateMixin):
    """Information about a change, "office:change-info".

    This element stores metadata about a change, including the author,
    timestamp, and any associated comments.

    Comments are stored as one or more "text:p" (Paragraph) elements and can
    be accessed as Paragraph objects or as plain text.

    Attributes:
        creator (str): The name of the author who made the change.
        date (datetime): The date and time when the change was made.
    """

    _tag = "office:change-info"

    def __init__(
        self,
        creator: str | None = None,
        date: datetime | None = None,
        **kwargs: Any,
    ) -> None:
        """Initializes the ChangeInfo element.

        Args:
            creator: The name of the author of the change. Defaults to "Unknown".
            date: The date and time of the change. Defaults to the current time if not provided.
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.creator = creator or "Unknown"
            self.date = date

    def get_comments(self, joined: bool = True) -> str | list[str]:
        """Gets the text content of the comments.

        Args:
            joined: If True (the default), concatenates the text of
                all comment paragraphs into a single string. If False,
                returns a list of strings, one for each paragraph.

        Returns:
            str | list[str]: The comment text as a single string or a list
                of strings.
        """
        content = self.paragraphs
        text = [para.get_formatted_text(simple=True) for para in content]
        if joined:
            return "\n".join(text)
        return text

    def set_comments(self, text: str = "", replace: bool = True) -> None:
        """Sets the text content of the comments.

        Args:
            text: The new text for the comments.
            replace: If True (the default), the new text replaces any
                existing comments. If False, it is appended as a new
                paragraph.
        """
        if replace:
            for para in self.paragraphs:
                self.delete(para)
        para = Paragraph()
        para.append_plain_text(text)
        self.insert(para, xmlposition=LAST_CHILD)


class TextInsertion(Element):
    """Represents a text insertion, "text:insertion".

    This element contains metadata about an insertion, including the author,
    date, and optional comments. It is linked to the actual inserted content
    in the document body via its parent "text:changed-region".
    """

    _tag = "text:insertion"

    def get_deleted(
        self,
        as_text: bool = False,
        no_header: bool = False,
    ) -> str | list[Element] | None:
        """Returns None, as this is a text insertion.

        This method is for consistency with other change types.

        Args:
            as_text: Ignored.
            no_header: Ignored.

        Returns:
            None | str: Always None for list return, empty string for text.
        """
        if as_text:
            return ""
        return None

    def get_inserted(
        self,
        as_text: bool = False,
        no_header: bool = False,
        clean: bool = True,
    ) -> str | Element | list[Element] | None:
        """Gets the content that was inserted.

        This is a shortcut to find the corresponding 'text:change-start' and
        'text:change-end' tags and return the content between them.

        Args:
            as_text: If True, returns the content as a plain text string.
            no_header: If True, converts any 'text:h' (heading)
                elements to 'text:p' (paragraph) elements.
            clean: If True, filters out unwanted elements from the result.

        Returns:
            str | Element | list[Element] | None: The inserted content,
                which can be a single element, a list of elements, a string,
                or None if not found.
        """
        current = self.parent  # text:changed-region
        if not isinstance(current, TextChangedRegion):
            raise TypeError("Missing parent TextChangedRegion")
        idx = current.get_id()
        body: Body | Element = self.document_body or self.root
        text_change = body.get_text_change_start(idx=idx)
        if not text_change:
            raise ValueError  # pragma: nocover
        return text_change.get_inserted(
            as_text=as_text, no_header=no_header, clean=clean
        )

    def get_change_info(self) -> ChangeInfo | None:
        """Gets the 'office:change-info' child of this element.

        Returns:
            ChangeInfo | None: The ChangeInfo element, or None if not found.
        """
        return cast(
            Union[None, ChangeInfo], self.get_element("descendant::office:change-info")
        )

    def set_change_info(
        self,
        change_info: Element | None = None,
        creator: str | None = None,
        date: datetime | None = None,
        comments: Element | list[Element] | None = None,
    ) -> None:
        """Sets the 'office:change-info' for this insertion.

        If `change_info` is not provided, a new one is created using the
        other arguments. Any existing change info is replaced.

        Args:
            change_info: An existing ChangeInfo element
                to set.
            creator: The name of the author. Defaults to
                'Unknown'.
            date: The date and time of the change.
                Defaults to the current time.
            comments: A Paragraph or list of Paragraphs to add as comments.
        """
        if change_info is None:
            new_change_info = ChangeInfo(creator, date)
            if comments is not None:
                if isinstance(comments, Element):
                    # single paragraph comment
                    comments_list = [comments]
                else:
                    comments_list = comments
                # assume iterable of Paragraph
                for paragraph in comments_list:
                    if not isinstance(paragraph, Paragraph):
                        raise TypeError(f"Not a Paragraph: '{paragraph!r}'")
                    new_change_info.insert(paragraph, xmlposition=LAST_CHILD)
        else:
            if not isinstance(change_info, ChangeInfo):
                raise TypeError(f"Not a ChangeInfo: '{change_info!r}'")
            new_change_info = change_info

        old = self.get_change_info()
        if old is not None:
            self.replace_element(old, new_change_info)
        else:
            self.insert(new_change_info, xmlposition=FIRST_CHILD)


class TextDeletion(TocMixin, SectionMixin, TextInsertion):
    """Represents a text deletion, "text:deletion".

    This element contains metadata about a deletion (author, date, comments)
    and stores the actual content that was deleted. The position in the
    document where the deletion occurred is marked by a "text:change"
    element.
    """

    _tag = "text:deletion"

    def get_deleted(
        self,
        as_text: bool = False,
        no_header: bool = False,
    ) -> str | list[Element] | None:
        """Gets the content that was deleted.

        Args:
            as_text: If True, returns the content as a plain text
                string.
            no_header: If True, converts any 'text:h' (heading)
                elements to 'text:p' (paragraph) elements.

        Returns:
            str | list[Element] | None: The deleted content, which is
                typically a list of Paragraph or Header elements, a string,
                or None.
        """
        children = self.children
        inner = [elem for elem in children if elem.tag != "office:change-info"]
        if no_header:  # crude replace t:h by t:p
            print("noheaders")
            new_inner = []
            for element in inner:
                if element.tag == "text:h":
                    children = element.children
                    text = element.text
                    para = Element.from_tag("text:p")
                    para.text = text
                    for child in children:
                        para.append(child)  # pragma: nocover
                    new_inner.append(para)
                else:
                    new_inner.append(element)
            inner = new_inner
        if as_text:
            return "\n".join([elem.get_formatted_text(context=None) for elem in inner])
        return inner

    def set_deleted(self, paragraph_or_list: Element | list[Element]) -> None:
        """Sets the content that was deleted.

        This method replaces any existing deleted content within this element.

        Args:
            paragraph_or_list: A Paragraph,
                Header, or a list of such elements representing the deleted
                content.
        """
        for element in self.get_deleted():  # type: ignore
            self.delete(element)  # type: ignore
        if isinstance(paragraph_or_list, Element):
            paragraph_or_list = [paragraph_or_list]
        for element in paragraph_or_list:
            self.append(element)

    def get_inserted(
        self,
        as_text: bool = False,
        no_header: bool = False,
        clean: bool = True,
    ) -> str | Element | list[Element] | None:
        """Returns None, as this is a text deletion.

        This method is for consistency with other change types.

        Args:
            as_text: Ignored.
            no_header: Ignored.
            clean: Ignored.

        Returns:
            None | str: Always None for list return, empty string for text.
        """
        if as_text:
            return ""
        return None


class TextFormatChange(TextInsertion):
    """Represents a change in text formatting, "text:format-change".

    This element marks a change in formatting attributes. The actual region
    of the change is defined by "text:change-start" and "text:change-end"
    elements.

    Note: This element itself does not contain the specific formatting
    changes, only metadata about the change event.
    """

    _tag = "text:format-change"


class TextChangedRegion(Element):
    """A container for a single tracked change, "text:changed-region".

    This element links a change marker in the document body (like
    "text:change-start") to the details of the change (like
    "text:insertion" or "text:deletion"). It contains exactly one of:
    TextInsertion, TextDeletion, or TextFormatChange.

    The 'xml:id' or 'text:id' of this element is referenced by the
    corresponding change marker elements.

    Warning:
        This implementation expects that a 'text:changed-region' is
        referenced only once, which differs from the ODF 1.2 specification.
    """

    _tag = "text:changed-region"

    def get_change_info(self) -> ChangeInfo | None:
        """Gets the ChangeInfo from the underlying change element.

        This is a shortcut to access the 'office:change-info' of the
        child (e.g., TextInsertion).

        Returns:
            ChangeInfo | None: The ChangeInfo element, or None if not found.
        """
        return cast(
            Union[None, ChangeInfo], self.get_element("descendant::office:change-info")
        )

    def set_change_info(
        self,
        change_info: Element | None = None,
        creator: str | None = None,
        date: datetime | None = None,
        comments: Element | list[Element] | None = None,
    ) -> None:
        """Sets the ChangeInfo on the underlying change element.

        This is a shortcut to set the 'office:change-info' of the child
        (e.g., TextInsertion). See `TextInsertion.set_change_info()` for
        more details.

        Args:
            change_info: An existing ChangeInfo element.
            creator: The author's name.
            date: The date of the change.
            comments: Comments to add.
        """
        child = self.get_change_element()
        if not child:
            raise ValueError("Empty TextChangedRegion")
        child.set_change_info(  # type: ignore
            change_info=change_info, creator=creator, date=date, comments=comments
        )

    def get_change_element(self) -> Element | None:
        """Gets the underlying change element.

        This will be one of TextInsertion, TextDeletion, or TextFormatChange.

        Returns:
            Element | None: The change element, or None if not found.
        """
        request = (
            "descendant::text:insertion "
            "| descendant::text:deletion"
            "| descendant::text:format-change"
        )
        return self._filtered_element(request, 0)

    def _get_text_id(self) -> str | None:
        return self.get_attribute_string("text:id")

    def _set_text_id(self, text_id: str) -> None:
        self.set_attribute("text:id", text_id)

    def _get_xml_id(self) -> str | None:
        return self.get_attribute_string("xml:id")

    def _set_xml_id(self, xml_id: str) -> None:
        self.set_attribute("xml:id", xml_id)

    def get_id(self) -> str | None:
        """Gets the "text:id" attribute of the region.

        Returns:
            str | None: The ID of the changed region.
        """
        return self._get_text_id()

    def set_id(self, idx: str) -> None:
        """Sets both the "text:id" and "xml:id" attributes to the same value.

        Args:
            idx: The ID to set.
        """
        self._set_text_id(idx)
        self._set_xml_id(idx)


class TrackedChanges(MDZap, Element):
    """The main container for all tracked changes, "text:tracked-changes".

    This element holds all the 'text:changed-region' elements that describe
    the individual changes (insertions, deletions, format changes) within
    its scope (e.g., the document body or a header).

    If this element is absent, change tracking is considered disabled for that
    scope, and any change markers should be ignored.
    """

    _tag = "text:tracked-changes"

    def get_changed_regions(
        self,
        creator: str | None = None,
        date: datetime | None = None,
        content: str | None = None,
        role: str | None = None,
    ) -> list[Element]:
        """Gets a list of 'text:changed-region' elements matching criteria.

        Args:
            creator: Filter by the author's name.
            date: Filter by the date of the change.
            content: Filter by a regex match in the content.
            role: Filter by the type of change ('insertion', 'deletion', 'format-change').

        Returns:
            list[Element]: A list of matching TextChangedRegion elements.
        """
        changed_regions = self._filtered_elements(
            "text:changed-region",
            dc_creator=creator,
            dc_date=date,
            content=content,
        )
        if role is None:
            return changed_regions
        result: list[Element] = []
        for region in changed_regions:
            changed = region.get_change_element()  # type: ignore
            if not changed:
                continue  # pragma: nocover
            if changed.tag.endswith(role):
                result.append(region)
        return result

    def get_changed_region(
        self,
        position: int = 0,
        text_id: str | None = None,
        creator: str | None = None,
        date: datetime | None = None,
        content: str | None = None,
    ) -> Element | None:
        """Gets a single 'text:changed-region' element by position or criteria.

        Args:
            position: The index of the region to retrieve.
            text_id: Get the region with this specific ID.
            creator: Filter by the author's name.
            date: Filter by the date of the change.
            content: Filter by a regex match in the content.

        Returns:
            Element | None: The matching TextChangedRegion element, or None
                if not found.
        """
        return self._filtered_element(
            "text:changed-region",
            position,
            text_id=text_id,
            dc_creator=creator,
            dc_date=date,
            content=content,
        )


class TextChange(Element):
    """A text change position, "text:change".

    The TextChange "text:change" element marks a position in an empty region
    where text has been deleted.
    """

    _tag = "text:change"

    def get_id(self) -> str | None:
        """Gets the ID of the change this marker refers to.

        Returns:
            str | None: The 'text:change-id' attribute value.
        """
        return self.get_attribute_string("text:change-id")

    def set_id(self, idx: str) -> None:
        """Sets the ID of the change this marker refers to.

        Args:
            idx: The ID to set as 'text:change-id'.
        """
        self.set_attribute("text:change-id", idx)

    def _get_tracked_changes(self) -> TrackedChanges | None:
        body: Text | None = self.document_body  # type: ignore[assignment]
        if body and body.tag == "office:text":
            return body.get_tracked_changes()
        raise ValueError

    def get_changed_region(
        self,
        tracked_changes: TrackedChanges | None = None,
    ) -> Element | None:
        """Finds the 'text:changed-region' this marker is associated with.

        Args:
            tracked_changes: The parent tracked
                changes container to search in. If not provided, it is
                inferred from the document.

        Returns:
            Element | None: The associated TextChangedRegion element, or
                None if not found.
        """
        if not tracked_changes:
            tracked_changes = self._get_tracked_changes()
        idx = self.get_id()
        return tracked_changes.get_changed_region(text_id=idx)  # type: ignore

    def get_change_info(
        self,
        tracked_changes: TrackedChanges | None = None,
    ) -> Element | None:
        """Gets the 'office:change-info' for the change this marker refers to.

        Args:
            tracked_changes: The parent tracked changes container to search in.

        Returns:
            Element | None: The ChangeInfo element, or None if not found.
        """
        changed_region = self.get_changed_region(tracked_changes=tracked_changes)
        if not changed_region:
            return None  # pragma: nocover
        return changed_region.get_change_info()  # type: ignore

    def get_change_element(
        self,
        tracked_changes: TrackedChanges | None = None,
    ) -> Element | None:
        """Gets the underlying change element for this marker.

        This will be one of TextInsertion, TextDeletion, or TextFormatChange.

        Args:
            tracked_changes: The parent tracked changes container to search in.

        Returns:
            Element | None: The change element, or None if not found.
        """
        changed_region = self.get_changed_region(tracked_changes=tracked_changes)
        if not changed_region:
            return None  # pragma: nocover
        return changed_region.get_change_element()  # type: ignore

    def get_deleted(
        self,
        tracked_changes: TrackedChanges | None = None,
        as_text: bool = False,
        no_header: bool = False,
        clean: bool = True,
    ) -> Element | None:
        """Gets the deleted content associated with this change marker.

        This is a shortcut to find the related TextDeletion element and
        retrieve its content.

        Args:
            tracked_changes: The parent tracked changes container.
            as_text: Return content as a plain text string.
            no_header: Convert headings to paragraphs.
            clean: Ignored.

        Returns:
            Element | None: The deleted content.
        """
        changed = self.get_change_element(tracked_changes=tracked_changes)
        if not changed:
            return None  # pragma: nocover
        return changed.get_deleted(  # type: ignore
            as_text=as_text,
            no_header=no_header,
        )

    def get_inserted(
        self,
        as_text: bool = False,
        no_header: bool = False,
        clean: bool = True,
    ) -> str | Element | list[Element] | None:
        """Returns None, as 'text:change' marks a deletion point.

        Returns:
            None: Always returns None.
        """
        return None

    def get_start(self) -> TextChangeStart | None:
        """Returns None, as this is a single-point marker.

        Returns:
            None: Always returns None.
        """
        return None

    def get_end(self) -> TextChangeEnd | None:
        """Returns None, as this is a single-point marker.

        Returns:
            None: Always returns None.
        """
        return None


class TextChangeEnd(TextChange):
    """End of a changed region, "text:change-end".

    The TextChangeEnd "text:change-end" element marks the end of a region with
    content where text has been inserted or the format has been changed.
    """

    _tag = "text:change-end"

    def get_start(self) -> TextChangeStart | None:
        """Gets the corresponding 'text:change-start' tag.

        Returns:
            TextChangeStart | None: The start marker with the same ID, or
                None if not found.
        """
        idx = self.get_id()
        parent = self.parent
        if parent is None:
            raise ValueError(
                "Can not find end tag: no parent available."
            )  # pragma: nocover
        body: Body | Element = self.document_body or self.root
        return body.get_text_change_start(idx=idx)

    def get_end(self) -> TextChangeEnd | None:
        """Returns self, as this is the end marker.

        Returns:
            TextChangeEnd: This element.
        """
        return self

    def get_deleted(self, *args: Any, **kwargs: Any) -> Element | None:
        """Returns None, as this marks an insertion or format change.

        Returns:
            None: Always returns None.
        """
        return None

    def get_inserted(
        self,
        as_text: bool = False,
        no_header: bool = False,
        clean: bool = True,
    ) -> str | Element | list[Element] | None:
        """Gets the content between the start and end change markers.

        Args:
            as_text: If True, returns the content as a plain text string.
            no_header: If True, converts any 'text:h' (heading) elements to 'text:p' (paragraph) elements.
            clean: If True, filters out unwanted elements from the result.

        Returns:
            str | Element | list[Element] | None: The inserted content.
        """

        # idx = self.get_id()
        start = self.get_start()
        end = self.get_end()
        if end is None or start is None:
            if as_text:
                return ""
            return None
        body: Body | Element = self.document_body or self.root
        return elements_between(
            body, start, end, as_text=as_text, no_header=no_header, clean=clean
        )


class TextChangeStart(TextChangeEnd):
    """Start of a changed region, "text:change-start".

    The TextChangeStart "text:change-start" element marks the start of a region
    with content where text has been inserted or the format has been changed.
    """

    _tag = "text:change-start"

    def get_start(self) -> TextChangeStart:
        """Returns self, as this is the start marker.

        Returns:
            TextChangeStart: This element.
        """
        return self

    def get_end(self) -> TextChangeEnd:
        """Gets the corresponding 'text:change-end' tag.

        Returns:
            TextChangeEnd | None: The end marker with the same ID, or
                None if not found.
        """
        idx = self.get_id()
        parent = self.parent
        if parent is None:
            raise ValueError(
                "Can not find end tag: no parent available."
            )  # pragma: nocover
        body: Body | Element = self.document_body or self.root
        return body.get_text_change_end(idx=idx)  # type: ignore

    def delete(
        self,
        child: Element | None = None,
        keep_tail: bool = True,
    ) -> None:
        """Deletes the element from the XML tree.

        For a TextChangeStart, this also deletes the corresponding
        'text:change-end' tag if it exists.

        Args:
            child: A specific child to delete. If None,
                the element itself is deleted.
            keep_tail: If True, the text that follows the element
                is preserved. Defaults to True.
        """
        if child is not None:  # act like normal delete
            return super().delete(child, keep_tail)  # pragma: nocover
        idx = self.get_id()
        if self.parent is None:
            raise ValueError("cannot delete the root element")  # pragma: nocover
        body: Body | Element = self.document_body or self.root
        end = body.get_text_change_end(idx=idx)
        if end:  # pragma: nocover
            end.delete()
        # act like normal delete
        super().delete()


register_element_class(ChangeInfo)
register_element_class(TextInsertion)
register_element_class(TextDeletion)
register_element_class(TextFormatChange)
register_element_class(TextChangedRegion)
register_element_class(TrackedChanges)
register_element_class(TextChange)
register_element_class(TextChangeEnd)
register_element_class(TextChangeStart)
