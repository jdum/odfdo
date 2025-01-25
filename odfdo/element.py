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
#          Romain Gauthier <romain@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
"""Element, super class of all ODF classes.
"""
from __future__ import annotations

import contextlib
import re
import sys
from collections.abc import Callable, Iterable
from copy import deepcopy
from datetime import datetime, timedelta
from decimal import Decimal
from functools import cache
from re import search
from typing import Any, NamedTuple

from lxml.etree import Element as lxml_Element
from lxml.etree import XPath, _Element, fromstring, tostring

from .const import ODF_COLOR_PROPERTY, OFFICE_PREFIX, OFFICE_VERSION
from .datatype import Boolean, DateTime
from .mixin_md import MDBase
from .utils import (
    FAMILY_MAPPING,
    FAMILY_ODF_STD,
    hexa_color,
    make_xpath_query,
    str_to_bytes,
    to_str,
)

ODF_NAMESPACES = {
    "anim": "urn:oasis:names:tc:opendocument:xmlns:animation:1.0",
    "calcext": "urn:org:documentfoundation:names:experimental:calc:xmlns:calcext:1.0",
    "chart": "urn:oasis:names:tc:opendocument:xmlns:chart:1.0",
    "config": "urn:oasis:names:tc:opendocument:xmlns:config:1.0",
    "css3t": "http://www.w3.org/TR/css3-text/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dom": "http://www.w3.org/2001/xml-events",
    "dr3d": "urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0",
    "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
    "drawooo": "http://openoffice.org/2010/draw",
    "field": "urn:openoffice:names:experimental:ooo-ms-interop:xmlns:field:1.0",
    "fo": "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
    "form": "urn:oasis:names:tc:opendocument:xmlns:form:1.0",
    "formx": "urn:openoffice:names:experimental:ooxml-odf-interop:xmlns:form:1.0",
    "grddl": "http://www.w3.org/2003/g/data-view#",
    "loext": "urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0",
    "manifest": "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0",
    "math": "http://www.w3.org/1998/Math/MathML",
    "meta": "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
    "number": "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0",
    "of": "urn:oasis:names:tc:opendocument:xmlns:of:1.2",
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "officeooo": "http://openoffice.org/2009/office",
    "ooo": "http://openoffice.org/2004/office",
    "oooc": "http://openoffice.org/2004/calc",
    "ooow": "http://openoffice.org/2004/writer",
    "presentation": "urn:oasis:names:tc:opendocument:xmlns:presentation:1.0",
    "rdfa": "http://docs.oasis-open.org/opendocument/meta/rdfa#",
    "rpt": "http://openoffice.org/2005/report",
    "script": "urn:oasis:names:tc:opendocument:xmlns:script:1.0",
    "smil": "urn:oasis:names:tc:opendocument:xmlns:smil-compatible:1.0",
    "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "svg": "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "tableooo": "http://openoffice.org/2009/table",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "xforms": "http://www.w3.org/2002/xforms",
    "xhtml": "http://www.w3.org/1999/xhtml",
    "xlink": "http://www.w3.org/1999/xlink",
    "xml": "http://www.w3.org/XML/1998/namespace",
    "xsd": "http://www.w3.org/2001/XMLSchema",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}
FIRST_CHILD = 0
LAST_CHILD = 1
NEXT_SIBLING = 2
PREV_SIBLING = 3
STOPMARKER = 5

"office:version="
# An empty XML document with all namespaces declared
NAMESPACES_XML = (
    OFFICE_PREFIX
    + f'office:version="{OFFICE_VERSION}">'.encode()
    + b"%s</office:document>"
)

_re_anyspace = re.compile(r" +")


class PropDef(NamedTuple):
    name: str
    attr: str
    family: str = ""


def _decode_qname(qname: str) -> tuple[str | None, str]:
    """Turn a prefixed qualified name to a (uri, name) pair."""
    if ":" in qname:
        prefix, name = qname.split(":")
        try:
            uri = ODF_NAMESPACES[prefix]
        except KeyError as e:
            raise ValueError(f'XML prefix "{prefix}" is unknown') from e
        return uri, name
    return None, qname


def _uri_to_prefix(uri: str) -> str:
    """Find the prefix associated to the given URI."""
    for key, value in ODF_NAMESPACES.items():
        if value == uri:
            return key
    raise ValueError(f"uri {uri!r} not found")


def _get_prefixed_name(tag: str) -> str:
    """Replace lxml "{uri}name" syntax with "prefix:name" one."""
    if "}" not in tag:
        return f":{tag}"
    uri, name = tag.split("}", 1)
    prefix = _uri_to_prefix(uri[1:])
    return f"{prefix}:{name}"


def _get_lxml_tag(qname: str) -> str:
    """Replace "prefix:name" syntax with lxml "{uri}name" one."""
    uri, name = _decode_qname(qname)
    return f"{{{uri}}}{name}"


def _get_lxml_tag_or_name(qname: str) -> str:
    """Replace "prefix:name" syntax with lxml "{uri}name" one or "name"."""
    uri, name = _decode_qname(qname)
    if uri is None:
        return name
    return f"{{{uri}}}{name}"


def _family_style_tagname(family: str) -> str:
    try:
        return FAMILY_MAPPING[family]
    except KeyError as e:
        raise ValueError(f"unknown family: {family}") from e


@cache
def xpath_compile(path: str) -> XPath:
    return XPath(path, namespaces=ODF_NAMESPACES, regexp=False)


_xpath_text = xpath_compile("//text()")  #  descendant and self
_xpath_text_descendant = xpath_compile("descendant::text()")
_xpath_text_main = xpath_compile("//*[not (parent::office:annotation)]/text()")
_xpath_text_main_descendant = xpath_compile(
    "descendant::text()[not (parent::office:annotation)]"
)

_class_registry: dict[str, type[Element]] = {}


def register_element_class(cls: type[Element]) -> None:
    """Associate a qualified element name to a Python class that handles this
    type of element.

    Getting the right Python class when loading an existing ODF document is
    then transparent. Unassociated elements will be handled by the base
    Element class.

    Arguments:

        cls -- Python class, subtype of Element.
    """
    # Turn tag name into what lxml is expecting
    _register_element_class(cls, cls._tag)


def register_element_class_list(cls: type[Element], tag_list: Iterable[str]) -> None:
    """Associate a qualified element name to a Python class that handles this
    type of element.

    Getting the right Python class when loading an existing ODF document is
    then transparent. Unassociated elements will be handled by the base
    Element class.

    Most styles use the "style:style" qualified name and only differ by their
    "style:family" attribute. So the "family" attribute was added to register
    specialized style classes.

    Arguments:

        cls -- Python class

        tag_list -- iterable of qname tags for the class
    """
    # Turn tag name into what lxml is expecting
    for qname in tag_list:
        _register_element_class(cls, qname)


def _register_element_class(cls: type[Element], qname: str) -> None:
    # Turn tag name into what lxml is expecting
    tag = _get_lxml_tag(qname)
    if tag not in _class_registry:
        _class_registry[tag] = cls


class EText(str):
    """Representation of an XML text node. Created to hide the specifics of
    lxml in searching text nodes using XPath.

    Constructed like any str object but only accepts lxml text objects.
    """

    # There's some black magic in inheriting from str
    def __init__(
        self,
        text_result: str | bytes,
    ) -> None:
        self.__parent = text_result.getparent()  # type: ignore
        self.__is_text = text_result.is_text
        self.__is_tail = text_result.is_tail

    @property
    def parent(self) -> Element | None:
        parent = self.__parent
        # XXX happens just because of the unit test
        if parent is None:
            return None
        return Element.from_tag(tag_or_elem=parent)

    def is_text(self) -> bool:
        return self.__is_text

    def is_tail(self) -> bool:
        return self.__is_tail


