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
# Authors: Hervé Cauwelier <herve@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>

from collections.abc import Iterable

import pytest
from lxml.etree import _ElementTree

from odfdo.const import ODF_CONTENT, ODF_META
from odfdo.container import Container
from odfdo.content import Content
from odfdo.element import Element
from odfdo.xmlpart import XmlPart


@pytest.fixture
def exemple_container(samples) -> Iterable[Container]:
    container = Container()
    container.open(samples("example.odt"))
    yield container


def test_get_element_list(exemple_container):
    content_part = XmlPart(ODF_CONTENT, exemple_container)
    elements = content_part.get_elements("//text:p")
    # The annotation paragraph is counted
    assert len(elements) == 8


def test_tree(exemple_container):
    # Testing a private but important method
    content = XmlPart(ODF_CONTENT, exemple_container)
    tree = content._get_tree()
    assert isinstance(tree, _ElementTree)
    assert content._XmlPart__tree is not None


def test_root(exemple_container):
    content = XmlPart(ODF_CONTENT, exemple_container)
    root = content.root
    assert isinstance(root, Element)
    assert root.tag == "office:document-content"
    assert content._XmlPart__root is not None


def test_serialize(exemple_container):
    content_bytes = exemple_container.get_part(ODF_CONTENT)
    content_part = XmlPart(ODF_CONTENT, exemple_container)
    # differences with lxml
    serialized = content_part.serialize().replace(b"'", b"&apos;")
    print(serialized)
    print(content_bytes)
    assert content_bytes == serialized


def test_pretty_serialize_base():
    # With pretty = True
    element = Element.from_tag("<root><a>spam</a><b/></root>")
    serialized = element.serialize(pretty=True)
    expected = "<root>\n  <a>spam</a>\n  <b/>\n</root>\n"
    assert serialized == expected


def test_clone(exemple_container):
    # Testing that the clone works on subclasses too
    content = Content(ODF_CONTENT, exemple_container)
    clone = content.clone
    assert clone.part_name == content.part_name
    assert id(exemple_container) != id(clone.container)
    assert clone._XmlPart__tree is None


def test_delete(exemple_container):
    content = XmlPart(ODF_CONTENT, exemple_container)
    paragraphs = content.get_elements("//text:p")
    for paragraph in paragraphs:
        content.delete_element(paragraph)
    serialized = content.serialize()
    assert serialized.count(b"<text:p") == 0


def test_repr(exemple_container):
    content_part = XmlPart(ODF_CONTENT, exemple_container)
    result = repr(content_part)
    assert result == "<XmlPart part_name=content.xml>"


def test_str(exemple_container):
    content_part = XmlPart(ODF_CONTENT, exemple_container)
    assert str(content_part) == repr(content_part)


def test_get_body(exemple_container):
    content_part = XmlPart(ODF_CONTENT, exemple_container)
    body = content_part.body
    assert body.tag == "office:text"


def test_get_body_none(exemple_container):
    content_part = XmlPart(ODF_META, exemple_container)
    with pytest.raises(TypeError):
        _ = content_part.body


def test_set_body(exemple_container):
    content_part = XmlPart(ODF_CONTENT, exemple_container)
    body = content_part.body
    body_clone = body.clone
    content_part.body = body_clone
    assert content_part.body.tag == "office:text"


def test_pretty_serialize_internal_not_pretty(samples):
    container = Container()
    container.open(samples("issue_28_pretty.odt"))
    content = XmlPart(ODF_CONTENT, container)
    serialized = content.serialize()
    expected = b'This is an example with =&gt;</text:span><text:span text:style-name="T4"> v</text:span><text:span text:style-name="T5">8</text:span><text:span text:style-name="T4">.1.</text:span><text:span text:style-name="T5">4</text:span><text:span text:style-name="T4"> &lt;</text:span><text:span text:style-name="T6">= spaces </text:span><text:span text:style-name="T7">after reading and writing with odfdo.'
    assert expected in serialized


def test_pretty_serialize_internal_pretty(samples):
    container = Container()
    container.open(samples("issue_28_pretty.odt"))
    content = XmlPart(ODF_CONTENT, container)
    serialized = content.pretty_serialize()
    print(serialized.decode())
    expected = b'This is an example with =&gt;</text:span><text:span text:style-name="T4"> v</text:span><text:span text:style-name="T5">8</text:span><text:span text:style-name="T4">.1.</text:span><text:span text:style-name="T5">4</text:span><text:span text:style-name="T4"> &lt;</text:span><text:span text:style-name="T6">= spaces </text:span><text:span text:style-name="T7">after reading and writing with odfdo.'
    assert expected in serialized


def test_pretty_serialize_internal_pretty2(samples):
    container = Container()
    container.open(samples("issue_28_pretty.odt"))
    content = XmlPart(ODF_CONTENT, container)
    serialized = content.serialize(pretty=True)
    expected = b'This is an example with =&gt;</text:span><text:span text:style-name="T4"> v</text:span><text:span text:style-name="T5">8</text:span><text:span text:style-name="T4">.1.</text:span><text:span text:style-name="T5">4</text:span><text:span text:style-name="T4"> &lt;</text:span><text:span text:style-name="T6">= spaces </text:span><text:span text:style-name="T7">after reading and writing with odfdo.'
    assert expected in serialized
