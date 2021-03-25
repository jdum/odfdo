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
#          Romain Gauthier <romain@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
"""TrackedChanges class for "text:tracked-changes" and related classes
(ChangeInfo, TextInsertion, TextChange...)
"""
from datetime import datetime
from .datatype import DateTime

from .element import register_element_class, Element
from .element import FIRST_CHILD, LAST_CHILD
from .paragraph import Paragraph
from .utils import _get_elements, _get_element


class ChangeInfo(Element):
    """The "office:change-info" element represents who made a change and when.
    It may also contain a comment (one or more Paragrah "text:p" elements)
    on the change.

    The comments available in the ChangeInfo are available through:
      - get_paragraphs and get_paragraph methods for actual Paragraph.
      - get_comments for a plain text version

      Arguments:

         creator -- str (or None)

         date -- datetime
    """

    _tag = "office:change-info"

    def __init__(self, creator=None, date=None, **kwargs):
        super().__init__(**kwargs)
        if self._do_init:
            self.set_dc_creator(creator)
            self.set_dc_date(date)

    def set_dc_creator(self, creator=None):
        """Set the creator of the change. Default for creator is 'Unknown'.

        Arguments:

            creator -- str (or None)
        """
        element = self.get_element("dc:creator")
        if element is None:
            element = Element.from_tag("dc:creator")
            self.insert(element, xmlposition=FIRST_CHILD)
        if not creator:
            creator = "Unknown"
        element.text = creator

    def set_dc_date(self, date=None):
        """Set the date of the change. If date is None, use current time.

        Arguments:

            date -- datetime
        """
        if date is None:
            date = datetime.now()
        dcdate = DateTime.encode(date)
        element = self.get_element("dc:date")
        if element is None:
            element = Element.from_tag("dc:date")
            self.insert(element, xmlposition=LAST_CHILD)
        element.text = dcdate

    def get_comments(self, joined=True):
        """Get text content of the comments. If joined is True (default), the
        text of different paragraphs is concatenated, else a list of strings,
        one per paragraph, is returned.

        Arguments:

            joined -- boolean (default is True)

        Return: str or list of unicode.
        """
        content = self.get_paragraphs()
        if content is None:
            content = []
        text = [para.get_formatted_text(simple=True) for para in content]
        if joined:
            return "\n".join(text)
        return text

    def set_comments(self, text="", replace=True):
        """Set the text content of the comments. If replace is True (default),
        the new text replace old comments, else it is added at the end.

        Arguments:

            text -- str

            replace -- boolean
        """
        if replace:
            for para in self.get_paragraphs():
                self.delete(para)
        para = Paragraph()
        para.append_plain_text(text)
        self.insert(para, xmlposition=LAST_CHILD)


class TextInsertion(Element):
    """The TextInsertion "text:insertion" element contains the information
    that identifies the person responsible for a change and the date of
    that change. This information may also contain one or more "text:p"
    Paragraph which contain a comment on the insertion. The
    TextInsertion element's parent "text:changed-region" element has an
    xml:id or text:id attribute, the value of which binds that parent
    element to the text:change-id attribute on the "text:change-start"
    and "text:change-end" elements.
    """

    _tag = "text:insertion"

    def get_deleted(self, as_text=False, no_header=False):
        """Return: None."""
        if as_text:
            return ""
        return None

    def get_inserted(self, as_text=False, no_header=False, clean=True):
        """Shortcut to text:change-start.get_inserted(). Return the content
        between text:change-start and text:change-end.

        If no content exists (deletion tag), returns None (or str if text flag
        is True).
        if pragraph is True: returns the content embedded in a Paragraph.
        If text is True: returns the annotated text.
        By default: returns a list of Text or Element.

        Arguments:

            paragraph -- boolean

            text -- boolean

        Return: list or Paragraph or text
        """
        cr = self.parent  # text:changed-region
        idx = cr.get_id()
        body = self.document_body
        if not body:
            body = self.root
        text_change = body.get_text_change_start(idx=idx)
        return text_change.get_inserted(
            as_text=as_text, no_header=no_header, clean=clean
        )

    def get_change_info(self):
        """Get the ChangeInfo child of the element.

        Return: ChangeInfo element.
        """
        return self.get_element("descendant::office:change-info")

    def set_change_info(self, change_info=None, creator=None, date=None, comments=None):
        """Set the ChangeInfo element for the change element. If change_info
        is not provided, creator, date and comments will be used to build a
        suitable change info element. Default for creator is 'Unknown',
        default for date is current time and default for comments is no
        comment at all.
        The new change info element will replace any existant ChangeInfo.

        Arguments:

             change_info -- ChangeInfo element (or None)

             cretor -- str (or None)

             date -- datetime (or None)

             comments -- list of Paragraph elements (or None)
        """
        if change_info is None:
            new_change_info = ChangeInfo(creator, date)
            if comments is not None:
                if isinstance(comments, Paragraph):
                    # single pararagraph comment
                    comments = [comments]
                # assume iterable of Paragraph
                for paragraph in comments:
                    if not isinstance(paragraph, Paragraph):
                        raise ValueError("%s is not a Paragraph." % paragraph)
                    new_change_info.insert(paragraph, xmlposition=LAST_CHILD)
        else:
            if not isinstance(change_info, ChangeInfo):
                raise ValueError("%s is not a ChangeInfo" % change_info)
            new_change_info = change_info

        old = self.get_change_info()
        if old is not None:
            self.replace_element(old, new_change_info)
        else:
            self.insert(new_change_info, xmlposition=FIRST_CHILD)


