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
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
"""XmlPart base class for XML parts
"""
from copy import deepcopy
from io import BytesIO

from lxml.etree import parse, tostring

from .element import Element


class XmlPart:
    """Representation of an XML part.
    Abstraction of the XML library behind.
    """

    def __init__(self, part_name, container):
        self.part_name = part_name
        self.container = container

        # Internal state
        self.__tree = None
        self.__root = None

    def __get_tree(self):
        if self.__tree is None:
            container = self.container
            part = container.get_part(self.part_name)
            self.__tree = parse(BytesIO(part))
        return self.__tree

    # Public API

    @property
    def root(self):
        if self.__root is None:
            tree = self.__get_tree()
            self.__root = Element.from_tag(tree.getroot())
        return self.__root

    def get_elements(self, xpath_query):
        root = self.root
        return root.xpath(xpath_query)

    def get_element(self, xpath_query):
        result = self.get_elements(xpath_query)
        if not result:
            return None
        return result[0]

    def delete_element(self, child):
        child.delete()

    def xpath(self, xpath_query):
        """Apply XPath query to the XML part. Return list of Element or
        Text instances translated from the nodes found.
        """
        root = self.root
        return root.xpath(xpath_query)

    @property
    def clone(self):
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

    def serialize(self, pretty=False):
        tree = self.__get_tree()
        # Lxml declaration is too exotic to me
        data = [b'<?xml version="1.0" encoding="UTF-8"?>']
        tree = tostring(tree, pretty_print=pretty, encoding="UTF-8")
        # Lxml with pretty_print is adding a empty line
        if pretty:
            tree = tree.strip()
        data.append(tree)
        return b"\n".join(data)