class Element(MDBase):
    """Super class of all ODF classes.

    Representation of an XML element. Abstraction of the XML library behind.
    """

    _tag: str = ""
    _properties: tuple[PropDef, ...] = ()

    def __init__(self, **kwargs: Any) -> None:
        tag_or_elem = kwargs.pop("tag_or_elem", None)
        if tag_or_elem is None:
            # Instance for newly created object: create new lxml element and
            # continue by subclass __init__
            # If the tag key word exists, make a custom element
            self._do_init = True
            tag = kwargs.pop("tag", self._tag)
            self.__element = self.make_etree_element(tag)
        else:
            # called with an existing lxml element, sould be a result of
            # from_tag() casting, do not execute the subclass __init__
            if not isinstance(tag_or_elem, _Element):
                raise TypeError(f'"{type(tag_or_elem)}" is not an element node')
            self._do_init = False
            self.__element = tag_or_elem

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} tag={self.tag}>"

    @classmethod
    def from_tag(cls, tag_or_elem: str | _Element) -> Element:
        """Element class and subclass factory.

        Turn an lxml Element or ODF string tag into an ODF XML Element
        of the relevant class.

        Arguments:

            tag_or_elem -- ODF str tag or lxml.Element

        Return: Element (or subclass) instance
        """
        if isinstance(tag_or_elem, str):
            # assume the argument is a prefix:name tag
            elem = cls.make_etree_element(tag_or_elem)
        else:
            elem = tag_or_elem
        klass = _class_registry.get(elem.tag, cls)
        return klass(tag_or_elem=elem)

    @classmethod
    def from_tag_for_clone(
        cls: Any,  # ABCMeta, type, ...
        tree_element: _Element,
        cache: tuple | None,
    ) -> Element:
        tag = to_str(tree_element.tag)
        klass = _class_registry.get(tag, cls)
        element = klass(tag_or_elem=tree_element)
        element._copy_cache(cache)
        return element

    def _copy_cache(self, cache: tuple | None) -> None:
        """Method eredefined for cahched elements."""
        pass

    @staticmethod
    def make_etree_element(tag: str) -> _Element:
        if not isinstance(tag, str):
            raise TypeError(f"Tag is not str: {tag!r}")
        tag = tag.strip()
        if not tag:
            raise ValueError("Tag is empty")
        if "<" not in tag:
            # Qualified name
            # XXX don't build the element from scratch or lxml will pollute with
            # repeated namespace declarations
            tag = f"<{tag}/>"
        # XML fragment
        root = fromstring(NAMESPACES_XML % str_to_bytes(tag))
        return root[0]

    @staticmethod
    def _generic_attrib_getter(attr_name: str, family: str | None = None) -> Callable:
        name = _get_lxml_tag(attr_name)

        def getter(self: Element) -> str | bool | None:
            try:
                if family and self.family != family:  # type: ignore
                    return None
            except AttributeError:
                return None
            value = self.__element.get(name)
            if value is None:
                return None
            elif value in ("true", "false"):
                return Boolean.decode(value)
            return str(value)

        return getter

    @staticmethod
    def _generic_attrib_setter(attr_name: str, family: str | None = None) -> Callable:
        name = _get_lxml_tag(attr_name)

        def setter(self: Element, value: Any) -> None:
            try:
                if family and self.family != family:  # type: ignore
                    return None
            except AttributeError:
                return None
            if value is None:
                with contextlib.suppress(KeyError):
                    del self.__element.attrib[name]
                return
            if isinstance(value, bool):
                value = Boolean.encode(value)
            self.__element.set(name, str(value))

        return setter

    @classmethod
    def _define_attribut_property(cls: type[Element]) -> None:
        for prop in cls._properties:
            setattr(
                cls,
                prop.name,
                property(
                    cls._generic_attrib_getter(prop.attr, prop.family or None),
                    cls._generic_attrib_setter(prop.attr, prop.family or None),
                    None,
                    f"Get/set the attribute {prop.attr}",
                ),
            )

    @staticmethod
    def _make_before_regex(
        before: str | None,
        after: str | None,
    ) -> re.Pattern:
        # 1) before xor after is not None
        if before is not None:
            return re.compile(before)
        else:
            if after is None:
                raise ValueError("Both 'before' and 'after' are None")
            return re.compile(after)

    @staticmethod
    def _search_negative_position(
        xpath_result: list,
        regex: re.Pattern,
    ) -> tuple[str, re.Match]:
        # Found the last text that matches the regex
        text = None
        for a_text in xpath_result:
            if regex.search(str(a_text)) is not None:
                text = a_text
        if text is None:
            raise ValueError(f"Text not found: '{xpath_result}'")
        if not isinstance(text, str):
            raise TypeError(f"Text not found or text not of type str: '{text}'")
        return text, list(regex.finditer(text))[-1]

    @staticmethod
    def _search_positive_position(
        xpath_result: list,
        regex: re.Pattern,
        position: int,
    ) -> tuple[str, re.Match]:
        # Found the last text that matches the regex
        count = 0
        for text in xpath_result:
            found_nb = len(regex.findall(str(text)))
            if found_nb + count >= position + 1:
                break
            count += found_nb
        else:
            raise ValueError(f"Text not found: '{xpath_result}'")
        if not isinstance(text, str):
            raise TypeError(f"Text not found or text not of type str: '{text}'")
        return text, list(regex.finditer(text))[position - count]

    def _insert_before_after(
        self,
        current: _Element,
        element: _Element,
        before: str | None,
        after: str | None,
        position: int,
        xpath_text: XPath,
    ) -> tuple[int, str]:
        regex = self._make_before_regex(before, after)
        xpath_result = xpath_text(current)
        if not isinstance(xpath_result, list):
            raise TypeError("Bad XPath result")
        # position = -1
        if position < 0:
            text, sre = self._search_negative_position(xpath_result, regex)
        # position >= 0
        else:
            text, sre = self._search_positive_position(xpath_result, regex, position)
        # Compute pos
        if before is None:
            pos = sre.end()
        else:
            pos = sre.start()
        return pos, text

    def _insert_find_text(
        self,
        current: _Element,
        element: _Element,
        before: str | None,
        after: str | None,
        position: int,
        xpath_text: XPath,
    ) -> tuple[int, str]:
        # Find the text
        xpath_result = xpath_text(current)
        if not isinstance(xpath_result, list):
            raise TypeError("Bad XPath result")
        count = 0
        for text in xpath_result:
            if not isinstance(text, str):
                continue
            found_nb = len(text)
            if found_nb + count >= position:
                break
            count += found_nb
        else:
            raise ValueError("Text not found")
        # We insert before the character
        pos = position - count
        return pos, text

    def _insert(
        self,
        element: Element,
        before: str | None = None,
        after: str | None = None,
        position: int = 0,
        main_text: bool = False,
    ) -> None:
        """Insert an element before or after the characters in the text which
        match the regex before/after.

        When the regex matches more of one part of the text, position can be
        set to choice which part must be used. If before and after are None,
        we use only position that is the number of characters. If position is
        positive and before=after=None, we insert before the position
        character. But if position=-1, we insert after the last character.


        Arguments:

        element -- Element

        before -- str regex

        after -- str regex

        position -- int
        """
        # not implemented: if main_text is True, filter out the annotations texts in computation.
        current = self.__element
        xelement = element.__element

        if main_text:
            xpath_text = _xpath_text_main_descendant
        else:
            xpath_text = _xpath_text_descendant

        # 1) before xor after is not None
        if (before is not None) ^ (after is not None):
            pos, text = self._insert_before_after(
                current,
                xelement,
                before,
                after,
                position,
                xpath_text,
            )
        # 2) before=after=None => only with position
        elif before is None and after is None:
            # Hack if position is negative => quickly
            if position < 0:
                current.append(xelement)
                return
            pos, text = self._insert_find_text(
                current,
                xelement,
                before,
                after,
                position,
                xpath_text,
            )
        else:
            raise ValueError("bad combination of arguments")

        # Compute new texts
        text_before = text[:pos] if text[:pos] else None
        text_after = text[pos:] if text[pos:] else None

        # Insert!
        parent = text.getparent()  # type: ignore
        if text.is_text:  # type: ignore
            parent.text = text_before
            element.tail = text_after
            parent.insert(0, xelement)
        else:
            parent.addnext(xelement)
            parent.tail = text_before
            element.tail = text_after

    def _insert_between(  # noqa: C901
        self,
        element: Element,
        from_: str,
        to: str,
    ) -> None:
        """Insert the given empty element to wrap the text beginning with
        "from_" and ending with "to".

        Example 1: '<p>toto tata titi</p>

        We want to insert a link around "tata".

        Result 1: '<p>toto <a>tata</a> titi</p>

        Example 2: '<p><span>toto</span> tata titi</p>

        We want to insert a link around "tata".

        Result 2: '<p><span>toto</span> <a>tata</a> titi</p>

        Example 3: '<p>toto <span> tata </span> titi</p>'

        We want to insert a link from "tata" to "titi" included.

        Result 3: '<p>toto <span> </span>'
                  '<a><span>tata </span> titi</a></p>'

        Example 4: '<p>toto <span>tata titi</span> tutu</p>'

        We want to insert a link from "titi" to "tutu"

        Result 4: '<p>toto <span>tata </span><a><span>titi</span></a>'
                  '<a> tutu</a></p>'

        Example 5: '<p>toto <span>tata titi</span> '
                   '<span>tutu tyty</span></p>'

        We want to insert a link from "titi" to "tutu"

        Result 5: '<p>toto <span>tata </span><a><span>titi</span><a> '
                  '<a> <span>tutu</span></a><span> tyty</span></p>'
        """
        current = self.__element
        wrapper = element.__element

        xpath_result = _xpath_text_descendant(current)
        if not isinstance(xpath_result, list):
            raise TypeError("Bad XPath result")

        for text in xpath_result:
            if not isinstance(text, str):
                raise TypeError("Text not found or text not of type str")
            if from_ not in text:
                continue
            from_index = text.index(from_)
            text_before = text[:from_index]
            text_after = text[from_index:]
            from_container = text.getparent()  # type: ignore
            if not isinstance(from_container, _Element):
                raise TypeError("Bad XPath result")
            # Include from_index to match a single word
            to_index = text.find(to, from_index)
            if to_index >= 0:
                # Simple case: "from" and "to" in the same element
                to_end = to_index + len(to)
                if text.is_text:  # type: ignore
                    from_container.text = text_before
                    wrapper.text = text[to_index:to_end]
                    wrapper.tail = text[to_end:]
                    from_container.insert(0, wrapper)
                else:
                    from_container.tail = text_before
                    wrapper.text = text[to_index:to_end]
                    wrapper.tail = text[to_end:]
                    parent = from_container.getparent()
                    index = parent.index(from_container)  # type: ignore
                    parent.insert(index + 1, wrapper)  # type: ignore
                return
            else:
                # Exit to the second part where we search for the end text
                break
        else:
            raise ValueError("Start text not found")

        # The container is split in two
        container2 = deepcopy(from_container)
        if text.is_text:  # type: ignore
            from_container.text = text_before
            from_container.tail = None
            container2.text = text_after
            from_container.tail = None
        else:
            from_container.tail = text_before
            container2.tail = text_after
        # Stack the copy into the surrounding element
        wrapper.append(container2)
        parent = from_container.getparent()
        index = parent.index(from_container)  # type: ignore
        parent.insert(index + 1, wrapper)  # type: ignore

        xpath_result = _xpath_text_descendant(wrapper)
        if not isinstance(xpath_result, list):
            raise TypeError("Bad XPath result")

        for text in xpath_result:
            if not isinstance(text, str):
                raise TypeError("Text not found or text not of type str")
            if to not in text:
                continue
            to_end = text.index(to) + len(to)
            text_before = text[:to_end]
            text_after = text[to_end:]
            container_to = text.getparent()  # type: ignore
            if not isinstance(container_to, _Element):
                raise TypeError("Bad XPath result")
            if text.is_text:  # type: ignore
                container_to.text = text_before
                container_to.tail = text_after
            else:
                container_to.tail = text_before
                next_one = container_to.getnext()
                if next_one is None:
                    next_one = container_to.getparent()
                next_one.tail = text_after  # type: ignore
            return
        raise ValueError("End text not found")

    @property
    def tag(self) -> str:
        """Get/set the underlying xml tag with the given qualified name.

        Warning: direct change of tag does not change the element class.

        Arguments:

            qname -- str (e.g. "text:span")
        """
        return _get_prefixed_name(self.__element.tag)

    @tag.setter
    def tag(self, qname: str) -> None:
        self.__element.tag = _get_lxml_tag(qname)

    def elements_repeated_sequence(
        self,
        xpath_instance: XPath,
        name: str,
    ) -> list[tuple[int, int]]:
        """Utility method for table module."""
        lxml_tag = _get_lxml_tag_or_name(name)
        element = self.__element
        sub_elements = xpath_instance(element)
        if not isinstance(sub_elements, list):
            raise TypeError("Bad XPath result.")
        result: list[tuple[int, int]] = []
        idx = -1
        for sub_element in sub_elements:
            if not isinstance(sub_element, _Element):
                continue
            idx += 1
            value = sub_element.get(lxml_tag)
            if value is None:
                result.append((idx, 1))
                continue
            try:
                int_value = int(value)
            except ValueError:
                int_value = 1
            result.append((idx, max(int_value, 1)))
        return result

    def get_elements(self, xpath_query: XPath | str) -> list[Element]:
        cache: tuple | None = None
        element = self.__element
        if isinstance(xpath_query, str):
            new_xpath_query = xpath_compile(xpath_query)
            result = new_xpath_query(element)
        else:
            result = xpath_query(element)
        if not isinstance(result, list):
            raise TypeError("Bad XPath result")
        return [
            Element.from_tag_for_clone(e, cache)
            for e in result
            if isinstance(e, _Element)
        ]

    # fixme : need original get_element as wrapper of get_elements

    def get_element(self, xpath_query: XPath | str) -> Element | None:
        element = self.__element
        result = element.xpath(f"({xpath_query})[1]", namespaces=ODF_NAMESPACES)
        if result:
            return Element.from_tag(result[0])  # type:ignore
        return None

    def _get_element_idx(self, xpath_query: XPath | str, idx: int) -> Element | None:
        element = self.__element
        result = element.xpath(f"({xpath_query})[{idx + 1}]", namespaces=ODF_NAMESPACES)
        if result:
            return Element.from_tag(result[0])  # type:ignore
        return None

    def _get_element_idx2(self, xpath_instance: XPath, idx: int) -> Element | None:
        element = self.__element
        result = xpath_instance(element, idx=idx + 1)
        if result:
            return Element.from_tag(result[0])  # type:ignore
        return None

    @property
    def attributes(self) -> dict[str, str]:
        return {
            _get_prefixed_name(str(key)): str(value)
            for key, value in self.__element.attrib.items()
        }

    def get_attribute(self, name: str) -> str | bool | None:
        """Return the attribute value as type str | bool | None."""
        element = self.__element
        lxml_tag = _get_lxml_tag_or_name(name)
        value = element.get(lxml_tag)
        if value is None:
            return None
        elif value in ("true", "false"):
            return Boolean.decode(value)
        return str(value)

    def get_attribute_integer(self, name: str) -> int | None:
        """Return either the attribute as type int, or None."""
        element = self.__element
        lxml_tag = _get_lxml_tag_or_name(name)
        value = element.get(lxml_tag)
        if value is None:
            return None
        try:
            return int(value)
        except ValueError:
            return None

    def get_attribute_string(self, name: str) -> str | None:
        """Return either the attribute as type str, or None."""
        element = self.__element
        lxml_tag = _get_lxml_tag_or_name(name)
        value = element.get(lxml_tag)
        if value is None:
            return None
        return str(value)

    def set_attribute(
        self, name: str, value: bool | str | tuple[int, int, int] | None
    ) -> None:
        if name in ODF_COLOR_PROPERTY:
            if isinstance(value, bool):
                raise TypeError(f"Wrong color type {value!r}")
            if value != "transparent":
                value = hexa_color(value)
        element = self.__element
        lxml_tag = _get_lxml_tag_or_name(name)
        if isinstance(value, bool):
            value = Boolean.encode(value)
        elif value is None:
            with contextlib.suppress(KeyError):
                del element.attrib[lxml_tag]
            return
        element.set(lxml_tag, str(value))

    def set_style_attribute(self, name: str, value: Element | str) -> None:
        """Shortcut to accept a style object as a value."""
        if isinstance(value, Element):
            value = str(value.name)  # type:ignore
        return self.set_attribute(name, value)

    def del_attribute(self, name: str) -> None:
        element = self.__element
        lxml_tag = _get_lxml_tag_or_name(name)
        del element.attrib[lxml_tag]

    @property
    def text(self) -> str:
        """Get / set the text content of the element."""
        return self.__element.text or ""

    @text.setter
    def text(self, text: str | None) -> None:
        if text is None:
            text = ""
        try:
            self.__element.text = text
        except TypeError as e:
            raise TypeError(f'Str type expected: "{type(text)}"') from e

    def __str__(self) -> str:
        return self.inner_text

    @property
    def _text_tail(self) -> str:
        return str(self) + (self.tail or "")

    # def _elements_descendants(self) -> Iterator[Element]:
    #     for elem in self.__element.iterdescendants():
    #         if isinstance(elem, _Element):
    #             yield Element.from_tag(elem)

    @property
    def inner_text(self) -> str:
        return self.text + "".join(e._text_tail for e in self.children)

    @property
    def text_recursive(self) -> str:
        return self.inner_text + (self.tail or "")

    @property
    def tail(self) -> str | None:
        """Get / set the text immediately following the element."""
        return self.__element.tail

    @tail.setter
    def tail(self, text: str | None) -> None:
        self.__element.tail = text or ""

    def search(self, pattern: str) -> int | None:
        """Return the first position of the pattern in the text content of
        the element, or None if not found.

        Python regular expression syntax applies.

        Arguments:

            pattern -- str

        Return: int or None
        """
        match = re.search(pattern, self.text_recursive)
        if match is None:
            return None
        return match.start()

    def search_first(self, pattern: str) -> tuple[int, int] | None:
        """Return the start and end position of the first occurence
        of the regex pattern in the text content of the element.

        Result is tuples of start and end position, or None.
        Python regular expression syntax applies.

        Arguments:

            pattern -- str

        Return: tuple[int,int] or None
        """
        match = re.search(pattern, self.text_recursive)
        if match is None:
            return None
        return match.start(), match.end()

    def search_all(self, pattern: str) -> list[tuple[int, int]]:
        """Return all start and end positions of the regex pattern in
        the text content of the element.

        Result is a list of tuples of start and end position of
        the matches.
        Python regular expression syntax applies.

        Arguments:

            pattern -- str

        Return: list[tuple[int,int]]
        """
        results: list[tuple[int, int]] = []
        for match in re.finditer(pattern, self.text_recursive):
            results.append((match.start(), match.end()))
        return results

    def text_at(self, start: int, end: int | None = None) -> str:
        """Return the text (recursive) content of the element between
        start and end position.

        If the end parameter is not set, return from start to the end
        of the recursive text.

        Arguments:

            start -- int
            end -- int or None

        Return: str
        """
        if start < 0:
            start = 0
        if end is None:
            return self.text_recursive[start:]
        else:
            if end < start:
                end = start
            return self.text_recursive[start:end]

    def match(self, pattern: str) -> bool:
        """return True if the pattern is found one or more times anywhere in
        the text content of the element.

        Python regular expression syntax applies.

        Arguments:

            pattern -- str

        Return: bool
        """
        return self.search(pattern) is not None

    def replace(
        self,
        pattern: str,
        new: str | None = None,
        formatted: bool = False,
    ) -> int:
        """Replace the pattern with the given text, or delete if text is an
        empty string, and return the number of replacements. By default, only
        return the number of occurences that would be replaced.

        It cannot replace patterns found across several element, like a word
        split into two consecutive spans.

        Python regular expression syntax applies.

        If formatted is True, and the target is a Paragraph, Span or Header,
        and the replacement text contains spaces, tabs or newlines, try to
        convert them into actual ODF elements to obtain a formatted result.
        On very complex contents, result may differ of expectations.

        Arguments:

            pattern -- str

            new -- str

            formatted -- bool

        Return: int
        """
        if not isinstance(pattern, str):
            # Fail properly if the pattern is an non-ascii bytestring
            pattern = str(pattern)
        cpattern = re.compile(pattern)
        count = 0
        for text in self.xpath("descendant::text()"):
            if new is None:
                count += len(cpattern.findall(str(text)))
            else:
                new_text, number = cpattern.subn(new, str(text))
                container = text.parent
                if not container:
                    continue
                if text.is_text():  # type: ignore
                    container.text = new_text  # type: ignore
                else:
                    container.tail = new_text  # type: ignore
                if formatted and container.tag in {  # type; ignore
                    "text:h",
                    "text:p",
                    "text:span",
                }:
                    container.append_plain_text("")  # type; ignore
                count += number
        return count

    @property
    def root(self) -> Element:
        element = self.__element
        tree = element.getroottree()
        root = tree.getroot()
        return Element.from_tag(root)

    @property
    def parent(self) -> Element | None:
        element = self.__element
        parent = element.getparent()
        if parent is None:
            # Already at root
            return None
        return Element.from_tag(parent)

    @property
    def is_bound(self) -> bool:
        return self.parent is not None

    # def get_next_sibling(self):
    #     element = self.__element
    #     next_one = element.getnext()
    #     if next_one is None:
    #         return None
    #     return Element.from_tag(next_one)
    #
    # def get_prev_sibling(self):
    #     element = self.__element
    #     prev = element.getprevious()
    #     if prev is None:
    #         return None
    #     return Element.from_tag(prev)

    @property
    def children(self) -> list[Element]:
        element = self.__element
        return [
            Element.from_tag(e)
            for e in element.iterchildren()
            if isinstance(e, _Element)
        ]

    def index(self, child: Element) -> int:
        """Return the position of the child in this element.

        Inspired by lxml
        """
        return self.__element.index(child.__element)

    @property
    def text_content(self) -> str:
        """Get / set the text of the embedded paragraphs, including embeded
        annotations, cells...

        Set does create a paragraph if missing.
        """
        content = "".join(
            str(child) for child in self.get_elements("descendant::text:p")
        )
        if content.endswith("\n"):
            return content[:-1]
        return content

    @text_content.setter
    def text_content(self, text: str | None) -> None:
        paragraphs = self.get_elements("text:p")
        if not paragraphs:
            # E.g., text:p in draw:text-box in draw:frame
            paragraphs = self.get_elements("*/text:p")
        if paragraphs:
            paragraph = paragraphs.pop(0)
            for obsolete in paragraphs:
                obsolete.delete()
        else:
            paragraph = Element.from_tag("text:p")
            self.insert(paragraph, FIRST_CHILD)
        # As "text_content" returned all text nodes, "text_content"
        # will overwrite all text nodes and children that may contain them
        element = paragraph.__element
        # Clear but the attributes
        del element[:]
        element.text = text

    def _erase_text_content(self) -> None:
        paragraphs = self.get_elements("text:p")
        if not paragraphs:
            # E.g., text:p in draw:text-box in draw:frame
            paragraphs = self.get_elements("*/text:p")
        if paragraphs:
            paragraphs.pop(0)
            for obsolete in paragraphs:
                obsolete.delete()

    def is_empty(self) -> bool:
        """Check if the element is empty : no text, no children, no tail.

        Return: Boolean
        """
        element = self.__element
        if element.tail is not None:
            return False
        if element.text is not None:
            return False
        if list(element.iterchildren()):
            return False
        return True

    def _get_successor(self, target: Element) -> tuple[Element | None, Element | None]:
        element = self.__element
        next_one = element.getnext()
        if next_one is not None:
            return Element.from_tag(next_one), target
        parent = self.parent
        if parent is None:
            return None, None
        return parent._get_successor(target.parent)  # type:ignore

    def _get_between_base(  # noqa:C901
        self,
        tag1: Element,
        tag2: Element,
    ) -> list[Element]:
        def find_any_id(elem: Element) -> tuple[str, str, str]:
            elem_tag = elem.tag
            for attribute in (
                "text:id",
                "text:change-id",
                "text:name",
                "office:name",
                "text:ref-name",
                "xml:id",
            ):
                idx = elem.get_attribute(attribute)
                if idx is not None:
                    return elem_tag, attribute, str(idx)
            raise ValueError(f"No Id found in {elem.serialize()}")

        def common_ancestor(
            tag1: str,
            attr1: str,
            val1: str,
            tag2: str,
            attr2: str,
            val2: str,
        ) -> Element | None:
            root = self.root
            request1 = f'descendant::{tag1}[@{attr1}="{val1}"]'
            request2 = f'descendant::{tag2}[@{attr2}="{val2}"]'
            ancestor = root.xpath(request1)[0]
            if ancestor is None:
                return None
            while True:
                # print "up",
                new_ancestor = ancestor.parent
                if new_ancestor is None:
                    return None
                has_tag2 = new_ancestor.xpath(request2)
                ancestor = new_ancestor
                if not has_tag2:
                    continue
                # print 'found'
                break
            # print up.serialize()
            return ancestor

        elem1_tag, elem1_attr, elem1_val = find_any_id(tag1)
        elem2_tag, elem2_attr, elem2_val = find_any_id(tag2)
        ancestor_result = common_ancestor(
            elem1_tag,
            elem1_attr,
            elem1_val,
            elem2_tag,
            elem2_attr,
            elem2_val,
        )
        if ancestor_result is None:
            raise RuntimeError(f"No common ancestor for {elem1_tag} {elem2_tag}")
        ancestor = ancestor_result.clone
        path1 = f'{elem1_tag}[@{elem1_attr}="{elem1_val}"]'
        path2 = f'{elem2_tag}[@{elem2_attr}="{elem2_val}"]'
        result = ancestor.clone
        for child in result.children:
            result.delete(child)
        result.text = ""
        result.tail = ""
        target = result
        current = ancestor.children[0]

        state = 0
        while True:
            if current is None:
                raise RuntimeError(f"No current ancestor for {elem1_tag} {elem2_tag}")
            # print 'current', state, current.serialize()
            if state == 0:  # before tag 1
                if current.xpath(f"descendant-or-self::{path1}"):
                    if current.xpath(f"self::{path1}"):
                        tail = current.tail
                        if tail:
                            # got a tail => the parent should be either t:p or t:h
                            target.text = tail  # type: ignore
                        current, target = current._get_successor(target)  # type: ignore
                        state = 1
                        continue
                    # got T1 in chidren, need further analysis
                    new_target = current.clone
                    for child in new_target.children:
                        new_target.delete(child)
                    new_target.text = ""
                    new_target.tail = ""
                    target.__append(new_target)  # type: ignore
                    target = new_target
                    current = current.children[0]
                    continue
                else:
                    # before tag1 : forget element, go to next one
                    current, target = current._get_successor(target)  # type: ignore
                    continue
            elif state == 1:  # collect elements
                further = False
                if current.xpath(f"descendant-or-self::{path2}"):
                    if current.xpath(f"self::{path2}"):
                        # end of trip
                        break
                    # got T2 in chidren, need further analysis
                    further = True
                # further analysis needed :
                if further:
                    new_target = current.clone
                    for child in new_target.children:
                        new_target.delete(child)
                    new_target.text = ""
                    new_target.tail = ""
                    target.__append(new_target)  # type: ignore
                    target = new_target
                    current = current.children[0]
                    continue
                # collect
                target.__append(current.clone)  # type: ignore
                current, target = current._get_successor(target)  # type: ignore
                continue
        # Now resu should be the "parent" of inserted parts
        # - a text:h or text:p sigle item (simple case)
        # - a upper element, with some text:p, text:h in it => need to be
        #   stripped to have a list of text:p, text:h
        if result.tag in {"text:p", "text:h"}:
            inner = [result]
        else:
            inner = result.children
        return inner

    def get_between(
        self,
        tag1: Element,
        tag2: Element,
        as_text: bool = False,
        clean: bool = True,
        no_header: bool = True,
    ) -> list | Element | str:
        """Returns elements between tag1 and tag2, tag1 and tag2 shall
        be unique and having an id attribute.
        (WARN: buggy if tag1/tag2 defines a malformed odf xml.)
        If as_text is True: returns the text content.
        If clean is True: suppress unwanted tags (deletions marks, ...)
        If no_header is True: existing text:h are changed in text:p
        By default: returns a list of Element, cleaned and without headers.

        Implementation and standard retrictions:
        Only text:h and text:p sould be 'cut' by an insert tag, so inner parts
        of insert tags are:

            - any text:h, text:p or sub tag of these

            - some text, part of a parent text:h or text:p

        Arguments:

            tag1 -- Element

            tag2 -- Element

            as_text -- boolean

            clean -- boolean

            no_header -- boolean

        Return: list of odf_paragraph or odf_header
        """
        inner = self._get_between_base(tag1, tag2)

        if clean:
            clean_tags = (
                "text:change",
                "text:change-start",
                "text:change-end",
                "text:reference-mark",
                "text:reference-mark-start",
                "text:reference-mark-end",
            )
            request_self = " | ".join([f"self::{tag}" for tag in clean_tags])
            inner = [e for e in inner if not e.xpath(request_self)]
            request = " | ".join([f"descendant::{tag}" for tag in clean_tags])
            for element in inner:
                to_del = element.xpath(request)
                for elem in to_del:
                    if isinstance(elem, Element):
                        element.delete(elem)
        if no_header:  # crude replace t:h by t:p
            new_inner = []
            for element in inner:
                if element.tag == "text:h":
                    children = element.children
                    text = element.__element.text
                    para = Element.from_tag("text:p")
                    para.text = text or ""
                    for child in children:
                        para.__append(child)
                    new_inner.append(para)
                else:
                    new_inner.append(element)
            inner = new_inner
        if as_text:
            return "\n".join([e.get_formatted_text() for e in inner])
        else:
            return inner

    def insert(
        self,
        element: Element,
        xmlposition: int | None = None,
        position: int | None = None,
        start: bool = False,
    ) -> None:
        """Insert an element relatively to ourself.

        Insert either using DOM vocabulary or by numeric position.
        If text start is True, insert the element before any existing text.

        Position start at 0.

        Arguments:

            element -- Element

            xmlposition -- FIRST_CHILD, LAST_CHILD, NEXT_SIBLING
                           or PREV_SIBLING

            start -- Boolean

            position -- int
        """
        # child_tag = element.tag
        current = self.__element
        _element = element.__element
        if start:
            text = current.text
            if text is not None:
                current.text = None
                tail = _element.tail
                if tail is None:
                    tail = text
                else:
                    tail = tail + text
                _element.tail = tail
            position = 0
        if position is not None:
            current.insert(position, _element)
        elif xmlposition is FIRST_CHILD:
            current.insert(0, _element)
        elif xmlposition is LAST_CHILD:
            current.append(_element)
        elif xmlposition is NEXT_SIBLING:
            parent = current.getparent()
            index = parent.index(current)  # type: ignore
            parent.insert(index + 1, _element)  # type: ignore
        elif xmlposition is PREV_SIBLING:
            parent = current.getparent()
            index = parent.index(current)  # type: ignore
            parent.insert(index, _element)  # type: ignore
        else:
            raise ValueError("(xml)position must be defined")

    def extend(self, odf_elements: Iterable[Element]) -> None:
        """Fast append elements at the end of ourself using extend."""
        if odf_elements:
            current = self.__element
            elements = [element.__element for element in odf_elements]
            current.extend(elements)

    @staticmethod
    def _add_text(text1: str | None, text2: str | None) -> str:
        if text1 is None:
            text1 = ""
        if text2 is None:
            text2 = ""
        return _re_anyspace.sub(" ", text1 + text2)

    def _cut_text_tail(self) -> str:
        removed = ""
        current = self.__element
        children = list(current.iterchildren())
        if children:
            # Append to tail of the last child
            last_child = children[-1]
            if last_child.tail:
                removed = last_child.tail
                last_child.tail = ""
        else:
            removed = current.text or ""
            current.text = ""
        return removed

    def __append(self, str_or_element: str | Element) -> None:
        """Insert element or text in the last position."""
        current = self.__element
        if isinstance(str_or_element, str):
            # Has children ?
            children = list(current.iterchildren())
            if children:
                # Append to tail of the last child
                last_child = children[-1]
                last_child.tail = self._add_text(last_child.tail, str_or_element)
            else:
                # Append to text of the element
                current.text = self._add_text(current.text, str_or_element)
        elif isinstance(str_or_element, Element):
            current.append(str_or_element.__element)
        else:
            raise TypeError(f'Element or string expected, not "{type(str_or_element)}"')

    append = __append

    def delete(self, child: Element | None = None, keep_tail: bool = True) -> None:
        """Delete the given element from the XML tree. If no element is given,
        "self" is deleted. The XML library may allow to continue to use an
        element now "orphan" as long as you have a reference to it.

        if keep_tail is True (default), the tail text is not erased.

        Arguments:

            child -- Element

            keep_tail -- boolean (default to True), True for most usages.
        """
        if child is None:
            parent = self.parent
            if parent is None:
                raise ValueError(f"Can't delete the root element\n{self.serialize()}")
            child = self
        else:
            parent = self
        if keep_tail and child.__element.tail is not None:
            current = child.__element
            tail = str(current.tail)
            current.tail = None
            prev = current.getprevious()
            if prev is not None:
                if prev.tail is None:
                    prev.tail = tail
                else:
                    prev.tail += tail
            else:
                if parent.__element.text is None:
                    parent.__element.text = tail
                else:
                    parent.__element.text += tail
        parent.__element.remove(child.__element)

    def replace_element(self, old_element: Element, new_element: Element) -> None:
        """Replaces in place a sub element with the element passed as second
        argument.

        Warning : no clone for old element.
        """
        current = self.__element
        current.replace(old_element.__element, new_element.__element)

    def strip_elements(
        self,
        sub_elements: Element | Iterable[Element],
    ) -> Element | list:
        """Remove the tags of provided elements, keeping inner childs and text.

        Return : the striped element.

        Warning : no clone in sub_elements list.

        Arguments:

            sub_elements -- Element or list of Element
        """
        if not sub_elements:
            return self
        if isinstance(sub_elements, Element):
            sub_elements = (sub_elements,)
        replacer = _get_lxml_tag("text:this-will-be-removed")
        for element in sub_elements:
            element.__element.tag = replacer
        strip = ("text:this-will-be-removed",)
        return self.strip_tags(strip=strip, default=None)

    def strip_tags(
        self,
        strip: Iterable[str] | None = None,
        protect: Iterable[str] | None = None,
        default: str | None = "text:p",
    ) -> Element | list:
        """Remove the tags listed in strip, recursively, keeping inner childs
        and text. Tags listed in protect stop the removal one level depth. If
        the first level element is stripped, default is used to embed the
        content in the default element. If default is None and first level is
        striped, a list of text and children is returned. Return : the striped
        element.

        strip_tags should be used by on purpose methods (strip_span ...)
        (Method name taken from lxml).

        Arguments:

            strip -- iterable list of str odf tags, or None

            protect -- iterable list of str odf tags, or None

            default -- str odf tag, or None

        Return:

            Element.
        """
        if not strip:
            return self
        if not protect:
            protect = ()
        protected = False
        element, modified = Element._strip_tags(self, strip, protect, protected)
        if modified and isinstance(element, list) and default:
            new = Element.from_tag(default)
            for content in element:
                if isinstance(content, Element):
                    new.__append(content)
                else:
                    new.text = content
            element = new
        return element

    @staticmethod
    def _strip_tags(  # noqa:C901
        element: Element,
        strip: Iterable[str],
        protect: Iterable[str],
        protected: bool,
    ) -> tuple[Element | list, bool]:
        """Sub method for strip_tags()."""
        element_clone = element.clone
        modified = False
        children = []
        if protect and element.tag in protect:
            protect_below = True
        else:
            protect_below = False
        for child in element_clone.children:
            striped_child, is_modified = Element._strip_tags(
                child, strip, protect, protect_below
            )
            if is_modified:
                modified = True
            if isinstance(striped_child, list):
                children.extend(striped_child)
            else:
                children.append(striped_child)

        text = element_clone.text
        tail = element_clone.tail
        if not protected and strip and element.tag in strip:
            element_result: list[Element | str] = []
            if text is not None:
                element_result.append(text)
            for child in children:
                element_result.append(child)
            if tail is not None:
                element_result.append(tail)
            return (element_result, True)
        else:
            if not modified:
                return (element, False)
            element.clear()
            try:
                for key, value in element_clone.attributes.items():
                    element.set_attribute(key, value)
            except ValueError:
                sys.stderr.write(f"strip_tags(): bad attribute in {element_clone}\n")
            if text is not None:
                element.__append(text)
            for child in children:
                element.__append(child)
            if tail is not None:
                element.tail = tail
            return (element, True)

    def xpath(self, xpath_query: str) -> list[Element | EText]:
        """Apply XPath query to the element and its subtree. Return list of
        Element or EText instances translated from the nodes found.
        """
        element = self.__element
        xpath_instance = xpath_compile(xpath_query)
        elements = xpath_instance(element)
        result: list[Element | EText] = []
        if hasattr(elements, "__iter__"):
            for obj in elements:  # type: ignore
                if isinstance(obj, (str, bytes)):
                    result.append(EText(obj))
                elif isinstance(obj, _Element):
                    result.append(Element.from_tag(obj))
                # else:
                #     result.append(obj)
        return result

    def clear(self) -> None:
        """Remove text, children and attributes from the element."""
        self.__element.clear()

    @property
    def clone(self) -> Element:
        clone = deepcopy(self.__element)
        root = lxml_Element("ROOT", nsmap=ODF_NAMESPACES)
        root.append(clone)
        return self.from_tag(clone)

        # slow data = tostring(self.__element, encoding='unicode')
        # return self.from_tag(data)

    @staticmethod
    def _strip_namespaces(data: str) -> str:
        """Remove xmlns:* fields from serialized XML."""
        return re.sub(r' xmlns:\w*="[\w:\-\/\.#]*"', "", data)

    def serialize(self, pretty: bool = False, with_ns: bool = False) -> str:
        """Return text serialization of XML element."""
        # This copy bypasses serialization side-effects in lxml
        native = deepcopy(self.__element)
        data = tostring(
            native, with_tail=False, pretty_print=pretty, encoding="unicode"
        )
        if with_ns:
            return data
        # Remove namespaces
        return self._strip_namespaces(data)

    # Element helpers usable from any context

    @property
    def document_body(self) -> Element | None:
        """Return the first children of document body if any: 'office:body/*[1]'"""
        return self.get_element("//office:body/*[1]")

    def get_formatted_text(self, context: dict | None = None) -> str:
        """This function should return a beautiful version of the text."""
        return ""

    def get_styled_elements(self, name: str = "") -> list[Element]:
        """Brute-force to find paragraphs, tables, etc. using the given style
        name (or all by default).

        Arguments:

            name -- str

        Return: list
        """
        # FIXME incomplete (and possibly inaccurate)
        return (
            self._filtered_elements("descendant::*", text_style=name)
            + self._filtered_elements("descendant::*", draw_style=name)
            + self._filtered_elements("descendant::*", draw_text_style=name)
            + self._filtered_elements("descendant::*", table_style=name)
            + self._filtered_elements("descendant::*", page_layout=name)
            + self._filtered_elements("descendant::*", master_page=name)
            + self._filtered_elements("descendant::*", parent_style=name)
        )

    # Common attributes

    def _get_inner_text(self, tag: str) -> str | None:
        element = self.get_element(tag)
        if element is None:
            return None
        return element.text

    def _set_inner_text(self, tag: str, text: str) -> None:
        element = self.get_element(tag)
        if element is None:
            element = Element.from_tag(tag)
            self.__append(element)
        element.text = text

    # SVG

    @property
    def svg_title(self) -> str | None:
        return self._get_inner_text("svg:title")

    @svg_title.setter
    def svg_title(self, title: str) -> None:
        self._set_inner_text("svg:title", title)

    @property
    def svg_description(self) -> str | None:
        return self._get_inner_text("svg:desc")

    @svg_description.setter
    def svg_description(self, description: str) -> None:
        self._set_inner_text("svg:desc", description)

    # Sections

    def get_sections(
        self,
        style: str | None = None,
        content: str | None = None,
    ) -> list[Element]:
        """Return all the sections that match the criteria.

        Arguments:

            style -- str

            content -- str regex

        Return: list of Element
        """
        return self._filtered_elements(
            "text:section", text_style=style, content=content
        )

    @property
    def sections(
        self,
    ) -> list[Element]:
        """Return all the sections.

        Return: list of Element
        """
        return self.get_elements("text:section")

    def get_section(
        self,
        position: int = 0,
        content: str | None = None,
    ) -> Element | None:
        """Return the section that matches the criteria.

        Arguments:

            position -- int

            content -- str regex

        Return: Element or None if not found
        """
        return self._filtered_element(
            "descendant::text:section", position, content=content
        )

    # Paragraphs

    def get_paragraphs(
        self,
        style: str | None = None,
        content: str | None = None,
    ) -> list[Element]:
        """Return all the paragraphs that match the criteria.

        Arguments:

            style -- str

            content -- str regex

        Return: list of Paragraph
        """
        return self._filtered_elements(
            "descendant::text:p", text_style=style, content=content
        )

    @property
    def paragraphs(self) -> list[Element]:
        """Return all the paragraphs.

        Return: list of Paragraph
        """
        return self.get_elements("descendant::text:p")

    def get_paragraph(
        self,
        position: int = 0,
        content: str | None = None,
    ) -> Element | None:
        """Return the paragraph that matches the criteria.

        Arguments:

            position -- int

            content -- str regex

        Return: Paragraph or None if not found
        """
        return self._filtered_element("descendant::text:p", position, content=content)

    # Span

    def get_spans(
        self,
        style: str | None = None,
        content: str | None = None,
    ) -> list[Element]:
        """Return all the spans that match the criteria.

        Arguments:

            style -- str

            content -- str regex

        Return: list of Span
        """
        return self._filtered_elements(
            "descendant::text:span", text_style=style, content=content
        )

    @property
    def spans(self) -> list[Element]:
        """Return all the spans.

        Return: list of Span
        """
        return self.get_elements("descendant::text:span")

    def get_span(
        self,
        position: int = 0,
        content: str | None = None,
    ) -> Element | None:
        """Return the span that matches the criteria.

        Arguments:

            position -- int

            content -- str regex

        Return: Span or None if not found
        """
        return self._filtered_element(
            "descendant::text:span", position, content=content
        )

    # Headers

    def get_headers(
        self,
        style: str | None = None,
        outline_level: str | None = None,
        content: str | None = None,
    ) -> list[Element]:
        """Return all the Headers that match the criteria.

        Arguments:

            style -- str

            content -- str regex

        Return: list of Header
        """
        return self._filtered_elements(
            "descendant::text:h",
            text_style=style,
            outline_level=outline_level,
            content=content,
        )

    @property
    def headers(self) -> list[Element]:
        """Return all the Headers.

        Return: list of Header
        """
        return self.get_elements("descendant::text:h")

    def get_header(
        self,
        position: int = 0,
        outline_level: str | None = None,
        content: str | None = None,
    ) -> Element | None:
        """Return the Header that matches the criteria.

        Arguments:

            position -- int

            content -- str regex

        Return: Header or None if not found
        """
        return self._filtered_element(
            "descendant::text:h",
            position,
            outline_level=outline_level,
            content=content,
        )

    # Lists

    def get_lists(
        self,
        style: str | None = None,
        content: str | None = None,
    ) -> list[Element]:
        """Return all the lists that match the criteria.

        Arguments:

            style -- str

            content -- str regex

        Return: list of List
        """
        return self._filtered_elements(
            "descendant::text:list", text_style=style, content=content
        )

    @property
    def lists(self) -> list[Element]:
        """Return all the lists.

        Return: list of List
        """
        return self.get_elements("descendant::text:list")

    def get_list(
        self,
        position: int = 0,
        content: str | None = None,
    ) -> Element | None:
        """Return the list that matches the criteria.

        Arguments:

            position -- int

            content -- str regex

        Return: List or None if not found
        """
        return self._filtered_element(
            "descendant::text:list", position, content=content
        )

    # Frames

    def get_frames(
        self,
        presentation_class: str | None = None,
        style: str | None = None,
        title: str | None = None,
        description: str | None = None,
        content: str | None = None,
    ) -> list[Element]:
        """Return all the frames that match the criteria.

        Arguments:

            presentation_class -- str

            style -- str

            title -- str regex

            description -- str regex

            content -- str regex

        Return: list of Frame
        """
        return self._filtered_elements(
            "descendant::draw:frame",
            presentation_class=presentation_class,
            draw_style=style,
            svg_title=title,
            svg_desc=description,
            content=content,
        )

    @property
    def frames(self) -> list[Element]:
        """Return all the frames.

        Return: list of Frame
        """
        return self.get_elements("descendant::draw:frame")

    def get_frame(
        self,
        position: int = 0,
        name: str | None = None,
        presentation_class: str | None = None,
        title: str | None = None,
        description: str | None = None,
        content: str | None = None,
    ) -> Element | None:
        """Return the section that matches the criteria.

        Arguments:

            position -- int

            name -- str

            presentation_class -- str

            title -- str regex

            description -- str regex

            content -- str regex

        Return: Frame or None if not found
        """
        return self._filtered_element(
            "descendant::draw:frame",
            position,
            draw_name=name,
            presentation_class=presentation_class,
            svg_title=title,
            svg_desc=description,
            content=content,
        )

    # Images

    def get_images(
        self,
        style: str | None = None,
        url: str | None = None,
        content: str | None = None,
    ) -> list[Element]:
        """Return all the images matching the criteria.

        Arguments:

            style -- str

            url -- str regex

            content -- str regex

        Return: list of Element
        """
        return self._filtered_elements(
            "descendant::draw:image", text_style=style, url=url, content=content
        )

    @property
    def images(self) -> list[Element]:
        """Return all the images.

        Return: list of Element
        """
        return self.get_elements("descendant::draw:image")

    def get_image(
        self,
        position: int = 0,
        name: str | None = None,
        url: str | None = None,
        content: str | None = None,
    ) -> Element | None:
        """Return the image matching the criteria.

        Arguments:

            position -- int

            name -- str

            url -- str regex

            content -- str regex

        Return: Element or None if not found
        """
        # The frame is holding the name
        if name is not None:
            frame = self._filtered_element(
                "descendant::draw:frame", position, draw_name=name
            )
            if frame is None:
                return None
            # The name is supposedly unique
            return frame.get_element("draw:image")
        return self._filtered_element(
            "descendant::draw:image", position, url=url, content=content
        )

    # Named Range

    def get_named_ranges(self) -> list[Element]:
        """Return all the tables named ranges.

        Return: list of odf_named_range
        """
        named_ranges = self.get_elements(
            "descendant::table:named-expressions/table:named-range"
        )
        return named_ranges

    def get_named_range(self, name: str) -> Element | None:
        """Return the named range of specified name, or None if not found.

        Arguments:

            name -- str

        Return: NamedRange
        """
        named_range = self.get_elements(
            f'descendant::table:named-expressions/table:named-range[@table:name="{name}"][1]'
        )
        if named_range:
            return named_range[0]
        else:
            return None

    def append_named_range(self, named_range: Element) -> None:
        """Append the named range to the spreadsheet, replacing existing named
        range of same name if any.

        Arguments:

            named_range --  NamedRange
        """
        if self.tag != "office:spreadsheet":
            raise ValueError(f"Element is no 'office:spreadsheet' : {self.tag}")
        named_expressions = self.get_element("table:named-expressions")
        if not named_expressions:
            named_expressions = Element.from_tag("table:named-expressions")
            self.__append(named_expressions)
        # exists ?
        current = named_expressions.get_element(
            f'table:named-range[@table:name="{named_range.name}"][1]'  # type:ignore
        )
        if current:
            named_expressions.delete(current)
        named_expressions.__append(named_range)

    def delete_named_range(self, name: str) -> None:
        """Delete the Named Range of specified name from the spreadsheet.

        Arguments:

            name -- str
        """
        if self.tag != "office:spreadsheet":
            raise ValueError(f"Element is no 'office:spreadsheet' : {self.tag}")
        named_range = self.get_named_range(name)
        if not named_range:
            return
        named_range.delete()
        named_expressions = self.get_element("table:named-expressions")
        if not named_expressions:
            return
        element = named_expressions.__element
        children = list(element.iterchildren())
        if not children:
            self.delete(named_expressions)

    # Notes

    def get_notes(
        self,
        note_class: str | None = None,
        content: str | None = None,
    ) -> list[Element]:
        """Return all the notes that match the criteria.

        Arguments:

            note_class -- 'footnote' or 'endnote'

            content -- str regex

        Return: list of Note
        """
        return self._filtered_elements(
            "descendant::text:note", note_class=note_class, content=content
        )

    def get_note(
        self,
        position: int = 0,
        note_id: str | None = None,
        note_class: str | None = None,
        content: str | None = None,
    ) -> Element | None:
        """Return the note that matches the criteria.

        Arguments:

            position -- int

            note_id -- str

            note_class -- 'footnote' or 'endnote'

            content -- str regex

        Return: Note or None if not found
        """
        return self._filtered_element(
            "descendant::text:note",
            position,
            text_id=note_id,
            note_class=note_class,
            content=content,
        )

    # Annotations

    def get_annotations(
        self,
        creator: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        content: str | None = None,
    ) -> list[Element]:
        """Return all the annotations that match the criteria.

        Arguments:

            creator -- str

            start_date -- datetime instance

            end_date --  datetime instance

            content -- str regex

        Return: list of Annotation
        """
        annotations = []
        for annotation in self._filtered_elements(
            "descendant::office:annotation", content=content
        ):
            if creator is not None and creator != annotation.dc_creator:
                continue
            date = annotation.date
            if date is None:
                continue
            if start_date is not None and date < start_date:
                continue
            if end_date is not None and date >= end_date:
                continue
            annotations.append(annotation)
        return annotations

    def get_annotation(
        self,
        position: int = 0,
        creator: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        content: str | None = None,
        name: str | None = None,
    ) -> Element | None:
        """Return the annotation that matches the criteria.

        Arguments:

            position -- int

            creator -- str

            start_date -- datetime instance

            end_date -- datetime instance

            content -- str regex

            name -- str

        Return: Annotation or None if not found
        """
        if name is not None:
            return self._filtered_element(
                "descendant::office:annotation", 0, office_name=name
            )
        annotations = self.get_annotations(
            creator=creator, start_date=start_date, end_date=end_date, content=content
        )
        if not annotations:
            return None
        try:
            return annotations[position]
        except IndexError:
            return None

    def get_annotation_ends(self) -> list[Element]:
        """Return all the annotation ends.

        Return: list of Element
        """
        return self._filtered_elements("descendant::office:annotation-end")

    def get_annotation_end(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> Element | None:
        """Return the annotation end that matches the criteria.

        Arguments:

            position -- int

            name -- str

        Return: Element or None if not found
        """
        return self._filtered_element(
            "descendant::office:annotation-end", position, office_name=name
        )

    # office:names

    def get_office_names(self) -> list[str]:
        """Return all the used office:name tags values of the element.

        Return: list of unique str
        """
        name_xpath_query = xpath_compile("//@office:name")
        response = name_xpath_query(self.__element)
        if not isinstance(response, list):
            return []
        return list({str(name) for name in response if name})

    # Variables

    def get_variable_decls(self) -> Element:
        """Return the container for variable declarations. Created if not
        found.

        Return: Element
        """
        variable_decls = self.get_element("//text:variable-decls")
        if variable_decls is None:
            body = self.document_body
            if not body:
                raise ValueError("Empty document.body")
            body.insert(Element.from_tag("text:variable-decls"), FIRST_CHILD)
            variable_decls = body.get_element("//text:variable-decls")

        return variable_decls  # type:ignore

    def get_variable_decl_list(self) -> list[Element]:
        """Return all the variable declarations.

        Return: list of Element
        """
        return self._filtered_elements("descendant::text:variable-decl")

    def get_variable_decl(self, name: str, position: int = 0) -> Element | None:
        """return the variable declaration for the given name.

        Arguments:

            name -- str

            position -- int

        return: Element or none if not found
        """
        return self._filtered_element(
            "descendant::text:variable-decl", position, text_name=name
        )

    def get_variable_sets(self, name: str | None = None) -> list[Element]:
        """Return all the variable sets that match the criteria.

        Arguments:

            name -- str

        Return: list of Element
        """
        return self._filtered_elements("descendant::text:variable-set", text_name=name)

    def get_variable_set(self, name: str, position: int = -1) -> Element | None:
        """Return the variable set for the given name (last one by default).

        Arguments:

            name -- str

            position -- int

        Return: Element or None if not found
        """
        return self._filtered_element(
            "descendant::text:variable-set", position, text_name=name
        )

    def get_variable_set_value(
        self,
        name: str,
        value_type: str | None = None,
    ) -> bool | str | int | float | Decimal | datetime | timedelta | None:
        """Return the last value of the given variable name.

        Arguments:

            name -- str

            value_type -- 'boolean', 'currency', 'date', 'float',
                          'percentage', 'string', 'time' or automatic

        Return: most appropriate Python type
        """
        variable_set = self.get_variable_set(name)
        if not variable_set:
            return None
        return variable_set.get_value(value_type)  # type: ignore

    # User fields

    def get_user_field_decls(self) -> Element | None:
        """Return the container for user field declarations. Created if not
        found.

        Return: Element
        """
        user_field_decls = self.get_element("//text:user-field-decls")
        if user_field_decls is None:
            body = self.document_body
            if not body:
                raise ValueError("Empty document.body")
            body.insert(Element.from_tag("text:user-field-decls"), FIRST_CHILD)
            user_field_decls = body.get_element("//text:user-field-decls")

        return user_field_decls

    def get_user_field_decl_list(self) -> list[Element]:
        """Return all the user field declarations.

        Return: list of Element
        """
        return self._filtered_elements("descendant::text:user-field-decl")

    def get_user_field_decl(self, name: str, position: int = 0) -> Element | None:
        """return the user field declaration for the given name.

        return: Element or none if not found
        """
        return self._filtered_element(
            "descendant::text:user-field-decl", position, text_name=name
        )

    def get_user_field_value(
        self, name: str, value_type: str | None = None
    ) -> bool | str | int | float | Decimal | datetime | timedelta | None:
        """Return the value of the given user field name.

        Arguments:

            name -- str

            value_type -- 'boolean', 'currency', 'date', 'float',
                          'percentage', 'string', 'time' or automatic

        Return: most appropriate Python type
        """
        user_field_decl = self.get_user_field_decl(name)
        if user_field_decl is None:
            return None
        return user_field_decl.get_value(value_type)  # type: ignore

    # User defined fields
    # They are fields who should contain a copy of a user defined medtadata

    def get_user_defined_list(self) -> list[Element]:
        """Return all the user defined field declarations.

        Return: list of Element
        """
        return self._filtered_elements("descendant::text:user-defined")

    @property
    def user_defined_list(self) -> list[Element]:
        """Return all the user defined field declarations.

        Return: list of Element
        """
        return self.get_user_defined_list()

    def get_user_defined(self, name: str, position: int = 0) -> Element | None:
        """return the user defined declaration for the given name.

        return: Element or none if not found
        """
        return self._filtered_element(
            "descendant::text:user-defined", position, text_name=name
        )

    def get_user_defined_value(
        self, name: str, value_type: str | None = None
    ) -> bool | str | int | float | Decimal | datetime | timedelta | None:
        """Return the value of the given user defined field name.

        Arguments:

            name -- str

            value_type -- 'boolean', 'date', 'float',
                          'string', 'time' or automatic

        Return: most appropriate Python type
        """
        user_defined = self.get_user_defined(name)
        if user_defined is None:
            return None
        return user_defined.get_value(value_type)  # type: ignore

    # Draw Pages

    def get_draw_pages(
        self,
        style: str | None = None,
        content: str | None = None,
    ) -> list[Element]:
        """Return all the draw pages that match the criteria.

        Arguments:

            style -- str

            content -- str regex

        Return: list of DrawPage
        """
        return self._filtered_elements(
            "descendant::draw:page", draw_style=style, content=content
        )

    def get_draw_page(
        self,
        position: int = 0,
        name: str | None = None,
        content: str | None = None,
    ) -> Element | None:
        """Return the draw page that matches the criteria.

        Arguments:

            position -- int

            name -- str

            content -- str regex

        Return: DrawPage or None if not found
        """
        return self._filtered_element(
            "descendant::draw:page", position, draw_name=name, content=content
        )

    # Links

    def get_links(
        self,
        name: str | None = None,
        title: str | None = None,
        url: str | None = None,
        content: str | None = None,
    ) -> list[Element]:
        """Return all the links that match the criteria.

        Arguments:

            name -- str

            title -- str

            url -- str regex

            content -- str regex

        Return: list of Element
        """
        return self._filtered_elements(
            "descendant::text:a",
            office_name=name,
            office_title=title,
            url=url,
            content=content,
        )

    def get_link(
        self,
        position: int = 0,
        name: str | None = None,
        title: str | None = None,
        url: str | None = None,
        content: str | None = None,
    ) -> Element | None:
        """Return the link that matches the criteria.

        Arguments:

            position -- int

            name -- str

            title -- str

            url -- str regex

            content -- str regex

        Return: Element or None if not found
        """
        return self._filtered_element(
            "descendant::text:a",
            position,
            office_name=name,
            office_title=title,
            url=url,
            content=content,
        )

    # Bookmarks

    def get_bookmarks(self) -> list[Element]:
        """Return all the bookmarks.

        Return: list of Element
        """
        return self._filtered_elements("descendant::text:bookmark")

    def get_bookmark(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> Element | None:
        """Return the bookmark that matches the criteria.

        Arguments:

            position -- int

            name -- str

        Return: Bookmark or None if not found
        """
        return self._filtered_element(
            "descendant::text:bookmark", position, text_name=name
        )

    def get_bookmark_starts(self) -> list[Element]:
        """Return all the bookmark starts.

        Return: list of Element
        """
        return self._filtered_elements("descendant::text:bookmark-start")

    def get_bookmark_start(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> Element | None:
        """Return the bookmark start that matches the criteria.

        Arguments:

            position -- int

            name -- str

        Return: Element or None if not found
        """
        return self._filtered_element(
            "descendant::text:bookmark-start", position, text_name=name
        )

    def get_bookmark_ends(self) -> list[Element]:
        """Return all the bookmark ends.

        Return: list of Element
        """
        return self._filtered_elements("descendant::text:bookmark-end")

    def get_bookmark_end(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> Element | None:
        """Return the bookmark end that matches the criteria.

        Arguments:

            position -- int

            name -- str

        Return: Element or None if not found
        """
        return self._filtered_element(
            "descendant::text:bookmark-end", position, text_name=name
        )

    # Reference marks

    def get_reference_marks_single(self) -> list[Element]:
        """Return all the reference marks. Search only the tags
        text:reference-mark.
        Consider using : get_reference_marks()

        Return: list of Element
        """
        return self._filtered_elements("descendant::text:reference-mark")

    def get_reference_mark_single(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> Element | None:
        """Return the reference mark that matches the criteria. Search only the
        tags text:reference-mark.
        Consider using : get_reference_mark()

        Arguments:

            position -- int

            name -- str

        Return: Element or None if not found
        """
        return self._filtered_element(
            "descendant::text:reference-mark", position, text_name=name
        )

    def get_reference_mark_starts(self) -> list[Element]:
        """Return all the reference mark starts. Search only the tags
        text:reference-mark-start.
        Consider using : get_reference_marks()

        Return: list of Element
        """
        return self._filtered_elements("descendant::text:reference-mark-start")

    def get_reference_mark_start(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> Element | None:
        """Return the reference mark start that matches the criteria. Search
        only the tags text:reference-mark-start.
        Consider using : get_reference_mark()

        Arguments:

            position -- int

            name -- str

        Return: Element or None if not found
        """
        return self._filtered_element(
            "descendant::text:reference-mark-start", position, text_name=name
        )

    def get_reference_mark_ends(self) -> list[Element]:
        """Return all the reference mark ends. Search only the tags
        text:reference-mark-end.
        Consider using : get_reference_marks()

        Return: list of Element
        """
        return self._filtered_elements("descendant::text:reference-mark-end")

    def get_reference_mark_end(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> Element | None:
        """Return the reference mark end that matches the criteria. Search only
        the tags text:reference-mark-end.
        Consider using : get_reference_marks()

        Arguments:

            position -- int

            name -- str

        Return: Element or None if not found
        """
        return self._filtered_element(
            "descendant::text:reference-mark-end", position, text_name=name
        )

    def get_reference_marks(self) -> list[Element]:
        """Return all the reference marks, either single position reference
        (text:reference-mark) or start of range reference
        (text:reference-mark-start).

        Return: list of Element
        """
        return self._filtered_elements(
            "descendant::text:reference-mark-start | descendant::text:reference-mark"
        )

    def get_reference_mark(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> Element | None:
        """Return the reference mark that match the criteria. Either single
        position reference mark (text:reference-mark) or start of range
        reference (text:reference-mark-start).

        Arguments:

            position -- int

            name -- str

        Return: Element or None if not found
        """
        if name:
            request = (
                f"descendant::text:reference-mark-start"
                f'[@text:name="{name}"] '
                f"| descendant::text:reference-mark"
                f'[@text:name="{name}"]'
            )
            return self._filtered_element(request, position=0)
        request = (
            "descendant::text:reference-mark-start | descendant::text:reference-mark"
        )
        return self._filtered_element(request, position)

    def get_references(self, name: str | None = None) -> list[Element]:
        """Return all the references (text:reference-ref). If name is
        provided, returns the references of that name.

        Return: list of Element

        Arguments:

            name -- str or None
        """
        if name is None:
            return self._filtered_elements("descendant::text:reference-ref")
        request = f'descendant::text:reference-ref[@text:ref-name="{name}"]'
        return self._filtered_elements(request)

    # Shapes elements

    # Groups

    def get_draw_groups(
        self,
        title: str | None = None,
        description: str | None = None,
        content: str | None = None,
    ) -> list[Element]:
        return self._filtered_elements(
            "descendant::draw:g",
            svg_title=title,
            svg_desc=description,
            content=content,
        )

    def get_draw_group(
        self,
        position: int = 0,
        name: str | None = None,
        title: str | None = None,
        description: str | None = None,
        content: str | None = None,
    ) -> Element | None:
        return self._filtered_element(
            "descendant::draw:g",
            position,
            draw_name=name,
            svg_title=title,
            svg_desc=description,
            content=content,
        )

    # Lines

    def get_draw_lines(
        self,
        draw_style: str | None = None,
        draw_text_style: str | None = None,
        content: str | None = None,
    ) -> list[Element]:
        """Return all the draw lines that match the criteria.

        Arguments:

            draw_style -- str

            draw_text_style -- str

            content -- str regex

        Return: list of odf_shape
        """
        return self._filtered_elements(
            "descendant::draw:line",
            draw_style=draw_style,
            draw_text_style=draw_text_style,
            content=content,
        )

    def get_draw_line(
        self,
        position: int = 0,
        id: str | None = None,  # noqa:A002
        content: str | None = None,
    ) -> Element | None:
        """Return the draw line that matches the criteria.

        Arguments:

            position -- int

            id -- str

            content -- str regex

        Return: odf_shape or None if not found
        """
        return self._filtered_element(
            "descendant::draw:line", position, draw_id=id, content=content
        )

    # Rectangles

    def get_draw_rectangles(
        self,
        draw_style: str | None = None,
        draw_text_style: str | None = None,
        content: str | None = None,
    ) -> list[Element]:
        """Return all the draw rectangles that match the criteria.

        Arguments:

            draw_style -- str

            draw_text_style -- str

            content -- str regex

        Return: list of odf_shape
        """
        return self._filtered_elements(
            "descendant::draw:rect",
            draw_style=draw_style,
            draw_text_style=draw_text_style,
            content=content,
        )

    def get_draw_rectangle(
        self,
        position: int = 0,
        id: str | None = None,  # noqa:A002
        content: str | None = None,
    ) -> Element | None:
        """Return the draw rectangle that matches the criteria.

        Arguments:

            position -- int

            id -- str

            content -- str regex

        Return: odf_shape or None if not found
        """
        return self._filtered_element(
            "descendant::draw:rect", position, draw_id=id, content=content
        )

    # Ellipse

    def get_draw_ellipses(
        self,
        draw_style: str | None = None,
        draw_text_style: str | None = None,
        content: str | None = None,
    ) -> list[Element]:
        """Return all the draw ellipses that match the criteria.

        Arguments:

            draw_style -- str

            draw_text_style -- str

            content -- str regex

        Return: list of odf_shape
        """
        return self._filtered_elements(
            "descendant::draw:ellipse",
            draw_style=draw_style,
            draw_text_style=draw_text_style,
            content=content,
        )

    def get_draw_ellipse(
        self,
        position: int = 0,
        id: str | None = None,  # noqa:A002
        content: str | None = None,
    ) -> Element | None:
        """Return the draw ellipse that matches the criteria.

        Arguments:

            position -- int

            id -- str

            content -- str regex

        Return: odf_shape or None if not found
        """
        return self._filtered_element(
            "descendant::draw:ellipse", position, draw_id=id, content=content
        )

    # Connectors

    def get_draw_connectors(
        self,
        draw_style: str | None = None,
        draw_text_style: str | None = None,
        content: str | None = None,
    ) -> list[Element]:
        """Return all the draw connectors that match the criteria.

        Arguments:

            draw_style -- str

            draw_text_style -- str

            content -- str regex

        Return: list of odf_shape
        """
        return self._filtered_elements(
            "descendant::draw:connector",
            draw_style=draw_style,
            draw_text_style=draw_text_style,
            content=content,
        )

    def get_draw_connector(
        self,
        position: int = 0,
        id: str | None = None,  # noqa:A002
        content: str | None = None,
    ) -> Element | None:
        """Return the draw connector that matches the criteria.

        Arguments:

            position -- int

            id -- str

            content -- str regex

        Return: odf_shape or None if not found
        """
        return self._filtered_element(
            "descendant::draw:connector", position, draw_id=id, content=content
        )

    def get_orphan_draw_connectors(self) -> list[Element]:
        """Return a list of connectors which don't have any shape connected
        to them.
        """
        connectors = []
        for connector in self.get_draw_connectors():
            start_shape = connector.get_attribute("draw:start-shape")
            end_shape = connector.get_attribute("draw:end-shape")
            if start_shape is None and end_shape is None:
                connectors.append(connector)
        return connectors

    # Tracked changes and text change

    def get_tracked_changes(self) -> Element | None:
        """Return the tracked-changes part in the text body.

        Return: Element or None
        """
        return self.get_element("//text:tracked-changes")

    @property
    def tracked_changes(self) -> Element | None:
        """Return the tracked-changes part in the text body.

        Return: Element or None
        """
        return self.get_tracked_changes()

    def get_changes_ids(self) -> list[Element | EText]:
        """Return a list of ids that refers to a change region in the tracked
        changes list.
        """
        # Insertion changes
        xpath_query = "descendant::text:change-start/@text:change-id"
        # Deletion changes
        xpath_query += " | descendant::text:change/@text:change-id"
        return self.xpath(xpath_query)

    def get_text_change_deletions(self) -> list[Element]:
        """Return all the text changes of deletion kind: the tags text:change.
        Consider using : get_text_changes()

        Return: list of Element
        """
        return self._filtered_elements("descendant::text:text:change")

    def get_text_change_deletion(
        self,
        position: int = 0,
        idx: str | None = None,
    ) -> Element | None:
        """Return the text change of deletion kind that matches the criteria.
        Search only for the tags text:change.
        Consider using : get_text_change()

        Arguments:

            position -- int

            idx -- str

        Return: Element or None if not found
        """
        return self._filtered_element(
            "descendant::text:change", position, change_id=idx
        )

    def get_text_change_starts(self) -> list[Element]:
        """Return all the text change-start. Search only for the tags
        text:change-start.
        Consider using : get_text_changes()

        Return: list of Element
        """
        return self._filtered_elements("descendant::text:change-start")

    def get_text_change_start(
        self,
        position: int = 0,
        idx: str | None = None,
    ) -> Element | None:
        """Return the text change-start that matches the criteria. Search
        only the tags text:change-start.
        Consider using : get_text_change()

        Arguments:

            position -- int

            idx -- str

        Return: Element or None if not found
        """
        return self._filtered_element(
            "descendant::text:change-start", position, change_id=idx
        )

    def get_text_change_ends(self) -> list[Element]:
        """Return all the text change-end. Search only the tags
        text:change-end.
        Consider using : get_text_changes()

        Return: list of Element
        """
        return self._filtered_elements("descendant::text:change-end")

    def get_text_change_end(
        self,
        position: int = 0,
        idx: str | None = None,
    ) -> Element | None:
        """Return the text change-end that matches the criteria. Search only
        the tags text:change-end.
        Consider using : get_text_change()

        Arguments:

            position -- int

            idx -- str

        Return: Element or None if not found
        """
        return self._filtered_element(
            "descendant::text:change-end", position, change_id=idx
        )

    def get_text_changes(self) -> list[Element]:
        """Return all the text changes, either single deletion
        (text:change) or start of range of changes (text:change-start).

        Return: list of Element
        """
        request = "descendant::text:change-start | descendant::text:change"
        return self._filtered_elements(request)

    @property
    def text_changes(self) -> list[Element]:
        """Return all the text changes, either single deletion
        (text:change) or start of range of changes (text:change-start).

        Return: list of Element
        """
        return self.get_text_changes()

    def get_text_change(
        self,
        position: int = 0,
        idx: str | None = None,
    ) -> Element | None:
        """Return the text change that matches the criteria. Either single
        deletion (text:change) or start of range of changes (text:change-start).
        position : index of the element to retrieve if several matches, default
        is 0.
        idx : change-id of the element.

        Arguments:

            position -- int

            idx -- str

        Return: Element or None if not found
        """
        if idx:
            request = (
                f'descendant::text:change-start[@text:change-id="{idx}"] '
                f'| descendant::text:change[@text:change-id="{idx}"]'
            )
            return self._filtered_element(request, 0)
        request = "descendant::text:change-start | descendant::text:change"
        return self._filtered_element(request, position)

    # Table Of Content

    def get_tocs(self) -> list[Element]:
        """Return all the tables of contents.

        Return: list of odf_toc
        """
        return self.get_elements("text:table-of-content")

    @property
    def tocs(self) -> list[Element]:
        """Return all the tables of contents.

        Return: list of odf_toc
        """
        return self.get_elements("text:table-of-content")

    def get_toc(
        self,
        position: int = 0,
        content: str | None = None,
    ) -> Element | None:
        """Return the table of contents that matches the criteria.

        Arguments:

            position -- int

            content -- str regex

        Return: odf_toc or None if not found
        """
        return self._filtered_element(
            "text:table-of-content", position, content=content
        )

    @property
    def toc(self) -> Element | None:
        """Return the first table of contents.

        Return: odf_toc or None if not found
        """
        return self.get_toc()

    # Styles

    @staticmethod
    def _get_style_tagname(family: str | None, is_default: bool = False) -> str:
        """Widely match possible tag names given the family (or not)."""
        if not family:
            tagname = "(style:default-style|*[@style:name]|draw:fill-image|draw:marker)"
        elif is_default:
            # Default style
            tagname = "style:default-style"
        else:
            tagname = _family_style_tagname(family)
            # if famattr:
            #    # Include family default style
            #    tagname = '(%s|style:default-style)' % tagname
            if family in FAMILY_ODF_STD:
                # Include family default style
                tagname = f"({tagname}|style:default-style)"
        return tagname

    def get_styles(self, family: str | None = None) -> list[Element]:
        # Both common and default styles
        tagname = self._get_style_tagname(family)
        return self._filtered_elements(tagname, family=family)

    def get_style(
        self,
        family: str,
        name_or_element: str | Element | None = None,
        display_name: str | None = None,
    ) -> Element | None:
        """Return the style uniquely identified by the family/name pair. If
        the argument is already a style object, it will return it.

        If the name is not the internal name but the name you gave in the
        desktop application, use display_name instead.

        Arguments:

            family -- 'paragraph', 'text', 'graphic', 'table', 'list',
                      'number'

            name_or_element -- str or Style

            display_name -- str

        Return: odf_style or None if not found
        """
        if isinstance(name_or_element, Element):
            name = self.get_attribute("style:name")
            if name is not None:
                return name_or_element
            else:
                raise ValueError(f"Not a odf_style ? {name_or_element!r}")
        style_name = name_or_element
        is_default = not (style_name or display_name)
        tagname = self._get_style_tagname(family, is_default=is_default)
        # famattr became None if no "style:family" attribute
        if family:
            return self._filtered_element(
                tagname,
                0,
                style_name=style_name,
                display_name=display_name,
                family=family,
            )
        else:
            return self._filtered_element(
                tagname,
                0,
                draw_name=style_name or display_name,
                family=family,
            )

    def _filtered_element(
        self,
        query_string: str,
        position: int,
        **kwargs: Any,
    ) -> Element | None:
        results = self._filtered_elements(query_string, **kwargs)
        try:
            return results[position]
        except IndexError:
            return None

    def _filtered_elements(
        self,
        query_string: str,
        content: str | None = None,
        url: str | None = None,
        svg_title: str | None = None,
        svg_desc: str | None = None,
        dc_creator: str | None = None,
        dc_date: datetime | None = None,
        **kwargs: Any,
    ) -> list[Element]:
        query = make_xpath_query(query_string, **kwargs)
        elements = self.get_elements(query)
        # Filter the elements with the regex (TODO use XPath)
        if content is not None:
            elements = [element for element in elements if element.match(content)]
        if url is not None:
            filtered = []
            for element in elements:
                url_attr = element.get_attribute("xlink:href")
                if isinstance(url_attr, str) and search(url, url_attr) is not None:
                    filtered.append(element)
            elements = filtered
        if dc_date is None:
            dt_dc_date = None
        else:
            dt_dc_date = DateTime.encode(dc_date)
        for variable, childname in [
            (svg_title, "svg:title"),
            (svg_desc, "svg:desc"),
            (dc_creator, "descendant::dc:creator"),
            (dt_dc_date, "descendant::dc:date"),
        ]:
            if not variable:
                continue
            filtered = []
            for element in elements:
                child = element.get_element(childname)
                if child and child.match(variable):
                    filtered.append(element)
            elements = filtered
        return elements
