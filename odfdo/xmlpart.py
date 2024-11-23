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
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
"""XmlPart base class for XML parts.
"""
from __future__ import annotations

from copy import deepcopy
from io import BytesIO
from typing import Any

from lxml.etree import _Element, _ElementTree, parse, tostring

from .container import Container
from .element import Element, EText

TAB = "  "
TEXT_CONTENT = {
    "office:script",
    "text:a",
    "text:deletion",
    "text:h",
    "text:meta",
    "text:meta-field",
    "text:p",
    "text:ruby-base",
    "text:span",
}


class XmlPart:
    """Representation of an XML part.

    Abstraction of the XML library behind.
    """

    def __init__(self, part_name: str, container: Container) -> None:
        self.part_name = part_name
        self.container = container

        # Internal state
        self.__tree: _ElementTree | None = None
        self.__root: Element | None = None

    def _get_tree(self) -> _ElementTree:
        if self.__tree is None:
            part = self.container.get_part(self.part_name)
            self.__tree = parse(BytesIO(part))  # type: ignore
        return self.__tree

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} part_name={self.part_name}>"

    # Public API

    @property
    def root(self) -> Element:
        if self.__root is None:
            tree = self._get_tree()
            self.__root = Element.from_tag(tree.getroot())
        return self.__root

    @property
    def body(self) -> Element:
        """Get or set the document body : 'office:body'"""
        body = self.root.document_body
        if not isinstance(body, Element):
            raise TypeError(f"No body found in {self.part_name!r}")
        return body

    @body.setter
    def body(self, new_body: Element) -> None:
        body = self.root.document_body
        if not isinstance(body, Element):
            raise TypeError("//office:body not found in document")
        tail = body.tail
        body.clear()
        for item in new_body.children:
            body.append(item)
        if tail:
            body.tail = tail

    def get_elements(self, xpath_query: str) -> list[Element | EText]:
        root = self.root
        return root.xpath(xpath_query)

    def get_element(self, xpath_query: str) -> Any:
        result = self.get_elements(xpath_query)
        if not result:
            return None
        return result[0]

    def delete_element(self, child: Element) -> None:
        child.delete()

    def xpath(self, xpath_query: str) -> list[Element | EText]:
        """Apply XPath query to the XML part. Return list of Element or
        EText instances translated from the nodes found.
        """
        root = self.root
        return root.xpath(xpath_query)

    @property
    def clone(self) -> XmlPart:
        clone = object.__new__(self.__class__)
        for name in self.__dict__:
            if name == "container":
                setattr(clone, name, self.container.clone)
            elif name in ("_XmlPart__tree",):
                setattr(clone, name, None)
            else:
                value = getattr(self, name)
                value = deepcopy(value)
                setattr(clone, name, value)
        return clone

    def serialize(self, pretty: bool = False) -> bytes:
        if pretty:
            return self.pretty_serialize()
        xml_header = b'<?xml version="1.0" encoding="UTF-8"?>\n'
        tree = self._get_tree()
        bytes_tree = tostring(tree, encoding="unicode").encode("utf8")
        return xml_header + bytes_tree

    def pretty_serialize(self) -> bytes:
        xml_header = b'<?xml version="1.0" encoding="UTF-8"?>\n'
        bytes_tree = tostring(self.custom_pretty_tree(), encoding="unicode").encode(
            "utf8"
        )
        return xml_header + bytes_tree

    def custom_pretty_tree(self) -> _ElementTree | _Element:
        tree = self._get_tree()
        root = tree.getroot()
        return self.indent(root)

    @staticmethod
    def ptag(elem: _Element) -> str:
        tag = elem.tag
        if "}" not in tag:
            return f"{elem.prefix}:{tag}"
        return f"{elem.prefix}:{tag.split('}', 1)[1]}"

    def indent(
        self,
        elem: _ElementTree | _Element,
        level: int = 0,
        next_level: int = 0,
    ) -> _ElementTree | _Element:
        if self.ptag(elem) in TEXT_CONTENT:
            elem.tail = "\n" + next_level * TAB
            return elem
        if len(elem):
            follow_level = level + 1
            if elem.text:
                elem.text = "\n" + follow_level * TAB + elem.text.lstrip()
            else:
                elem.text = "\n" + follow_level * TAB
            for sub_elem in elem[:-1]:
                self.indent(sub_elem, follow_level, follow_level)
            self.indent(elem[-1], follow_level, level)
            elem.tail = "\n" + next_level * TAB
        else:
            if elem.text:
                elem.text = "\n" + level * TAB + elem.text.lstrip()
            else:
                elem.text = "\n" + level * TAB
            elem.tail = "\n" + next_level * TAB
        return elem
