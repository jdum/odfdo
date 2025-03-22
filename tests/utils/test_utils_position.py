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
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>

from collections.abc import Iterable

import pytest

from odfdo.document import Document
from odfdo.element import Element


@pytest.fixture
def body(samples) -> Iterable[Element]:
    document = Document(samples("example.odt"))
    yield document.body


def test_first(body):
    last_paragraph = body.get_paragraph(position=0)
    expected = "This is the first paragraph."
    assert last_paragraph.inner_text == expected


def test_next_to_last(body):
    last_paragraph = body.get_paragraph(position=-2)
    expected = "This is an annotation."
    assert last_paragraph.inner_text == expected


def test_last(body):
    last_paragraph = body.get_paragraph(position=-1)
    expected = "With diacritical signs: éè"
    assert last_paragraph.inner_text == expected
