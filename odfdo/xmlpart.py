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

from lxml.etree import _ElementTree, parse, tostring

from .container import Container
from .element import Element, Text


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

    def get_elements(self, xpath_query: str) -> list[Element | Text]:
        root = self.root
        return root.xpath(xpath_query)

    def get_element(self, xpath_query: str) -> Any:
        result = self.get_elements(xpath_query)
        if not result:
            return None
        return result[0]

    def delete_element(self, child: Element) -> None:
        child.delete()

    def xpath(self, xpath_query: str) -> list[Element | Text]:
        """Apply XPath query to the XML part. Return list of Element or
        Text instances translated from the nodes found.
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
        tree = self._get_tree()
        # Lxml declaration is too exotic to me
        data = [b'<?xml version="1.0" encoding="UTF-8"?>']
        bytes_tree = tostring(tree, pretty_print=pretty, encoding="utf-8")
        # Lxml with pretty_print is adding a empty line
        if pretty:
            bytes_tree = bytes_tree.strip()
        data.append(bytes_tree)
        return b"\n".join(data)
