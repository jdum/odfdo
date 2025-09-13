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
"""Element, base class of all ODF classes."""

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
from typing import TYPE_CHECKING, Any, NamedTuple

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

if TYPE_CHECKING:
    from .annotation import Annotation, AnnotationEnd
    from .body import Body
    from .bookmark import Bookmark, BookmarkEnd, BookmarkStart
    from .draw_page import DrawPage
    from .frame import Frame
    from .header import Header
    from .image import DrawImage
    from .link import Link
    from .list import List
    from .named_range import NamedRange
    from .note import Note
    from .paragraph import Paragraph, Span
    from .reference import (
        Reference,
        ReferenceMark,
        ReferenceMarkEnd,
        ReferenceMarkStart,
    )
    from .section import Section
    from .shapes import (
        ConnectorShape,
        DrawGroup,
        EllipseShape,
        LineShape,
        RectangleShape,
    )
    from .style import Style
    from .toc import TOC
    from .tracked_changes import (
        TextChange,
        TextChangeEnd,
        TextChangeStart,
        TrackedChanges,
    )
    from .user_field import UserDefined, UserFieldDecl, UserFieldDecls
    from .variable import VarDecls, VarSet

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

# An empty XML document with all namespaces declared
NAMESPACES_XML = (
    OFFICE_PREFIX
    + f'office:version="{OFFICE_VERSION}">'.encode()
    + b"%s</office:document>"
)

_re_anyspace = re.compile(r" +")


class PropDef(NamedTuple):
    """Named tuple for class properties (internal)."""

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
    """(internal function) Return an XPath function compiled from a query in
    ODF namespace.
    """
    return XPath(path, namespaces=ODF_NAMESPACES, regexp=False)


def xpath_return_elements(xpath: XPath, target: _Element) -> list[_Element]:
    """(internal function) Return the _Elements resulting from XPath query on
    target.
    """
    elements = xpath(target)
    try:
        return [e for e in elements if isinstance(e, _Element)]
    except TypeError as e:  # pragma: nocover
        # cant happen
        msg = f"Bad XPath result, list expected, got {elements!r}"
        raise TypeError(msg) from e


def xpath_return_strings(xpath: XPath, target: _Element) -> list[str]:
    """(internal function) Return the strings resulting from XPath query on
    target.
    """
    elements = xpath(target)
    try:
        return [s for s in elements if isinstance(s, str)]
    except TypeError as e:  # pragma: nocover
        # cant happen
        msg = f"Bad XPath result, list expected, got {elements!r}"
        raise TypeError(msg) from e


# _xpath_text = xpath_compile("//text()")  # descendant and self
# _xpath_text_descendant = xpath_compile("descendant::text()")
# _xpath_text_main = xpath_compile("//*[not (parent::office:annotation)]/text()")
_xpath_text_descendant_no_annotation = xpath_compile(
    "descendant::text()[not (parent::office:annotation)]"
)

_class_registry: dict[str, type[Element]] = {}


def register_element_class(cls: type[Element]) -> None:
    """(internal function) Associate a qualified element name to a Python class
    that handles this type of element.

    Getting the right Python class when loading an existing ODF document is
    then transparent. Unassociated elements will be handled by the base
    Element class.

    Args:

        cls -- Python class, subtype of Element.
    """
    # Turn tag name into what lxml is expecting
    _register_element_class(cls, cls._tag)


