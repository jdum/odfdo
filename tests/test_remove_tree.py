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

from collections.abc import Iterable

import pytest

from odfdo.document import Document
from odfdo.element import Element
from odfdo.header import Header
from odfdo.line_break import LineBreak
from odfdo.paragraph import Paragraph
from odfdo.spacer import Spacer
from odfdo.tab import Tab
from odfdo.link import Link
from odfdo.list import List
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
        "<text:p>"
        "first<text:tab/>"
        "second<text:line-break/>"
        'third <text:s text:c="3"/>'
        "four"
        '<text:a xlink:href="http://example.com/" office:name="link1"/>'
        "</text:p>"
        "</office:text>"
    )
    assert document.body.serialize() == expected


def test_remove_link(document):
    remove_tree(document.body, Link)
    expected = (
        "<office:text>"
        '<text:h text:outline-level="1">header</text:h>'
        "<text:p>"
        "first<text:tab/>"
        "second<text:line-break/>"
        'third <text:s text:c="3"/>'
        "four"
        "</text:p>"
        "</office:text>"
    )
    assert document.body.serialize() == expected


def test_remove_tab(document):
    remove_tree(document.body, Tab)
    expected = (
        "<office:text>"
        '<text:h text:outline-level="1">header</text:h>'
        "<text:p>"
        "first second<text:line-break/>"
        'third <text:s text:c="3"/>four'
        '<text:a xlink:href="http://example.com/" office:name="link1"/>'
        "</text:p>"
        "</office:text>"
    )
    assert document.body.serialize() == expected


def test_remove_spacer(document):
    remove_tree(document.body, Spacer)
    expected = (
        "<office:text>"
        '<text:h text:outline-level="1">header</text:h>'
        "<text:p>"
        "first<text:tab/>"
        "second<text:line-break/>"
        "third "
        "four"
        '<text:a xlink:href="http://example.com/" office:name="link1"/>'
        "</text:p>"
        "</office:text>"
    )
    assert document.body.serialize() == expected


def test_remove_line_break(document):
    remove_tree(document.body, LineBreak)
    expected1 = (
        "<office:text>"
        '<text:h text:outline-level="1">header</text:h>'
        "<text:p>"
        "first<text:tab/>"
        "second "
        'third <text:s text:c="3"/>'
        "four"
        '<text:a xlink:href="http://example.com/" office:name="link1"/>'
        "</text:p>"
        "</office:text>"
    )
    expected2 = (
        "<office:text>"
        '<text:h text:outline-level="1">header</text:h>'
        "<text:p>"
        "first<text:tab/>"
        "second "
        'third<text:s text:c="4"/>'
        "four"
        '<text:a xlink:href="http://example.com/" office:name="link1"/>'
        "</text:p>"
        "</office:text>"
    )
    assert document.body.serialize() in (expected1, expected2)


def test_remove_header_wrong(document):
    # when removing header, we want to also remove the inner text
    remove_tree(document.body, Header)
    expected = (
        "<office:text>"
        "header"  # bad
        "<text:p>"
        "first"
        "<text:tab/>"
        "second<text:line-break/>"
        'third <text:s text:c="3"/>'
        "four"
        '<text:a xlink:href="http://example.com/" office:name="link1"/>'
        "</text:p>"
        "</office:text>"
    )
    assert document.body.serialize() == expected


def test_remove_header(document):
    # when removing header, we want to also remove the inner text
    remove_tree(document.body, Header, keep_children=False)
    expected = (
        "<office:text>"
        "<text:p>"
        "first"
        "<text:tab/>"
        "second<text:line-break/>"
        'third <text:s text:c="3"/>'
        "four"
        '<text:a xlink:href="http://example.com/" office:name="link1"/>'
        "</text:p>"
        "</office:text>"
    )
    assert document.body.serialize() == expected
