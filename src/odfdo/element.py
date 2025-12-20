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
from collections.abc import Callable, Iterable
from copy import deepcopy
from datetime import datetime, timedelta
from decimal import Decimal
from functools import cache
from re import search
from typing import TYPE_CHECKING, Any, NamedTuple, cast

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
    from .body import Body
    from .draw_page import DrawPage
    from .frame import Frame
    from .header import Header
    from .image import DrawImage
    from .list import List
    from .paragraph import Paragraph, Span
    from .shapes import (
        ConnectorShape,
        DrawGroup,
        EllipseShape,
        LineShape,
        RectangleShape,
    )
    from .style import Style
    from .style_base import StyleBase
    from .tracked_changes import (
        TextChange,
        TextChangeEnd,
        TextChangeStart,
    )
    from .variable import VarSet

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


class PropDefBool(NamedTuple):
    """Named tuple for boolean class properties (internal)."""

    name: str
    attr: str
    default: bool = False


def _decode_qname(qname: str) -> tuple[str | None, str]:
    """Decode a prefixed qualified XML name into its URI and local name.

    For example, "office:document" would be decoded to
    ("urn:oasis:names:tc:opendocument:xmlns:office:1.0", "document").

    Args:
        qname: The qualified name (e.g., "prefix:localname" or "localname").

    Returns:
        tuple[str | None, str]: A tuple containing the namespace URI (or None if no prefix)
            and the local name.

    Raises:
        ValueError: If the XML prefix is unknown.
    """
    if ":" in qname:
        prefix, name = qname.split(":")
        try:
            uri = ODF_NAMESPACES[prefix]
        except KeyError as e:
            raise ValueError(f'XML prefix "{prefix}" is unknown') from e
        return uri, name
    return None, qname


def _uri_to_prefix(uri: str) -> str:
    """Find the XML prefix associated with a given namespace URI.

    Args:
        uri: The namespace URI to look up.

    Returns:
        str: The corresponding XML prefix.

    Raises:
        ValueError: If the URI is not found in the known ODF namespaces.
    """
    for key, value in ODF_NAMESPACES.items():
        if value == uri:
            return key
    raise ValueError(f"uri {uri!r} not found")


def _get_prefixed_name(tag: str) -> str:
    """Convert an lxml-style tag name (e.g., "{uri}name") to a prefixed name (e.g., "prefix:name").

    Args:
        tag: The tag name in lxml's "{uri}name" format.

    Returns:
        str: The tag name in "prefix:name" format.
    """
    if "}" not in tag:
        return f":{tag}"
    uri, name = tag.split("}", 1)
    prefix = _uri_to_prefix(uri[1:])
    return f"{prefix}:{name}"


def _get_lxml_tag(qname: str) -> str:
    """Convert a prefixed qualified name (e.g., "prefix:name") to an lxml-style tag name (e.g., "{uri}name").

    Args:
        qname: The qualified name in "prefix:name" format.

    Returns:
        str: The tag name in lxml's "{uri}name" format.
    """
    uri, name = _decode_qname(qname)
    return f"{{{uri}}}{name}"


def _get_lxml_tag_or_name(qname: str) -> str:
    """Convert a prefixed qualified name to an lxml-style tag name or just the local name.

    If the qualified name has a prefix, it's converted to "{uri}name" format.
    If it has no prefix, it returns just the local name.

    Args:
        qname: The qualified name (e.g., "prefix:localname" or "localname").

    Returns:
        str: The tag name in lxml's "{uri}name" format, or the local name if no prefix.
    """
    uri, name = _decode_qname(qname)
    if uri is None:
        return name
    return f"{{{uri}}}{name}"


def _family_style_tagname(family: str) -> str:
    """Map a style family string to its corresponding ODF tag name.

    Args:
        family: The style family (e.g., "paragraph", "text").

    Returns:
        str: The ODF tag name associated with the style family.

    Raises:
        ValueError: If the provided family is unknown.
    """
    try:
        return FAMILY_MAPPING[family]
    except KeyError as e:
        raise ValueError(f"Unknown family: {family!r}") from e


@cache
def xpath_compile(path: str) -> XPath:
    """Compile an XPath query string into an `lxml.etree.XPath` object.

    This function pre-compiles XPath expressions for efficiency and
    automatically includes ODF namespaces. It is cached to avoid recompiling
    the same XPath query multiple times.

    Args:
        path: The XPath query string.

    Returns:
        XPath: A compiled `lxml.etree.XPath` object.
    """
    return XPath(path, namespaces=ODF_NAMESPACES, regexp=False)


def xpath_return_elements(xpath: XPath, target: _Element) -> list[_Element]:
    """Execute a compiled XPath query and return a list of matching lxml elements.

    This function filters the raw XPath results to ensure only `lxml.etree._Element`
    objects are returned.

    Args:
        xpath: A compiled `lxml.etree.XPath` object.
        target: The lxml element on which to apply the XPath query.

    Returns:
        list[_Element]: A list of matching `lxml.etree._Element` objects.
    """
    elements = xpath(target)
    try:
        return [e for e in elements if isinstance(e, _Element)]
    except TypeError as e:  # pragma: nocover
        # cant happen
        msg = f"Bad XPath result, list expected, got {elements!r}"
        raise TypeError(msg) from e


def xpath_return_strings(xpath: XPath, target: _Element) -> list[str]:
    """Execute a compiled XPath query and return a list of matching strings.

    This function filters the raw XPath results to ensure only string objects
    are returned.

    Args:
        xpath: A compiled `lxml.etree.XPath` object.
        target: The lxml element on which to apply the XPath query.

    Returns:
        list[str]: A list of matching string objects.
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
        cls: Python class, subtype of Element.
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
        cls: Python class.
        tag_list: Iterable of qname tags for the class.
    """
    # Turn tag name into what lxml is expecting
    for qname in tag_list:
        _register_element_class(cls, qname)


def _register_element_class(cls: type[Element], qname: str) -> None:
    # Turn tag name into what lxml is expecting
    tag = _get_lxml_tag(qname)
    if tag in _class_registry:  # pragma: nocover
        msg = f"Class with tag {qname!r} already seen: {_class_registry[tag]!r}"
        raise RuntimeError(msg)
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
        """Initialize EText instance.

        Args:
            text_result: The lxml element representing the text node.
        """
        self.__parent = text_result.getparent()
        self.__is_text: bool = bool(text_result.is_text)
        self.__is_tail: bool = bool(text_result.is_tail)

    @property
    def parent(self) -> Element | None:
        """Return the parent element of this text node.

        Returns:
            Element | None: The parent Element or None if it's a root text node.
        """
        parent = self.__parent
        # XXX happens just because of the unit test
        if parent is None:
            return None
        return Element.from_tag(tag_or_elem=parent)

    def is_text(self) -> bool:
        """Check if this text node represents the 'text' part of its parent.

        Returns:
            bool: True if it's the text part, False otherwise.
        """
        return self.__is_text

    def is_tail(self) -> bool:
        """Check if this text node represents the 'tail' part of its parent.

        Returns:
            bool: True if it's the tail part, False otherwise.
        """
        return self.__is_tail


