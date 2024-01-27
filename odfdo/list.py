# Copyright 2018-2024 Jérôme Dumonteil
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
"""List class for "text:list".
"""
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
from .paragraph import Paragraph


class ListItem(Element):
    """ODF element "text:list-item", item of a List."""

    _tag = "text:list-item"

    def __init__(
        self,
        text_or_element: str | Element | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a list item element, optionaly passing at creation time a
        string or Element as content.

        Arguments:

            text_or_element -- str or ODF Element
        """
        super().__init__(**kwargs)
        if self._do_init:
            if isinstance(text_or_element, str):
                self.text_content = text_or_element
            elif isinstance(text_or_element, Element):
                self.append(text_or_element)
            elif text_or_element is not None:
                raise TypeError("Expected str or Element")


class List(Element):
    """ODF List "text:list"."""

    _tag = "text:list"
    _properties = (PropDef("style", "text:style-name"),)

    def __init__(
        self,
        list_content: str | Element | Iterable[str | Element] | None = None,
        style: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a list element, optionaly loading the list by a list of
        item (str or elements).

        The list_content argument is just a shortcut for the most common case.
        To create more complex lists, first create an empty list, and fill it
        afterwards.

        Arguments:

            list_content -- str or Element, or a list of str or Element

            style -- str
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
        """Return all the list items that match the criteria.

        Arguments:

            style -- str

            content -- str regex

        Return: list of Element
        """
        return self._filtered_elements("text:list-item", content=content)

    def get_item(
        self,
        position: int = 0,
        content: str | None = None,
    ) -> Element | None:
        """Return the list item that matches the criteria. In nested lists,
        return the list item that really contains that content.

        Arguments:

            position -- int

            content -- str regex

        Return: Element or None if not found
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
        if not isinstance(item, ListItem):
            item = ListItem(item)
        self.append(item)

    def get_formatted_text(self, context: dict | None = None) -> str:
        if context is None:
            context = {}
        rst_mode = context["rst_mode"]
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
                    return text
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
