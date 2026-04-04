# Copyright 2018-2026 Jérôme Dumonteil
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
from __future__ import annotations

from collections.abc import Iterable

import pytest

from odfdo.document import Document
from odfdo.header import Header
from odfdo.line_break import LineBreak
from odfdo.link import Link
from odfdo.list import List
from odfdo.paragraph import Paragraph
from odfdo.spacer import Spacer
from odfdo.tab import Tab
from odfdo.utils.remove_tree import remove_tree


@pytest.fixture
def document(samples) -> Iterable[Document]:
    document = Document("odt")
    document.body.clear()
    document.body.append(Header(1, "header"))
    para = Paragraph("first\tsecond\nthird    four")
    link = Link("http://example.com/", name="link1")
    para.append(link)
    document.body.append(para)
    yield document


def test_remove_no_found(document):
    remove_tree(document.body, List)
    expected = (
        "<office:text>"
        '<text:h text:outline-level="1">header</text:h>'
        "<text:p>first"
        "<text:tab></text:tab>"
        "second"
        "<text:line-break></text:line-break>"
        "third "
        '<text:s text:c="3"></text:s>'
        "four"
        '<text:a xlink:href="http://example.com/" office:name="link1">'
        "</text:a>"
        "</text:p>"
        "</office:text>"
    )
    assert document.body._canonicalize() == expected


def test_remove_link(document):
    remove_tree(document.body, Link)
    expected = (
        "<office:text>"
        '<text:h text:outline-level="1">header</text:h>'
        "<text:p>first"
        "<text:tab></text:tab>"
        "second"
        "<text:line-break></text:line-break>"
        "third "
        '<text:s text:c="3">'
        "</text:s>"
        "four"
        "</text:p>"
        "</office:text>"
    )
    assert document.body._canonicalize() == expected


def test_remove_tab(document):
    remove_tree(document.body, Tab)
    expected = (
        "<office:text>"
        '<text:h text:outline-level="1">header</text:h>'
        "<text:p>"
        "first second"
        "<text:line-break></text:line-break>"
        "third "
        '<text:s text:c="3"></text:s>'
        "four"
        '<text:a xlink:href="http://example.com/" office:name="link1">'
        "</text:a>"
        "</text:p>"
        "</office:text>"
    )
    assert document.body._canonicalize() == expected


def test_remove_spacer(document):
    remove_tree(document.body, Spacer)
    expected = (
        "<office:text>"
        '<text:h text:outline-level="1">header</text:h>'
        "<text:p>first"
        "<text:tab></text:tab>"
        "second"
        "<text:line-break></text:line-break>"
        "third "
        "four"
        '<text:a xlink:href="http://example.com/" office:name="link1">'
        "</text:a>"
        "</text:p>"
        "</office:text>"
    )
    assert document.body._canonicalize() == expected


def test_remove_line_break(document):
    remove_tree(document.body, LineBreak)
    expected = (
        "<office:text>"
        '<text:h text:outline-level="1">header</text:h>'
        "<text:p>first"
        "<text:tab></text:tab>"
        "second third "
        '<text:s text:c="3"></text:s>'
        "four"
        '<text:a xlink:href="http://example.com/" office:name="link1">'
        "</text:a>"
        "</text:p>"
        "</office:text>"
    )
    assert document.body._canonicalize() == expected


def test_remove_header_wrong(document):
    # when removing header, we want to also remove the inner text
    remove_tree(document.body, Header)
    expected = (
        "<office:text>header"  # here children not removed
        "<text:p>first"
        "<text:tab></text:tab>"
        "second"
        "<text:line-break></text:line-break>"
        "third "
        '<text:s text:c="3"></text:s>'
        "four"
        '<text:a xlink:href="http://example.com/" office:name="link1">'
        "</text:a>"
        "</text:p>"
        "</office:text>"
    )
    assert document.body._canonicalize() == expected


def test_remove_header(document):
    # when removing header, we want to also remove the inner text
    remove_tree(document.body, Header, keep_children=False)
    expected = (
        "<office:text>"
        "<text:p>first"
        "<text:tab></text:tab>"
        "second"
        "<text:line-break></text:line-break>"
        "third "
        '<text:s text:c="3"></text:s>'
        "four"
        '<text:a xlink:href="http://example.com/" office:name="link1">'
        "</text:a>"
        "</text:p>"
        "</office:text>"
    )
    assert document.body._canonicalize() == expected


def test_remove_tree_safe(document):
    # Header contains text, which is internally a text node
    # Let's add a Link inside a Header and another in a Paragraph
    para = document.body.get_paragraph()
    link1 = Link("http://para.com/", name="link_para")
    para.append(link1)

    header = document.body.get_header()
    link2 = Link("http://header.com/", name="link_header")
    header.append(link2)

    # Remove links, but safe if inside Header
    remove_tree(document.body, Link, safe=Header)

    assert document.body.get_element('//text:a[@office:name="link_header"]') is not None
    assert document.body.get_element('//text:a[@office:name="link_para"]') is None


def test_remove_tree_tail(document):
    # Test tail preservation on modified element
    para = document.body.get_paragraph()
    para.clear()
    para.text = "Start"
    # Link uses text:a tag
    link = Link("http://test", name="test")
    link.text = "Inner"
    link.tail = "Tail"
    para.append(link)
    para.tail = "ParaTail"

    # Modify para by removing link
    remove_tree(para, Link, keep_children=True)

    # para should now have text "StartInnerTail" and tail "ParaTail"
    assert para.text == "StartInnerTail"
    assert para.tail == "ParaTail"


def test_remove_tree_bad_attribute(document, capsys):
    # Test ValueError in set_attribute
    para = document.body.get_paragraph()
    para.clear()
    para.text = "text"
    link = Link("http://ex.com")
    para.append(link)

    # Use a class where set_attribute is overridden to raise ValueError.
    class BadElement(Paragraph):
        def set_attribute(self, name, value):
            if hasattr(self, "_trigger_bad") and self._trigger_trigger:
                raise ValueError("Bad")
            super().set_attribute(name, value)

    bad = BadElement()
    bad.set_attribute("text:style-name", "some_style")
    bad._trigger_bad = True
    bad._trigger_trigger = True

    # bad -> link. remove link.
    bad.append(Link("http://x"))
    remove_tree(bad, Link)

    captured = capsys.readouterr()
    assert "Incorrect attribute" in captured.out
