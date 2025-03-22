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

from collections.abc import Iterable

import pytest

from odfdo import Element
from odfdo.bookmark import Bookmark, BookmarkEnd, BookmarkStart
from odfdo.document import Document
from odfdo.paragraph import Paragraph

ZOE = "你好 Zoé"


@pytest.fixture
def sample_body(samples) -> Iterable[Element]:
    document = Document(samples("bookmark.odt"))
    yield document.body


def test_create_bookmark():
    bookmark = Bookmark(ZOE)
    expected = f'<text:bookmark text:name="{ZOE}"/>'
    assert bookmark.serialize() == expected


def test_bookmark_str():
    bookmark = Bookmark(ZOE)
    assert str(bookmark) == ""


def test_create_bookmark_start():
    bookmark_start = BookmarkStart(ZOE)
    expected = f'<text:bookmark-start text:name="{ZOE}"/>'
    assert bookmark_start.serialize() == expected


def test_create_bookmark_end():
    bookmark_end = BookmarkEnd(ZOE)
    expected = f'<text:bookmark-end text:name="{ZOE}"/>'
    assert bookmark_end.serialize() == expected


def test_get_bookmark_main(sample_body):
    para = sample_body.get_paragraph()
    bookmark = Bookmark(ZOE)
    para.append(bookmark)
    read_book = sample_body.get_bookmark(name=ZOE)
    expected = f'<text:bookmark text:name="{ZOE}"/>'
    assert read_book.serialize() == expected


def test_get_bookmark_list(sample_body):
    result = sample_body.get_bookmarks()
    assert len(result) == 1
    element = result[0]
    expected = '<text:bookmark text:name="Repère de texte"/>'
    assert element.serialize() == expected


def test_get_bookmark_start(sample_body):
    para = sample_body.get_paragraph()
    bookmark_start = BookmarkStart(ZOE)
    para.append(bookmark_start)
    get = sample_body.get_bookmark_start(name=ZOE)
    expected = f'<text:bookmark-start text:name="{ZOE}"/>'
    assert get.serialize() == expected


def test_get_bookmark_start_list(sample_body):
    bookmark_start = BookmarkStart(ZOE)
    para = sample_body.get_paragraph()
    para.append(bookmark_start)
    get = sample_body.get_bookmark_starts()[0]
    expected = f'<text:bookmark-start text:name="{ZOE}"/>'
    assert get.serialize() == expected


def test_get_bookmark_end(sample_body):
    para = sample_body.get_paragraph()
    bookmark_end = BookmarkEnd(ZOE)
    para.append(bookmark_end)
    get = sample_body.get_bookmark_end(name=ZOE)
    expected = f'<text:bookmark-end text:name="{ZOE}"/>'
    assert get.serialize() == expected


def test_get_bookmark_end_list(sample_body):
    bookmark_end = BookmarkEnd(ZOE)
    para = sample_body.get_paragraph()
    para.append(bookmark_end)
    get = sample_body.get_bookmark_ends()[0]
    expected = f'<text:bookmark-end text:name="{ZOE}"/>'
    assert get.serialize() == expected


def test_set_bookmark_simple(sample_body):
    paragraph = sample_body.get_paragraph(position=-1)
    paragraph.set_bookmark("A bookmark")
    bookmark = paragraph.get_bookmark(name="A bookmark")
    assert bookmark is not None


