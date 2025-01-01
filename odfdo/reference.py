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
"""Reference related classes for "text:reference-..." tags.
"""
from __future__ import annotations

from typing import Any

from .element import Element, PropDef, register_element_class


def _get_referenced(
    body: Element,
    start: Element,
    end: Element,
    no_header: bool,
    clean: bool,
    as_xml: bool,
    as_list: bool,
) -> Element | list | str | None:
    """Retrieve data from body between some start and end."""
    if body is None or start is None or end is None:
        return None
    content_list = body.get_between(
        start, end, as_text=False, no_header=no_header, clean=clean
    )
    if as_list:
        return content_list
    referenced = Element.from_tag("office:text")
    if isinstance(content_list, list):
        for chunk in content_list:
            referenced.append(chunk)
    if as_xml:
        return referenced.serialize()
    else:
        return referenced


class Reference(Element):
    """A reference to a content marked by a reference mark.
    The odf_reference element ("text:reference-ref") represents a field that
    references a "text:reference-mark-start" or "text:reference-mark" element.
    Its text:reference-format attribute specifies what is displayed from the
    referenced element. Default is 'page'
    Actual content is not updated except for the 'text' format by the
    update() method.


    Creation of references can be tricky, consider using this method:
        odfdo.paragraph.insert_reference()

    Values for text:reference-format :
        The defined values for the text:reference-format attribute supported by
        all reference fields are:
          - 'chapter': displays the number of the chapter in which the
            referenced item appears.
          - 'direction': displays whether the referenced item is above or
            below the reference field.
          - 'page': displays the number of the page on which the referenced
            item appears.
          - 'text': displays the text of the referenced item.
        Additional defined values for the text:reference-format attribute
        supported by references to sequence fields are:
          - 'caption': displays the caption in which the sequence is used.
          - 'category-and-value': displays the name and value of the sequence.
          - 'value': displays the value of the sequence.

        References to bookmarks and other references support additional values,
        which display the list label of the referenced item. If the referenced
        item is contained in a list or a numbered paragraph, the list label is
        the formatted number of the paragraph which contains the referenced
        item. If the referenced item is not contained in a list or numbered
        paragraph, the list label is empty, and the referenced field therefore
        displays nothing. If the referenced bookmark or reference contains more
        than one paragraph, the list label of the paragraph at which the
        bookmark or reference starts is taken.

        Additional defined values for the text:reference-format attribute
        supported by all references to bookmark's or other reference fields
        are:
          - 'number': displays the list label of the referenced item. [...]
          - 'number-all-superior': displays the list label of the referenced
            item and adds the contents of all list labels of superior levels
            in front of it. [...]
          - 'number-no-superior': displays the contents of the list label of
            the referenced item.
    """

    _tag = "text:reference-ref"
    _properties = (PropDef("name", "text:ref-name"),)
    format_allowed = (
        "chapter",
        "direction",
        "page",
        "text",
        "caption",
        "category-and-value",
        "value",
        "number",
        "number-all-superior",
        "number-no-superior",
    )

    def __init__(self, name: str = "", ref_format: str = "", **kwargs: Any) -> None:
        """Create a reference to a content marked by a reference mark. An
        actual reference mark with the provided name should exist.

        Consider using: odfdo.paragraph.insert_reference()

        The text:ref-name attribute identifies a "text:reference-mark" or
        "text:referencemark-start" element by the value of that element's
        text:name attribute.
        If ref_format is 'text', the current text content of the reference_mark
        is retrieved.

        Arguments:

            name -- str : name of the reference mark

            ref_format -- str : format of the field. Default is 'page', allowed
                            values are 'chapter', 'direction', 'page', 'text',
                            'caption', 'category-and-value', 'value', 'number',
                            'number-all-superior', 'number-no-superior'.
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name
            self.ref_format = ref_format

    @property
    def ref_format(self) -> str | None:
        reference = self.get_attribute("text:reference-format")
        if isinstance(reference, str):
            return reference
        return None

    @ref_format.setter
    def ref_format(self, ref_format: str) -> None:
        """Set the text:reference-format attribute.

        Arguments:

            ref_format -- str
        """
        if not ref_format or ref_format not in self.format_allowed:
            ref_format = "page"
        self.set_attribute("text:reference-format", ref_format)

    def update(self) -> None:
        """Update the content of the reference text field. Currently only
        'text' format is implemented. Other values, for example the 'page' text
        field, may need to be refreshed through a visual ODF parser.
        """
        ref_format = self.ref_format
        if ref_format != "text":
            # only 'text' is implemented
            return None
        body = self.document_body
        if not body:
            body = self.root
        name = self.name
        reference = body.get_reference_mark(name=name)
        if not reference:
            return None
        # we know it is a ReferenceMarkStart:
        self.text = reference.referenced_text()  # type: ignore


Reference._define_attribut_property()


class ReferenceMark(Element):
    """A point reference.
    A point reference marks a position in text and is represented by a single
    "text:reference-mark" element.
    """

    _tag = "text:reference-mark"
    _properties = (PropDef("name", "text:name"),)

    def __init__(self, name: str = "", **kwargs: Any) -> None:
        """A point reference. A point reference marks a position in text and is
        represented by a single "text:reference-mark" element.
        Consider using the wrapper: odfdo.paragraph.set_reference_mark()

        Arguments:

            name -- str
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name


ReferenceMark._define_attribut_property()


