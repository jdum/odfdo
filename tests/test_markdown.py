# Copyright 2018-2024 Jérôme Dumonteil
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
from pathlib import Path
from textwrap import dedent

import pytest

from odfdo.document import Document
from odfdo.paragraph import Paragraph

SAMPLE_BT = Path(__file__).parent / "samples" / "base_text.odt"
SAMPLE_EX = Path(__file__).parent / "samples" / "example.odt"
SAMPLE_BOOK = Path(__file__).parent / "samples" / "bookmark.odt"
SAMPLE_I28 = Path(__file__).parent / "samples" / "issue_28_pretty.odt"
SAMPLE_LIST = Path(__file__).parent / "samples" / "list.odt"
SAMPLE_META = Path(__file__).parent / "samples" / "meta.odt"
SAMPLE_NOTE = Path(__file__).parent / "samples" / "note.odt"
SAMPLE_PB = Path(__file__).parent / "samples" / "pagebreak.odt"
SAMPLE_TOC2 = Path(__file__).parent / "samples" / "toc_done.odt"  # FAIL
SAMPLE_TOC = Path(__file__).parent / "samples" / "toc.odt"
SAMPLE_TC = Path(__file__).parent / "samples" / "tracked_changes.odt"  # TODO
SAMPLE_UF = Path(__file__).parent / "samples" / "user_fields.odt"
SAMPLE_VAR = Path(__file__).parent / "samples" / "variable.odt"
SAMPLE_BIG = Path(__file__).parent / "samples" / "base_md_text.odt"


@pytest.fixture
def document_base() -> Iterable[Document]:
    document = Document(SAMPLE_BT)
    yield document


@pytest.fixture
def document_example() -> Iterable[Document]:
    document = Document(SAMPLE_EX)
    yield document


@pytest.fixture
def document_bookmark() -> Iterable[Document]:
    document = Document(SAMPLE_BOOK)
    yield document


@pytest.fixture
def document_i28() -> Iterable[Document]:
    document = Document(SAMPLE_I28)
    yield document


@pytest.fixture
def document_list() -> Iterable[Document]:
    document = Document(SAMPLE_LIST)
    yield document


@pytest.fixture
def document_meta() -> Iterable[Document]:
    document = Document(SAMPLE_META)
    yield document


@pytest.fixture
def document_note() -> Iterable[Document]:
    document = Document(SAMPLE_NOTE)
    yield document


@pytest.fixture
def document_pb() -> Iterable[Document]:
    document = Document(SAMPLE_PB)
    yield document


@pytest.fixture
def document_toc2() -> Iterable[Document]:
    document = Document(SAMPLE_TOC2)
    yield document


@pytest.fixture
def document_toc() -> Iterable[Document]:
    document = Document(SAMPLE_TOC)
    yield document


@pytest.fixture
def document_tc() -> Iterable[Document]:
    document = Document(SAMPLE_TC)
    yield document


@pytest.fixture
def document_uf() -> Iterable[Document]:
    document = Document(SAMPLE_UF)
    yield document


@pytest.fixture
def document_var() -> Iterable[Document]:
    document = Document(SAMPLE_VAR)
    yield document


@pytest.fixture
def document_big() -> Iterable[Document]:
    document = Document(SAMPLE_BIG)
    yield document


def test_md_doc_ods():
    doc = Document("ods")
    with pytest.raises(NotImplementedError):
        _md = doc.to_markdown()


def test_md_doc_drawing():
    doc = Document("drawing")
    with pytest.raises(NotImplementedError):
        _md = doc.to_markdown()


def test_md_doc_empty():
    doc = Document("odt")
    md = doc.to_markdown()
    assert md == ""


def test_md_doc_minimal():
    text = "some text"
    doc = Document("odt")
    doc.body.clear()
    doc.body.append(Paragraph(text))
    md = doc.to_markdown()
    assert md.strip() == text


def test_md_base_text(document_base):
    md = document_base.to_markdown()
    expected = dedent(
        """\
    # odfdo Test Case Document

    This is the first paragraph.

    This is the second paragraph.

    This is a paragraph with a named style.

    ## Level 2 Title

    This is the first paragraph of the second title.

    This is the last paragraph with diacritical signs: éè

    # First Title of the Second Section

    First paragraph of the second section.

    This is the second paragraph with [an external link](https://github.com/jdum/odfdo) inside.
    """
    ).strip()
    assert md.strip() == expected