def register_element_class_list(cls: type[Element], tag_list: Iterable[str]) -> None:
    """(internal function) Associate a qualified element name to a Python class
    that handles this type of element.

    Getting the right Python class when loading an existing ODF document is
    then transparent. Unassociated elements will be handled by the base
    Element class.

    Most styles use the "style:style" qualified name and only differ by their
    "style:family" attribute. So the "family" attribute was added to register
    specialized style classes.

    Args:

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
    """Representation of an XML text node (internal).

    Created to hide the specifics of lxml in searching text nodes using XPath.

    Constructed like any str object but only accepts lxml text objects.
    """

    # There's some black magic in inheriting from str
    def __init__(
        self,
        text_result: _Element,
    ) -> None:
        self.__parent = text_result.getparent()
        self.__is_text: bool = bool(text_result.is_text)
        self.__is_tail: bool = bool(text_result.is_tail)

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
    """Base class of all ODF classes, abstraction of the underlying XML."""

    _tag: str = ""
    _properties: tuple[PropDef, ...] = ()

    def __init__(self, **kwargs: Any) -> None:
        """Base class of all ODF classes, abstraction of the underlying XML."""
        tag_or_elem = kwargs.pop("tag_or_elem", None)
        if tag_or_elem is None:
            # Instance for newly created object: create new lxml element and
            # continue by subclass __init__
            # If the tag key word exists, make a custom element
            self._do_init = True
            tag = kwargs.pop("tag", self._tag)
            self.__element = self._make_etree_element(tag)
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

        Args:

            tag_or_elem -- ODF str tag or lxml.Element

        Returns: Element (or subclass) instance
        """
        if isinstance(tag_or_elem, str):
            # assume the argument is a prefix:name tag
            elem = cls._make_etree_element(tag_or_elem)
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
        element: Element = klass(tag_or_elem=tree_element)
        if cache:
            element._copy_cache(cache)
        return element

    def _copy_cache(self, cache: tuple) -> None:
        """Method redefined for cached elements."""
        pass

    @staticmethod
    def _make_etree_element(tag: str) -> _Element:
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

    def _base_attrib_getter(self, attr_name: str) -> str | None:
        value = self.__element.get(_get_lxml_tag(attr_name))
        if value is None:
            return None
        return str(value)

    def _base_attrib_setter(
        self,
        attr_name: str,
        value: str | int | float | bool | None,
    ) -> None:
        if value is None:
            with contextlib.suppress(KeyError):
                del self.__element.attrib[_get_lxml_tag(attr_name)]
            return
        if isinstance(value, bool):
            value = Boolean.encode(value)
        self.__element.set(_get_lxml_tag(attr_name), str(value))

    @staticmethod
    def _generic_attrib_getter(attr_name: str, family: str | None = None) -> Callable:
        def getter(self: Element) -> str | bool | None:
            try:
                if family and self.family != family:  # type: ignore
                    return None
            except AttributeError:
                return None
            value = self._base_attrib_getter(attr_name)
            if value is None:
                return None
            elif value in ("true", "false"):
                return Boolean.decode(value)
            return value

        return getter

    @staticmethod
    def _generic_attrib_setter(attr_name: str, family: str | None = None) -> Callable:
        def setter(self: Element, value: Any) -> None:
            try:
                if family and self.family != family:  # type: ignore
                    return None
            except AttributeError:
                return None
            self._base_attrib_setter(attr_name, value)

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
        xpath_result: list[str],
        regex: re.Pattern,
    ) -> tuple[str, re.Match]:
        # Found the last text that matches the regex
        for text in xpath_result:
            if regex.search(text) is not None:
                break
        else:
            raise ValueError(f"Text not found: {xpath_result!r}")
        return text, list(regex.finditer(text))[-1]

    @staticmethod
    def _search_positive_position(
        xpath_result: list[str],
        regex: re.Pattern,
        position: int,
    ) -> tuple[str, re.Match]:
        # Found the last text that matches the regex
        count = 0
        for text in xpath_result:
            found_nb = len(regex.findall(text))
            if found_nb + count >= position + 1:
                break
            count += found_nb
        else:
            raise ValueError(f"Text not found: {xpath_result!r}")
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
        xpath_result = xpath_return_strings(xpath_text, current)
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
        xpath_result = xpath_return_strings(xpath_text, current)
        count = 0
        for text in xpath_result:
            found_nb = len(text)
            if found_nb + count >= position:
                break
            count += found_nb
        else:
            raise ValueError(f"Text not found: {xpath_result!r}")
        # We insert before the character
        pos = position - count
        return pos, text

    def _insert(
        self,
        element: Element,
        before: str | None = None,
        after: str | None = None,
        position: int = 0,
    ) -> None:
        """Insert an element before or after the characters in the text which
        match the regex before/after.

        When the regex matches more of one part of the text, position can be
        set to choice which part must be used. If before and after are None,
        we use only position that is the number of characters. If position is
        positive and before=after=None, we insert before the position
        character. But if position=-1, we insert after the last character.

        Annotation text content is ignored.


        Args:

        element -- Element

        before -- str regex

        after -- str regex

        position -- int
        """
        current = self.__element
        xelement = element.__element

        # 1) before xor after is not None
        if (before is not None) ^ (after is not None):
            pos, text = self._insert_before_after(
                current,
                xelement,
                before,
                after,
                position,
                _xpath_text_descendant_no_annotation,
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
                _xpath_text_descendant_no_annotation,
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

    @property
    def tag(self) -> str:
        """Get/set the underlying xml tag with the given qualified name.

        Warning: direct change of tag does not change the element class.

        Args:

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
        sub_elements = xpath_return_elements(xpath_instance, self.__element)
        result: list[tuple[int, int]] = []
        idx = -1
        for sub_element in sub_elements:
            idx += 1
            value = sub_element.get(lxml_tag)
            if value is None:
                result.append((idx, 1))
                continue
            try:
                int_value = int(value)
            except ValueError:  # pragma: nocover
                int_value = 1
            result.append((idx, max(int_value, 1)))
        return result

    def get_elements(self, xpath_query: XPath | str) -> list[Element]:
        """Returns the elements obtained from the XPath query applied to the
        current element.

        Return list of Element.
        """
        if isinstance(xpath_query, str):
            elements = xpath_return_elements(xpath_compile(xpath_query), self.__element)
        else:
            elements = xpath_return_elements(xpath_query, self.__element)
        return [Element.from_tag_for_clone(e, None) for e in elements]

    def get_element(self, xpath_query: str) -> Element | None:
        """Returns the first element obtained from the XPath query applied to
        the current element.

        Return an Element or None.
        """
        result = self.__element.xpath(f"({xpath_query})[1]", namespaces=ODF_NAMESPACES)
        if result:
            return Element.from_tag(result[0])
        return None

    def _get_element_idx(self, xpath_query: XPath | str, idx: int) -> Element | None:
        result = self.__element.xpath(
            f"({xpath_query})[{idx + 1}]", namespaces=ODF_NAMESPACES
        )
        if result:
            return Element.from_tag(result[0])
        return None

    def _get_element_idx2(self, xpath_instance: XPath, idx: int) -> Element | None:
        result = xpath_instance(self.__element, idx=idx + 1)
        if result:
            return Element.from_tag(result[0])
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

    def set_style_attribute(self, name: str, value: Element | str | None) -> None:
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
        return self.__element.tail  # type: ignore[no-any-return]

    @tail.setter
    def tail(self, text: str | None) -> None:
        self.__element.tail = text or ""

    def search(self, pattern: str) -> int | None:
        """Return the first position of the pattern in the text content of the
        element, or None if not found.

        Python regular expression syntax applies.

        Args:

            pattern -- str

        Returns: int or None
        """
        match = re.search(pattern, self.text_recursive)
        if match is None:
            return None
        return match.start()

    def search_first(self, pattern: str) -> tuple[int, int] | None:
        """Return the start and end position of the first occurence of the
        regex pattern in the text content of the element.

        Result is tuples of start and end position, or None.
        Python regular expression syntax applies.

        Args:

            pattern -- str

        Returns: tuple[int,int] or None
        """
        match = re.search(pattern, self.text_recursive)
        if match is None:
            return None
        return match.start(), match.end()

    def search_all(self, pattern: str) -> list[tuple[int, int]]:
        """Return all start and end positions of the regex pattern in the text
        content of the element.

        Result is a list of tuples of start and end position of
        the matches.
        Python regular expression syntax applies.

        Args:

            pattern -- str

        Returns: list[tuple[int,int]]
        """
        results: list[tuple[int, int]] = []
        for match in re.finditer(pattern, self.text_recursive):
            results.append((match.start(), match.end()))
        return results

    def text_at(self, start: int, end: int | None = None) -> str:
        """Return the text (recursive) content of the element between start and
        end position.

        If the end parameter is not set, return from start to the end
        of the recursive text.

        Args:

            start -- int
            end -- int or None

        Returns: str
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
        """Return True if the pattern is found one or more times anywhere in
        the text content of the element.

        Python regular expression syntax applies.

        Args:

            pattern -- str

        Returns: bool
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

        Args:

            pattern -- str

            new -- str

            formatted -- bool

        Returns: int
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
                if not container:  # pragma: nocover
                    continue
                if text.is_text():  # type: ignore
                    container.text = new_text
                else:
                    container.tail = new_text
                if formatted and container.tag in {  # type; ignore
                    "text:h",
                    "text:p",
                    "text:span",
                }:
                    container.append_plain_text("")  # type: ignore[attr-defined]
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

        Inspired by lxml.
        """
        idx: int = self.__element.index(child.__element)
        return idx

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
    def text_content(self, text: str | Element | None) -> None:
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
        if text is None:
            text = ""
        element.text = str(text)

    def is_empty(self) -> bool:
        """Check if the element is empty : no text, no children, no tail.

        Returns: Boolean
        """
        element = self.__element
        if element.tail is not None:
            return False
        if element.text is not None:
            return False
        if list(element.iterchildren()):  # noqa: SIM103
            return False
        return True

    def insert(
        self,
        element: Element,
        xmlposition: int | None = None,
        position: int | None = None,
        start: bool = False,
    ) -> None:
        """Insert an element relatively to ourself.

        Insert either using DOM vocabulary or by numeric position.
        If "start" is True, insert the element before any existing text.

        Position start at 0.

        Args:

            element -- Element

            xmlposition -- FIRST_CHILD, LAST_CHILD, NEXT_SIBLING
                           or PREV_SIBLING

            start -- Boolean

            position -- int
        """
        # child_tag = element.tag
        current = self.__element
        lx_element = element.__element
        if start:
            text = current.text
            if text is not None:
                current.text = None
                tail = lx_element.tail
                if tail is None:
                    tail = text
                else:
                    tail = tail + text
                lx_element.tail = tail
            position = 0
        if position is not None:
            current.insert(position, lx_element)
        elif xmlposition is FIRST_CHILD:
            current.insert(0, lx_element)
        elif xmlposition is LAST_CHILD:
            current.append(lx_element)
        elif xmlposition is NEXT_SIBLING:
            parent = current.getparent()
            index = parent.index(current)
            parent.insert(index + 1, lx_element)
        elif xmlposition is PREV_SIBLING:
            parent = current.getparent()
            index = parent.index(current)
            parent.insert(index, lx_element)
        else:
            raise ValueError("(xml)position must be defined")

    def extend(self, odf_elements: Iterable[Element]) -> None:
        """Fast append elements at the end of ourself using extend."""
        if odf_elements:
            current = self.__element
            elements = [element.__element for element in odf_elements]
            current.extend(elements)

    def __append(self, str_or_element: str | Element) -> None:
        """Insert element or text in the last position."""

        def _add_text(text1: str | None, text2: str | None) -> str:
            return _re_anyspace.sub(" ", (text1 or "") + (text2 or ""))

        current = self.__element
        if isinstance(str_or_element, str):
            # Has children ?
            children = list(current.iterchildren())
            if children:
                # Append to tail of the last child
                last_child = children[-1]
                last_child.tail = _add_text(last_child.tail, str_or_element)
            else:
                # Append to text of the element
                current.text = _add_text(current.text, str_or_element)
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

        Args:

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
    ) -> Element | list[Element | str]:
        """Remove the tags of provided elements, keeping inner childs and text.

        Return : the striped element.

        Warning : no clone in sub_elements list.

        Args:

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
    ) -> Element | list[Element | str]:
        """Remove the tags listed in strip, recursively, keeping inner childs
        and text. Tags listed in protect stop the removal one level depth. If
        the first level element is stripped, default is used to embed the
        content in the default element. If default is None and first level is
        striped, a list of text and children is returned. Return : the striped
        element.

        strip_tags should be used by on purpose methods (strip_span ...)
        (Method name taken from lxml).

        Args:

            strip -- iterable list of str odf tags, or None

            protect -- iterable list of str odf tags, or None

            default -- str odf tag, or None

        Returns:

            Element, or list of Element or string.
        """
        if not strip:
            return self
        if not protect:
            protect = ()
        protected = False
        result: Element | list[Element | str] = []
        result, modified = Element._strip_tags(self, strip, protect, protected)
        if modified and isinstance(result, list) and default:
            new: Element = Element.from_tag(default)
            for content in result:
                if isinstance(content, Element):
                    new.__append(content)
                else:
                    new.text = content
            result = new
        return result

    @staticmethod
    def _strip_tags(
        element: Element,
        strip: Iterable[str],
        protect: Iterable[str],
        protected: bool,
    ) -> tuple[Element | list[Element | str], bool]:
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
            for child2 in children:
                element_result.append(child2)
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
            for child3 in children:
                element.__append(child3)
            if tail is not None:
                element.tail = tail
            return (element, True)

    def xpath(self, xpath_query: str) -> list[Element | EText]:
        """Apply XPath query to the element and its subtree.

        Return list of Element or EText instances.
        """
        xpath_instance = xpath_compile(xpath_query)
        elements = xpath_instance(self.__element)
        result: list[Element | EText] = []
        if hasattr(elements, "__iter__"):
            for obj in elements:
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
        data: str = tostring(
            native, with_tail=False, pretty_print=pretty, encoding="unicode"
        )
        if with_ns:
            return data
        # Remove namespaces
        return self._strip_namespaces(data)

    # Element helpers usable from any context

    @property
    def document_body(self) -> Body | None:
        """Return the first children of document body if any: 'office:body/*[1]'"""
        return self.get_element("//office:body/*[1]")  # type: ignore[return-value]

    def get_formatted_text(self, context: dict | None = None) -> str:
        """This function should return a beautiful version of the text."""
        return ""

    def get_styled_elements(self, name: str = "") -> list[Element]:
        """Brute-force to find paragraphs, tables, etc. using the given style
        name (or all by default).

        Args:

            name -- str

        Returns: list of Element
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
    ) -> list[Section]:
        """Return all the sections that match the criteria.

        Args:

            style -- str

            content -- str regex

        Returns: list of Section
        """
        return self._filtered_elements(
            "text:section", text_style=style, content=content
        )  # type: ignore[return-value]

    @property
    def sections(
        self,
    ) -> list[Section]:
        """Return all the sections.

        Returns: list of Section
        """
        return self.get_elements("text:section")  # type: ignore[return-value]

    def get_section(
        self,
        position: int = 0,
        content: str | None = None,
    ) -> Section | None:
        """Return the section that matches the criteria.

        Args:

            position -- int

            content -- str regex

        Returns: Section or None if not found
        """
        return self._filtered_element(
            "descendant::text:section", position, content=content
        )  # type: ignore[return-value]

    # Paragraphs

    def get_paragraphs(
        self,
        style: str | None = None,
        content: str | None = None,
    ) -> list[Paragraph]:
        """Return all the paragraphs that match the criteria.

        Args:

            style -- str

            content -- str regex

        Returns: list of Paragraph
        """
        return self._filtered_elements(
            "descendant::text:p", text_style=style, content=content
        )  # type: ignore[return-value]

    @property
    def paragraphs(self) -> list[Paragraph]:
        """Return all the paragraphs.

        Returns: list of Paragraph
        """
        return self.get_elements(
            "descendant::text:p",
        )  # type: ignore[return-value]

    def get_paragraph(
        self,
        position: int = 0,
        content: str | None = None,
    ) -> Paragraph | None:
        """Return the paragraph that matches the criteria.

        Args:

            position -- int

            content -- str regex

        Returns: Paragraph or None if not found
        """
        return self._filtered_element(
            "descendant::text:p",
            position,
            content=content,
        )  # type: ignore[return-value]

    # Span

    def get_spans(
        self,
        style: str | None = None,
        content: str | None = None,
    ) -> list[Span]:
        """Return all the spans that match the criteria.

        Args:

            style -- str

            content -- str regex

        Returns: list of Span
        """
        return self._filtered_elements(
            "descendant::text:span", text_style=style, content=content
        )  # type: ignore[return-value]

    @property
    def spans(self) -> list[Span]:
        """Return all the spans.

        Returns: list of Span
        """
        return self.get_elements("descendant::text:span")  # type: ignore[return-value]

    def get_span(
        self,
        position: int = 0,
        content: str | None = None,
    ) -> Span | None:
        """Return the span that matches the criteria.

        Args:

            position -- int

            content -- str regex

        Returns: Span or None if not found
        """
        return self._filtered_element(
            "descendant::text:span", position, content=content
        )  # type: ignore[return-value]

    # Headers

    def get_headers(
        self,
        style: str | None = None,
        outline_level: str | None = None,
        content: str | None = None,
    ) -> list[Header]:
        """Return all the Headers that match the criteria.

        Args:

            style -- str

            content -- str regex

        Returns: list of Header
        """
        return self._filtered_elements(
            "descendant::text:h",
            text_style=style,
            outline_level=outline_level,
            content=content,
        )  # type: ignore[return-value]

    @property
    def headers(self) -> list[Header]:
        """Return all the Headers.

        Returns: list of Header
        """
        return self.get_elements("descendant::text:h")  # type: ignore[return-value]

    def get_header(
        self,
        position: int = 0,
        outline_level: str | None = None,
        content: str | None = None,
    ) -> Header | None:
        """Return the Header that matches the criteria.

        Args:

            position -- int

            content -- str regex

        Returns: Header or None if not found
        """
        return self._filtered_element(
            "descendant::text:h",
            position,
            outline_level=outline_level,
            content=content,
        )  # type: ignore[return-value]

    # Lists

    def get_lists(
        self,
        style: str | None = None,
        content: str | None = None,
    ) -> list[List]:
        """Return all the lists that match the criteria.

        Args:

            style -- str

            content -- str regex

        Returns: list of List
        """
        return self._filtered_elements(
            "descendant::text:list", text_style=style, content=content
        )  # type: ignore[return-value]

    @property
    def lists(self) -> list[List]:
        """Return all the lists.

        Returns: list of List
        """
        return self.get_elements("descendant::text:list")  # type: ignore[return-value]

    def get_list(
        self,
        position: int = 0,
        content: str | None = None,
    ) -> List | None:
        """Return the list that matches the criteria.

        Args:

            position -- int

            content -- str regex

        Returns: List or None if not found
        """
        return self._filtered_element(
            "descendant::text:list", position, content=content
        )  # type: ignore[return-value]

    # Frames

    def get_frames(
        self,
        presentation_class: str | None = None,
        style: str | None = None,
        title: str | None = None,
        description: str | None = None,
        content: str | None = None,
    ) -> list[Frame]:
        """Return all the frames that match the criteria.

        Args:

            presentation_class -- str

            style -- str

            title -- str regex

            description -- str regex

            content -- str regex

        Returns: list of Frame
        """
        return self._filtered_elements(
            "descendant::draw:frame",
            presentation_class=presentation_class,
            draw_style=style,
            svg_title=title,
            svg_desc=description,
            content=content,
        )  # type: ignore[return-value]

    @property
    def frames(self) -> list[Frame]:
        """Return all the frames.

        Returns: list of Frame
        """
        return self.get_elements("descendant::draw:frame")  # type: ignore[return-value]

    def get_frame(
        self,
        position: int = 0,
        name: str | None = None,
        presentation_class: str | None = None,
        title: str | None = None,
        description: str | None = None,
        content: str | None = None,
    ) -> Frame | None:
        """Return the section that matches the criteria.

        Args:

            position -- int

            name -- str

            presentation_class -- str

            title -- str regex

            description -- str regex

            content -- str regex

        Returns: Frame or None if not found
        """
        return self._filtered_element(
            "descendant::draw:frame",
            position,
            draw_name=name,
            presentation_class=presentation_class,
            svg_title=title,
            svg_desc=description,
            content=content,
        )  # type: ignore[return-value]

    # Images

    def get_images(
        self,
        style: str | None = None,
        url: str | None = None,
        content: str | None = None,
    ) -> list[DrawImage]:
        """Return all the images matching the criteria.

        Args:

            style -- str

            url -- str regex

            content -- str regex

        Returns: list of DrawImage
        """
        return self._filtered_elements(
            "descendant::draw:image", text_style=style, url=url, content=content
        )  # type: ignore[return-value]

    @property
    def images(self) -> list[DrawImage]:
        """Return all the images.

        Returns: list of DrawImage
        """
        return self.get_elements("descendant::draw:image")  # type: ignore[return-value]

    def get_image(
        self,
        position: int = 0,
        name: str | None = None,
        url: str | None = None,
        content: str | None = None,
    ) -> DrawImage | None:
        """Return the image matching the criteria.

        Args:

            position -- int

            name -- str

            url -- str regex

            content -- str regex

        Returns: DrawImage or None if not found
        """
        # The frame is holding the name
        if name is not None:
            frame = self._filtered_element(
                "descendant::draw:frame", position, draw_name=name
            )
            if frame is None:
                return None
            # The name is supposedly unique
            return frame.get_element("draw:image")  # type: ignore[return-value]
        return self._filtered_element(
            "descendant::draw:image", position, url=url, content=content
        )  # type: ignore[return-value]

    # Named Range

    def get_named_ranges(self) -> list[NamedRange]:
        """Return all the tables named ranges.

        Returns: list of NamedRange
        """
        named_ranges = self.get_elements(
            "descendant::table:named-expressions/table:named-range"
        )
        return named_ranges  # type: ignore[return-value]

    def get_named_range(self, name: str) -> NamedRange | None:
        """Return the named range of specified name, or None if not found.

        Args:

            name -- str

        Returns: NamedRange
        """
        named_range = self.get_elements(
            f'descendant::table:named-expressions/table:named-range[@table:name="{name}"][1]'
        )
        if named_range:
            return named_range[0]  # type: ignore[return-value]
        else:
            return None

    def append_named_range(self, named_range: NamedRange) -> None:
        """Append the named range to the spreadsheet, replacing existing named
        range of same name if any.

        Args:

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
            f'table:named-range[@table:name="{named_range.name}"][1]'
        )
        if current:
            named_expressions.delete(current)
        named_expressions.__append(named_range)

    def delete_named_range(self, name: str) -> None:
        """Delete the Named Range of specified name from the spreadsheet.

        Args:

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
    ) -> list[Note]:
        """Return all the notes that match the criteria.

        Args:

            note_class -- 'footnote' or 'endnote'

            content -- str regex

        Returns: list of Note
        """
        return self._filtered_elements(
            "descendant::text:note", note_class=note_class, content=content
        )  # type: ignore[return-value]

    def get_note(
        self,
        position: int = 0,
        note_id: str | None = None,
        note_class: str | None = None,
        content: str | None = None,
    ) -> Note | None:
        """Return the note that matches the criteria.

        Args:

            position -- int

            note_id -- str

            note_class -- 'footnote' or 'endnote'

            content -- str regex

        Returns: Note or None if not found
        """
        return self._filtered_element(
            "descendant::text:note",
            position,
            text_id=note_id,
            note_class=note_class,
            content=content,
        )  # type: ignore[return-value]

    # Annotations

    def get_annotations(
        self,
        creator: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        content: str | None = None,
    ) -> list[Annotation]:
        """Return all the annotations that match the criteria.

        Args:

            creator -- str

            start_date -- datetime instance

            end_date --  datetime instance

            content -- str regex

        Returns: list of Annotation
        """
        annotations: list[Annotation] = []
        for annotation in self._filtered_elements(
            "descendant::office:annotation", content=content
        ):
            if creator is not None and creator != annotation.dc_creator:  # type: ignore[attr-defined]
                continue
            date = annotation.date  # type: ignore[attr-defined]
            if date is None:
                continue
            if start_date is not None and date < start_date:
                continue
            if end_date is not None and date >= end_date:
                continue
            annotations.append(annotation)  # type: ignore[arg-type]
        return annotations

    def get_annotation(
        self,
        position: int = 0,
        creator: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        content: str | None = None,
        name: str | None = None,
    ) -> Annotation | None:
        """Return the annotation that matches the criteria.

        Args:

            position -- int

            creator -- str

            start_date -- datetime instance

            end_date -- datetime instance

            content -- str regex

            name -- str

        Returns: Annotation or None if not found
        """
        if name is not None:
            return self._filtered_element(
                "descendant::office:annotation", 0, office_name=name
            )  # type: ignore[return-value]
        annotations: list[Annotation] = self.get_annotations(
            creator=creator, start_date=start_date, end_date=end_date, content=content
        )
        if not annotations:
            return None
        try:
            return annotations[position]
        except IndexError:
            return None

    def get_annotation_ends(self) -> list[AnnotationEnd]:
        """Return all the annotation ends.

        Returns: list of AnnotationEnd
        """
        return self._filtered_elements(
            "descendant::office:annotation-end",
        )  # type: ignore[return-value]

    def get_annotation_end(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> AnnotationEnd | None:
        """Return the annotation end that matches the criteria.

        Args:

            position -- int

            name -- str

        Returns: AnnotationEnd or None if not found
        """
        return self._filtered_element(
            "descendant::office:annotation-end", position, office_name=name
        )  # type: ignore[return-value]

    # office:names

    def get_office_names(self) -> list[str]:
        """Return all the used office:name tags values of the element.

        Returns: list of unique str
        """
        name_xpath_query = xpath_compile("//@office:name")
        response = name_xpath_query(self.__element)
        if not isinstance(response, list):
            return []
        return list({str(name) for name in response if name})

    # Variables

    def get_variable_decls(self) -> VarDecls:
        """Return the container for variable declarations. Created if not
        found.

        Returns: VarDecls
        """
        variable_decls = self.get_element("//text:variable-decls")
        if variable_decls is None:
            body = self.document_body
            if not body:
                raise ValueError("Empty document.body")
            body.insert(Element.from_tag("text:variable-decls"), FIRST_CHILD)
            variable_decls = body.get_element("//text:variable-decls")

        return variable_decls  # type: ignore[return-value]

    def get_variable_decl_list(self) -> list[VarDecls]:
        """Return all the variable declarations.

        Returns: list of VarDecls
        """
        return self._filtered_elements(
            "descendant::text:variable-decl",
        )  # type: ignore[return-value]

    def get_variable_decl(self, name: str, position: int = 0) -> VarDecls | None:
        """Return the variable declaration for the given name.

        Args:

            name -- str

            position -- int

        Returns: VarDecls or none if not found
        """
        return self._filtered_element(
            "descendant::text:variable-decl", position, text_name=name
        )  # type: ignore[return-value]

    def get_variable_sets(self, name: str | None = None) -> list[VarSet]:
        """Return all the variable sets that match the criteria.

        Args:

            name -- str

        Returns: list of VarSet
        """
        return self._filtered_elements(
            "descendant::text:variable-set",
            text_name=name,
        )  # type: ignore[return-value]

    def get_variable_set(self, name: str, position: int = -1) -> VarSet | None:
        """Return the variable set for the given name (last one by default).

        Args:

            name -- str

            position -- int

        Returns: VarSet or None if not found
        """
        return self._filtered_element(
            "descendant::text:variable-set", position, text_name=name
        )  # type: ignore[return-value]

    def get_variable_set_value(
        self,
        name: str,
        value_type: str | None = None,
    ) -> bool | str | int | float | Decimal | datetime | timedelta | None:
        """Return the last value of the given variable name.

        Args:

            name -- str

            value_type -- 'boolean', 'currency', 'date', 'float',
                          'percentage', 'string', 'time' or automatic

        Returns: most appropriate Python type
        """
        variable_set = self.get_variable_set(name)
        if not variable_set:
            return None
        return variable_set.get_value(value_type)  # type: ignore[return-value]

    # User fields

    def get_user_field_decls(self) -> UserFieldDecls | None:
        """Return the container for user field declarations. Created if not
        found.

        Returns: UserFieldDecls
        """
        user_field_decls = self.get_element("//text:user-field-decls")
        if user_field_decls is None:
            body = self.document_body
            if not body:
                raise ValueError("Empty document.body")
            body.insert(Element.from_tag("text:user-field-decls"), FIRST_CHILD)
            user_field_decls = body.get_element("//text:user-field-decls")

        return user_field_decls  # type: ignore[return-value]

    def get_user_field_decl_list(self) -> list[UserFieldDecl]:
        """Return all the user field declarations.

        Returns: list of UserFieldDecl
        """
        return self._filtered_elements(
            "descendant::text:user-field-decl",
        )  # type: ignore[return-value]

    def get_user_field_decl(self, name: str, position: int = 0) -> UserFieldDecl | None:
        """Return the user field declaration for the given name.

        Returns: UserFieldDecl or none if not found
        """
        return self._filtered_element(
            "descendant::text:user-field-decl", position, text_name=name
        )  # type: ignore[return-value]

    def get_user_field_value(
        self, name: str, value_type: str | None = None
    ) -> bool | str | int | float | Decimal | datetime | timedelta | None:
        """Return the value of the given user field name.

        Args:

            name -- str

            value_type -- 'boolean', 'currency', 'date', 'float',
                          'percentage', 'string', 'time' or automatic

        Returns: most appropriate Python type
        """
        user_field_decl = self.get_user_field_decl(name)
        if user_field_decl is None:
            return None
        value = user_field_decl.get_value(value_type)
        return value  # type: ignore[return-value]

    # User defined fields
    # They are fields who should contain a copy of a user defined medtadata

    def get_user_defined_list(self) -> list[UserDefined]:
        """Return all the user defined field declarations.

        Returns: list of UserDefined
        """
        return self._filtered_elements(
            "descendant::text:user-defined",
        )  # type: ignore[return-value]

    @property
    def user_defined_list(self) -> list[UserDefined]:
        """Return all the user defined field declarations.

        Returns: list of UserDefined
        """
        return self.get_user_defined_list()

    def get_user_defined(self, name: str, position: int = 0) -> UserDefined | None:
        """Return the user defined declaration for the given name.

        Returns: UserDefined or none if not found
        """
        return self._filtered_element(
            "descendant::text:user-defined", position, text_name=name
        )  # type: ignore[return-value]

    def get_user_defined_value(
        self, name: str, value_type: str | None = None
    ) -> bool | str | int | float | Decimal | datetime | timedelta | None:
        """Return the value of the given user defined field name.

        Args:

            name -- str

            value_type -- 'boolean', 'date', 'float',
                          'string', 'time' or automatic

        Returns: most appropriate Python type
        """
        user_defined = self.get_user_defined(name)
        if user_defined is None:
            return None
        return user_defined.get_value(value_type)  # type: ignore[return-value]

    # Draw Pages

    def get_draw_pages(
        self,
        style: str | None = None,
        content: str | None = None,
    ) -> list[DrawPage]:
        """Return all the draw pages that match the criteria.

        Args:

            style -- str

            content -- str regex

        Returns: list of DrawPage
        """
        return self._filtered_elements(
            "descendant::draw:page", draw_style=style, content=content
        )  # type: ignore[return-value]

    def get_draw_page(
        self,
        position: int = 0,
        name: str | None = None,
        content: str | None = None,
    ) -> DrawPage | None:
        """Return the draw page that matches the criteria.

        Args:

            position -- int

            name -- str

            content -- str regex

        Returns: DrawPage or None if not found
        """
        return self._filtered_element(
            "descendant::draw:page", position, draw_name=name, content=content
        )  # type: ignore[return-value]

    # Links

    def get_links(
        self,
        name: str | None = None,
        title: str | None = None,
        url: str | None = None,
        content: str | None = None,
    ) -> list[Link]:
        """Return all the links that match the criteria.

        Args:

            name -- str

            title -- str

            url -- str regex

            content -- str regex

        Returns: list of Link
        """
        return self._filtered_elements(
            "descendant::text:a",
            office_name=name,
            office_title=title,
            url=url,
            content=content,
        )  # type: ignore[return-value]

    def get_link(
        self,
        position: int = 0,
        name: str | None = None,
        title: str | None = None,
        url: str | None = None,
        content: str | None = None,
    ) -> Link | None:
        """Return the link that matches the criteria.

        Args:

            position -- int

            name -- str

            title -- str

            url -- str regex

            content -- str regex

        Returns: Link or None if not found
        """
        return self._filtered_element(
            "descendant::text:a",
            position,
            office_name=name,
            office_title=title,
            url=url,
            content=content,
        )  # type: ignore[return-value]

    # Bookmarks

    def get_bookmarks(self) -> list[Bookmark]:
        """Return all the bookmarks.

        Returns: list of Bookmark
        """
        return self._filtered_elements(
            "descendant::text:bookmark",
        )  # type: ignore[return-value]

    def get_bookmark(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> Bookmark | None:
        """Return the bookmark that matches the criteria.

        Args:

            position -- int

            name -- str

        Returns: Bookmark or None if not found
        """
        return self._filtered_element(
            "descendant::text:bookmark", position, text_name=name
        )  # type: ignore[return-value]

    def get_bookmark_starts(self) -> list[BookmarkStart]:
        """Return all the bookmark starts.

        Returns: list of BookmarkStart
        """
        return self._filtered_elements(
            "descendant::text:bookmark-start",
        )  # type: ignore[return-value]

    def get_bookmark_start(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> BookmarkStart | None:
        """Return the bookmark start that matches the criteria.

        Args:

            position -- int

            name -- str

        Returns: BookmarkStart or None if not found
        """
        return self._filtered_element(
            "descendant::text:bookmark-start", position, text_name=name
        )  # type: ignore[return-value]

    def get_bookmark_ends(self) -> list[BookmarkEnd]:
        """Return all the bookmark ends.

        Returns: list of BookmarkEnd
        """
        return self._filtered_elements(
            "descendant::text:bookmark-end",
        )  # type: ignore[return-value]

    def get_bookmark_end(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> BookmarkEnd | None:
        """Return the bookmark end that matches the criteria.

        Args:

            position -- int

            name -- str

        Returns: BookmarkEnd or None if not found
        """
        return self._filtered_element(
            "descendant::text:bookmark-end", position, text_name=name
        )  # type: ignore[return-value]

    # Reference marks

    def get_reference_marks_single(self) -> list[ReferenceMark]:
        """Return all the reference marks. Search only the tags
        text:reference-mark.
        Consider using : get_reference_marks()

        Returns: list of ReferenceMark
        """
        return self._filtered_elements(
            "descendant::text:reference-mark",
        )  # type: ignore[return-value]

    def get_reference_mark_single(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> ReferenceMark | None:
        """Return the reference mark that matches the criteria. Search only the
        tags text:reference-mark.
        Consider using : get_reference_mark()

        Args:

            position -- int

            name -- str

        Returns: ReferenceMark or None if not found
        """
        return self._filtered_element(
            "descendant::text:reference-mark", position, text_name=name
        )  # type: ignore[return-value]

    def get_reference_mark_starts(self) -> list[ReferenceMarkStart]:
        """Return all the reference mark starts. Search only the tags
        text:reference-mark-start.
        Consider using : get_reference_marks()

        Returns: list of ReferenceMarkStart
        """
        return self._filtered_elements(
            "descendant::text:reference-mark-start",
        )  # type: ignore[return-value]

    def get_reference_mark_start(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> ReferenceMarkStart | None:
        """Return the reference mark start that matches the criteria. Search
        only the tags text:reference-mark-start.
        Consider using : get_reference_mark()

        Args:

            position -- int

            name -- str

        Returns: ReferenceMarkStart or None if not found
        """
        return self._filtered_element(
            "descendant::text:reference-mark-start", position, text_name=name
        )  # type: ignore[return-value]

    def get_reference_mark_ends(self) -> list[ReferenceMarkEnd]:
        """Return all the reference mark ends. Search only the tags
        text:reference-mark-end.
        Consider using : get_reference_marks()

        Returns: list of ReferenceMarkEnd
        """
        return self._filtered_elements(
            "descendant::text:reference-mark-end",
        )  # type: ignore[return-value]

    def get_reference_mark_end(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> ReferenceMarkEnd | None:
        """Return the reference mark end that matches the criteria. Search only
        the tags text:reference-mark-end.
        Consider using : get_reference_marks()

        Args:

            position -- int

            name -- str

        Returns: ReferenceMarkEnd or None if not found
        """
        return self._filtered_element(
            "descendant::text:reference-mark-end", position, text_name=name
        )  # type: ignore[return-value]

    def get_reference_marks(self) -> list[ReferenceMark | ReferenceMarkStart]:
        """Return all the reference marks, either single position reference
        (text:reference-mark) or start of range reference (text:reference-mark-
        start).

        Returns: list of ReferenceMark or ReferenceMarkStart
        """
        return self._filtered_elements(
            "descendant::text:reference-mark-start | descendant::text:reference-mark"
        )  # type: ignore[return-value]

    def get_reference_mark(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> ReferenceMark | ReferenceMarkStart | None:
        """Return the reference mark that match the criteria. Either single
        position reference mark (text:reference-mark) or start of range
        reference (text:reference-mark-start).

        Args:

            position -- int

            name -- str

        Returns: ReferenceMark or ReferenceMarkStart or None if not found
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
        return self._filtered_element(request, position)  # type: ignore[return-value]

    def get_references(self, name: str | None = None) -> list[Reference]:
        """Return all the references (text:reference-ref). If name is provided,
        returns the references of that name.

        Args:

            name -- str or None

        Returns: list of Reference
        """
        if name is None:
            return self._filtered_elements(
                "descendant::text:reference-ref",
            )  # type: ignore[return-value]
        request = f'descendant::text:reference-ref[@text:ref-name="{name}"]'
        return self._filtered_elements(request)  # type: ignore[return-value]

    # Shapes elements

    # Groups

    def get_draw_groups(
        self,
        title: str | None = None,
        description: str | None = None,
        content: str | None = None,
    ) -> list[DrawGroup]:
        """Return all the draw groups that match the criteria.

        Args:

            title -- str or None

            description -- str regex or None

            content -- str regex or None

        Returns: list of DrawGroup
        """
        return self._filtered_elements(
            "descendant::draw:g",
            svg_title=title,
            svg_desc=description,
            content=content,
        )  # type: ignore[return-value]

    def get_draw_group(
        self,
        position: int = 0,
        name: str | None = None,
        title: str | None = None,
        description: str | None = None,
        content: str | None = None,
    ) -> DrawGroup | None:
        """Return the  draw group that matches the criteria.

        Args:

            position -- int

            name  -- str or None

            title -- str or None

            description -- str regex or None

            content -- str regex or None

        Returns: DrawGroup or None if not found
        """
        return self._filtered_element(
            "descendant::draw:g",
            position,
            draw_name=name,
            svg_title=title,
            svg_desc=description,
            content=content,
        )  # type: ignore[return-value]

    # Lines

    def get_draw_lines(
        self,
        draw_style: str | None = None,
        draw_text_style: str | None = None,
        content: str | None = None,
    ) -> list[LineShape]:
        """Return all the draw lines that match the criteria.

        Args:

            draw_style -- str

            draw_text_style -- str

            content -- str regex

        Returns: list of LineShape
        """
        return self._filtered_elements(
            "descendant::draw:line",
            draw_style=draw_style,
            draw_text_style=draw_text_style,
            content=content,
        )  # type: ignore[return-value]

    def get_draw_line(
        self,
        position: int = 0,
        id: str | None = None,  # noqa:A002
        content: str | None = None,
    ) -> LineShape | None:
        """Return the draw line that matches the criteria.

        Args:

            position -- int

            id -- str

            content -- str regex

        Returns: LineShape or None if not found
        """
        return self._filtered_element(
            "descendant::draw:line", position, draw_id=id, content=content
        )  # type: ignore[return-value]

    # Rectangles

    def get_draw_rectangles(
        self,
        draw_style: str | None = None,
        draw_text_style: str | None = None,
        content: str | None = None,
    ) -> list[RectangleShape]:
        """Return all the draw rectangles that match the criteria.

        Args:

            draw_style -- str

            draw_text_style -- str

            content -- str regex

        Returns: list of RectangleShape
        """
        return self._filtered_elements(
            "descendant::draw:rect",
            draw_style=draw_style,
            draw_text_style=draw_text_style,
            content=content,
        )  # type: ignore[return-value]

    def get_draw_rectangle(
        self,
        position: int = 0,
        id: str | None = None,  # noqa:A002
        content: str | None = None,
    ) -> RectangleShape | None:
        """Return the draw rectangle that matches the criteria.

        Args:

            position -- int

            id -- str

            content -- str regex

        Returns: RectangleShape or None if not found
        """
        return self._filtered_element(
            "descendant::draw:rect", position, draw_id=id, content=content
        )  # type: ignore[return-value]

    # Ellipse

    def get_draw_ellipses(
        self,
        draw_style: str | None = None,
        draw_text_style: str | None = None,
        content: str | None = None,
    ) -> list[EllipseShape]:
        """Return all the draw ellipses that match the criteria.

        Args:

            draw_style -- str

            draw_text_style -- str

            content -- str regex

        Returns: list of EllipseShape
        """
        return self._filtered_elements(
            "descendant::draw:ellipse",
            draw_style=draw_style,
            draw_text_style=draw_text_style,
            content=content,
        )  # type: ignore[return-value]

    def get_draw_ellipse(
        self,
        position: int = 0,
        id: str | None = None,  # noqa:A002
        content: str | None = None,
    ) -> EllipseShape | None:
        """Return the draw ellipse that matches the criteria.

        Args:

            position -- int

            id -- str

            content -- str regex

        Returns: EllipseShape or None if not found
        """
        return self._filtered_element(
            "descendant::draw:ellipse", position, draw_id=id, content=content
        )  # type: ignore[return-value]

    # Connectors

    def get_draw_connectors(
        self,
        draw_style: str | None = None,
        draw_text_style: str | None = None,
        content: str | None = None,
    ) -> list[ConnectorShape]:
        """Return all the draw connectors that match the criteria.

        Args:

            draw_style -- str

            draw_text_style -- str

            content -- str regex

        Returns: list of ConnectorShape
        """
        return self._filtered_elements(
            "descendant::draw:connector",
            draw_style=draw_style,
            draw_text_style=draw_text_style,
            content=content,
        )  # type: ignore[return-value]

    def get_draw_connector(
        self,
        position: int = 0,
        id: str | None = None,  # noqa:A002
        content: str | None = None,
    ) -> ConnectorShape | None:
        """Return the draw connector that matches the criteria.

        Args:

            position -- int

            id -- str

            content -- str regex

        Returns: ConnectorShape or None if not found
        """
        return self._filtered_element(
            "descendant::draw:connector", position, draw_id=id, content=content
        )  # type: ignore[return-value]

    def get_orphan_draw_connectors(self) -> list[ConnectorShape]:
        """Return a list of connectors which don't have any shape connected to
        them.

        Returns: list of ConnectorShape
        """
        connectors = []
        for connector in self.get_draw_connectors():
            start_shape = connector.get_attribute("draw:start-shape")
            end_shape = connector.get_attribute("draw:end-shape")
            if start_shape is None and end_shape is None:
                connectors.append(connector)
        return connectors

    # Tracked changes and text change

    def get_tracked_changes(self) -> TrackedChanges | None:
        """Return the tracked-changes part in the text body.

        Returns: TrackedChanges or None
        """
        return self.get_element("//text:tracked-changes")  # type: ignore[return-value]

    @property
    def tracked_changes(self) -> Element | None:
        """Return the tracked-changes part in the text body.

        Returns: Element or None
        """
        return self.get_tracked_changes()

    def get_changes_ids(self) -> list[Element | EText]:
        """Return a list of ids that refers to a change region in the tracked
        changes list.
        """
        # Insertion changes or deletion changes
        xpath_query = (
            "descendant::text:change-start/@text:change-id "
            "| descendant::text:change/@text:change-id"
        )
        return self.xpath(xpath_query)

    def get_text_change_deletions(self) -> list[TextChange]:
        """Return all the text changes of deletion kind: the tags text:change.
        Consider using : get_text_changes()

        Returns: list of TextChange
        """
        return self._filtered_elements(
            "descendant::text:text:change",
        )  # type: ignore[return-value]

    def get_text_change_deletion(
        self,
        position: int = 0,
        idx: str | None = None,
    ) -> TextChange | None:
        """Return the text change of deletion kind that matches the criteria.
        Search only for the tags text:change.
        Consider using : get_text_change()

        Args:

            position -- int

            idx -- str

        Returns: TextChange or None if not found
        """
        return self._filtered_element(
            "descendant::text:change", position, change_id=idx
        )  # type: ignore[return-value]

    def get_text_change_starts(self) -> list[TextChangeStart]:
        """Return all the text change-start. Search only for the tags
        text:change-start.
        Consider using : get_text_changes()

        Returns: list of TextChangeStart
        """
        return self._filtered_elements(
            "descendant::text:change-start",
        )  # type: ignore[return-value]

    def get_text_change_start(
        self,
        position: int = 0,
        idx: str | None = None,
    ) -> TextChangeStart | None:
        """Return the text change-start that matches the criteria. Search
        only the tags text:change-start.
        Consider using : get_text_change()

        Args:

            position -- int

            idx -- str

        Returns: TextChangeStart or None if not found
        """
        return self._filtered_element(
            "descendant::text:change-start", position, change_id=idx
        )  # type: ignore[return-value]

    def get_text_change_ends(self) -> list[TextChangeEnd]:
        """Return all the text change-end. Search only the tags
        text:change-end.
        Consider using : get_text_changes()

        Returns: list of TextChangeEnd
        """
        return self._filtered_elements(
            "descendant::text:change-end",
        )  # type: ignore[return-value]

    def get_text_change_end(
        self,
        position: int = 0,
        idx: str | None = None,
    ) -> TextChangeEnd | None:
        """Return the text change-end that matches the criteria. Search only
        the tags text:change-end.
        Consider using : get_text_change()

        Args:

            position -- int

            idx -- str

        Returns: TextChangeEnd or None if not found
        """
        return self._filtered_element(
            "descendant::text:change-end", position, change_id=idx
        )  # type: ignore[return-value]

    def get_text_changes(self) -> list[TextChange | TextChangeStart]:
        """Return all the text changes, either single deletion (text:change) or
        start of range of changes (text:change-start).

        Returns: list of TextChange or TextChangeStart
        """
        request = "descendant::text:change-start | descendant::text:change"
        return self._filtered_elements(request)  # type: ignore[return-value]

    @property
    def text_changes(self) -> list[TextChange | TextChangeStart]:
        """Return all the text changes, either single deletion (text:change) or
        start of range of changes (text:change-start).

        Returns: list of Element
        """
        return self.get_text_changes()

    def get_text_change(
        self,
        position: int = 0,
        idx: str | None = None,
    ) -> TextChange | TextChangeStart | None:
        """Return the text change that matches the criteria. Either single
        deletion (text:change) or start of range of changes (text:change-start).
        position : index of the element to retrieve if several matches, default
        is 0.
        idx : change-id of the element.

        Args:

            position -- int

            idx -- str

        Returns: Element or None if not found
        """
        if idx:
            request = (
                f'descendant::text:change-start[@text:change-id="{idx}"] '
                f'| descendant::text:change[@text:change-id="{idx}"]'
            )
            return self._filtered_element(request, 0)  # type: ignore[return-value]

        request = "descendant::text:change-start | descendant::text:change"
        return self._filtered_element(request, position)  # type: ignore[return-value]

    # Table Of Content

    def get_tocs(self) -> list[TOC]:
        """Return all the tables of contents.

        Returns: list of TOC
        """
        return self.get_elements("text:table-of-content")  # type: ignore[return-value]

    @property
    def tocs(self) -> list[TOC]:
        """Return all the tables of contents.

        Returns: list of TOC
        """
        return self.get_elements("text:table-of-content")  # type: ignore[return-value]

    def get_toc(
        self,
        position: int = 0,
        content: str | None = None,
    ) -> TOC | None:
        """Return the table of contents that matches the criteria.

        Args:

            position -- int

            content -- str regex

        Returns: TOC or None if not found
        """
        return self._filtered_element(
            "text:table-of-content", position, content=content
        )  # type: ignore[return-value]

    @property
    def toc(self) -> TOC | None:
        """Return the first table of contents.

        Returns: odf_toc or None if not found
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

    def get_styles(self, family: str | None = None) -> list[Style]:
        # Both common and default styles
        tagname = self._get_style_tagname(family)
        return self._filtered_elements(tagname, family=family)  # type: ignore[return-value]

    def get_style(
        self,
        family: str,
        name_or_element: str | Element | None = None,
        display_name: str | None = None,
    ) -> Style | None:
        """Return the style uniquely identified by the family/name pair. If the
        argument is already a style object, it will return it.

        If the name is not the internal name but the name you gave in the
        desktop application, use display_name instead.

        Args:

            family -- 'paragraph', 'text', 'graphic', 'table', 'list',
                      'number'

            name_or_element -- str or Style

            display_name -- str

        Returns: Style or None if not found
        """
        if isinstance(name_or_element, Element):
            name = self.get_attribute("style:name")
            if name is not None:
                return name_or_element  # type: ignore[return-value]
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
            )  # type: ignore[return-value]
        else:
            return self._filtered_element(
                tagname,
                0,
                draw_name=style_name or display_name,
                family=family,
            )  # type: ignore[return-value]

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
