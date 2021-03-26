# Copyright 2018-2020 Jérôme Dumonteil
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
"""Element, super class of all ODF classes
"""
import sys
from copy import deepcopy
import re

from lxml.etree import fromstring, tostring, _Element
from lxml.etree import _ElementStringResult, _ElementUnicodeResult
from lxml.etree import Element as lxml_Element

from lxml.etree import XPath

from .datatype import DateTime, Boolean
from .utils import _get_elements, _get_element
from .utils import _family_style_tagname, get_value
from .utils import to_bytes, to_str, FAMILY_ODF_STD

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

ns_stripper = re.compile(r' xmlns:\w*="[\w:\-\/\.#]*"')

__xpath_query_cache = {}

# An empty XML document with all namespaces declared
NAMESPACES_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<office:document
  xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
  xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
  xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
  xmlns:xlink="http://www.w3.org/1999/xlink"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
  xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
  xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
  xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
  xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0"
  xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0"
  xmlns:math="http://www.w3.org/1998/Math/MathML"
  xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0"
  xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0"
  xmlns:ooo="http://openoffice.org/2004/office"
  xmlns:oooc="http://openoffice.org/2004/calc"
  xmlns:ooow="http://openoffice.org/2004/writer"
  xmlns:xforms="http://www.w3.org/2002/xforms"
  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:smil="urn:oasis:names:tc:opendocument:xmlns:smil-compatible:1.0"
  xmlns:anim="urn:oasis:names:tc:opendocument:xmlns:animation:1.0"
  xmlns:rpt="http://openoffice.org/2005/report"
  xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2"
  xmlns:xhtml="http://www.w3.org/1999/xhtml"
  xmlns:grddl="http://www.w3.org/2003/g/data-view#"
  xmlns:officeooo="http://openoffice.org/2009/office"
  xmlns:tableooo="http://openoffice.org/2009/table"
  xmlns:drawooo="http://openoffice.org/2010/draw"
  xmlns:calcext="urn:org:documentfoundation:names:experimental:calc:xmlns:calcext:1.0"
  xmlns:loext="urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0"
  xmlns:field="urn:openoffice:names:experimental:ooo-ms-interop:xmlns:field:1.0"
  xmlns:formx="urn:openoffice:names:experimental:ooxml-odf-interop:xmlns:form:1.0"
  xmlns:css3t="http://www.w3.org/TR/css3-text/"
  xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0"
  xmlns:dom="http://www.w3.org/2001/xml-events"
  xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"
  xmlns:rdfa="http://docs.oasis-open.org/opendocument/meta/rdfa#"
  office:version="1.1">%s</office:document>
"""


def _decode_qname(qname):
    """Turn a prefixed qualified name to a (uri, name) pair."""
    qname = to_str(qname)
    if ":" in qname:
        prefix, name = qname.split(":")
        try:
            uri = ODF_NAMESPACES[prefix]
        except KeyError:
            raise ValueError('XML prefix "%s" is unknown' % prefix)
        return uri, name
    return None, qname


def _uri_to_prefix(uri):
    """Find the prefix associated to the given URI."""
    for key, value in ODF_NAMESPACES.items():
        if value == uri:
            return key
    raise ValueError('uri "%s" not found' % uri)


def _get_prefixed_name(tag):
    """Replace lxml "{uri}name" syntax with "prefix:name" one."""
    uri, name = to_str(tag).split("}", 1)
    prefix = _uri_to_prefix(uri[1:])
    return f"{prefix}:{name}"


def _get_lxml_tag(qname):
    """Replace "prefix:name" syntax with lxml "{uri}name" one."""
    return "{%s}%s" % _decode_qname(qname)


def _xpath_compile(path):
    return XPath(to_str(path), namespaces=ODF_NAMESPACES, regexp=False)


def _find_query_in_cache(query):
    xpath = __xpath_query_cache.get(query, None)
    if xpath is None:
        xpath = _xpath_compile(query)
        __xpath_query_cache[query] = xpath
    return xpath


_xpath_text = _find_query_in_cache("//text()")  #  descendant and self
_xpath_text_descendant = _find_query_in_cache("descendant::text()")
_xpath_text_main = _find_query_in_cache("//*[not (parent::office:annotation)]/text()")
_xpath_text_main_descendant = _find_query_in_cache(
    "descendant::text()[not (parent::office:annotation)]"
)

_class_registry = {}


def register_element_class(cls, tag_list=None):
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

        qname -- (optionnal) iterable of qname tag for the class
    """
    # Turn tag name into what lxml is expecting
    if not tag_list:
        tag_list = [cls._tag]
    for k in tag_list:
        tag = _get_lxml_tag(k)
        if tag not in _class_registry:
            _class_registry[tag] = cls


# TODO remove some day
def _debug_element(tag_or_elem):
    return repr(Element(tag_or_elem=tag_or_elem).serialize(pretty=True))


def _debug_registry():
    for k, v in _class_registry.items():
        print("%50s" % v, _get_prefixed_name(k))


class Text(str):
    """Representation of an XML text node. Created to hide the specifics of
    lxml in searching text nodes using XPath.

    Constructed like any str object but only accepts lxml text objects.
    """

    # There's some black magic in inheriting from str
    def __init__(self, text_result):
        self.__parent = text_result.getparent()
        self.__is_text = text_result.is_text
        self.__is_tail = text_result.is_tail

    @property
    def parent(self):
        parent = self.__parent
        # XXX happens just because of the unit test
        if parent is None:
            return None
        return Element.from_tag(tag_or_elem=parent)

    def is_text(self):
        return self.__is_text

    def is_tail(self):
        return self.__is_tail