class Element(MDBase):
    """Base class for all ODF elements, providing an abstraction of the underlying XML structure.

    This class handles the creation, manipulation, and serialization of ODF elements,
    acting as a wrapper around `lxml.etree._Element` objects.
    """

    _tag: str = ""
    _properties: tuple[PropDef | PropDefBool, ...] = ()

    def __init__(self, **kwargs: Any) -> None:
        """Initialize an Element instance.

        This constructor can be used to create a new ODF element from scratch
        or to wrap an existing `lxml.etree._Element` object.

        Args:
            **kwargs (Any):
                - tag_or_elem (str | lxml.etree._Element, optional): An existing
                  lxml element to wrap, or an ODF tag string (e.g., "text:p")
                  to create a new element. If not provided, a new element is
                  created based on the class's `_tag` attribute.
                - tag (str, optional): The ODF tag string to use when creating a
                  new element, if `tag_or_elem` is not provided. Defaults to
                  `_tag` of the class.

        Raises:
            TypeError: If `tag_or_elem` is provided but is not an `_Element` instance.
        """
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
        """Factory method to create an Element instance (or a subclass) from an XML tag.

        This method can convert an lxml Element or an ODF string tag into an
        ODF XML Element of the appropriate class (e.g., Paragraph, Table, etc.).

        Args:
            tag_or_elem: Either an ODF string tag (e.g., "text:p")
                or an existing `lxml.etree._Element` instance.

        Returns:
            Element: An instance of Element or its appropriate subclass.
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
        """Factory method used internally for cloning elements.

        This method is similar to `from_tag` but is specifically optimized
        for cloning operations, potentially utilizing a cache.

        Args:
            tree_element: The `lxml.etree._Element` instance to clone.
            cache: An optional cache to be copied to the new element.

        Returns:
            Element: A new Element instance (or subclass) representing the cloned element.
        """
        tag = to_str(tree_element.tag)
        klass = _class_registry.get(tag, cls)
        element: Element = klass(tag_or_elem=tree_element)
        if cache:
            element._copy_cache(cache)
        return element

    def _copy_cache(self, cache: tuple) -> None:
        """Copies cache data to the element.

        This method is intended to be redefined by subclasses that utilize caching.

        Args:
            cache: The cache data to be copied.
        """
        pass

    @staticmethod
    def _make_etree_element(tag: str) -> _Element:
        """Create an lxml Element from an ODF tag string.

        Args:
            tag: The ODF tag string (e.g., "text:p", "<text:p/>").

        Returns:
            _Element: An lxml Element instance.

        Raises:
            TypeError: If the tag is not a string.
            ValueError: If the tag is empty.
        """
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
        """Internal method to get the value of an attribute by its qualified name.

        Args:
            attr_name (str): The qualified name of the attribute (e.g., "office:name").

        Returns:
            str | None: The attribute's value as a string, or None if the attribute is not found.
        """
        value = self.__element.get(_get_lxml_tag(attr_name))
        if value is None:
            return None
        return str(value)

    def _base_attrib_setter(
        self,
        attr_name: str,
        value: str | int | float | bool | None,
    ) -> None:
        """Internal method to set the value of an attribute by its qualified name.

        Args:
            attr_name (str): The qualified name of the attribute (e.g., "office:name").
            value (str | int | float | bool | None): The value to set for the attribute.
                If None, the attribute is removed. Boolean values are encoded.
        """
        if value is None:
            with contextlib.suppress(KeyError):
                del self.__element.attrib[_get_lxml_tag(attr_name)]
            return
        if isinstance(value, bool):
            value = Boolean.encode(value)
        self.__element.set(_get_lxml_tag(attr_name), str(value))

    @staticmethod
    def _generic_attrib_getter(attr_name: str, family: str | None = None) -> Callable:
        """Creates a getter function for a generic attribute.

        Args:
            attr_name (str): The qualified name of the attribute.
            family (str | None): Optional family name to filter by.

        Returns:
            Callable: A getter function that takes an Element instance and returns
                the attribute's value as a string, boolean, or None.
        """

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
        """Creates a setter function for a generic attribute.

        Args:
            attr_name (str): The qualified name of the attribute.
            family (str | None): Optional family name to filter by.

        Returns:
            Callable: A setter function that takes an Element instance and the value
                to set for the attribute.
        """

        def setter(self: Element, value: Any) -> None:
            try:
                if family and self.family != family:  # type: ignore
                    return None
            except AttributeError:
                return None
            self._base_attrib_setter(attr_name, value)

        return setter

    @staticmethod
    def _boolean_attrib_getter(prop: PropDefBool) -> Callable:
        """Creates a getter function for a boolean attribute.

        Args:
            prop (PropDefBool): A NamedTuple defining the boolean property.

        Returns:
            Callable: A getter function that takes an Element instance and returns
                the boolean value of the attribute, or its default.
        """

        def getter(self: Element) -> bool:
            return self._get_attribute_bool_default(prop.attr, prop.default)

        return getter

    @staticmethod
    def _boolean_attrib_setter(prop: PropDefBool) -> Callable:
        """Creates a setter function for a boolean attribute.

        Args:
            prop (PropDefBool): A NamedTuple defining the boolean property.

        Returns:
            Callable: A setter function that takes an Element instance and the boolean
                value to set for the attribute.
        """

        def setter(self: Element, value: bool) -> None:
            self._set_attribute_bool_default(prop.attr, value, prop.default)

        return setter

    @classmethod
    def _define_attribut_property(cls: type[Element]) -> None:
        """Dynamically defines properties for the class based on `_properties`.

        This method iterates through the `_properties` tuple of the class and
        creates corresponding getter and setter properties for XML attributes.
        """
        for prop in cls._properties:
            if isinstance(prop, PropDef):
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
            else:
                setattr(
                    cls,
                    prop.name,
                    property(
                        cls._boolean_attrib_getter(prop),
                        cls._boolean_attrib_setter(prop),
                        None,
                        f"Get/set the attribute {prop.attr}",
                    ),
                )

    @staticmethod
    def _make_before_regex(
        before: str | None,
        after: str | None,
    ) -> re.Pattern:
        """Compiles a regular expression for insertion before or after text.

        Args:
            before (str | None): A regex pattern to match text before which to insert.
            after (str | None): A regex pattern to match text after which to insert.

        Returns:
            re.Pattern: A compiled regex pattern based on `before` or `after`.

        Raises:
            ValueError: If both `before` and `after` are None.
        """
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
        """Searches for the last occurrence of a regex pattern in a list of strings.

        Args:
            xpath_result (list[str]): A list of strings to search within.
            regex (re.Pattern): The compiled regex pattern to search for.

        Returns:
            tuple[str, re.Match]: A tuple containing the string where the match was
                found and the match object itself.

        Raises:
            ValueError: If the text matching the regex is not found.
        """
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
        """Searches for the nth occurrence of a regex pattern in a list of strings.

        Args:
            xpath_result (list[str]): A list of strings to search within.
            regex (re.Pattern): The compiled regex pattern to search for.
            position (int): The 0-based index of the match to find.

        Returns:
            tuple[str, re.Match]: A tuple containing the string where the match was
                found and the match object itself.

        Raises:
            ValueError: If the text matching the regex is not found.
        """
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
        """Calculates the insertion position based on 'before' or 'after' regex.

        Args:
            current (_Element): The current lxml element.
            element (_Element): The element to be inserted.
            before (str | None): Regex pattern to find position before.
            after (str | None): Regex pattern to find position after.
            position (int): The occurrence of the regex to consider (negative for last).
            xpath_text (XPath): Compiled XPath for text extraction.

        Returns:
            tuple[int, str]: A tuple containing the calculated insertion position
                and the text string where the insertion will occur.
        """
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
        """Finds the text and insertion point based on a character position.

        Args:
            current (_Element): The current lxml element.
            element (_Element): The element to be inserted.
            before (str | None): Not used in this method, kept for signature compatibility.
            after (str | None): Not used in this method, kept for signature compatibility.
            position (int): The character position for insertion.
            xpath_text (XPath): Compiled XPath for text extraction.

        Returns:
            tuple[int, str]: A tuple containing the calculated insertion point within
                the text and the text string where the insertion will occur.

        Raises:
            ValueError: If the text at the specified position is not found.
        """
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
        """Insert an element before or after characters matching a regex.

        When the regex matches multiple parts of the text, `position` can specify
        which part to use. If both `before` and `after` are None, `position`
        refers to the character index. A positive `position` inserts before that
        character; `position=-1` inserts after the last character.
        Annotation text content is ignored.

        Args:
            element (Element): The element to insert.
            before (str | None): A regex pattern. The element will be inserted
                before the text matching this pattern.
            after (str | None): A regex pattern. The element will be inserted
                after the text matching this pattern.
            position (int): The 0-based index of the regex match to consider,
                or a character position if `before` and `after` are None.

        Raises:
            ValueError: If an invalid combination of arguments is provided.
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
        """Gets the underlying XML tag with the qualified name.

        Returns:
            str: The qualified name of the XML tag (e.g., "text:span").
        """
        return _get_prefixed_name(self.__element.tag)

    @tag.setter
    def tag(self, qname: str) -> None:
        """Sets the underlying XML tag with the given qualified name.

        Warning: Direct change of the tag does not change the Python element class itself.

        Args:
            qname (str): The new qualified name for the XML tag (e.g., "text:span").
        """
        self.__element.tag = _get_lxml_tag(qname)

    def elements_repeated_sequence(
        self,
        xpath_instance: XPath,
        name: str,
    ) -> list[tuple[int, int]]:
        """Extracts repeated sequence information from elements for table handling.

        This utility method is primarily used by the table module to process
        elements that might have a 'number-columns-repeated' or similar attribute.
        It returns a list of tuples, where each tuple contains the index of the
        element and how many times it is logically repeated.

        Args:
            xpath_instance (XPath): A compiled XPath object to select sub-elements.
            name (str): The name of the attribute (e.g., "table:number-columns-repeated")
                that indicates repetition.

        Returns:
            list[tuple[int, int]]: A list of (index, repetition_count) tuples.
        """
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
        """Returns a list of elements obtained by applying an XPath query.

        Args:
            xpath_query (XPath | str): The XPath query string or a compiled `lxml.etree.XPath` object.

        Returns:
            list[Element]: A list of Element instances matching the query.
        """
        if isinstance(xpath_query, str):
            elements = xpath_return_elements(xpath_compile(xpath_query), self.__element)
        else:
            elements = xpath_return_elements(xpath_query, self.__element)
        return [Element.from_tag_for_clone(e, None) for e in elements]

    def get_element(self, xpath_query: str) -> Element | None:
        """Returns the first element obtained by applying an XPath query.

        Args:
            xpath_query (str): The XPath query string.

        Returns:
            Element | None: The first Element instance matching the query, or None if no match.
        """
        result = self.__element.xpath(f"({xpath_query})[1]", namespaces=ODF_NAMESPACES)
        if result:
            return Element.from_tag(result[0])
        return None

    def _get_element_idx(self, xpath_query: XPath | str, idx: int) -> Element | None:
        """Returns the element at a specific index from an XPath query result.

        Args:
            xpath_query (XPath | str): The XPath query string or a compiled `lxml.etree.XPath` object.
            idx (int): The 0-based index of the desired element in the query result.

        Returns:
            Element | None: The Element instance at the specified index, or None if not found.
        """
        result = self.__element.xpath(
            f"({xpath_query})[{idx + 1}]", namespaces=ODF_NAMESPACES
        )
        if result:
            return Element.from_tag(result[0])
        return None

    def _get_element_idx2(self, xpath_instance: XPath, idx: int) -> Element | None:
        """Returns the element at a specific index using a pre-compiled XPath instance.

        Args:
            xpath_instance (XPath): A compiled `lxml.etree.XPath` object.
            idx (int): The 0-based index of the desired element in the query result.

        Returns:
            Element | None: The Element instance at the specified index, or None if not found.
        """
        result = xpath_instance(self.__element, idx=idx + 1)
        if result:
            return Element.from_tag(result[0])
        return None

    @property
    def attributes(self) -> dict[str, str]:
        """Gets all attributes of the element as a dictionary.

        The keys are qualified attribute names (e.g., "office:name"),
        and the values are their string representations.

        Returns:
            dict[str, str]: A dictionary of attribute names and their values.
        """
        return {
            _get_prefixed_name(str(key)): str(value)
            for key, value in self.__element.attrib.items()
        }

    def get_attribute(self, name: str) -> str | bool | None:
        """Returns the value of a specified attribute.

        Args:
            name (str): The qualified name of the attribute to retrieve (e.g., "office:name").

        Returns:
            str | bool | None: The attribute's value, which can be a string, a boolean
                (if the original value was "true" or "false"), or None if the attribute is not found.
        """
        element = self.__element
        lxml_tag = _get_lxml_tag_or_name(name)
        value = element.get(lxml_tag)
        if value is None:
            return None
        elif value in ("true", "false"):
            return Boolean.decode(value)
        return str(value)

    def get_attribute_integer(self, name: str) -> int | None:
        """Returns the value of a specified attribute as an integer.

        Args:
            name (str): The qualified name of the attribute to retrieve.

        Returns:
            int | None: The attribute's value as an integer, or None if the attribute
                is not found or cannot be converted to an integer.
        """
        element = self.__element
        lxml_tag = _get_lxml_tag_or_name(name)
        value = element.get(lxml_tag)
        if value is None:
            return None
        try:
            return int(value)
        except ValueError:
            return None

    def get_attribute_number(self, name: str) -> int | Decimal | None:
        """Returns the value of a specified attribute as a number (Decimal or int).

        Args:
            name (str): The qualified name of the attribute to retrieve.

        Returns:
            int | Decimal | None: The attribute's value as an int (if it's a whole number)
                or a Decimal, or None if the attribute is not found or cannot be
                converted to a number.
        """
        element = self.__element
        lxml_tag = _get_lxml_tag_or_name(name)
        value = element.get(lxml_tag)
        if value is None:
            return None
        value = Decimal(value)
        # Return 3 instead of 3.0 if possible
        with contextlib.suppress(ValueError):
            if int(value) == value:
                return int(value)
        return value

    def get_attribute_string(self, name: str) -> str | None:
        """Returns the value of a specified attribute as a string.

        Args:
            name (str): The qualified name of the attribute to retrieve.

        Returns:
            str | None: The attribute's value as a string, or None if the attribute is not found.
        """
        element = self.__element
        lxml_tag = _get_lxml_tag_or_name(name)
        value = element.get(lxml_tag)
        if value is None:
            return None
        return str(value)

    def _get_attribute_bool_default(self, name: str, default: bool = True) -> bool:
        """Returns the value of a specified boolean attribute, using a default if not present.

        Args:
            name (str): The qualified name of the attribute to retrieve.
            default (bool): The default boolean value to return if the attribute is not found.

        Returns:
            bool: The attribute's boolean value or the provided default value.
        """
        element = self.__element
        lxml_tag = _get_lxml_tag_or_name(name)
        value = element.get(lxml_tag)
        if value is None:
            return default
        return Boolean.decode(value)

    def _set_attribute_bool_default(
        self, name: str, value: bool | str | None, default: bool = True
    ) -> None:
        """Sets the value of a specified boolean attribute, removing it if it matches the default.

        Args:
            name (str): The qualified name of the attribute to set.
            value (bool | str | None): The boolean value to set. Can be a bool,
                "true"/"false" string, or None. If None, it defaults to False.
            default (bool): The default boolean value. If the `value` to set
                matches this default, the attribute is removed.
        """
        element = self.__element
        lxml_tag = _get_lxml_tag_or_name(name)
        if value is None:
            value = False
        if isinstance(value, str):
            value = value.lower() == "true"
        if value == default:
            with contextlib.suppress(KeyError):
                del element.attrib[lxml_tag]
            return
        element.set(lxml_tag, Boolean.encode(value))

    def _get_attribute_str_default(self, name: str, default: str = "") -> str:
        """Returns the value of a specified string attribute, using a default if not present.

        Args:
            name (str): The qualified name of the attribute to retrieve.
            default (str): The default string value to return if the attribute is not found.

        Returns:
            str: The attribute's string value or the provided default value.
        """
        element = self.__element
        lxml_tag = _get_lxml_tag_or_name(name)
        value = element.get(lxml_tag)
        if value is None:
            return default
        return str(value)

    def _set_attribute_str_default(
        self, name: str, value: str | None, default: str = ""
    ) -> None:
        """Sets the value of a specified string attribute, removing it if it matches the default.

        Args:
            name (str): The qualified name of the attribute to set.
            value (str | None): The string value to set. If None or matches `default`,
                the attribute is removed.
            default (str): The default string value. If the `value` to set
                matches this default, the attribute is removed.
        """
        element = self.__element
        lxml_tag = _get_lxml_tag_or_name(name)
        if value is None or value == default:
            with contextlib.suppress(KeyError):
                del element.attrib[lxml_tag]
            return
        element.set(lxml_tag, value)

    def _get_attribute_int_default(self, name: str, default: int) -> int:
        """Returns the value of a specified integer attribute, using a default if not present.

        Args:
            name (str): The qualified name of the attribute to retrieve.
            default (int): The default integer value to return if the attribute is not found
                or cannot be converted.

        Returns:
            int: The attribute's integer value or the provided default value.
        """
        element = self.__element
        lxml_tag = _get_lxml_tag_or_name(name)
        value = element.get(lxml_tag)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    def _set_attribute_int_default(
        self, name: str, value: int | None, default: int
    ) -> None:
        """Sets the value of a specified integer attribute, removing it if it matches the default.

        Args:
            name (str): The qualified name of the attribute to set.
            value (int | None): The integer value to set. If None or matches `default`,
                the attribute is removed.
            default (int): The default integer value. If the `value` to set
                matches this default, the attribute is removed.
        """
        element = self.__element
        lxml_tag = _get_lxml_tag_or_name(name)
        if value is None or value == default:
            with contextlib.suppress(KeyError):
                del element.attrib[lxml_tag]
            return
        element.set(lxml_tag, str(value))

    def _set_attribute_number_default(
        self,
        name: str,
        value: Decimal | int | float | None,
        default: Decimal | int | float | None,
    ) -> None:
        """Sets the value of a specified number attribute (Decimal, int, or float),
        removing it if it matches the default.

        Args:
            name (str): The qualified name of the attribute to set.
            value (Decimal | int | float | None): The numeric value to set.
                If None or matches `default`, the attribute is removed.
            default (Decimal | int | float | None): The default numeric value.
                If the `value` to set matches this default, the attribute is removed.
        """
        element = self.__element
        lxml_tag = _get_lxml_tag_or_name(name)
        if value is None or value == default:
            with contextlib.suppress(KeyError):
                del element.attrib[lxml_tag]
            return
        element.set(lxml_tag, str(value))

    def set_attribute(
        self, name: str, value: bool | str | tuple[int, int, int] | None
    ) -> None:
        """Sets the value of a specified attribute.

        Handles special cases for color properties and boolean values.

        Args:
            name (str): The qualified name of the attribute to set.
            value (bool | str | tuple[int, int, int] | None): The value to set.
                Can be a boolean, string, a color tuple (R, G, B), or None.
                If None, the attribute is removed.

        Raises:
            TypeError: If a boolean value is provided for a color property.
        """
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

    def set_style_attribute(self, name: str, value: Style | str | None) -> None:
        """Sets a style-related attribute, allowing a Style object as a value.

        Args:
            name (str): The qualified name of the style attribute to set.
            value (Style | str | None): The value for the style attribute.
                Can be a `Style` object (its name will be used), a string, or None.
        """
        if isinstance(value, Element):
            value = str(value.name)
        return self.set_attribute(name, value)

    def del_attribute(self, name: str) -> None:
        """Deletes a specified attribute from the element.

        Args:
            name (str): The qualified name of the attribute to delete.

        Raises:
            KeyError: If the specified attribute does not exist.
        """
        element = self.__element
        lxml_tag = _get_lxml_tag_or_name(name)
        del element.attrib[lxml_tag]

    @property
    def text(self) -> str:
        """Gets the text content of the element.

        Returns:
            str: The text content of the element. Defaults to an empty string if no text is present.
        """
        return self.__element.text or ""

    @text.setter
    def text(self, text: str | None) -> None:
        """Sets the text content of the element.

        Args:
            text (str | None): The new text content. If None, it is set to an empty string.

        Raises:
            TypeError: If the provided text is not a string type.
        """
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
        """Returns the concatenated inner text and tail of the element.

        Returns:
            str: The string representation of the element's inner text plus its tail.
        """
        return str(self) + (self.tail or "")

    # def _elements_descendants(self) -> Iterator[Element]:
    #     for elem in self.__element.iterdescendants():
    #         if isinstance(elem, _Element):
    #             yield Element.from_tag(elem)

    @property
    def inner_text(self) -> str:
        """Returns the concatenated text content of the element and its children (excluding its own tail).

        Returns:
            str: The inner text of the element.
        """
        return self.text + "".join(e._text_tail for e in self.children)

    @property
    def text_recursive(self) -> str:
        """Returns the full recursive text content of the element, including its own tail.

        Returns:
            str: The entire text content, recursively.
        """
        return self.inner_text + (self.tail or "")

    @property
    def tail(self) -> str | None:
        """Gets the text immediately following the element.

        Returns:
            str | None: The tail text, or None if no tail text is present.
        """
        return self.__element.tail  # type: ignore[no-any-return]

    @tail.setter
    def tail(self, text: str | None) -> None:
        """Sets the text immediately following the element.

        Args:
            text (str | None): The new tail text. If None, it is set to an empty string.
        """
        self.__element.tail = text or ""

    def search(self, pattern: str) -> int | None:
        """Returns the first position of a pattern in the element's text content.

        Python regular expression syntax applies.

        Args:
            pattern (str): The regex pattern to search for.

        Returns:
            int | None: The starting index of the first match, or None if not found.
        """
        match = re.search(pattern, self.text_recursive)
        if match is None:
            return None
        return match.start()

    def search_first(self, pattern: str) -> tuple[int, int] | None:
        """Returns the start and end positions of the first occurrence of a regex pattern.

        Python regular expression syntax applies.

        Args:
            pattern (str): The regex pattern to search for.

        Returns:
            tuple[int, int] | None: A tuple (start_position, end_position) of the
                first match, or None if no match is found.
        """
        match = re.search(pattern, self.text_recursive)
        if match is None:
            return None
        return match.start(), match.end()

    def search_all(self, pattern: str) -> list[tuple[int, int]]:
        """Returns all start and end positions of a regex pattern in the element's text content.

        Python regular expression syntax applies.

        Args:
            pattern (str): The regex pattern to search for.

        Returns:
            list[tuple[int, int]]: A list of (start_position, end_position) tuples for all matches.
        """
        results: list[tuple[int, int]] = []
        for match in re.finditer(pattern, self.text_recursive):
            results.append((match.start(), match.end()))
        return results

    def text_at(self, start: int, end: int | None = None) -> str:
        """Returns the recursive text content of the element between specified positions.

        Args:
            start (int): The starting character position (0-based).
            end (int | None): The ending character position (exclusive). If None,
                returns text from `start` to the end.

        Returns:
            str: The substring of the element's recursive text.
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
        """Checks if a pattern is found one or more times within the element's text content.

        Python regular expression syntax applies.

        Args:
            pattern (str): The regex pattern to match.

        Returns:
            bool: True if the pattern is found, False otherwise.
        """
        return self.search(pattern) is not None

    def replace(
        self,
        pattern: str,
        new: str | None = None,
        formatted: bool = False,
    ) -> int:
        """Replaces occurrences of a pattern with new text within the element's content.

        It cannot replace patterns found across several elements (e.g., a word
        split into two consecutive spans).

        Python regular expression syntax applies.

        If `formatted` is True, and the target is a Paragraph, Span, or Header,
        and the replacement text contains spaces, tabs, or newlines, an attempt
        is made to convert them into actual ODF elements to obtain a formatted result.
        On very complex contents, the result may differ from expectations.

        Args:
            pattern (str): The regex pattern to search and replace.
            new (str | None): The replacement string. If None, it counts occurrences.
                If an empty string, it deletes matches.
            formatted (bool): If True, attempts to convert whitespace in replacement
                text to ODF elements for formatting.

        Returns:
            int: The number of replacements made.
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
        """Returns the root element of the XML tree containing this element.

        Returns:
            Element: The root Element instance.
        """
        element = self.__element
        tree = element.getroottree()
        root = tree.getroot()
        return Element.from_tag(root)

    @property
    def parent(self) -> Element | None:
        """Returns the parent element of this element.

        Returns:
            Element | None: The parent Element instance, or None if this element is the root.
        """
        element = self.__element
        parent = element.getparent()
        if parent is None:
            # Already at root
            return None
        return Element.from_tag(parent)

    @property
    def is_bound(self) -> bool:
        """Checks if the element is currently part of an XML tree (has a parent).

        Returns:
            bool: True if the element has a parent, False otherwise.
        """
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
        """Returns a list of immediate child elements.

        Returns:
            list[Element]: A list of Element instances representing the direct children.
        """
        element = self.__element
        return [
            Element.from_tag(e)
            for e in element.iterchildren()
            if isinstance(e, _Element)
        ]

    def index(self, child: Element) -> int:
        """Returns the position of a child element within this element.

        Inspired by lxml's behavior.

        Args:
            child (Element): The child element to find the index of.

        Returns:
            int: The 0-based index of the child element.
        """
        idx: int = self.__element.index(child.__element)
        return idx

    @property
    def text_content(self) -> str:
        """Gets the text content of embedded paragraphs, including annotations and cells.

        Returns:
            str: The concatenated text content of all embedded paragraphs.
        """
        content = "".join(
            str(child) for child in self.get_elements("descendant::text:p")
        )
        if content.endswith("\n"):
            return content[:-1]
        return content

    @text_content.setter
    def text_content(self, text: str | Element | None) -> None:
        """Sets the text content of the embedded paragraphs.

        If no paragraph exists, one is created. This operation overwrites all
        existing text nodes and children that may contain text.

        Args:
            text (str | Element | None): The new text content. Can be a string,
                another `Element`, or None (clears content).
        """
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
        """Checks if the element is empty (no text, no children, no tail).

        Returns:
            bool: True if the element is empty, False otherwise.
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
        """Inserts an element relative to the current element.

        Insertion can be done using DOM vocabulary (`xmlposition`) or by numeric position.
        If `start` is True, the element is inserted before any existing text content.
        Positions are 0-based.

        Args:
            element (Element): The element to insert.
            xmlposition (int | None): Specifies insertion relative to DOM, using
                `FIRST_CHILD`, `LAST_CHILD`, `NEXT_SIBLING`, or `PREV_SIBLING`.
            position (int | None): A 0-based numeric index for insertion. Used if
                `xmlposition` is None.
            start (bool): If True, insert the element before any existing text of the
                current element, preserving the text as the tail of the inserted element.

        Raises:
            ValueError: If `xmlposition` is not defined and `position` is also None.
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
        """Appends multiple ODF elements efficiently to the end of the current element.

        Args:
            odf_elements (Iterable[Element]): An iterable (e.g., list) of Element instances to append.
        """
        if odf_elements:
            current = self.__element
            elements = [element.__element for element in odf_elements]
            current.extend(elements)

    def _xml_append(self, element: Element) -> None:
        """Appends the underlying lxml element of another Element instance.

        Args:
            element (Element): The Element instance whose underlying XML element will be appended.
        """
        self.__element.append(element.__element)

    @property
    def _xml_element(self) -> _Element:
        """Returns the underlying lxml.etree._Element object.

        Returns:
            _Element: The raw lxml element.
        """
        return self.__element

    def __append(self, str_or_element: str | Element) -> None:
        """Appends an element or text to the end of the current element.

        If `str_or_element` is a string, it is appended as text. If it is an
        `Element`, its underlying XML element is appended.

        Args:
            str_or_element (str | Element): The string or Element to append.

        Raises:
            TypeError: If the provided argument is neither a string nor an Element.
        """

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
        """Deletes an element from the XML tree.

        If `child` is provided, that specific child element is deleted from this element.
        If `child` is None, the current element (`self`) is deleted from its parent.
        The XML library may allow orphaned elements to be used as long as a reference exists.

        Args:
            child (Element | None): The child element to delete. If None, `self` is deleted.
            keep_tail (bool): If True (default), the tail text of the deleted element
                is preserved and appended to the previous sibling or parent's text.

        Raises:
            ValueError: If an attempt is made to delete the root element (`self` has no parent).
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
        """Replaces an existing sub-element with a new one in place.

        Warning: This operation does not clone the `old_element`; it is directly
        removed from the tree.

        Args:
            old_element (Element): The existing child element to be replaced.
            new_element (Element): The new element to insert in place of `old_element`.
        """
        current = self.__element
        current.replace(old_element.__element, new_element.__element)

    def xpath(self, xpath_query: str) -> list[Element | EText]:
        """Applies an XPath query to the element and its subtree.

        Args:
            xpath_query (str): The XPath query string to apply.

        Returns:
            list[Element | EText]: A list of matching Element or EText instances.
        """
        xpath_instance = xpath_compile(xpath_query)
        x_elements = xpath_instance(self.__element)
        result: list[Element | EText] = []
        if isinstance(x_elements, list):
            for obj in x_elements:
                if isinstance(obj, (str, bytes)):
                    result.append(EText(obj))
                elif isinstance(obj, _Element):  # pragma: nocover
                    result.append(Element.from_tag(obj))
        return result

    def clear(self) -> None:
        """Removes all text content, child elements, and attributes from the element."""
        self.__element.clear()

    @property
    def clone(self) -> Element:
        """Creates a deep copy of the current element.

        Returns:
            Element: A new Element instance that is a deep copy of the original.
        """
        clone = deepcopy(self.__element)
        root = lxml_Element("ROOT", nsmap=ODF_NAMESPACES)
        root.append(clone)
        return self.from_tag(clone)

        # slow data = tostring(self.__element, encoding='unicode')
        # return self.from_tag(data)

    @staticmethod
    def _strip_namespaces(data: str) -> str:
        """Removes xmlns:* attributes from a serialized XML string.

        Args:
            data (str): The serialized XML string.

        Returns:
            str: The XML string with xmlns attributes removed.
        """
        return re.sub(r' xmlns:\w*="[\w:\-\/\.#]*"', "", data)

    def serialize(self, pretty: bool = False, with_ns: bool = False) -> str:
        """Returns the text serialization of the XML element.

        Args:
            pretty (bool): If True, the output XML will be pretty-printed.
            with_ns (bool): If True, namespace declarations will be included in the output.

        Returns:
            str: The serialized XML content as a string.
        """
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
        """Returns the first child of the document body, if any.

        This typically corresponds to the main content area of an ODF document.

        Returns:
            Body | None: The first child Element of `office:body`, or None if not found.
        """
        return self.get_element("//office:body/*[1]")  # type: ignore[return-value]

    def get_formatted_text(self, context: dict | None = None) -> str:
        """Returns a formatted version of the element's text.

        This method is typically overridden by subclasses to provide specific
        text formatting based on the element type and context.

        Args:
            context (dict | None): Optional dictionary providing context for formatting.

        Returns:
            str: A formatted string representation of the element's text.
        """
        return ""

    def get_styled_elements(self, name: str = "") -> list[Element]:
        """Finds elements (paragraphs, tables, etc.) using a given style name.

        Args:
            name (str): The name of the style to filter by. If an empty string,
                all styled elements are returned.

        Returns:
            list[Element]: A list of Element instances that match the specified style.
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
        """Retrieves the text content of a specified inner element.

        Args:
            tag (str): The qualified name of the inner element (e.g., "svg:title").

        Returns:
            str | None: The text content of the inner element, or None if the element is not found.
        """
        element = self.get_element(tag)
        if element is None:
            return None
        return element.text

    def _set_inner_text(self, tag: str, text: str) -> None:
        """Sets the text content of a specified inner element.

        If the inner element does not exist, it is created.

        Args:
            tag (str): The qualified name of the inner element (e.g., "svg:title").
            text (str): The new text content to set.
        """
        element = self.get_element(tag)
        if element is None:
            element = Element.from_tag(tag)
            self.__append(element)
        element.text = text

    # SVG

    @property
    def svg_title(self) -> str | None:
        """Gets the SVG title of the element.

        Returns:
            str | None: The title string, or None if not present.
        """
        return self._get_inner_text("svg:title")

    @svg_title.setter
    def svg_title(self, title: str) -> None:
        """Sets the SVG title of the element.

        Args:
            title (str): The title string to set.
        """
        self._set_inner_text("svg:title", title)

    @property
    def svg_description(self) -> str | None:
        """Gets the SVG description of the element.

        Returns:
            str | None: The description string, or None if not present.
        """
        return self._get_inner_text("svg:desc")

    @svg_description.setter
    def svg_description(self, description: str) -> None:
        """Sets the SVG description of the element.

        Args:
            description (str): The description string to set.
        """
        self._set_inner_text("svg:desc", description)

    # Paragraphs

    def get_paragraphs(
        self,
        style: str | None = None,
        content: str | None = None,
    ) -> list[Paragraph]:
        """Returns all paragraphs that match the specified criteria.

        Args:
            style: The name of the style to filter paragraphs by.
            content: A regex pattern to match against the paragraph's content.

        Returns:
            list[Paragraph]: A list of Paragraph instances matching the criteria.
        """
        return self._filtered_elements(
            "descendant::text:p", text_style=style, content=content
        )  # type: ignore[return-value]

    @property
    def paragraphs(self) -> list[Paragraph]:
        """Returns all paragraphs as a list.

        Returns:
            list[Paragraph]: A list of all Paragraph instances that are descendants of this element.
        """
        return self.get_elements(
            "descendant::text:p",
        )  # type: ignore[return-value]

    def get_paragraph(
        self,
        position: int = 0,
        content: str | None = None,
    ) -> Paragraph | None:
        """Returns a single paragraph that matches the specified criteria.

        Args:
            position: The 0-based index of the matching paragraph to return.
            content: A regex pattern to match against the paragraph's content.

        Returns:
            Paragraph | None: A Paragraph instance, or None if no paragraph matches the criteria.
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
        """Returns all spans that match the specified criteria.

        Args:
            style: The name of the style to filter spans by.
            content: A regex pattern to match against the span's content.

        Returns:
            list[Span]: A list of Span instances matching the criteria.
        """
        return self._filtered_elements(
            "descendant::text:span", text_style=style, content=content
        )  # type: ignore[return-value]

    @property
    def spans(self) -> list[Span]:
        """Returns all spans as a list.

        Returns:
            list[Span]: A list of all Span instances that are descendants of this element.
        """
        return self.get_elements("descendant::text:span")  # type: ignore[return-value]

    def get_span(
        self,
        position: int = 0,
        content: str | None = None,
    ) -> Span | None:
        """Returns a single span that matches the specified criteria.

        Args:
            position: The 0-based index of the matching span to return.
            content: A regex pattern to match against the span's content.

        Returns:
            Span | None: A Span instance, or None if no span matches the criteria.
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
        """Returns all headers that match the specified criteria.

        Args:
            style: The name of the style to filter headers by.
            outline_level: The outline level to filter headers by.
            content: A regex pattern to match against the header's content.

        Returns:
            list[Header]: A list of Header instances matching the criteria.
        """
        return self._filtered_elements(
            "descendant::text:h",
            text_style=style,
            outline_level=outline_level,
            content=content,
        )  # type: ignore[return-value]

    @property
    def headers(self) -> list[Header]:
        """Returns all headers as a list.

        Returns:
            list[Header]: A list of all Header instances that are descendants of this element.
        """
        return self.get_elements("descendant::text:h")  # type: ignore[return-value]

    def get_header(
        self,
        position: int = 0,
        outline_level: str | None = None,
        content: str | None = None,
    ) -> Header | None:
        """Returns a single header that matches the specified criteria.

        Args:
            position: The 0-based index of the matching header to return.
            outline_level: The outline level to filter headers by.
            content: A regex pattern to match against the header's content.

        Returns:
            Header | None: A Header instance, or None if no header matches the criteria.
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
        """Returns all lists that match the specified criteria.

        Args:
            style: The name of the style to filter lists by.
            content: A regex pattern to match against the list's content.

        Returns:
            list[List]: A list of List instances matching the criteria.
        """
        return cast(
            "list[List]",
            self._filtered_elements(
                "descendant::text:list", text_style=style, content=content
            ),
        )

    @property
    def lists(self) -> list[List]:
        """Returns all lists as a list.

        Returns:
            list[List]: A list of all List instances that are descendants of this element.
        """
        return cast("list[List]", self.get_elements("descendant::text:list"))

    def get_list(
        self,
        position: int = 0,
        content: str | None = None,
    ) -> List | None:
        """Returns a single list that matches the specified criteria.

        Args:
            position: The 0-based index of the matching list to return.
            content: A regex pattern to match against the list's content.

        Returns:
            List | None: A List instance, or None if no list matches the criteria.
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
        """Returns all frames that match the specified criteria.

        Args:
            presentation_class: The presentation class to filter frames by.
            style: The name of the style to filter frames by.
            title: A regex pattern to match against the frame's title.
            description: A regex pattern to match against the frame's description.
            content: A regex pattern to match against the frame's content.

        Returns:
            list[Frame]: A list of Frame instances matching the criteria.
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
        """Returns all frames as a list.

        Returns:
            list[Frame]: A list of all Frame instances that are descendants of this element.
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
        """Returns a single frame that matches the specified criteria.

        Args:
            position: The 0-based index of the matching frame to return.
            name: The name of the frame.
            presentation_class: The presentation class to filter frames by.
            title: A regex pattern to match against the frame's title.
            description: A regex pattern to match against the frame's description.
            content: A regex pattern to match against the frame's content.

        Returns:
            Frame | None: A Frame instance, or None if no frame matches the criteria.
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
        """Returns all images that match the specified criteria.

        Args:
            style: The name of the style to filter images by.
            url: A regex pattern to match against the image's URL.
            content: A regex pattern to match against the image's content.

        Returns:
            list[DrawImage]: A list of DrawImage instances matching the criteria.
        """
        return self._filtered_elements(
            "descendant::draw:image", text_style=style, url=url, content=content
        )  # type: ignore[return-value]

    @property
    def images(self) -> list[DrawImage]:
        """Returns all images as a list.

        Returns:
            list[DrawImage]: A list of all DrawImage instances that are descendants of this element.
        """
        return self.get_elements("descendant::draw:image")  # type: ignore[return-value]

    def get_image(
        self,
        position: int = 0,
        name: str | None = None,
        url: str | None = None,
        content: str | None = None,
    ) -> DrawImage | None:
        """Returns a single image that matches the specified criteria.

        Args:
            position: The 0-based index of the matching image to return.
            name: The name of the image (stored in its parent frame).
            url: A regex pattern to match against the image's URL.
            content: A regex pattern to match against the image's content.

        Returns:
            DrawImage | None: A DrawImage instance, or None if no image matches the criteria.
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

    # office:names

    def get_office_names(self) -> list[str]:
        """Returns all unique values of 'office:name' attributes within the element's subtree.

        Returns:
            list[str]: A list of unique strings representing the 'office:name' attribute values.
        """
        name_xpath_query = xpath_compile("//@office:name")
        strings = xpath_return_strings(name_xpath_query, self.__element)
        return list({name for name in strings if name})

    # Variables

    def get_variable_sets(self, name: str | None = None) -> list[VarSet]:
        """Returns all variable sets that match the specified criteria.

        Args:
            name: The name of the variable set to filter by.

        Returns:
            list[VarSet]: A list of VarSet instances matching the criteria.
        """
        return self._filtered_elements(
            "descendant::text:variable-set",
            text_name=name,
        )  # type: ignore[return-value]

    def get_variable_set(self, name: str, position: int = -1) -> VarSet | None:
        """Returns a single variable set that matches the specified criteria.

        Args:
            name: The name of the variable set to retrieve.
            position: The 0-based index of the matching variable set to return.
                A negative value (e.g., -1) typically refers to the last one found.

        Returns:
            VarSet | None: A VarSet instance, or None if no variable set matches the criteria.
        """
        return self._filtered_element(
            "descendant::text:variable-set", position, text_name=name
        )  # type: ignore[return-value]

    def get_variable_set_value(
        self,
        name: str,
        value_type: str | None = None,
    ) -> bool | str | int | float | Decimal | datetime | timedelta | None:
        """Returns the value of the last variable set for the given name.

        Args:
            name: The name of the variable to retrieve its value.
            value_type: The expected type of the variable's value.
                Can be 'boolean', 'currency', 'date', 'float', 'percentage',
                'string', 'time', or None for automatic type detection.

        Returns:
            bool | str | int | float | Decimal | datetime | timedelta | None:
                The value of the variable, cast to the most appropriate Python type,
                or None if the variable set is not found.
        """
        variable_set = self.get_variable_set(name)
        if not variable_set:
            return None
        return variable_set.get_value(value_type)  # type: ignore[return-value]

    # Draw Pages

    def get_draw_pages(
        self,
        style: str | None = None,
        content: str | None = None,
    ) -> list[DrawPage]:
        """Returns all draw pages that match the specified criteria.

        Args:
            style: The name of the style to filter draw pages by.
            content: A regex pattern to match against the draw page's content.

        Returns:
            list[DrawPage]: A list of DrawPage instances matching the criteria.
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
        """Returns a single draw page that matches the specified criteria.

        Args:
            position: The 0-based index of the matching draw page to return.
            name: The name of the draw page.
            content: A regex pattern to match against the draw page's content.

        Returns:
            DrawPage | None: A DrawPage instance, or None if no draw page matches the criteria.
        """
        return self._filtered_element(
            "descendant::draw:page", position, draw_name=name, content=content
        )  # type: ignore[return-value]

    # Shapes elements

    # Groups

    def get_draw_groups(
        self,
        title: str | None = None,
        description: str | None = None,
        content: str | None = None,
    ) -> list[DrawGroup]:
        """Returns all draw groups that match the specified criteria.

        Args:
            title: A regex pattern to match against the group's title.
            description: A regex pattern to match against the group's description.
            content: A regex pattern to match against the group's content.

        Returns:
            list[DrawGroup]: A list of DrawGroup instances matching the criteria.
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
        """Returns a single draw group that matches the specified criteria.

        Args:
            position: The 0-based index of the matching draw group to return.
            name: The name of the draw group.
            title: A regex pattern to match against the group's title.
            description: A regex pattern to match against the group's description.
            content: A regex pattern to match against the group's content.

        Returns:
            DrawGroup | None: A DrawGroup instance, or None if no group matches the criteria.
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
        """Returns all draw lines that match the specified criteria.

        Args:
            draw_style: The name of the draw style to filter lines by.
            draw_text_style: The name of the draw text style to filter lines by.
            content: A regex pattern to match against the line's content.

        Returns:
            list[LineShape]: A list of LineShape instances matching the criteria.
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
        """Returns a single draw line that matches the specified criteria.

        Args:
            position: The 0-based index of the matching draw line to return.
            id: The ID of the draw line.
            content: A regex pattern to match against the line's content.

        Returns:
            LineShape | None: A LineShape instance, or None if no line matches the criteria.
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
        """Returns all draw rectangles that match the specified criteria.

        Args:
            draw_style (str | None): The name of the draw style to filter rectangles by.
            draw_text_style (str | None): The name of the draw text style to filter rectangles by.
            content (str | None): A regex pattern to match against the rectangle's content.

        Returns:
            list[RectangleShape]: A list of RectangleShape instances matching the criteria.
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
        """Returns a single draw rectangle that matches the specified criteria.

        Args:
            position (int): The 0-based index of the matching draw rectangle to return.
            id (str | None): The ID of the draw rectangle.
            content (str | None): A regex pattern to match against the rectangle's content.

        Returns:
            RectangleShape | None: A RectangleShape instance, or None if no rectangle matches the criteria.
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
        """Returns all draw ellipses that match the specified criteria.

        Args:
            draw_style (str | None): The name of the draw style to filter ellipses by.
            draw_text_style (str | None): The name of the draw text style to filter ellipses by.
            content (str | None): A regex pattern to match against the ellipse's content.

        Returns:
            list[EllipseShape]: A list of EllipseShape instances matching the criteria.
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
        """Returns a single draw ellipse that matches the specified criteria.

        Args:
            position (int): The 0-based index of the matching draw ellipse to return.
            id (str | None): The ID of the draw ellipse.
            content (str | None): A regex pattern to match against the ellipse's content.

        Returns:
            EllipseShape | None: An EllipseShape instance, or None if no ellipse matches the criteria.
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
        """Returns all draw connectors that match the specified criteria.

        Args:
            draw_style (str | None): The name of the draw style to filter connectors by.
            draw_text_style (str | None): The name of the draw text style to filter connectors by.
            content (str | None): A regex pattern to match against the connector's content.

        Returns:
            list[ConnectorShape]: A list of ConnectorShape instances matching the criteria.
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
        """Returns a single draw connector that matches the specified criteria.

        Args:
            position (int): The 0-based index of the matching draw connector to return.
            id (str | None): The ID of the draw connector.
            content (str | None): A regex pattern to match against the connector's content.

        Returns:
            ConnectorShape | None: A ConnectorShape instance, or None if no connector matches the criteria.
        """
        return self._filtered_element(
            "descendant::draw:connector", position, draw_id=id, content=content
        )  # type: ignore[return-value]

    def get_orphan_draw_connectors(self) -> list[ConnectorShape]:
        """Returns a list of connectors that are not connected to any shapes.

        Returns:
            list[ConnectorShape]: A list of ConnectorShape instances that are orphans.
        """
        connectors = []
        for connector in self.get_draw_connectors():
            start_shape = connector.get_attribute("draw:start-shape")
            end_shape = connector.get_attribute("draw:end-shape")
            if start_shape is None and end_shape is None:
                connectors.append(connector)
        return connectors

    # Tracked changes and text change

    def get_changes_ids(self) -> list[Element | EText]:
        """Returns a list of IDs that refer to change regions in the tracked changes list.

        Returns:
            list[Element | EText]: A list of Element or EText instances representing change IDs.
        """
        # Insertion changes or deletion changes
        xpath_query = (
            "descendant::text:change-start/@text:change-id "
            "| descendant::text:change/@text:change-id"
        )
        return self.xpath(xpath_query)

    def get_text_change_deletions(self) -> list[TextChange]:
        """Returns all text changes representing deletions (text:change tags).

        Consider using `get_text_changes()` for a more general approach.

        Returns:
            list[TextChange]: A list of TextChange instances representing deletions.
        """
        return self._filtered_elements(
            "descendant::text:text:change",
        )  # type: ignore[return-value]

    def get_text_change_deletion(
        self,
        position: int = 0,
        idx: str | None = None,
    ) -> TextChange | None:
        """Returns a single text change of deletion kind (text:change tag) matching criteria.

        Consider using `get_text_change()` for a more general approach.

        Args:
            position (int): The 0-based index of the matching text:change element to return.
            idx (str | None): The `change-id` attribute of the element.

        Returns:
            TextChange | None: A TextChange instance, or None if no match is found.
        """
        return self._filtered_element(
            "descendant::text:change", position, change_id=idx
        )  # type: ignore[return-value]

    def get_text_change_starts(self) -> list[TextChangeStart]:
        """Returns all text change-start elements (text:change-start tags).

        Consider using `get_text_changes()` for a more general approach.

        Returns:
            list[TextChangeStart]: A list of TextChangeStart instances.
        """
        return self._filtered_elements(
            "descendant::text:change-start",
        )  # type: ignore[return-value]

    def get_text_change_start(
        self,
        position: int = 0,
        idx: str | None = None,
    ) -> TextChangeStart | None:
        """Returns a single text change-start element (text:change-start tag) matching criteria.

        Consider using `get_text_change()` for a more general approach.

        Args:
            position (int): The 0-based index of the matching text:change-start element to return.
            idx (str | None): The `change-id` attribute of the element.

        Returns:
            TextChangeStart | None: A TextChangeStart instance, or None if no match is found.
        """
        return self._filtered_element(
            "descendant::text:change-start", position, change_id=idx
        )  # type: ignore[return-value]

    def get_text_change_ends(self) -> list[TextChangeEnd]:
        """Returns all text change-end elements (text:change-end tags).

        Consider using `get_text_changes()` for a more general approach.

        Returns:
            list[TextChangeEnd]: A list of TextChangeEnd instances.
        """
        return self._filtered_elements(
            "descendant::text:change-end",
        )  # type: ignore[return-value]

    def get_text_change_end(
        self,
        position: int = 0,
        idx: str | None = None,
    ) -> TextChangeEnd | None:
        """Returns a single text change-end element (text:change-end tag) matching criteria.

        Consider using `get_text_change()` for a more general approach.

        Args:
            position (int): The 0-based index of the matching text:change-end element to return.
            idx (str | None): The `change-id` attribute of the element.

        Returns:
            TextChangeEnd | None: A TextChangeEnd instance, or None if no match is found.
        """
        return self._filtered_element(
            "descendant::text:change-end", position, change_id=idx
        )  # type: ignore[return-value]

    def get_text_changes(self) -> list[TextChange | TextChangeStart]:
        """Returns all text changes, including single deletions (text:change) and
        starts of change ranges (text:change-start).

        Returns:
            list[TextChange | TextChangeStart]: A list of TextChange or TextChangeStart instances.
        """
        request = "descendant::text:change-start | descendant::text:change"
        return self._filtered_elements(request)  # type: ignore[return-value]

    @property
    def text_changes(self) -> list[TextChange | TextChangeStart]:
        """Returns all text changes, including single deletions (text:change) and
        starts of change ranges (text:change-start).

        Returns:
            list[TextChange | TextChangeStart]: A list of TextChange or TextChangeStart instances.
        """
        return self.get_text_changes()

    def get_text_change(
        self,
        position: int = 0,
        idx: str | None = None,
    ) -> TextChange | TextChangeStart | None:
        """Returns a single text change that matches the specified criteria.

        The change can be either a single deletion (text:change) or the start
        of a range of changes (text:change-start).

        Args:
            position (int): The 0-based index of the element to retrieve if
                several matches are found. Defaults to 0.
            idx (str | None): The `change-id` attribute of the element to match.

        Returns:
            TextChange | TextChangeStart | None: A TextChange or TextChangeStart
                instance, or None if no match is found.
        """
        if idx:
            request = (
                f'descendant::text:change-start[@text:change-id="{idx}"] '
                f'| descendant::text:change[@text:change-id="{idx}"]'
            )
            return self._filtered_element(request, 0)  # type: ignore[return-value]

        request = "descendant::text:change-start | descendant::text:change"
        return self._filtered_element(request, position)  # type: ignore[return-value]

    # Styles

    @staticmethod
    def _get_style_tagname(family: str | None, is_default: bool = False) -> str:
        """Determines the appropriate ODF tag name for a given style family.

        Args:
            family (str | None): The style family (e.g., "paragraph", "text").
            is_default (bool): If True, specifically look for default styles.

        Returns:
            str: The ODF tag name(s) to match for the given style family.
        """
        tagname: str
        if not family:
            tagname = "(style:default-style|*[@style:name]|draw:fill-image|draw:marker)"
        elif is_default:
            # Default style
            tagname = "style:default-style"
        else:
            # This calls _family_style_tagname, which can raise ValueError
            # If it does, the exception will propagate from here.
            tagname = _family_style_tagname(family)
            if family in FAMILY_ODF_STD:
                tagname = f"({tagname}|style:default-style)"
        return tagname

    def get_styles(self, family: str | None = None) -> list[StyleBase]:
        """Returns all styles (common and default) that match the specified family.

        Args:
            family (str | None): The style family to filter by (e.g., "paragraph", "text").
                If None, retrieves all styles regardless of family.

        Returns:
            list[StyleBase]: A list of StyleBase instances matching the criteria.
        """
        # Both common and default styles
        tagname = self._get_style_tagname(family)
        return self._filtered_elements(tagname, family=family)  # type: ignore[return-value]

    def get_style(
        self,
        family: str,
        name_or_element: str | Element | None = None,
        display_name: str | None = None,
    ) -> StyleBase | None:
        """Returns a single style uniquely identified by family/name, or a provided style object.

        If the provided `name_or_element` is already a style object, it is returned directly.
        Use `display_name` if the style is known by its user-facing name instead of its
        internal name.

        Args:
            family (str): The style family (e.g., "paragraph", "text", "graphic", "table", "list", "number").
            name_or_element (str | Element | None): The internal name of the style, or
                an existing Style (or subclass) instance.
            display_name (str | None): The user-facing name of the style.

        Returns:
            StyleBase | None: A StyleBase instance, or None if no matching style is found.

        Raises:
            ValueError: If `name_or_element` is an Element but not a recognized odf_style.
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
        """Returns a single filtered element at a specific position.

        Args:
            query_string (str): The XPath query string to apply.
            position (int): The 0-based index of the desired element from the filtered results.
            **kwargs (Any): Additional keyword arguments to pass to `_filtered_elements`
                for filtering criteria.

        Returns:
            Element | None: The Element instance at the specified position, or None if not found.
        """
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
        """Returns a list of elements filtered by various criteria.

        This internal method applies an XPath query first and then further
        filters the results based on content, URL, SVG title/description,
        Dublin Core creator/date, and other keyword arguments.

        Args:
            query_string (str): The initial XPath query string to select elements.
            content (str | None): A regex pattern to match against the element's text content.
            url (str | None): A regex pattern to match against the `xlink:href` attribute.
            svg_title (str | None): A regex pattern to match against an inner `svg:title` element.
            svg_desc (str | None): A regex pattern to match against an inner `svg:desc` element.
            dc_creator (str | None): A regex pattern to match against an inner `dc:creator` element.
            dc_date (datetime | None): A datetime object to match against an inner `dc:date` element.
            **kwargs (Any): Additional keyword arguments representing attribute filters
                (e.g., `text_style="MyStyle"`, `draw_name="MyDraw"`, etc.).

        Returns:
            list[Element]: A list of Element instances that match all specified criteria.
        """
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
