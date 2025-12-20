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
"""Reference related classes for "text:reference-..." tags."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union, cast

from .element import Element, PropDef, register_element_class
from .element_strip import strip_elements, strip_tags
from .elements_between import elements_between

if TYPE_CHECKING:
    from .body import Body


class ReferenceMixin(Element):
    """Mixin class for classes containing References.

    Used by the following classes: "text:a", "text:h", "text:meta", "text:meta-field",
    "text:p", "text:ruby-base", "text:span". And with "office:text" for compatibility
    with previous versions.
    """

    def get_reference_marks_single(self) -> list[ReferenceMark]:
        """Get all single-point reference marks (`text:reference-mark`).

        It is recommended to use `get_reference_marks()` for a more comprehensive search.

        Returns:
            A list of `ReferenceMark` instances.
        """
        return cast(
            list[ReferenceMark],
            self._filtered_elements(
                "descendant::text:reference-mark",
            ),
        )

    def get_reference_mark_single(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> ReferenceMark | None:
        """Get a specific single-point reference mark (`text:reference-mark`).

        It is recommended to use `get_reference_mark()` for a more comprehensive search.

        Args:
            position: The index of the mark to retrieve. Defaults to 0.
            name: The name of the reference mark.

        Returns:
            ReferenceMark | None: The `ReferenceMark` instance if found, otherwise `None`.
        """
        return cast(
            Union[None, ReferenceMark],
            self._filtered_element(
                "descendant::text:reference-mark", position, text_name=name
            ),
        )

    def get_reference_mark_starts(self) -> list[ReferenceMarkStart]:
        """Get all reference mark start tags (`text:reference-mark-start`).

        It is recommended to use `get_reference_marks()` for a more comprehensive search.

        Returns:
            list[ReferenceMarkStart]: A list of `ReferenceMarkStart` instances.
        """
        return cast(
            list[ReferenceMarkStart],
            self._filtered_elements(
                "descendant::text:reference-mark-start",
            ),
        )

    def get_reference_mark_start(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> ReferenceMarkStart | None:
        """Get a specific reference mark start tag (`text:reference-mark-start`).

        It is recommended to use `get_reference_mark()` for a more comprehensive search.

        Args:
            position: The index of the mark to retrieve. Defaults to 0.
            name: The name of the reference mark.

        Returns:
            ReferenceMarkStart | None: The `ReferenceMarkStart` instance if found, otherwise `None`.
        """
        return cast(
            Union[None, ReferenceMarkStart],
            self._filtered_element(
                "descendant::text:reference-mark-start", position, text_name=name
            ),
        )

    def get_reference_mark_ends(self) -> list[ReferenceMarkEnd]:
        """Get all reference mark end tags (`text:reference-mark-end`).

        It is recommended to use `get_reference_marks()` for a more comprehensive search.

        Returns:
            list[ReferenceMarkEnd]: A list of `ReferenceMarkEnd` instances.
        """
        return cast(
            list[ReferenceMarkEnd],
            self._filtered_elements(
                "descendant::text:reference-mark-end",
            ),
        )

    def get_reference_mark_end(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> ReferenceMarkEnd | None:
        """Get a specific reference mark end tag (`text:reference-mark-end`).

        It is recommended to use `get_reference_mark()` for a more comprehensive search.

        Args:
            position: The index of the mark to retrieve. Defaults to 0.
            name: The name of the reference mark.

        Returns:
            ReferenceMarkEnd | None: The `ReferenceMarkEnd` instance if found, otherwise `None`.
        """
        return cast(
            Union[None, ReferenceMarkEnd],
            self._filtered_element(
                "descendant::text:reference-mark-end", position, text_name=name
            ),
        )

    def get_reference_marks(self) -> list[ReferenceMark | ReferenceMarkStart]:
        """Get all reference marks.

        This includes both single-point marks (`text:reference-mark`) and the
        start of ranged marks (`text:reference-mark-start`).

        Returns:
            list[ReferenceMark | ReferenceMarkStart]: A list of `ReferenceMark` and
                `ReferenceMarkStart` instances.
        """
        return cast(
            list[ReferenceMark | ReferenceMarkStart],
            self._filtered_elements(
                "descendant::text:reference-mark-start | descendant::text:reference-mark"
            ),
        )

    def get_reference_mark(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> ReferenceMark | ReferenceMarkStart | None:
        """Get a specific reference mark by name or position.

        This can be either a single-point mark (`text:reference-mark`) or the
        start of a ranged mark (`text:reference-mark-start`).

        Args:
            position: The index of the mark to retrieve if `name` is not provided.
            name: The name of the reference mark.

        Returns:
            ReferenceMark | ReferenceMarkStart | None: The found reference mark element,
                or `None` if not found.
        """
        if name:
            request = (
                f"descendant::text:reference-mark-start"
                f'[@text:name="{name}"] '
                f"| descendant::text:reference-mark"
                f'[@text:name="{name}"]'
            )
            return self._filtered_element(
                request,
                position=0,
            )  # type: ignore[return-value]
        request = (
            "descendant::text:reference-mark-start | descendant::text:reference-mark"
        )
        return cast(
            Union[None, ReferenceMark, ReferenceMarkStart],
            self._filtered_element(request, position),
        )

    def get_references(self, name: str | None = None) -> list[Reference]:
        """Get all reference fields (`text:reference-ref`).

        Args:
            name: If provided, filter references by their `text:ref-name`.

        Returns:
            list[Reference]: A list of `Reference` instances.
        """
        if name is None:
            return self._filtered_elements(
                "descendant::text:reference-ref",
            )  # type: ignore[return-value]
        request = f'descendant::text:reference-ref[@text:ref-name="{name}"]'
        return cast(list[Reference], self._filtered_elements(request))


class Reference(Element):
    """A reference to a content marked by a reference mark, "text:reference-
    ref".".

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
    FORMAT_ALLOWED = (
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
        """Initialize a Reference element (`text:reference-ref`).

        A `Reference` represents a field that refers to a `ReferenceMark`
        or `ReferenceMarkStart`. An existing reference mark with the provided
        `name` is expected.

        Consider using the `odfdo.paragraph.insert_reference()` method for easier creation.

        Args:
            name: The name of the reference mark to refer to.
            ref_format: The format of the reference field, which determines
                what is displayed (e.g., "page", "chapter", "text").
                Defaults to "page".
            **kwargs: Additional keyword arguments for the parent `Element` class.
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name
            self.ref_format = ref_format

    @property
    def ref_format(self) -> str | None:
        """Get the `text:reference-format` of the reference.

        Returns:
            str | None: The reference format string.
        """
        reference = self.get_attribute("text:reference-format")
        if isinstance(reference, str):
            return reference
        return None

    @ref_format.setter
    def ref_format(self, ref_format: str) -> None:
        """Set the `text:reference-format` attribute.

        Args:
            ref_format: The new reference format. If invalid, defaults to "page".
        """
        if not ref_format or ref_format not in self.FORMAT_ALLOWED:
            ref_format = "page"
        self.set_attribute("text:reference-format", ref_format)

    def update(self) -> None:
        """Update the content of the reference text field.

        Currently only 'text' format is implemented. Other values, for example
        the 'page' text field, may need to be refreshed through a visual ODF
        parser.
        """
        ref_format = self.ref_format
        if ref_format != "text":
            # only 'text' is implemented
            return None
        body: Body | Element = self.document_body or self.root
        name = self.name
        if hasattr(body, "get_reference_mark"):
            reference = body.get_reference_mark(name=name)
            if isinstance(reference, ReferenceMarkStart):
                self.text = reference.referenced_text()


Reference._define_attribut_property()


class ReferenceMark(Element):
    """A point reference, "text:reference-mark".

    A point reference marks a position in text and is represented by a single
    "text:reference-mark" element.
    """

    _tag = "text:reference-mark"
    _properties = (PropDef("name", "text:name"),)

    def __init__(self, name: str = "", **kwargs: Any) -> None:
        """Initialize a ReferenceMark element.

        A point reference marks a position in text and is represented by
        a single `text:reference-mark` element.

        Consider using the `odfdo.paragraph.set_reference_mark()` method
        for easier creation.

        Args:
            name: The name of the reference mark.
            **kwargs: Additional keyword arguments for the parent `Element` class.
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name


ReferenceMark._define_attribut_property()


class ReferenceMarkEnd(Element):
    """End of a range reference, "text:reference-mark-end"."""

    _tag = "text:reference-mark-end"
    _properties = (PropDef("name", "text:name"),)

    def __init__(self, name: str = "", **kwargs: Any) -> None:
        """Initialize a ReferenceMarkEnd element.

        Represents the end of a range reference. It's recommended to use the
        helper methods `odfdo.paragraph.set_reference_mark()` or
        `odfdo.paragraph.set_reference_mark_end()` for creation.

        Args:
            name: The name of the reference mark this element ends.
            **kwargs: Additional keyword arguments for the parent `Element` class.
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name

    def referenced_text(self) -> str:
        """Return the text between reference-mark-start and reference-mark-
        end.
        """
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
    """Start of a range reference, "text:reference-mark-start"."""

    _tag = "text:reference-mark-start"
    _properties = (PropDef("name", "text:name"),)

    def __init__(self, name: str = "", **kwargs: Any) -> None:
        """Initialize a ReferenceMarkStart element.

        Represents the start of a range reference. It's recommended to use the
        helper method `odfdo.paragraph.set_reference_mark()` for creation.

        Args:
            name: The name of the reference mark this element starts.
            **kwargs: Additional keyword arguments for the parent `Element` class.
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name

    def referenced_text(self) -> str:
        """Return the text between reference-mark-start and reference-mark-
        end.
        """
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
        """Get the content between the start and end tags of the reference mark.

        This method can return the content in various formats (as a single `Element`,
        a list of `Element`s, or an XML string).

        Args:
            no_header: If True, converts `text:h` elements to `text:p` elements.
            clean: If True, removes unwanted tags like tracked changes marks.
            as_xml: If True, returns the content as a serialized XML string.
            as_list: If True, returns the content as a list of `Element` objects
                instead of being wrapped in an `office:text` element.

        Returns:
            Element | list | str | None: The referenced content in the specified format.
        """
        if self.parent is None:
            raise ValueError(
                "Reference need some upper document part"
            )  # pragma: nocover
        body: Body | Element = self.document_body or self.parent
        if hasattr(body, "get_reference_mark_end"):
            end = body.get_reference_mark_end(name=self.name)
        else:
            end = None
        if end is None:
            raise ValueError("No reference-end found")
        content_list = elements_between(
            body, self, end, as_text=False, no_header=no_header, clean=clean
        )
        if as_list:
            return content_list
        referenced = Element.from_tag("office:text")
        for chunk in content_list:
            referenced.append(chunk)
        if as_xml:
            return referenced.serialize()
        else:
            return referenced

    def delete(self, child: Element | None = None, keep_tail: bool = True) -> None:
        """Delete the element from the XML tree.

        If `child` is provided, it deletes a child element. If no `child` is
        given, "self" is deleted, along with its corresponding `ReferenceMarkEnd`
        tag if it exists.

        Args:
            child: The child element to delete. If `None`,
                the current element (`self`) is deleted.
            keep_tail: If True, the `tail` text of the deleted element
                is preserved.
        """
        if child is not None:  # act like normal delete
            return super().delete(child, keep_tail)  # pragma: nocover
        name = self.name
        if self.parent is None:
            raise ValueError("Can't delete the root element")  # pragma: nocover
        body: Body | Element = self.document_body or self.parent
        if hasattr(body, "get_reference_mark_end"):
            ref_end = body.get_reference_mark_end(name=name)
        else:
            ref_end = None
        if ref_end:  # pragma: nocover
            ref_end.delete()
        # act like normal delete
        return super().delete()


ReferenceMarkStart._define_attribut_property()


def strip_references(element: Element) -> Element | list:
    """Remove all `text:reference-ref` tags from an element.

    This function keeps the inner content of the stripped tags.

    Note: Using the `.delete()` method on a reference mark directly will
    also delete its inner content.

    Args:
        element: The element from which to strip reference tags.

    Returns:
        Element | list: The element with reference tags removed, or a list
            of elements if the top-level element itself is stripped.
    """
    to_strip = ("text:reference-ref",)
    return strip_tags(element, to_strip)


def remove_all_reference_marks(element: Element) -> Element | list:
    """Remove all reference mark tags from an element.

    This includes `text:reference-mark`, `text:reference-mark-start`, and
    `text:reference-mark-end`. The inner content of the tags is preserved.

    Note: Using the `.delete()` method on a reference mark directly will
    also delete its inner content.

    Args:
        element: The element from which to remove reference marks.

    Returns:
        Element | list: The element with reference marks removed, or a list
            of elements if the top-level element itself is stripped.
    """
    to_strip = (
        "text:reference-mark",
        "text:reference-mark-start",
        "text:reference-mark-end",
    )
    return strip_tags(element, to_strip)


def remove_reference_mark(
    element: Element,
    position: int = 0,
    name: str | None = None,
) -> None:
    """Remove a specific reference mark from an element by name or position.

    This removes `text:reference-mark`, `text:reference-mark-start`, and
    `text:reference-mark-end` tags, while keeping their inner content.

    Note: Using the `.delete()` method on a reference mark directly will
    also delete its inner content.

    Args:
        element: The element from which to remove the reference mark.
        position: The index of the mark to remove if `name` is not provided.
        name: The name of the reference mark to remove.
    """
    if hasattr(element, "get_reference_mark"):
        start_ref = element.get_reference_mark(position=position, name=name)
    else:
        start_ref = None
    if hasattr(element, "get_reference_mark_end"):
        end_ref = element.get_reference_mark_end(position=position, name=name)
    else:
        end_ref = None
    to_strip: list[ReferenceMark | ReferenceMarkStart | ReferenceMarkEnd] = []
    if start_ref:
        to_strip.append(start_ref)
    if end_ref:
        to_strip.append(end_ref)
    strip_elements(element, to_strip)


register_element_class(Reference)
register_element_class(ReferenceMark)
register_element_class(ReferenceMarkStart)
register_element_class(ReferenceMarkEnd)