class TextDeletion(TextInsertion):
    """The TextDeletion "text:deletion" contains information that identifies
    the person responsible for a deletion and the date of that deletion.
    This information may also contain one or more Paragraph which contains
    a comment on the deletion. The TextDeletion element may also contain
    content that was deleted while change tracking was enabled. The position
    where the text was deleted is marked by a "text:change" element. Deleted
    text is contained in a paragraph element. To reconstruct the original
    text, the paragraph containing the deleted text is merged with its
    surrounding paragraph or heading element. To reconstruct the text before
    a deletion took place:
      - If the change mark is inside a paragraph, insert the content that was
      deleted, but remove all leading start tags up to and including the
      first "text:p" element and all trailing end tags up to and including
      the last "/text:p" or "/text:h" element. If the last trailing element
      is a "/text:h", change the end tag "/text:p" following this insertion
      to a "/text:h" element.
      - If the change mark is inside a heading, insert the content that was
      deleted, but remove all leading start tags up to and including the
      first "text:h" element and all trailing end tags up to and including
      the last "/text:h" or "/text:p" element. If the last trailing element
      is a "/text:p", change the end tag "/text:h" following this insertion
      to a "/text:p" element.
      - Otherwise, copy the text content of the "text:deletion" element in
      place of the change mark.
    """

    _tag = "text:deletion"

    def get_deleted(self, as_text=False, no_header=False):
        """Get the deleted informations stored in the TextDeletion.
        If as_text is True: returns the text content.
        If no_header is True: existing Heading are changed in Paragraph

        Arguments:

            as_text -- boolean

            no_header -- boolean

        Return: Paragraph and Header list
        """
        children = self.children
        inner = [e for e in children if e.tag != "office:change-info"]
        if no_header:  # crude replace t:h by t:p
            new_inner = []
            for element in inner:
                if element.tag == "text:h":
                    children = element.children
                    text = element.text
                    para = Element.from_tag("text:p")
                    para.text = text
                    for c in children:
                        para.append(c)
                    new_inner.append(para)
                else:
                    new_inner.append(element)
            inner = new_inner
        if as_text:
            return "\n".join([e.get_formatted_text(context=None) for e in inner])
        return inner

    def set_deleted(self, paragraph_or_list):
        """Set the deleted informations stored in the TextDeletion. An
        actual content that was deleted is expected, embeded in a Paragraph
        element or Header.

        Arguments:

            paragraph_or_list -- Paragraph or Header element (or list)
        """
        for element in self.get_deleted():
            self.delete(element)
        if isinstance(paragraph_or_list, Element):
            paragraph_or_list = [paragraph_or_list]
        for element in paragraph_or_list:
            self.append(element)

    def get_inserted(self, as_text=False, no_header=False, clean=True):
        """Return None (or u'')."""
        if as_text:
            return ""
        return None