class Element:
    """Super class of all ODF classes. Representation of an XML element.
    Abstraction of the XML library behind.
    """

    _tag = None
    _caching = False

    def __init__(self, **kwargs):
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
            # from_tag() casting, do not execute the subclass __ini__
            if not isinstance(tag_or_elem, _Element):
                raise TypeError('"%s" is not an element node' % type(tag_or_elem))
            self._do_init = False
            self.__element = tag_or_elem

    @classmethod
    def from_tag(cls, tag_or_elem):
        """Element class and subclass factory. Turn an lxml Element or ODF
        string tag into an ODF XML Element from the relevant class.

        Arguments:

            tag_or_elem -- ODF str tag or lxml.Element

        Return: Element (or subclass) instance
        """
        if not isinstance(tag_or_elem, _Element):
            # assume the argument is a prefix:name tag
            tag_or_elem = cls.make_etree_element(tag_or_elem)
        tag = to_str(tag_or_elem.tag)
        klass = _class_registry.get(tag, cls)
        return klass(tag_or_elem=tag_or_elem)

    @classmethod
    def from_tag_for_clone(cls, tag_or_elem, cache):
        tag = to_str(tag_or_elem.tag)
        klass = _class_registry.get(tag, cls)
        element = klass(tag_or_elem=tag_or_elem)
        if cache and element._caching:
            element._tmap = cache[0]
            element._cmap = cache[1]
            if len(cache) == 3:
                element._rmap = cache[2]
        return element

    @staticmethod
    def make_etree_element(tag):
        if not isinstance(tag, (str, bytes)):
            raise TypeError("tag is not str or bytes: %s" % tag)
        tag = to_bytes(tag).strip()
        if not tag:
            raise ValueError("tag is empty")
        if b"<" not in tag:
            # Qualified name
            # XXX don't build the element from scratch or lxml will pollute with
            # repeated namespace declarations
            tag = b"<%s/>" % tag
        # XML fragment
        root = fromstring(NAMESPACES_XML % tag)
        return root[0]

    def __str__(self):
        return '%s "%s"' % (repr(self), self.tag)

    @staticmethod
    def _generic_attrib_getter(attr_name, family=None):
        name = _get_lxml_tag(attr_name)

        def getter(self):
            if family and self.family != family:
                return None
            value = self.__element.get(name)
            if value is None:
                return None
            elif value in ("true", "false"):
                return Boolean.decode(value)
            return str(value)

        return getter

    @staticmethod
    def _generic_attrib_setter(attr_name, family=None):
        name = _get_lxml_tag(attr_name)

        def setter(self, value):
            if family and self.family != family:
                return None
            if value is None:
                try:
                    del self.__element.attrib[name]
                except KeyError:
                    pass
                return
            if isinstance(value, bool):
                value = Boolean.encode(value)
            self.__element.set(name, str(value))

        return setter

    @classmethod
    def _define_attribut_property(cls):
        for tpl in cls._properties:
            name = tpl[0]
            attr = tpl[1]
            if len(tpl) == 3:
                family = tpl[2]
            else:
                family = None
            setattr(
                cls,
                name,
                property(
                    cls._generic_attrib_getter(attr, family),
                    cls._generic_attrib_setter(attr, family),
                    None,
                    f"Get/set the attribute {attr}",
                ),
            )

    def _insert(self, element, before=None, after=None, position=0, main_text=False):
        """Insert an element before or after the characters in the text which
        match the regex before/after. When the regex matches more of one part
        of the text, position can be set to choice which part must be used. If
        before and after are None, we use only position that is the number of
        characters. If position is positive and before=after=None, we insert
        before the position character. But if position=-1, we insert after the
        last character.

        if main_text is True, filter out the annotations texts in computation.

        Arguments:

        element -- Element

        before -- str regex

        after -- str regex

        position -- int

        main_text -- boolean
        """
        current = self.__element
        element = element.__element

        if main_text:
            xpath_text = _xpath_text_main_descendant
        else:
            xpath_text = _xpath_text_descendant

        # 1) before xor after is not None
        if (before is not None) ^ (after is not None):
            if before is not None:
                regex = re.compile(before)
            else:
                regex = re.compile(after)

            # position = -1
            if position < 0:
                # Found the last text that matches the regex
                text = None
                for a_text in xpath_text(current):
                    if regex.search(a_text) is not None:
                        text = a_text
                if text is None:
                    raise ValueError("text not found")
                sre = list(regex.finditer(text))[-1]
            # position >= 0
            else:
                count = 0
                for text in xpath_text(current):
                    found_nb = len(regex.findall(text))
                    if found_nb + count >= position + 1:
                        break
                    count += found_nb
                else:
                    raise ValueError("text not found")
                sre = list(regex.finditer(text))[position - count]

            # Compute pos
            pos = sre.start() if before is not None else sre.end()
        # 2) before=after=None => only with position
        elif before is None and after is None:
            # Hack if position is negative => quickly
            if position < 0:
                current.append(element)
                return

            # Found the text
            count = 0
            for text in xpath_text(current):
                found_nb = len(text)
                if found_nb + count >= position:
                    break
                count += found_nb
            else:
                raise ValueError("text not found")

            # We insert before the character
            pos = position - count
        else:
            raise ValueError("bad combination of arguments")

        # Compute new texts
        text_before = text[:pos] if text[:pos] else None
        text_after = text[pos:] if text[pos:] else None

        # Insert!
        parent = text.getparent()
        if text.is_text:
            parent.text = text_before
            element.tail = text_after
            parent.insert(0, element)
        else:
            parent.addnext(element)
            parent.tail = text_before
            element.tail = text_after

    def _insert_between(self, element, from_, to):
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
        for text in _xpath_text_descendant(current):
            if not from_ in text:
                continue
            from_index = text.index(from_)
            text_before = text[:from_index]
            text_after = text[from_index:]
            from_container = text.getparent()
            # Include from_index to match a single word
            to_index = text.find(to, from_index)
            if to_index >= 0:
                # Simple case: "from" and "to" in the same element
                to_end = to_index + len(to)
                if text.is_text:
                    from_container.text = text_before
                    wrapper.text = text[to_index:to_end]
                    wrapper.tail = text[to_end:]
                    from_container.insert(0, wrapper)
                else:
                    from_container.tail = text_before
                    wrapper.text = text[to_index:to_end]
                    wrapper.tail = text[to_end:]
                    parent = from_container.getparent()
                    index = parent.index(from_container)
                    parent.insert(index + 1, wrapper)
                return
            else:
                # Exit to the second part where we search for the end text
                break
        else:
            raise ValueError("start text not found")
        # The container is split in two
        container2 = deepcopy(from_container)
        if text.is_text:
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
        index = parent.index(from_container)
        parent.insert(index + 1, wrapper)
        for text in _xpath_text_descendant(wrapper):
            if not to in text:
                continue
            to_end = text.index(to) + len(to)
            text_before = text[:to_end]
            text_after = text[to_end:]
            container_to = text.getparent()
            if text.is_text:
                container_to.text = text_before
                container_to.tail = text_after
            else:
                container_to.tail = text_before
                next_one = container_to.getnext()
                if next_one is None:
                    next_one = container_to.getparent()
                next_one.tail = text_after
            return
        raise ValueError("end text not found")

    @property
    def tag(self):
        """Get/set the underlying xml tag with the given qualified name.

        Warning: direct change of tag does not change the element class.

        Arguments:

            qname -- str (e.g. "text:span")
        """
        return _get_prefixed_name(self.__element.tag)

    @tag.setter
    def tag(self, qname):
        self.__element.tag = to_bytes(_get_lxml_tag(qname))

    def elements_repeated_sequence(self, xpath_instance, name):
        uri, name = _decode_qname(name)
        if uri is not None:
            name = "{%s}%s" % (uri, name)
        element = self.__element
        sub_elements = xpath_instance(element)
        result = []
        idx = -1
        for sub_element in sub_elements:
            idx += 1
            value = sub_element.get(name)
            if value is None:
                result.append((idx, 1))
                continue
            try:
                value = int(value)
            except ValueError:
                value = 1
            result.append((idx, max(value, 1)))
        return result

    def get_elements(self, xpath_query):
        element = self.__element
        if isinstance(xpath_query, XPath):
            result = xpath_query(element)
        else:
            new_xpath_query = _find_query_in_cache(to_bytes(xpath_query))
            result = new_xpath_query(element)
        if hasattr(self, "_tmap"):
            if hasattr(self, "_rmap"):
                cache = (self._tmap, self._cmap, self._rmap)
            else:
                cache = (self._tmap, self._cmap)
        else:
            cache = None
        return [Element.from_tag_for_clone(e, cache) for e in result]

    # fixme : need original get_element as wrapper of get_elements

    def get_element(self, xpath_query):
        element = self.__element
        result = element.xpath("(%s)[1]" % xpath_query, namespaces=ODF_NAMESPACES)
        if result:
            return Element.from_tag(result[0])
        return None

    def _get_element_idx(self, xpath_query, idx):
        element = self.__element
        result = element.xpath(
            "(%s)[%s]" % (xpath_query, idx + 1), namespaces=ODF_NAMESPACES
        )
        if result:
            return Element.from_tag(result[0])
        return None

    def _get_element_idx2(self, xpath_instance, idx):
        element = self.__element
        result = xpath_instance(element, idx=idx + 1)
        if result:
            return Element.from_tag(result[0])
        return None

    @property
    def attributes(self):
        e = self.__element
        return {_get_prefixed_name(k): v for k, v in e.attrib.items()}

    def get_attribute(self, name):
        element = self.__element
        uri, name = _decode_qname(name)
        if uri is not None:
            name = "{%s}%s" % (uri, name)
        value = element.get(name)
        if value is None:
            return None
        elif value in ("true", "false"):
            return Boolean.decode(value)
        return str(value)

    def get_attribute_integer(self, name):
        atr = self.get_attribute(name)
        if atr is None:
            return atr
        try:
            return int(atr)
        except ValueError:
            return None

    def set_attribute(self, name, value):
        element = self.__element
        uri, name = _decode_qname(name)
        if uri is not None:
            name = "{%s}%s" % (uri, name)

        if isinstance(value, bool):
            value = Boolean.encode(value)
        elif value is None:
            try:
                del element.attrib[name]
            except KeyError:
                pass
            return
        element.set(name, str(value))

    def set_style_attribute(self, name, value):
        """Shortcut to accept a style object as a value."""
        if isinstance(value, Element):
            value = value.name
        return self.set_attribute(name, value)

    def del_attribute(self, name):
        element = self.__element
        uri, name = _decode_qname(name)
        if uri is not None:
            name = "{%s}%s" % (uri, name)
        del element.attrib[name]

    @property
    def text(self):
        """Get / set the text content of the element."""
        return self.__element.text or ""

    @text.setter
    def text(self, text):
        if text is None:
            text = ""
        try:
            self.__element.text = to_str(text)
        except TypeError:
            raise TypeError('str type expected: "%s"' % type(text))

    @property
    def text_recursive(self):
        return "".join(self.__element.itertext())

    @property
    def tail(self):
        """Get / set the text immediately following the element."""
        return self.__element.tail

    @tail.setter
    def tail(self, text):
        self.__element.tail = text or ""

    def search(self, pattern):
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

    def match(self, pattern):
        """return True if the pattern is found one or more times anywhere in
        the text content of the element.

        Python regular expression syntax applies.

        Arguments:

            pattern -- str

        Return: bool
        """
        return self.search(pattern) is not None

    def replace(self, pattern, new=None):
        """Replace the pattern with the given text, or delete if text is an
        empty string, and return the number of replacements. By default, only
        return the number of occurences that would be replaced.

        It cannot replace patterns found across several element, like a word
        split into two consecutive spans.

        Python regular expression syntax applies.

        Arguments:

            pattern -- str

            new -- str

        Return: int
        """
        if isinstance(pattern, str):
            # Fail properly if the pattern is an non-ascii bytestring
            pattern = str(pattern)
        cpattern = re.compile(pattern)
        count = 0
        for text in self.xpath("descendant::text()"):
            if new is None:
                count += len(cpattern.findall(text))
            else:
                new_text, number = cpattern.subn(new, text)
                container = text.parent
                if text.is_text():
                    container.text = new_text
                else:
                    container.tail = new_text
                count += number
        return count

    @property
    def root(self):
        element = self.__element
        tree = element.getroottree()
        root = tree.getroot()
        return Element.from_tag(root)

    @property
    def parent(self):
        element = self.__element
        parent = element.getparent()
        if parent is None:
            # Already at root
            return None
        return Element.from_tag(parent)

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
    def children(self):
        element = self.__element
        return [Element.from_tag(e) for e in element.getchildren()]

    def index(self, child):
        """Return the position of the child in this element.

        Inspired by lxml
        """
        return self.__element.index(child.__element)

    @property
    def text_content(self):
        """Get / set the text of the embedded paragraph, including embeded
        annotations, cells...

        Set create a paragraph if missing
        """
        return "\n".join(
            child.text_recursive for child in self.get_elements("descendant::text:p")
        )

    @text_content.setter
    def text_content(self, text):
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

    def _erase_text_content(self):
        paragraphs = self.get_elements("text:p")
        if not paragraphs:
            # E.g., text:p in draw:text-box in draw:frame
            paragraphs = self.get_elements("*/text:p")
        if paragraphs:
            paragraphs.pop(0)
            for obsolete in paragraphs:
                obsolete.delete()

    def is_empty(self):
        """Check if the element is empty : no text, no children, no tail

        Return: Boolean
        """
        element = self.__element
        if element.tail is not None:
            return False
        if element.text is not None:
            return False
        if element.getchildren():
            return False
        return True

    def _get_successor(self, target):
        element = self.__element
        next_one = element.getnext()
        if next_one is not None:
            return Element.from_tag(next_one), target
        parent = self.parent
        if parent is None:
            return None, None
        return parent._get_successor(target.parent)

    def _get_between_base(self, tag1, tag2):
        def find_any_id(tag):
            stag = tag.tag
            for attribute in (
                "text:id",
                "text:change-id",
                "text:name",
                "office:name",
                "text:ref-name",
                "xml:id",
            ):
                idx = tag.get_attribute(attribute)
                if idx is not None:
                    return stag, attribute, idx
            raise ValueError("No Id found in %s" % tag.serialize())

        def common_ancestor(t1, a1, v1, t2, a2, v2):
            root = self.root
            request1 = 'descendant::%s[@%s="%s"]' % (t1, a1, v1)
            request2 = 'descendant::%s[@%s="%s"]' % (t2, a2, v2)
            up = root.xpath(request1)[0]
            while True:
                # print "up",
                up = up.parent
                has_tag2 = up.xpath(request2)
                if not has_tag2:
                    continue
                # print 'found'
                break
            # print up.serialize()
            return up

        t1, a1, v1 = find_any_id(tag1)
        t2, a2, v2 = find_any_id(tag2)
        ancestor = common_ancestor(t1, a1, v1, t2, a2, v2).clone
        r1 = '%s[@%s="%s"]' % (t1, a1, v1)
        r2 = '%s[@%s="%s"]' % (t2, a2, v2)
        resu = ancestor.clone
        for child in resu.children:
            resu.delete(child)
        resu.text = ""
        resu.tail = ""
        target = resu
        current = ancestor.children[0]
        state = 0
        while True:
            # print 'current', state, current.serialize()
            if state == 0:  # before tag 1
                if current.xpath("descendant-or-self::%s" % r1):
                    if current.xpath("self::%s" % r1):
                        tail = current.tail
                        if tail:
                            # got a tail => the parent should be either t:p or t:h
                            target.text = tail
                        current, target = current._get_successor(target)
                        state = 1
                        continue
                    # got T1 in chidren, need further analysis
                    new_target = current.clone
                    for child in new_target.children:
                        new_target.delete(child)
                    new_target.text = ""
                    new_target.tail = ""
                    target.append(new_target)
                    target = new_target
                    current = current.children[0]
                    continue
                else:
                    # before tag1 : forget element, go to next one
                    current, target = current._get_successor(target)
                    continue
            elif state == 1:  # collect elements
                further = False
                if current.xpath("descendant-or-self::%s" % r2):
                    if current.xpath("self::%s" % r2):
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
                    target.append(new_target)
                    target = new_target
                    current = current.children[0]
                    continue
                # collect
                target.append(current.clone)
                current, target = current._get_successor(target)
                continue
        # Now resu should be the "parent" of inserted parts
        # - a text:h or text:p sigle item (simple case)
        # - a upper element, with some text:p, text:h in it => need to be
        #   stripped to have a list of text:p, text:h
        if resu.tag in ("text:p", "text:h"):
            inner = [resu]
        else:
            inner = resu.children
        return inner

    def get_between(self, tag1, tag2, as_text=False, clean=True, no_header=True):
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
            request_self = " | ".join(["self::%s" % c for c in clean_tags])
            inner = [e for e in inner if not e.xpath(request_self)]
            request = " | ".join(["descendant::%s" % c for c in clean_tags])
            for element in inner:
                to_del = element.xpath(request)
                for e in to_del:
                    element.delete(e)
        if no_header:  # crude replace t:h by t:p
            new_inner = []
            for element in inner:
                if element.tag == "text:h":
                    children = element.children
                    text = element.__element.text
                    para = Element.from_tag("text:p")
                    para.text = text
                    for c in children:
                        para.append(c)
                    new_inner.append(para)
                else:
                    new_inner.append(element)
            inner = new_inner
        if as_text:
            return "\n".join([e.get_formatted_text() for e in inner])
        else:
            return inner

    def insert(self, element, xmlposition=None, position=None, start=False):
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
        element = element.__element
        if start:
            text = current.text
            if text is not None:
                current.text = None
                tail = element.tail
                if tail is None:
                    tail = text
                else:
                    tail = tail + text
                element.tail = tail
            position = 0
        if position is not None:
            current.insert(position, element)
        elif xmlposition is FIRST_CHILD:
            current.insert(0, element)
        elif xmlposition is LAST_CHILD:
            current.append(element)
        elif xmlposition is NEXT_SIBLING:
            parent = current.getparent()
            index = parent.index(current)
            parent.insert(index + 1, element)
        elif xmlposition is PREV_SIBLING:
            parent = current.getparent()
            index = parent.index(current)
            parent.insert(index, element)
        else:
            raise ValueError("(xml)position must be defined")

    def extend(self, odf_elements):
        """Fast append elements at the end of ourself using extend."""
        if odf_elements:
            current = self.__element
            elements = [element.__element for element in odf_elements]
            current.extend(elements)

    def append(self, str_or_element):
        """Insert element or text in the last position."""
        current = self.__element

        # Unicode ?
        if isinstance(str_or_element, str):
            # Has children ?
            children = current.getchildren()
            if children:
                # Append to tail of the last child
                last_child = children[-1]
                text = last_child.tail
                text = text if text is not None else ""
                text += str_or_element
                last_child.tail = text
            else:
                # Append to text of the element
                text = current.text
                text = text if text is not None else ""
                text += str_or_element
                current.text = text
        elif isinstance(str_or_element, Element):
            current.append(str_or_element.__element)
        else:
            raise TypeError(
                'Element or unicode expected, not "%s"' % (type(str_or_element))
            )

    def delete(self, child=None, keep_tail=True):
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
                info = self.serialize()
                raise ValueError("cannot delete the root element\n%s" % info)
            child = self
        else:
            parent = self
        if keep_tail and child.__element.tail is not None:
            current = child.__element
            tail = current.tail
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

    def replace_element(self, old_element, new_element):
        """Replaces in place a sub element with the element passed as second
        argument.

        Warning : no clone for old element.
        """
        current = self.__element
        current.replace(old_element.__element, new_element.__element)

    def strip_elements(self, sub_elements):
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
        replacer = to_bytes(_get_lxml_tag("text:this-will-be-removed"))
        for element in sub_elements:
            element.__element.tag = replacer
        strip = ("text:this-will-be-removed",)
        return self.strip_tags(strip=strip, default=None)

    def strip_tags(self, strip=None, protect=None, default="text:p"):
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

            Element or list.
        """
        if not strip:
            return self
        if not protect:
            protect = ()
        protected = False
        element, modified = Element._strip_tags(self, strip, protect, protected)
        if modified:
            if isinstance(element, list) and default:
                new = Element.from_tag(default)
                for content in element:
                    if isinstance(content, Element):
                        new.append(content)
                    else:
                        new.text = content
                element = new
        return element

    @staticmethod
    def _strip_tags(element, strip, protect, protected):
        """sub method for strip_tags()"""
        copy = element.clone
        modified = False
        children = []
        if protect and element.tag in protect:
            protect_below = True
        else:
            protect_below = False
        for child in copy.children:
            striped_child, is_modified = Element._strip_tags(
                child, strip, protect, protect_below
            )
            if is_modified:
                modified = True
            if isinstance(striped_child, list):
                children.extend(striped_child)
            else:
                children.append(striped_child)
        if not protected and strip and element.tag in strip:
            element = []
            modified = True
        else:
            if not modified:
                return (element, False)
            element.clear()
            try:
                for key, value in copy.attributes.items():
                    element.set_attribute(key, value)
            except ValueError:
                sys.stderr.write("strip_tags(): bad attribute in %s\n" % copy)
        text = copy.text
        tail = copy.tail
        if text is not None:
            element.append(text)
        for child in children:
            element.append(child)
        if tail is not None:
            if isinstance(element, list):
                element.append(tail)
            else:
                element.tail = tail
        return (element, True)

    def xpath(self, xpath_query):
        """Apply XPath query to the element and its subtree. Return list of
        Element or Text instances translated from the nodes found.
        """
        element = self.__element
        xpath_instance = _find_query_in_cache(xpath_query)
        elements = xpath_instance(element)
        result = []
        for obj in elements:
            if isinstance(obj, (_ElementStringResult, _ElementUnicodeResult)):
                result.append(Text(obj))
            elif isinstance(obj, _Element):
                result.append(Element.from_tag(obj))
            else:
                result.append(obj)
        return result

    def clear(self):
        """Remove text, children and attributes from the element."""
        self.__element.clear()
        if hasattr(self, "_tmap"):
            self._tmap = []
        if hasattr(self, "_cmap"):
            self._cmap = []
        if hasattr(self, "_rmap"):
            self._rmap = []
        if hasattr(self, "_indexes"):
            remember = False
            if "_rmap" in self._indexes:
                remember = True
            self._indexes = {}
            self._indexes["_cmap"] = {}
            self._indexes["_tmap"] = {}
            if remember:
                self._indexes["_rmap"] = {}

    @property
    def clone(self):
        clone = deepcopy(self.__element)
        root = lxml_Element("ROOT", nsmap=ODF_NAMESPACES)
        root.append(clone)
        return self.from_tag(clone)

        # slow data = tostring(self.__element, encoding='unicode')
        # return self.from_tag(data)

    def serialize(self, pretty=False, with_ns=False):
        # This copy bypasses serialization side-effects in lxml
        native = deepcopy(self.__element)
        data = tostring(
            native, with_tail=False, pretty_print=pretty, encoding="unicode"
        )
        if not with_ns:
            # Remove namespaces
            data = ns_stripper.sub("", data)
        return data

    def serialize2(self, pretty=False, with_ns=False):
        # This copy bypasses serialization side-effects in lxml
        native = deepcopy(self.__element)
        data = tostring(
            native, with_tail=False, pretty_print=pretty, encoding="unicode"
        )
        if not with_ns:
            # Remove namespaces
            data = ns_stripper.sub("", data)
        return data + str(len(data))

    # Element helpers usable from any context

    @property
    def document_body(self):
        """Return the document body : 'office:body'"""
        return self.get_element("//office:body/*[1]")

    @document_body.setter
    def document_body(self, new_body):
        """Change in place the full document body content."""
        body = self.document_body
        tail = body.tail
        body.clear()
        for item in new_body.children:
            body.append(item)
        if tail:
            body.tail = tail

    def get_formatted_text(self, context):
        """This function must return a beautiful version of the text"""
        return ""

    def get_styled_elements(self, name=""):
        """Brute-force to find paragraphs, tables, etc. using the given style
        name (or all by default).

        Arguments:

            name -- str

        Return: list
        """
        # FIXME incomplete (and possibly inaccurate)
        return (
            _get_elements(self, "descendant::*", text_style=name)
            + _get_elements(self, "descendant::*", draw_style=name)
            + _get_elements(self, "descendant::*", draw_text_style=name)
            + _get_elements(self, "descendant::*", table_style=name)
            + _get_elements(self, "descendant::*", page_layout=name)
            + _get_elements(self, "descendant::*", master_page=name)
            + _get_elements(self, "descendant::*", parent_style=name)
        )

    # Common attributes

    def _get_inner_text(self, tag):
        element = self.get_element(tag)
        if element is None:
            return None
        return element.text

    def _set_inner_text(self, tag, text):
        element = self.get_element(tag)
        if element is None:
            element = Element.from_tag(tag)
            self.append(element)
        element.text = text

    # Dublin core

    @property
    def dc_creator(self):
        """Get dc:creator value.

        Return: str (or None if inexistant)
        """
        return self._get_inner_text("dc:creator")

    @dc_creator.setter
    def dc_creator(self, creator):
        """Set dc:creator value.

        Arguments:

            creator -- str
        """
        self._set_inner_text("dc:creator", creator)

    @property
    def dc_date(self):
        """Get the dc:date value.

        Return: datetime (or None if inexistant)
        """
        date = self._get_inner_text("dc:date")
        if date is None:
            return None
        return DateTime.decode(date)

    @dc_date.setter
    def dc_date(self, date):
        """Set the dc:date value.

        Arguments:

            darz -- DateTime
        """
        self._set_inner_text("dc:date", DateTime.encode(date))

    # SVG

    @property
    def svg_title(self):
        return self._get_inner_text("svg:title")

    @svg_title.setter
    def svg_title(self, title):
        self._set_inner_text("svg:title", title)

    @property
    def svg_description(self):
        return self._get_inner_text("svg:desc")

    @svg_description.setter
    def svg_description(self, description):
        self._set_inner_text("svg:desc", description)

    # Sections

    def get_sections(self, style=None, content=None):
        """Return all the sections that match the criteria.

        Arguments:

            style -- str

            content -- str regex

        Return: list of Element
        """
        return _get_elements(self, "text:section", text_style=style, content=content)

    def get_section(self, position=0, content=None):
        """Return the section that matches the criteria.

        Arguments:

            position -- int

            content -- str regex

        Return: Element or None if not found
        """
        return _get_element(self, "descendant::text:section", position, content=content)

    # Paragraphs

    def get_paragraphs(self, style=None, content=None):
        """Return all the paragraphs that match the criteria.

        Arguments:

            style -- str

            content -- str regex

        Return: list of Paragraph
        """
        return _get_elements(
            self, "descendant::text:p", text_style=style, content=content
        )

    def get_paragraph(self, position=0, content=None):
        """Return the paragraph that matches the criteria.

        Arguments:

            position -- int

            content -- str regex

        Return: Paragraph or None if not found
        """
        return _get_element(self, "descendant::text:p", position, content=content)

    # Span

    def get_spans(self, style=None, content=None):
        """Return all the spans that match the criteria.

        Arguments:

            style -- str

            content -- str regex

        Return: list of Span
        """
        return _get_elements(
            self, "descendant::text:span", text_style=style, content=content
        )

    def get_span(self, position=0, content=None):
        """Return the span that matches the criteria.

        Arguments:

            position -- int

            content -- str regex

        Return: Span or None if not found
        """
        return _get_element(self, "descendant::text:span", position, content=content)

    # Headers

    def get_headers(self, style=None, outline_level=None, content=None):
        """Return all the Headers that match the criteria.

        Arguments:

            style -- str

            content -- str regex

        Return: list of Header
        """
        return _get_elements(
            self,
            "descendant::text:h",
            text_style=style,
            outline_level=outline_level,
            content=content,
        )

    def get_header(self, position=0, outline_level=None, content=None):
        """Return the Header that matches the criteria.

        Arguments:

            position -- int

            content -- str regex

        Return: Header or None if not found
        """
        return _get_element(
            self,
            "descendant::text:h",
            position,
            outline_level=outline_level,
            content=content,
        )

    # Lists

    def get_lists(self, style=None, content=None):
        """Return all the lists that match the criteria.

        Arguments:

            style -- str

            content -- str regex

        Return: list of List
        """
        return _get_elements(
            self, "descendant::text:list", text_style=style, content=content
        )

    def get_list(self, position=0, content=None):
        """Return the list that matches the criteria.

        Arguments:

            position -- int

            content -- str regex

        Return: List or None if not found
        """
        return _get_element(self, "descendant::text:list", position, content=content)

    # Frames

    def get_frames(
        self,
        presentation_class=None,
        style=None,
        title=None,
        description=None,
        content=None,
    ):
        """Return all the frames that match the criteria.

        Arguments:

            style -- str

            title -- str regex

            description -- str regex

            content -- str regex

        Return: list of Frame
        """
        return _get_elements(
            self,
            "descendant::draw:frame",
            presentation_class=presentation_class,
            draw_style=style,
            svg_title=title,
            svg_desc=description,
            content=content,
        )

    def get_frame(
        self,
        position=0,
        name=None,
        presentation_class=None,
        title=None,
        description=None,
        content=None,
    ):
        """Return the section that matches the criteria.

        Arguments:

            position -- int

            title -- str regex

            description -- str regex

            content -- str regex

        Return: Frame or None if not found
        """
        return _get_element(
            self,
            "descendant::draw:frame",
            position,
            draw_name=name,
            presentation_class=presentation_class,
            svg_title=title,
            svg_desc=description,
            content=content,
        )

    # Images

    def get_images(self, style=None, url=None, content=None):
        """Return all the images matching the criteria.

        Arguments:

            style -- str

            url -- str regex

            content -- str regex

        Return: list of Element
        """
        return _get_elements(
            self, "descendant::draw:image", text_style=style, url=url, content=content
        )

    def get_image(self, position=0, name=None, url=None, content=None):
        """Return the image matching the criteria.

        Arguments:

            position -- int

            content -- str regex

        Return: Element or None if not found
        """
        # The frame is holding the name
        if name is not None:
            frame = _get_element(
                self, "descendant::draw:frame", position=position, draw_name=name
            )
            if frame is None:
                return None
            # The name is supposedly unique
            return frame.get_element("draw:image")
        return _get_element(
            self, "descendant::draw:image", position, url=url, content=content
        )

    # Tables

    def get_tables(self, style=None, content=None):
        """Return all the tables that match the criteria.

        Arguments:

            style -- str

            content -- str regex

        Return: list of Table
        """
        return _get_elements(
            self, "descendant::table:table", table_style=style, content=content
        )

    def get_table(self, position=0, name=None, content=None):
        """Return the table that matches the criteria.

        Arguments:

            position -- int

            name -- str

            content -- str regex

        Return: Table or None if not found
        """
        if name is None and content is None:
            result = self._get_element_idx("descendant::table:table", position)
        else:
            result = _get_element(
                self,
                "descendant::table:table",
                position,
                table_name=name,
                content=content,
            )
        return result

    # Named Range

    def get_named_ranges(self):
        """Return all the tables named ranges.

        Return: list of odf_named_range
        """
        named_ranges = self.get_elements(
            "descendant::table:named-expressions/table:named-range"
        )
        return named_ranges

    def get_named_range(self, name):
        """Return the named range of specified name, or None if not found.

        Arguments:

            name -- str

        Return: NamedRange
        """
        named_range = self.get_elements(
            'descendant::table:named-expressions/table:named-range[@table:name="%s"][1]'
            % name
        )
        if named_range:
            return named_range[0]
        else:
            return None

    def append_named_range(self, named_range):
        """Append the named range to the spreadsheet, replacing existing named
        range of same name if any.

        Arguments:

            named_range --  NamedRange
        """
        if self.tag != "office:spreadsheet":
            raise ValueError("Element is no 'office:spreadsheet' : %s" % self.tag)
        named_expressions = self.get_element("table:named-expressions")
        if not named_expressions:
            named_expressions = Element.from_tag("table:named-expressions")
            self.append(named_expressions)
        # exists ?
        current = named_expressions.get_element(
            'table:named-range[@table:name="%s"][1]' % named_range.name
        )
        if current:
            named_expressions.delete(current)
        named_expressions.append(named_range)

    def delete_named_range(self, name):
        """Delete the Named Range of specified name from the spreadsheet.

        Arguments:

            name -- str
        """
        if self.tag != "office:spreadsheet":
            raise ValueError("Element is no 'office:spreadsheet' : %s" % self.tag)
        named_range = self.get_named_range(name)
        if not named_range:
            return
        named_range.delete()
        named_expressions = self.get_element("table:named-expressions")
        element = named_expressions.__element
        children = len(element.getchildren())
        if not children:
            self.delete(named_expressions)

    # Notes

    def get_notes(self, note_class=None, content=None):
        """Return all the notes that match the criteria.

        Arguments:

            note_class -- 'footnote' or 'endnote'

            content -- str regex

        Return: list of Note
        """
        return _get_elements(
            self, "descendant::text:note", note_class=note_class, content=content
        )

    def get_note(self, position=0, note_id=None, note_class=None, content=None):
        """Return the note that matches the criteria.

        Arguments:

            position -- int

            note_id -- str

            note_class -- 'footnote' or 'endnote'

            content -- str regex

        Return: Note or None if not found
        """
        return _get_element(
            self,
            "descendant::text:note",
            position,
            text_id=note_id,
            note_class=note_class,
            content=content,
        )

    # Annotations

    def get_annotations(
        self, creator=None, start_date=None, end_date=None, content=None
    ):
        """Return all the annotations that match the criteria.

        Arguments:

            creator -- str

            start_date -- date object

            end_date -- date object

            content -- str regex

        Return: list of Annotation
        """
        annotations = []
        for annotation in _get_elements(
            self, "descendant::office:annotation", content=content
        ):
            if creator is not None and creator != annotation.dc_creator:
                continue
            date = annotation.dc_date
            if start_date is not None and date < start_date:
                continue
            if end_date is not None and date >= end_date:
                continue
            annotations.append(annotation)
        return annotations

    def get_annotation(
        self,
        position=0,
        creator=None,
        start_date=None,
        end_date=None,
        content=None,
        name=None,
    ):
        """Return the annotation that matches the criteria.

        Arguments:

            position -- int

            creator -- str

            start_date -- date object

            end_date -- date object

            content -- str regex

            name -- str

        Return: Annotation or None if not found
        """
        if name is not None:
            return _get_element(
                self, "descendant::office:annotation", 0, office_name=name
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

    def get_annotation_ends(self):
        """Return all the annotation ends.

        Return: list of Element
        """
        return _get_elements(self, "descendant::office:annotation-end")

    def get_annotation_end(self, position=0, name=None):
        """Return the annotation end that matches the criteria.

        Arguments:

            position -- int

            name -- str

        Return: Element or None if not found
        """
        return _get_element(
            self, "descendant::office:annotation-end", position, office_name=name
        )

    # office:names

    def get_office_names(self):
        """Return all the used office:name tags values of the element.

        Return: list of unique str
        """
        name_xpath_query = _find_query_in_cache("//@office:name")
        names = name_xpath_query(self.__element)
        uniq_names = list(set(names))
        return uniq_names

    # Variables

    def get_variable_decls(self):
        """Return the container for variable declarations. Created if not
        found.

        Return: Element
        """
        variable_decls = self.get_element("//text:variable-decls")
        if variable_decls is None:
            body = self.document_body
            body.insert(Element.from_tag("text:variable-decls"), FIRST_CHILD)
            variable_decls = body.get_element("//text:variable-decls")

        return variable_decls

    def get_variable_decl_list(self):
        """Return all the variable declarations.

        Return: list of Element
        """
        return _get_elements(self, "descendant::text:variable-decl")

    def get_variable_decl(self, name, position=0):
        """return the variable declaration for the given name.

        return: Element or none if not found
        """
        return _get_element(
            self, "descendant::text:variable-decl", position, text_name=name
        )

    def get_variable_sets(self, name=None):
        """Return all the variable sets that match the criteria.

        Arguments:

            name -- str

        Return: list of Element
        """
        return _get_elements(self, "descendant::text:variable-set", text_name=name)

    def get_variable_set(self, name, position=-1):
        """Return the variable set for the given name (last one by default).

        Arguments:

            name -- str

            position -- int

        Return: Element or None if not found
        """
        return _get_element(
            self, "descendant::text:variable-set", position, text_name=name
        )

    def get_variable_set_value(self, name, value_type=None):
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
        return get_value(variable_set, value_type)

    # User fields

    def get_user_field_decls(self):
        """Return the container for user field declarations. Created if not
        found.

        Return: Element
        """
        user_field_decls = self.get_element("//text:user-field-decls")
        if user_field_decls is None:
            body = self.document_body
            body.insert(Element.from_tag("text:user-field-decls"), FIRST_CHILD)
            user_field_decls = body.get_element("//text:user-field-decls")

        return user_field_decls

    def get_user_field_decl_list(self):
        """Return all the user field declarations.

        Return: list of Element
        """
        return _get_elements(self, "descendant::text:user-field-decl")

    def get_user_field_decl(self, name, position=0):
        """return the user field declaration for the given name.

        return: Element or none if not found
        """
        return _get_element(
            self, "descendant::text:user-field-decl", position, text_name=name
        )

    def get_user_field_value(self, name, value_type=None):
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
        return get_value(user_field_decl, value_type)

    # User defined fields
    # They are fields who should contain a copy of a user defined medtadata

    def get_user_defined_list(self):
        """Return all the user defined field declarations.

        Return: list of Element
        """
        return _get_elements(self, "descendant::text:user-defined")

    def get_user_defined(self, name, position=0):
        """return the user defined declaration for the given name.

        return: Element or none if not found
        """
        return _get_element(
            self, "descendant::text:user-defined", position, text_name=name
        )

    def get_user_defined_value(self, name, value_type=None):
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
        return get_value(user_defined, value_type)

    # Draw Pages

    def get_draw_pages(self, style=None, content=None):
        """Return all the draw pages that match the criteria.

        Arguments:

            style -- str

            content -- str regex

        Return: list of DrawPage
        """
        return _get_elements(
            self, "descendant::draw:page", draw_style=style, content=content
        )

    def get_draw_page(self, position=0, name=None, content=None):
        """Return the draw page that matches the criteria.

        Arguments:

            position -- int

            name -- str

            content -- str regex

        Return: DrawPage or None if not found
        """
        return _get_element(
            self, "descendant::draw:page", position, draw_name=name, content=content
        )

    # Links

    def get_links(self, name=None, title=None, url=None, content=None):
        """Return all the links that match the criteria.

        Arguments:

            name -- str

            title -- str

            url -- str regex

            content -- str regex

        Return: list of Element
        """
        return _get_elements(
            self,
            "descendant::text:a",
            office_name=name,
            office_title=title,
            url=url,
            content=content,
        )

    def get_link(self, position=0, name=None, title=None, url=None, content=None):
        """Return the link that matches the criteria.

        Arguments:

            position -- int

            name -- str

            title -- str

            url -- str regex

            content -- str regex

        Return: Element or None if not found
        """
        return _get_element(
            self,
            "descendant::text:a",
            position,
            office_name=name,
            office_title=title,
            url=url,
            content=content,
        )

    # Bookmarks

    def get_bookmarks(self):
        """Return all the bookmarks.

        Return: list of Element
        """
        return _get_elements(self, "descendant::text:bookmark")

    def get_bookmark(self, position=0, name=None):
        """Return the bookmark that matches the criteria.

        Arguments:

            position -- int

            name -- str

        Return: Bookmark or None if not found
        """
        return _get_element(self, "descendant::text:bookmark", position, text_name=name)

    def get_bookmark_starts(self):
        """Return all the bookmark starts.

        Return: list of Element
        """
        return _get_elements(self, "descendant::text:bookmark-start")

    def get_bookmark_start(self, position=0, name=None):
        """Return the bookmark start that matches the criteria.

        Arguments:

            position -- int

            name -- str

        Return: Element or None if not found
        """
        return _get_element(
            self, "descendant::text:bookmark-start", position, text_name=name
        )

    def get_bookmark_ends(self):
        """Return all the bookmark ends.

        Return: list of Element
        """
        return _get_elements(self, "descendant::text:bookmark-end")

    def get_bookmark_end(self, position=0, name=None):
        """Return the bookmark end that matches the criteria.

        Arguments:

            position -- int

            name -- str

        Return: Element or None if not found
        """
        return _get_element(
            self, "descendant::text:bookmark-end", position, text_name=name
        )

    # Reference marks

    def get_reference_marks_single(self):
        """Return all the reference marks. Search only the tags
        text:reference-mark.
        Consider using : get_reference_marks()

        Return: list of Element
        """
        return _get_elements(self, "descendant::text:reference-mark")

    def get_reference_mark_single(self, position=0, name=None):
        """Return the reference mark that matches the criteria. Search only the
        tags text:reference-mark.
        Consider using : get_reference_mark()

        Arguments:

            position -- int

            name -- str

        Return: Element or None if not found
        """
        return _get_element(
            self, "descendant::text:reference-mark", position, text_name=name
        )

    def get_reference_mark_starts(self):
        """Return all the reference mark starts. Search only the tags
        text:reference-mark-start.
        Consider using : get_reference_marks()

        Return: list of Element
        """
        return _get_elements(self, "descendant::text:reference-mark-start")

    def get_reference_mark_start(self, position=0, name=None):
        """Return the reference mark start that matches the criteria. Search
        only the tags text:reference-mark-start.
        Consider using : get_reference_mark()

        Arguments:

            position -- int

            name -- str

        Return: Element or None if not found
        """
        return _get_element(
            self, "descendant::text:reference-mark-start", position, text_name=name
        )

    def get_reference_mark_ends(self):
        """Return all the reference mark ends. Search only the tags
        text:reference-mark-end.
        Consider using : get_reference_marks()

        Return: list of Element
        """
        return _get_elements(self, "descendant::text:reference-mark-end")

    def get_reference_mark_end(self, position=0, name=None):
        """Return the reference mark end that matches the criteria. Search only
        the tags text:reference-mark-end.
        Consider using : get_reference_marks()

        Arguments:

            position -- int

            name -- str

        Return: Element or None if not found
        """
        return _get_element(
            self, "descendant::text:reference-mark-end", position, text_name=name
        )

    def get_reference_marks(self):
        """Return all the reference marks, either single position reference
        (text:reference-mark) or start of range reference
        (text:reference-mark-start).

        Return: list of Element
        """
        request = (
            "descendant::text:reference-mark-start | descendant::text:reference-mark"
        )
        return _get_elements(self, request)

    def get_reference_mark(self, position=0, name=None):
        """Return the reference mark that match the criteria. Either single
        position reference mark (text:reference-mark) or start of range
        reference (text:reference-mark-start).

        Arguments:

            position -- int

            name -- str

        Return: Element or None if not found
        """
        name = to_str(name)
        if name:
            request = (
                f"descendant::text:reference-mark-start"
                f'[@text:name="{name}"] '
                f"| descendant::text:reference-mark"
                f'[@text:name="{name}"]'
            )
            return _get_element(self, request, position=0)
        request = (
            "descendant::text:reference-mark-start | descendant::text:reference-mark"
        )
        return _get_element(self, request, position)

    def get_references(self, name=None):
        """Return all the references (text:reference-ref). If name is
        provided, returns the references of that name.

        Return: list of Element

        Arguments:

            name -- str or None
        """
        if name is None:
            return _get_elements(self, "descendant::text:reference-ref")
        request = 'descendant::text:reference-ref[@text:ref-name="%s"]' % to_bytes(name)
        return _get_elements(self, request)

    # Shapes elements

    # Groups

    def get_draw_groups(self, title=None, description=None, content=None):
        return _get_elements(
            self,
            "descendant::draw:g",
            svg_title=title,
            svg_desc=description,
            content=content,
        )

    def get_draw_group(
        self, position=0, name=None, title=None, description=None, content=None
    ):
        return _get_element(
            self,
            "descendant::draw:g",
            position,
            draw_name=name,
            svg_title=title,
            svg_desc=description,
            content=content,
        )

    # Lines

    def get_draw_lines(self, draw_style=None, draw_text_style=None, content=None):
        """Return all the draw lines that match the criteria.

        Arguments:

            draw_style -- str

            draw_text_style -- str

            content -- str regex

        Return: list of odf_shape
        """
        return _get_elements(
            self,
            "descendant::draw:line",
            draw_style=draw_style,
            draw_text_style=draw_text_style,
            content=content,
        )

    def get_draw_line(self, position=0, id=None, content=None):
        """Return the draw line that matches the criteria.

        Arguments:

            position -- int

            id -- str

            content -- str regex

        Return: odf_shape or None if not found
        """
        return _get_element(
            self, "descendant::draw:line", position, draw_id=id, content=content
        )

    # Rectangles

    def get_draw_rectangles(self, draw_style=None, draw_text_style=None, content=None):
        """Return all the draw rectangles that match the criteria.

        Arguments:

            draw_style -- str

            draw_text_style -- str

            content -- str regex

        Return: list of odf_shape
        """
        return _get_elements(
            self,
            "descendant::draw:rect",
            draw_style=draw_style,
            draw_text_style=draw_text_style,
            content=content,
        )

    def get_draw_rectangle(self, position=0, id=None, content=None):
        """Return the draw rectangle that matches the criteria.

        Arguments:

            position -- int

            id -- str

            content -- str regex

        Return: odf_shape or None if not found
        """
        return _get_element(
            self, "descendant::draw:rect", position, draw_id=id, content=content
        )

    # Ellipse

    def get_draw_ellipses(self, draw_style=None, draw_text_style=None, content=None):
        """Return all the draw ellipses that match the criteria.

        Arguments:

            draw_style -- str

            draw_text_style -- str

            content -- str regex

        Return: list of odf_shape
        """
        return _get_elements(
            self,
            "descendant::draw:ellipse",
            draw_style=draw_style,
            draw_text_style=draw_text_style,
            content=content,
        )

    def get_draw_ellipse(self, position=0, id=None, content=None):
        """Return the draw ellipse that matches the criteria.

        Arguments:

            position -- int

            id -- str

            content -- str regex

        Return: odf_shape or None if not found
        """
        return _get_element(
            self, "descendant::draw:ellipse", position, draw_id=id, content=content
        )

    # Connectors

    def get_draw_connectors(self, draw_style=None, draw_text_style=None, content=None):
        """Return all the draw connectors that match the criteria.

        Arguments:

            draw_style -- str

            draw_text_style -- str

            content -- str regex

        Return: list of odf_shape
        """
        return _get_elements(
            self,
            "descendant::draw:connector",
            draw_style=draw_style,
            draw_text_style=draw_text_style,
            content=content,
        )

    def get_draw_connector(self, position=0, id=None, content=None):
        """Return the draw connector that matches the criteria.

        Arguments:

            position -- int

            id -- str

            content -- str regex

        Return: odf_shape or None if not found
        """
        return _get_element(
            self, "descendant::draw:connector", position, draw_id=id, content=content
        )

    def get_orphan_draw_connectors(self):
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

    def get_tracked_changes(self):
        """Return the tracked-changes part in the text body."""
        return self.get_element("//text:tracked-changes")

    def get_changes_ids(self):
        """Return a list of ids that refers to a change region in the tracked
        changes list.
        """
        # Insertion changes
        xpath_query = "descendant::text:change-start/@text:change-id"
        # Deletion changes
        xpath_query += " | descendant::text:change/@text:change-id"
        return self.xpath(xpath_query)

    def get_text_change_deletions(self):
        """Return all the text changes of deletion kind: the tags text:change.
        Consider using : get_text_changes()

        Return: list of Element
        """
        return _get_elements(self, "descendant::text:text:change")

    def get_text_change_deletion(self, position=0, idx=None):
        """Return the text change of deletion kind that matches the criteria.
        Search only for the tags text:change.
        Consider using : get_text_change()

        Arguments:

            position -- int

            idx -- str

        Return: Element or None if not found
        """
        return _get_element(self, "descendant::text:change", position, change_id=idx)

    def get_text_change_starts(self):
        """Return all the text change-start. Search only for the tags
        text:change-start.
        Consider using : get_text_changes()

        Return: list of Element
        """
        return _get_elements(self, "descendant::text:change-start")

    def get_text_change_start(self, position=0, idx=None):
        """Return the text change-start that matches the criteria. Search
        only the tags text:change-start.
        Consider using : get_text_change()

        Arguments:

            position -- int

            idx -- str

        Return: Element or None if not found
        """
        return _get_element(
            self, "descendant::text:change-start", position, change_id=idx
        )

    def get_text_change_ends(self):
        """Return all the text change-end. Search only the tags
        text:change-end.
        Consider using : get_text_changes()

        Return: list of Element
        """
        return _get_elements(self, "descendant::text:change-end")

    def get_text_change_end(self, position=0, idx=None):
        """Return the text change-end that matches the criteria. Search only
        the tags text:change-end.
        Consider using : get_text_change()

        Arguments:

            position -- int

            idx -- str

        Return: Element or None if not found
        """
        return _get_element(
            self, "descendant::text:change-end", position, change_id=idx
        )

    def get_text_changes(self):
        """Return all the text changes, either single deletion
        (text:change) or start of range of changes (text:change-start).

        Return: list of Element
        """
        request = "descendant::text:change-start | descendant::text:change"
        return _get_elements(self, request)

    def get_text_change(self, position=0, idx=None):
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
                'descendant::text:change-start[@text:change-id="%s"] '
                '| descendant::text:change[@text:change-id="%s"]'
            ) % (idx, idx)
            return _get_element(self, request, position=0)
        request = "descendant::text:change-start | descendant::text:change"
        return _get_element(self, request, position)

    # Table Of Content

    def get_tocs(self):
        """Return all the tables of contents.

        Return: list of odf_toc
        """
        return _get_elements(self, "text:table-of-content")

    def get_toc(self, position=0, content=None):
        """Return the table of contents that matches the criteria.

        Arguments:

            position -- int

            content -- str regex

        Return: odf_toc or None if not found
        """
        return _get_element(self, "text:table-of-content", position, content=content)

    # Styles

    @staticmethod
    def _get_style_tagname(family, is_default=False):
        """Widely match possible tag names given the family (or not)."""
        if family is None:
            tagname = (
                "("
                + "|".join(
                    [
                        "style:default-style",
                        "*[@style:name]",
                        "draw:fill-image",
                        "draw:marker",
                    ]
                )
                + ")"
            )
        elif is_default is True:
            # Default style
            tagname = "style:default-style"
        else:
            tagname = _family_style_tagname(family)
            # if famattr:
            #    # Include family default style
            #    tagname = '(%s|style:default-style)' % tagname
            if family in FAMILY_ODF_STD:
                # Include family default style
                tagname = "(%s|style:default-style)" % tagname
        return tagname

    def get_styles(self, family=None):
        # Both common and default styles
        tagname = self._get_style_tagname(family)
        return _get_elements(self, tagname, family=family)

    def get_style(self, family, name_or_element=None, display_name=None):
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
                raise ValueError("Not a odf_style ?  %s" % name_or_element)
        style_name = name_or_element
        is_default = not (style_name or display_name)
        tagname = self._get_style_tagname(family, is_default=is_default)
        # famattr became None if no "style:family" attribute
        return _get_element(
            self,
            tagname,
            0,
            style_name=style_name,
            display_name=display_name,
            family=family,
        )
