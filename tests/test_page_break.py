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
from odfdo.paragraph import PageBreak, Paragraph
from odfdo.style import Style


@pytest.fixture
def document(samples) -> Iterable[Document]:
    yield Document(samples("pagebreak.odt"))


def test_add_style_page_break():
    document = Document("text")
    document.add_page_break_style()
    result = document.get_style("paragraph", "odfdopagebreak")
    assert isinstance(result, Style)
    assert result.get_properties()["fo:break-after"] == "page"


def test_add_style_page_break_twice():
    document = Document("text")
    document.add_page_break_style()
    document.add_page_break_style()
    result = document.get_style("paragraph", "odfdopagebreak")
    assert isinstance(result, Style)
    assert result.get_properties()["fo:break-after"] == "page"


def test_break_page_is_paragraph():
    page_break = PageBreak()
    assert isinstance(page_break, Paragraph)


def test_break_str():
    page_break = PageBreak()
    assert str(page_break) == "\n"


def test_break_page_as_style():
    page_break = PageBreak()
    assert page_break.style == "odfdopagebreak"


def test_style_stay_in_doc(document):
    result = document.get_style("paragraph", "odfdopagebreak")
    assert isinstance(result, Style)
    assert result.get_properties()["fo:break-after"] == "page"