class TextFormatChange(TextInsertion):
    """The TextFormatChange "text:format-change" element represents any change
    in formatting attributes. The region where the change took place is
    marked by "text:change-start", "text:change-end" or "text:change"
    elements.

    Note: This element does not contain formatting changes that have taken
    place.
    """

    _tag = "text:format-change"


class TextChangedRegion(Element):
    """Each TextChangedRegion "text:changed-region" element contains a single
    element, one of TextInsertion, TextDeletion or TextFormatChange that
    corresponds to a change being tracked within the scope of the
    "text:tracked-changes" element that contains the "text:changed-region"
    instance.
    The xml:id attribute of the TextChangedRegion is referenced
    from the "text:change", "text:change-start" and "text:change-end"
    elements that identify where the change applies to markup in the scope of
    the "text:tracked-changes" element.

    Warning : for this implementation, text:change should be referenced only
              once in the scope, which is different from ODF 1.2 requirement:
             " A "text:changed-region" can be referenced by more than one
             change, but the corresponding referencing change mark elements
             shall be of the same change type - insertion, format change or
             deletion. "
    """

    _tag = "text:changed-region"

    def get_change_info(self):
        """Shortcut to get the ChangeInfo element of the change
        element child.

        Return: ChangeInfo element.
        """
        return self.get_element("descendant::office:change-info")

    def set_change_info(self, change_info=None, creator=None, date=None, comments=None):
        """Shortcut to set the ChangeInfo element of the sub change element.
        See TextInsertion.set_change_info() for details.
        """
        child = self.get_change_element()
        child.set_change_info(
            change_info=change_info, creator=creator, date=date, comments=comments
        )

    def get_change_element(self):
        """Get the change element child. It can be either: TextInsertion,
        TextDeletion, or TextFormatChange as an Element object.

        Return: Element.
        """
        request = (
            "descendant::text:insertion "
            "| descendant::text:deletion"
            "| descendant::text:format-change"
        )
        return _get_element(self, request, position=0)

    def _get_text_id(self):
        return self.get_attribute("text:id")

    def _set_text_id(self, text_id):
        return self.set_attribute("text:id", text_id)

    def _get_xml_id(self):
        return self.get_attribute("xml:id")

    def _set_xml_id(self, xml_id):
        return self.set_attribute("xml:id", xml_id)

    def get_id(self):
        """Get the "text:id" attribute.

        Return: str
        """
        return self._get_text_id()

    def set_id(self, idx):
        """Set both the "text:id" and "xml:id" attributes."""
        self._set_text_id(idx)
        self._set_xml_id(idx)


class TrackedChanges(Element):
    """The TrackedChanges "text:tracked-changes" element acts as a container
    for TextChangedRegion elements that represent changes in a certain
    scope of an OpenDocument document. This scope is the element in which
    the TrackedChanges element occurs. Changes in this scope shall be
    tracked by TextChangedRegion elements contained in the
    TrackedChanges element in this scope. If a TrackedChanges
    element is absent, there are no tracked changes in the corresponding
    scope. In this case, all change mark elements in this scope shall be
    ignored.
    """

    _tag = "text:tracked-changes"

    def get_changed_regions(self, creator=None, date=None, content=None, role=None):
        changed_regions = _get_elements(
            self,
            "text:changed-region",
            dc_creator=creator,
            dc_date=date,
            content=content,
        )
        if role is None:
            return changed_regions
        result = []
        for cr in changed_regions:
            ce = cr.get_change_element()
            if not ce:
                continue
            if ce.tag.endswith(role):
                result.append(cr)
        return result

    def get_changed_region(
        self, position=0, text_id=None, creator=None, date=None, content=None
    ):
        return _get_element(
            self,
            "text:changed-region",
            position,
            text_id=text_id,
            dc_creator=creator,
            dc_date=date,
            content=content,
        )


