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

from odfdo.element import Element, EText


@pytest.fixture
def results() -> Iterable[Element]:
    element = Element.from_tag("<text:p>text<text:span/>tail</text:p>")
    yield element.xpath("descendant::text()")


def test_nodes(results):
    assert len(results) == 2


def test_type(results):
    assert isinstance(results[0], EText)


def test_text(results):
    text = results[0]
    assert text == "text"
    assert text.is_text() is True
    assert text.is_tail() is False


def test_tail(results):
    tail = results[1]
    assert tail == "tail"
    assert tail.is_text() is False
    assert tail.is_tail() is True


def test_text_parent(results):
    text = results[0]
    assert text.parent.tag == "text:p"


def test_tail_parent(results):
    tail = results[1]
    assert tail.parent.tag == "text:span"