class ReferenceMarkEnd(Element):
    """The "text:reference-mark-end" element represents the end of a range
    reference.
    """

    _tag = "text:reference-mark-end"
    _properties = (PropDef("name", "text:name"),)

    def __init__(self, name: str = "", **kwargs: Any) -> None:
        """The "text:reference-mark-end" element represent the end of a range
        reference.
        Consider using the wrappers: odfdo.paragraph.set_reference_mark() and
        odfdo.paragraph.set_reference_mark_end()

        Arguments:

            name -- str
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name

    def referenced_text(self) -> str:
        """Return the text between reference-mark-start and reference-mark-end."""
        name = self.name
        request = (
            f"//text()"
            f"[preceding::text:reference-mark-start[@text:name='{name}'] "
            f"and following::text:reference-mark-end[@text:name='{name}']]"
        )
        result = " ".join(str(x) for x in self.xpath(request))
        return result


ReferenceMarkEnd._define_attribut_property()


class ReferenceMarkStart(Element):
    """The "text:reference-mark-start" element represents the start of a
    range reference.
    """

    _tag = "text:reference-mark-start"
    _properties = (PropDef("name", "text:name"),)

    def __init__(self, name: str = "", **kwargs: Any) -> None:
        """The "text:reference-mark-start" element represent the start of a range
        reference.
        Consider using the wrapper: odfdo.paragraph.set_reference_mark()

        Arguments:

            name -- str
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name

    def referenced_text(self) -> str:
        """Return the text between reference-mark-start and reference-mark-end."""
        name = self.name
        request = (
            f"//text()"
            f"[preceding::text:reference-mark-start[@text:name='{name}'] "
            f"and following::text:reference-mark-end[@text:name='{name}']]"
        )
        result = " ".join(str(x) for x in self.xpath(request))
        return result

    def get_referenced(
        self,
        no_header: bool = False,
        clean: bool = True,
        as_xml: bool = False,
        as_list: bool = False,
    ) -> Element | list | str | None:
        """Return the document content between the start and end tags of the
        reference. The content returned by this method can spread over several
        headers and paragraphs.
        By default, the content is returned as an "office:text" odf element.


        Arguments:

            no_header -- boolean (default to False), translate existing headers
                         tags "text:h" into paragraphs "text:p".

            clean -- boolean (default to True), suppress unwanted tags. Striped
                     tags are : 'text:change', 'text:change-start',
                     'text:change-end', 'text:reference-mark',
                     'text:reference-mark-start', 'text:reference-mark-end'.

            as_xml -- boolean (default to False), format the returned content as
                      a XML string (serialization).

            as_list -- boolean (default to False), do not embed the returned
                       content in a "office:text'" element, instead simply
                       return a raw list of odf elements.
        """
        name = self.name
        parent = self.parent
        if parent is None:
            raise ValueError("Reference need some upper document part")
        body = self.document_body
        if not body:
            body = parent
        end = body.get_reference_mark_end(name=name)
        if end is None:
            raise ValueError("No reference-end found")
        start = self
        return _get_referenced(body, start, end, no_header, clean, as_xml, as_list)

    def delete(self, child: Element | None = None, keep_tail: bool = True) -> None:
        """Delete the given element from the XML tree. If no element is given,
        "self" is deleted. The XML library may allow to continue to use an
        element now "orphan" as long as you have a reference to it.

        For odf_reference_mark_start : delete the reference-end tag if exists.

        Arguments:

            child -- Element

            keep_tail -- boolean (default to True), True for most usages.
        """
        if child is not None:  # act like normal delete
            return super().delete(child, keep_tail)
        name = self.name
        parent = self.parent
        if parent is None:
            raise ValueError("Can't delete the root element")
        body = self.document_body
        if not body:
            body = parent
        end = body.get_reference_mark_end(name=name)
        if end:
            end.delete()
        # act like normal delete
        return super().delete()


ReferenceMarkStart._define_attribut_property()


def strip_references(element: Element) -> Element | list:
    """Remove all the 'text:reference-ref' tags of the element, keeping inner
    sub elements (for example the referenced value if format is 'text').
    Nota : using the .delete() on the reference mark will delete inner content.
    """
    strip = ("text:reference-ref",)
    return element.strip_tags(strip)


def remove_all_reference_marks(element: Element) -> Element | list:
    """Remove all the 'text:reference-mark', 'text:reference-mark-start', and
    'text:reference-mark-end' tags of the element, keeping inner sub elements.
    Nota : using the .delete() on the reference mark will delete inner content.
    """
    strip = (
        "text:reference-mark",
        "text:reference-mark-start",
        "text:reference-mark-end",
    )
    return element.strip_tags(strip)


def remove_reference_mark(
    element: Element,
    position: int = 0,
    name: str | None = None,
) -> None:
    """Remove the 'text:reference-mark', 'text:reference-mark-start', and
    'text:reference-mark-end' tags of the element, identified by name or
    position, keeping inner sub elements.
    Nota : using the .delete() on the reference mark will delete inner content.
    """
    start = element.get_reference_mark(position=position, name=name)
    end = element.get_reference_mark_end(position=position, name=name)
    target = []
    if start:
        target.append(start)
    if end:
        target.append(end)
    element.strip_elements(target)


register_element_class(Reference)
register_element_class(ReferenceMark)
register_element_class(ReferenceMarkStart)
register_element_class(ReferenceMarkEnd)
