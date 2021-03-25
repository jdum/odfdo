# Copyright 2018-2020 Jérôme Dumonteil
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
"""List class for "text:list"
"""
from .element import (
    register_element_class,
    Element,
    FIRST_CHILD,
    PREV_SIBLING,
    NEXT_SIBLING,
)
from .paragraph import Paragraph
from .utils import _get_element, _get_elements, isiterable


class ListItem(Element):
    """ODF element "text:list-item", item of a List."""

    _tag = "text:list-item"

    def __init__(self, text_or_element=None, **kwargs):
        """Create a list item element, optionaly passing at creation time a
        string or Element as content.

        Arguments:

            text_or_element -- str or ODF Element

        Return: ListItem
        """
        super().__init__(**kwargs)
        if self._do_init:
            if isinstance(text_or_element, str):
                self.text_content = text_or_element
            elif isinstance(text_or_element, Element):
                self.append(text_or_element)
            elif text_or_element is not None:
                raise TypeError("expected str or Element")


class List(Element):
    """ODF List "text:list"."""

    _tag = "text:list"
    _properties = (("style", "text:style-name"),)

    def __init__(self, list_content=None, style=None, **kwargs):
        """Create a list element, optionaly loading the list by a list of
        item (str or elements).

        The list_content argument is just a shortcut for the most common case.
        To create more complex lists, first create an empty list, and fill it
        afterwards.

        Arguments:

            list_content -- a list of str or Element

            style -- str

        Return: List
        """
        super().__init__(**kwargs)
        if self._do_init:
            if list_content:
                if not isiterable(list_content):
                    list_content = [list_content]
                for item in list_content:
                    self.append(ListItem(item))
            if style is not None:
                self.style = style

    def get_items(self, content=None):
        """Return all the list items that match the criteria.

        Arguments:

            style -- str

            content -- str regex

        Return: list of Element
        """
        return _get_elements(self, "text:list-item", content=content)

    def get_item(self, position=0, content=None):
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
        return _get_element(self, "text:list-item", position)

    def set_list_header(self, text_or_element):
        if not isiterable(text_or_element):
            text_or_element = [text_or_element]
        # Remove existing header
        for element in self.get_elements("text:p"):
            self.delete(element)
        for paragraph in reversed(text_or_element):
            if isinstance(paragraph, str):
                paragraph = Paragraph(paragraph)
            self.insert(paragraph, FIRST_CHILD)

    def insert_item(self, item, position=None, before=None, after=None):
        if not isinstance(item, ListItem):
            item = ListItem(item)

        if before is not None:
            before.insert(item, xmlposition=PREV_SIBLING)
        elif after is not None:
            after.insert(item, xmlposition=NEXT_SIBLING)
        elif position is not None:
            self.insert(item, position=position)
        else:
            raise ValueError("position must be defined")

    def append_item(self, item):
        if not isinstance(item, ListItem):
            item = ListItem(item)
        self.append(item)

    def get_formatted_text(self, context):
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
            textbuf = "".join(textbuf)
            textbuf = textbuf.strip("\n")
            # Indent the text
            textbuf = "- %s\n" % textbuf.replace("\n", "\n  ")
            result.append(textbuf)
        if rst_mode:
            result.append("\n")
        return "".join(result)


List._define_attribut_property()

register_element_class(ListItem)
register_element_class(List)
