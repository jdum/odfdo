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
"""List class for "text:list" tag and ListItem for "text:list-item" tag ."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .element import (
    FIRST_CHILD,
    NEXT_SIBLING,
    PREV_SIBLING,
    Element,
    PropDef,
    register_element_class,
)
from .mixin_md import MDList, MDListItem
from .paragraph import Paragraph


class ListItem(MDListItem, Element):
    """An item of a list, "text:list-item"."""

    _tag = "text:list-item"

    def __init__(
        self,
        text_or_element: str | Element | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the ListItem.

        A `ListItem` can be initialized with text content or another element.

        Args:
            text_or_element: The initial
                content of the list item. If a string, a paragraph containing
                the text is created. If an element, it is appended as a child.
            **kwargs: Additional keyword arguments for the parent `Element` class.
        """
        super().__init__(**kwargs)
        if self._do_init:
            if isinstance(text_or_element, str):
                self.text_content = text_or_element
            elif isinstance(text_or_element, Element):
                self.append(text_or_element)
            elif text_or_element is not None:
                raise TypeError(f"Expected str or Element, not {type(text_or_element)}")

    def __str__(self) -> str:
        self._md_initialize_level()
        return "\n".join(self._md_collect())


class List(MDList, Element):
    """A list of elements, "text:list"."""

    _tag = "text:list"
    _properties = (PropDef("style", "text:style-name"),)

    def __init__(
        self,
        list_content: str | Element | Iterable[str | Element] | None = None,
        style: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the List.

        A `List` can be initialized with content, which can be a single item
        (string or element) or an iterable of items.

        Args:
            list_content: The initial content of the list. Each item is wrapped in a
                `ListItem`.
            style: The name of the style to apply to the list.
            **kwargs: Additional keyword arguments for the parent `Element` class.
        """
        super().__init__(**kwargs)
        if self._do_init:
            if list_content:
                if isinstance(list_content, (Element, str)):
                    self.append(ListItem(list_content))
                elif hasattr(list_content, "__iter__"):
                    for item in list_content:
                        self.append(ListItem(item))
            if style is not None:
                self.style = style

    def get_items(self, content: str | None = None) -> list[Element]:
        """Get all list items (`ListItem`) within the list.

        Optionally filters items by their textual content.

        Args:
            content: A regular expression to match against
                the text content of the items.

        Returns:
            list[Element]: A list of `ListItem` elements that match the criteria.
        """
        return self._filtered_elements("text:list-item", content=content)

    def get_item(
        self,
        position: int = 0,
        content: str | None = None,
    ) -> Element | None:
        """Get a single list item from the list.

        Can retrieve an item by its position or by matching its text content.
        In nested lists, it returns the `ListItem` that directly contains
        the matched content.

        Args:
            position: The index of the item to retrieve. Defaults to 0.
            content: A regular expression to match against
                the text content of the items. If provided, `position` is
                ignored.

        Returns:
            Element | None: The matching `ListItem` element, or `None` if not found.
        """
        # Custom implementation because of nested lists
        if content:
            # Don't search recursively but on the very own paragraph(s) of
            # each list item
            for paragraph in self.get_elements("descendant::text:p"):
                if paragraph.match(content):
                    return paragraph.get_element("parent::text:list-item")
            return None
        return self._filtered_element("text:list-item", position)

    def set_list_header(
        self,
        text_or_element: str | Element | Iterable[str | Element],
    ) -> None:
        """Set the header of the list.

        This method replaces any existing header paragraphs (`text:p`) with
        the provided content.

        Args:
            text_or_element: The content for the list header. Can be a single string or element,
                or an iterable of strings and/or elements.
        """
        if isinstance(text_or_element, (str, Element)):
            actual_list: list[str | Element] | tuple = [text_or_element]
        elif isinstance(text_or_element, (list, tuple)):
            actual_list = text_or_element
        else:
            raise TypeError
        # Remove existing header
        for element in self.get_elements("text:p"):
            self.delete(element)
        for paragraph in reversed(actual_list):
            if isinstance(paragraph, str):
                paragraph = Paragraph(paragraph)
            self.insert(paragraph, FIRST_CHILD)

    def insert_item(
        self,
        item: ListItem | str | Element | None,
        position: int | None = None,
        before: Element | None = None,
        after: Element | None = None,
    ) -> None:
        """Insert a new item into the list.

        The item can be inserted at a specific `position`, or `before` or
        `after` an existing element.

        Args:
            item: The item to insert.
                If not a `ListItem`, it will be wrapped in one.
            position: The index at which to insert the item.
            before: An existing element to insert the item
                before.
            after: An existing element to insert the item
                after.

        Raises:
            ValueError: If no position (`position`, `before`, or `after`) is specified.
        """
        if not isinstance(item, ListItem):
            item = ListItem(item)
        if before is not None:
            before.insert(item, xmlposition=PREV_SIBLING)
        elif after is not None:
            after.insert(item, xmlposition=NEXT_SIBLING)
        elif position is not None:
            self.insert(item, position=position)
        else:
            raise ValueError("Position must be defined")

    def append_item(
        self,
        item: ListItem | str | Element | None,
    ) -> None:
        """Append a new item to the end of the list.

        Args:
            item: The item to append.
                If not a `ListItem`, it will be wrapped in one.
        """
        if not isinstance(item, ListItem):
            item = ListItem(item)
        self.append(item)

    def get_formatted_text(self, context: dict | None = None) -> str:
        """Return a formatted string representation of the list.

        Each list item is prefixed with "- " and indented.

        Args:
            context: A dictionary providing context for
                formatting. If `rst_mode` is True in the context, additional
                newlines are added for reStructuredText compatibility.

        Returns:
            str: The formatted text content of the list.
        """
        if context is None:
            context = {
                "document": None,
                "footnotes": [],
                "endnotes": [],
                "annotations": [],
                "rst_mode": False,
                "img_counter": 0,
                "images": [],
                "no_img_level": 0,
            }
        rst_mode = bool(context.get("rst_mode"))
        result = []
        if rst_mode:
            result.append("\n")
        for list_item in self.get_elements("text:list-item"):
            textbuf = []
            for child in list_item.children:
                text = child.get_formatted_text(context)
                tag = child.tag
                if tag == "text:h":
                    # A title in a list is a bug
                    return text
                if tag == "text:list" and not text.lstrip().startswith("-"):
                    # If the list didn't indent, don't either
                    # (inner title)
                    return text  # pragma: nocover
                textbuf.append(text)
            text_sum = "".join(textbuf)
            text_sum = text_sum.strip("\n")
            # Indent the text
            text_sum = text_sum.replace("\n", "\n  ")
            text_sum = f"- {text_sum}\n"
            result.append(text_sum)
        if rst_mode:
            result.append("\n")
        return "".join(result)


List._define_attribut_property()

register_element_class(ListItem)
register_element_class(List)
