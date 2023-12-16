# Copyright 2018-2023 Jérôme Dumonteil
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
from pathlib import Path

import pytest
from lxml.etree import _ElementTree

from odfdo.const import ODF_CONTENT
from odfdo.container import Container
from odfdo.content import Content
from odfdo.element import Element
from odfdo.xmlpart import XmlPart

SAMPLES = Path(__file__).parent / "samples"


@pytest.fixture
def exemple_container() -> Iterable[Container]:
    container = Container()
    container.open(SAMPLES / "example.odt")
    yield container


def test_get_element_list(exemple_container):
    content_part = XmlPart(ODF_CONTENT, exemple_container)
    elements = content_part.get_elements("//text:p")
    # The annotation paragraph is counted
    assert len(elements) == 8


def test_tree(exemple_container):
    # Testing a private but important method
    content = XmlPart(ODF_CONTENT, exemple_container)
    tree = content._XmlPart__get_tree()
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
    assert content_bytes == serialized


def test_pretty_serialize():
    # With pretty = True
    element = Element.from_tag("<root><a>spam</a><b/></root>")
    serialized = element.serialize(pretty=True)
    expected = "<root>\n" "  <a>spam</a>\n" "  <b/>\n" "</root>\n"
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