def test_md_example_text(document_example):
    md = document_example.to_markdown()
    expected = dedent(
        """\
    # odfdo Test Case Document

    This is the first paragraph.

    This is the second paragraph.

    This is a paragraph with a named style.

    ## Level 2 Title

    This is the first paragraph of the second title.

    This is the last paragraph with diacritical signs: éè

    # First Title of the Second Section

    First paragraph of the second section.
    """
    ).strip()
    # First paragraphAuteur inconnu2009-06-22T17:18:42This is an annotation.With diacritical signs: éè
    assert md.strip() == expected


def test_md_bookmark_text(document_bookmark):
    md = document_bookmark.to_markdown()
    expected = "Lettre à Élise (cf. page 1)."
    # First paragraphAuteur inconnu2009-06-22T17:18:42This is an annotation.With diacritical signs: éè
    assert md.strip() == expected


def test_md_i28_text(document_i28):
    md = document_i28.to_markdown()
    expected = (
        "This is an example with => v8.1.4 <= spaces after "
        "reading and writing with odfdo."
    )
    # First paragraphAuteur inconnu2009-06-22T17:18:42This is an annotation.With diacritical signs: éè
    assert md.strip() == expected


def test_md_list_text(document_list):
    md = document_list.to_markdown()
    expected = dedent(
        """\
        Some text

          - une liste accentuée
            - un sous-élément

          - une liste numérotée
          - et de deux !
    """
    ).strip()
    # First paragraphAuteur inconnu2009-06-22T17:18:42This is an annotation.With diacritical signs: éè
    assert md.strip() == expected


def test_md_meta_text(document_meta):
    md = document_meta.to_markdown()
    expected = "Only testing meta.xml here…"
    assert md.strip() == expected


def test_md_note_text(document_note):
    md = document_note.to_markdown()
    expected = "Un paragraphe d'apparence banale."
    # First paragraphAuteur inconnu2009-06-22T17:18:42This is an annotation.With diacritical signs: éè
    assert md.strip() == expected


def test_md_pagebreak_text(document_pb):
    md = document_pb.to_markdown()
    expected = dedent(
        """\
    first paragraph

    second paragraph
    """
    ).strip()
    assert md.strip() == expected


def test_md_toc_text(document_toc):
    md = document_toc.to_markdown()
    expected = dedent(
        """\
    # Level 1 title 1

    ## Level 2 title 1

    # Level 1 title 2

    ### Level 3 title 1

    ## Level 2 title 2

    # Level 1 title 3

    ## Level 2 title 1

    ### Level 3 title 1

    ### Level 3 title 2

    ## Level 2 title 2

    ### Level 3 title 1

    ### Level 3 title 2

    """
    ).strip()
    assert md.strip() == expected


# def test_md_toc_done_text(document_toc2):  # FAIL
#     md = document_toc2.to_markdown()
#     expected = dedent(
#         """\
#         xxx
#     """
#     ).strip()
#     assert md.strip() == expected


def test_user_fields_text(document_uf):
    md = document_uf.to_markdown()
    expected = dedent(
        """\
    A document with user-field declarations.

    Paris

    77 77 77 77 77

    42
    """
    ).strip()
    assert md.strip() == expected


def test_md_variable_text(document_var):  # FAIL
    md = document_var.to_markdown()
    expected = dedent(
        """\
    Today is 12/08/09 15:17:27.

    This document is named Intitulé.

    This is page 1 out of 1.

    Reference to page 1.

    Declaring variable 123.

    Inserting variable 123.

    Inserting a user field VRAI.
    """
    ).strip()
    assert md.strip() == expected


def test_md_big_text(document_big):  # FAIL
    md = document_big.to_markdown()
    expected = dedent(
        """\
        # odfdo Test Case Document

        This is the first paragraph with a link: [the odfdo project](https://github.com/jdum/odfdo).

        This is the second paragraph.

        This is a paragraph with a named style.

        Some list :

          - item1
          - item2
          - item3
            - sub item a
            - sub item (with link: [odfdo b link](https://github.com/jdum/odfdo)) b
            - sub item c
          - item4

        last paragraph

        ## Level 2 Title with [odfdo project again](https://github.com/jdum/odfdo) embeded

        This is the first paragraph of the second title.

        This is the last paragraph with diacritical signs: éè

        # First Title of the Second Section

        First paragraph of the second section.
    """
    ).strip()
    print(md.strip())
    assert md.strip() == expected
