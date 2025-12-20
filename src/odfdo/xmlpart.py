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
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
"""Provides the XmlPart base class for handling XML parts within ODF documents.

This module abstracts the interaction with XML content, allowing for easy
access, manipulation, and serialization of specific XML parts of an ODF file.
"""

from __future__ import annotations

from copy import deepcopy
from io import BytesIO
from typing import TYPE_CHECKING

from lxml.etree import _Element, _ElementTree, parse, tostring

from .container import Container, pretty_indent
from .element import Element, EText

if TYPE_CHECKING:
    from .body import Body


class XmlPart:
    """Represents an XML part within an ODF document.

    This class provides an abstraction layer over the underlying XML library
    (lxml), allowing for easier manipulation of XML content within ODF
    parts (e.g., 'content.xml', 'styles.xml').

    Attributes:
        part_name (str): The name of the XML part (e.g., "content.xml").
        container (Container): The ODF container associated with this XML part.
    """

    def __init__(self, part_name: str, container: Container) -> None:
        """Initializes an XmlPart instance.

        Args:
            part_name: The name of the XML part (e.g., "content.xml").
            container: The ODF container (zip file) that holds
                this XML part.
        """
        self.part_name = part_name
        self.container = container

        # Internal state
        self.__tree: _ElementTree | None = None
        self.__root: Element | None = None

    def _get_tree(self) -> _ElementTree:
        """Loads and returns the XML tree for the part.

        If the tree has not been loaded yet, it reads the part from the
        container and parses it.

        Returns:
            _ElementTree: The parsed XML ElementTree object.
        """
        if self.__tree is None:
            part = self.container.get_part(self.part_name)
            self.__tree = parse(BytesIO(part))  # type: ignore[arg-type]
        return self.__tree

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} part_name={self.part_name}>"

    # Public API

    @property
    def root(self) -> Element:
        """The root Element of this XML part.

        When accessed for the first time, it loads and parses the XML part
        into an Element object.
        """
        if self.__root is None:
            tree = self._get_tree()
            self.__root = Element.from_tag(tree.getroot())
        return self.__root

    def _get_body(self) -> Body:
        """Retrieves the document body ('office:body') from the root element.

        Returns:
            Body: The document body element.

        Raises:
            TypeError: If no 'office:body' element is found in the part.
        """
        body = self.root.document_body
        if not isinstance(body, Element):
            raise TypeError(f"No body found in {self.part_name!r}")
        return body

    @property
    def body(self) -> Body:
        """The document body element ('office:body').

        This property provides access to the main content body of the XML part.
        """
        return self._get_body()

    @body.setter
    def body(self, new_body: Element) -> None:
        """Sets the document body with a new Element.

        Args:
            new_body: The new 'office:body' element to set.
        """
        body = self._get_body()
        tail = body.tail
        body.clear()
        for item in new_body.children:
            body.append(item)
        if tail:  # pragma: nocover
            body.tail = tail

    def get_elements(self, xpath_query: str) -> list[Element]:
        """Returns a list of elements matching the XPath query.

        The XPath query is applied to the root of this XML part.

        Args:
            xpath_query: The XPath query string.

        Returns:
            list[Element]: A list of matching Element objects.
        """
        return self.root.get_elements(xpath_query)

    def get_element(self, xpath_query: str) -> Element | None:
        """Returns the first element matching the XPath query.

        The XPath query is applied to the root of this XML part.

        Args:
            xpath_query: The XPath query string.

        Returns:
            Element | None: The first matching Element object, or None if
                no match is found.
        """
        return self.root.get_element(xpath_query)

    def delete_element(self, child: Element) -> None:
        """Deletes a specified child element from the XML tree.

        Args:
            child: The child element to delete.
        """
        child.delete()

    def xpath(self, xpath_query: str) -> list[Element | EText]:
        """Applies an XPath query to the root of the XML part and its subtree.

        Args:
            xpath_query: The XPath query string.

        Returns:
            list[Element | EText]: A list of Element or EText instances
                matching the query.
        """
        return self.root.xpath(xpath_query)

    @property
    def clone(self) -> XmlPart:
        """Creates a deep copy of the XmlPart instance.

        The cloned part will have its own independent XML tree.

        Returns:
            XmlPart: A new XmlPart instance that is a clone of the original.
        """
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
        """Serializes the XML part to bytes.

        Args:
            pretty: If True, the output XML will be pretty-printed.
                Defaults to False.

        Returns:
            bytes: The XML content as bytes, including the XML declaration.
        """
        if pretty:
            return self.pretty_serialize()
        xml_header = b'<?xml version="1.0" encoding="UTF-8"?>\n'
        tree = self._get_tree()
        bytes_tree = tostring(tree, encoding="unicode").encode("utf8")
        return xml_header + bytes_tree  # type: ignore[no-any-return]

    def pretty_serialize(self) -> bytes:
        """Serializes the XML part to bytes with pretty-printing.

        Returns:
            bytes: The pretty-printed XML content as bytes, including the
                XML declaration.
        """
        xml_header = b'<?xml version="1.0" encoding="UTF-8"?>\n'
        bytes_tree = tostring(
            self.custom_pretty_tree(),
            encoding="unicode",
        ).encode("utf8")
        return xml_header + bytes_tree  # type: ignore[no-any-return]

    def custom_pretty_tree(self) -> _ElementTree | _Element:
        """Returns a pretty-printed version of the XML tree.

        This method applies custom indentation for readability.

        Returns:
            _ElementTree | _Element: The pretty-printed XML tree or its root.
        """
        tree = self._get_tree()
        root = tree.getroot()
        return pretty_indent(root)