def test_set_bookmark_with_after_without_position():
    paragraph = Paragraph("aa bb aa aa cc aa dd")
    paragraph.set_span(style="style", regex="bb aa aa")
    paragraph.set_span(style="style", regex="dd")
    paragraph.set_bookmark("bookmark", after="aa")
    expected = (
        '<text:p>aa<text:bookmark text:name="bookmark"/> '
        '<text:span text:style-name="style">bb aa aa'
        "</text:span>"
        ' cc aa <text:span text:style-name="style">dd</text:span>'
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_set_bookmark_with_before():
    paragraph = Paragraph("aa bb aa aa cc aa dd")
    paragraph.set_span(style="style", regex="bb aa aa")
    paragraph.set_span(style="style", regex="dd")
    paragraph.set_bookmark("bookmark", before="aa", position=1)
    expected = (
        "<text:p>aa "
        '<text:span text:style-name="style">bb '
        '<text:bookmark text:name="bookmark"/>aa aa'
        "</text:span>"
        ' cc aa <text:span text:style-name="style">dd</text:span>'
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_set_bookmark_with_after():
    paragraph = Paragraph("aa bb aa aa cc aa dd")
    paragraph.set_span(style="style", regex="bb aa aa")
    paragraph.set_span(style="style", regex="dd")
    paragraph.set_bookmark("bookmark", after="aa", position=1)
    expected = (
        "<text:p>aa "
        '<text:span text:style-name="style">bb '
        'aa<text:bookmark text:name="bookmark"/> aa'
        "</text:span>"
        ' cc aa <text:span text:style-name="style">dd</text:span>'
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_set_bookmark_with_position():
    paragraph = Paragraph("aa bb aa aa cc aa dd")
    paragraph.set_span(style="style", regex="bb aa aa")
    paragraph.set_span(style="style", regex="dd")
    paragraph.set_bookmark("bookmark1", position=0)
    paragraph.set_bookmark("bookmark2", position=2)
    paragraph.set_bookmark("bookmark3", position=len("aa bb aa aa cc aa dd"))
    expected = (
        '<text:p><text:bookmark text:name="bookmark1"/>aa'
        '<text:bookmark text:name="bookmark2"/> '
        '<text:span text:style-name="style">bb aa aa</text:span>'
        ' cc aa <text:span text:style-name="style">dd'
        '<text:bookmark text:name="bookmark3"/></text:span>'
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_set_bookmark_with_end():
    paragraph = Paragraph("aa bb aa aa cc aa dd")
    paragraph.set_span(style="style", regex="bb aa aa")
    paragraph.set_span(style="style", regex="dd")
    paragraph.set_bookmark("bookmark1", after="cc", position=-1)
    paragraph.set_bookmark("bookmark2", position=-1)
    expected = (
        "<text:p>aa "
        '<text:span text:style-name="style">'
        "bb aa aa"
        "</text:span>"
        ' cc<text:bookmark text:name="bookmark1"/> aa '
        '<text:span text:style-name="style">dd</text:span>'
        '<text:bookmark text:name="bookmark2"/>'
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_set_bookmark_with_role():
    paragraph = Paragraph("aa")
    paragraph.set_bookmark("bookmark", role="start")
    paragraph.set_bookmark("bookmark", role="end", position=-1)
    expected = (
        "<text:p>"
        '<text:bookmark-start text:name="bookmark"/>'
        "aa"
        '<text:bookmark-end text:name="bookmark"/>'
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_set_bookmark_with_content():
    paragraph = Paragraph("aa bb bb aa")
    paragraph.set_bookmark("bookmark", content="bb", position=1)
    expected = (
        "<text:p>aa bb "
        '<text:bookmark-start text:name="bookmark"/>'
        "bb"
        '<text:bookmark-end text:name="bookmark"/>'
        " aa"
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_set_bookmark_with_content_str():
    paragraph = Paragraph("aa bb bb aa")
    paragraph.set_bookmark("bookmark", content="bb", position=1)
    assert str(paragraph) == "aa bb bb aa\n"


def test_set_bookmark_with_limits():
    paragraph = Paragraph("aa bb bb aa")
    paragraph.set_bookmark("bookmark", position=(6, 8))
    expected = (
        "<text:p>aa bb "
        '<text:bookmark-start text:name="bookmark"/>'
        "bb"
        '<text:bookmark-end text:name="bookmark"/>'
        " aa"
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_repr(sample_body):
    para = sample_body.get_paragraph()
    bookmark = Bookmark(ZOE)
    para.append(bookmark)
    read_book = sample_body.get_bookmark(name=ZOE)
    assert repr(read_book) == "<Bookmark tag=text:bookmark>"


def test_str(sample_body):
    para = sample_body.get_paragraph()
    bookmark = Bookmark(ZOE)
    para.append(bookmark)
    read_book = sample_body.get_bookmark(name=ZOE)
    assert str(read_book) == ""