class TextChange(Element):
    """The TextChange "text:change" element marks a position in an empty
    region where text has been deleted.
    """

    _tag = "text:change"

    def get_id(self):
        return self.get_attribute("text:change-id")

    def set_id(self, idx):
        return self.set_attribute("text:change-id", idx)

    def _get_tracked_changes(self):
        body = self.document_body
        return body.get_tracked_changes()

    def get_changed_region(self, tracked_changes=None):
        if not tracked_changes:
            tracked_changes = self._get_tracked_changes()
        idx = self.get_id()
        return tracked_changes.get_changed_region(text_id=idx)

    def get_change_info(self, tracked_changes=None):
        cr = self.get_changed_region(tracked_changes=tracked_changes)
        return cr.get_change_info()

    def get_change_element(self, tracked_changes=None):
        cr = self.get_changed_region(tracked_changes=tracked_changes)
        return cr.get_change_element()

    def get_deleted(
        self, tracked_changes=None, as_text=False, no_header=False, clean=True
    ):
        """Shortcut to get the deleted informations stored in the
        TextDeletion stored in the tracked changes.

        Return: Paragraph (or None)."
        """
        ce = self.get_change_element(tracked_changes=tracked_changes)
        return ce.get_deleted(as_text=as_text, no_header=no_header, clean=clean)

    def get_inserted(self, *args, **kwargs):
        """Return None."""
        return None

    def get_start(self):
        """Return None."""
        return None

    def get_end(self):
        """Return None."""
        return None


class TextChangeEnd(TextChange):
    """The TextChangeEnd "text:change-end" element marks the end of a region
    with content where text has been inserted or the format has been
    changed.
    """

    _tag = "text:change-end"

    def get_start(self):
        """Return the corresponding annotation starting tag or None."""
        idx = self.get_id()
        parent = self.parent
        if parent is None:
            raise ValueError("Can not find end tag: no parent available.")
        body = self.document_body
        if not body:
            body = self.root
        return body.get_text_change_start(idx=idx)

    def get_end(self):
        """Return self."""
        return self

    def get_deleted(self, *args, **kwargs):
        """Return None."""
        return None

    def get_inserted(self, as_text=False, no_header=False, clean=True):
        """Return the content between text:change-start and text:change-end.

        If no content exists (deletion tag), returns None (or '' if text flag
        is True).
        If as_text is True: returns the text content.
        If clean is True: suppress unwanted tags (deletions marks, ...)
        If no_header is True: existing text:h are changed in text:p
        By default: returns a list of Element, cleaned and with headers
        By default: returns a list of Text or Element.

        Arguments:

            as_text -- boolean

            clean -- boolean

            no_header -- boolean

        Return: list or Paragraph or text
        """

        # idx = self.get_id()
        start = self.get_start()
        end = self.get_end()
        if end is None or start is None:
            if as_text:
                return ""
            return None
        body = self.document_body
        if not body:
            body = self.root
        return body.get_between(
            start, end, as_text=as_text, no_header=no_header, clean=clean
        )


class TextChangeStart(TextChangeEnd):
    """The TextChangeStart "text:change-start" element marks the start of a
    region with content where text has been inserted or the format has
    been changed.
    """

    _tag = "text:change-start"

    def get_start(self):
        """Return self."""
        return self

    def get_end(self):
        """Return the corresponding change-end tag or None."""
        idx = self.get_id()
        parent = self.parent
        if parent is None:
            raise ValueError("Can not find end tag: no parent available.")
        body = self.document_body
        if not body:
            body = self.root
        return body.get_text_change_end(idx=idx)

    def delete(self, child=None, keep_tail=True):
        """Delete the given element from the XML tree. If no element is given,
        "self" is deleted. The XML library may allow to continue to use an
        element now "orphan" as long as you have a reference to it.

        For TextChangeStart : delete also the end tag if exists.

        Arguments:

            child -- Element

            keep_tail -- boolean (default to True), True for most usages.
        """
        if child is not None:  # act like normal delete
            return super().delete(child, keep_tail)
        idx = self.get_id()
        parent = self.parent
        if parent is None:
            raise ValueError("cannot delete the root element")
        body = self.document_body
        if not body:
            body = parent
        end = body.get_text_change_end(idx=idx)
        if end:
            end.delete()
        # act like normal delete
        return super().delete()


register_element_class(ChangeInfo)
register_element_class(TextInsertion)
register_element_class(TextDeletion)
register_element_class(TextFormatChange)
register_element_class(TextChangedRegion)
register_element_class(TrackedChanges)
register_element_class(TextChange)
register_element_class(TextChangeEnd)
register_element_class(TextChangeStart)
