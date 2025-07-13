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
from textwrap import dedent

import pytest

from odfdo.document import Document
from odfdo.paragraph import Paragraph
from odfdo.mixin_md import (
    _md_swap_spaces,
    _as_bold,
    _as_bold_italic,
    _as_strike,
    MDStyle,
    MDToc,
    MDNote,
    MDZap,
    MDLineBreak,
    MDParagraph,
    MDHeader,
    MDListItem,
    MDList,
    MDSpan,
    MDLink,
    MDDrawTextBox,
    MDDrawFrame,
    _restore_global,
    MDTable,
    SplitSpace,
    _set_global,
    MD_GLOBAL,
    _copy_global,
)


# def test_md_doc_empty():
#     doc = Document("odt")
#     md = doc.to_markdown()
#     assert md == ""


# def test_md_doc_minimal():
#     text = "some text"
#     doc = Document("odt")
#     doc.body.clear()
#     doc.body.append(Paragraph(text))
#     md = doc.to_markdown()
#     assert md.strip() == text


def test_md_swap_spaces_empty():
    word = ""
    assert _md_swap_spaces(word) == SplitSpace("", "", "")


def test_set_global():
    doc = "any"
    _set_global(doc)
    assert MD_GLOBAL["document"] == doc
    assert MD_GLOBAL["list_level"] == {}
    assert MD_GLOBAL["footnote"] == []
    assert MD_GLOBAL["endnote"] == []


def test_copy_global():
    doc = "any"
    _set_global(doc)
    glob_copy = _copy_global()
    assert glob_copy["document"] == "any"
    _set_global("other")
    assert glob_copy["document"] == "any"


def test_restore_global():
    data = {"document": "initial"}
    doc = "any"
    _set_global(doc)
    _restore_global(data)
    assert MD_GLOBAL["document"] == "initial"
