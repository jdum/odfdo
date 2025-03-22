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
# Authors: David Versmisse <david.versmisse@itaapy.com>

from collections.abc import Iterable

import pytest

from odfdo.document import Document
from odfdo.toc import TOC

SAMPLE_EXPECTED = [
    "Table des matières",
    "1. Level 1 title 1",
    "1.1. Level 2 title 1",
    "2. Level 1 title 2",
    "2.1.1. Level 3 title 1",
    "2.2. Level 2 title 2",
    "3. Level 1 title 3",
    "3.1. Level 2 title 1",
    "3.1.1. Level 3 title 1",
    "3.1.2. Level 3 title 2",
    "3.2. Level 2 title 2",
    "3.2.1. Level 3 title 1",
    "3.2.2. Level 3 title 2",
]


@pytest.fixture
def sample(samples) -> Iterable[Document]:
    document = Document(samples("toc.odt"))
    yield document


@pytest.fixture
def sample_toc(samples) -> Iterable[Document]:
    document = Document(samples("toc_done.odt"))
    yield document


def get_toc_lines(toc):
    return [paragraph.text for paragraph in toc.paragraphs]


def test_get_tocs(sample_toc):
    tocs = sample_toc.body.get_tocs()
    assert len(tocs) == 1
    assert isinstance(tocs[0], TOC)


def test_get_tocs_empty(sample):
    tocs = sample.body.get_tocs()
    assert len(tocs) == 0


def test_get_tocs_property(sample_toc):
    tocs = sample_toc.body.tocs
    assert len(tocs) == 1
    assert isinstance(tocs[0], TOC)


def test_get_toc(sample_toc):
    toc = sample_toc.body.get_toc()
    assert isinstance(toc, TOC)


def test_get_toc_property(sample_toc):
    toc = sample_toc.body.toc
    assert isinstance(toc, TOC)


def test_toc_fill_unattached():
    toc = TOC("Table des matières")
    with pytest.raises(ValueError):
        toc.fill()


def test_toc_fill_unattached_document(sample):
    toc = TOC("Table des matières")
    toc.fill(sample)
    toc_lines = get_toc_lines(toc)
    assert toc_lines == SAMPLE_EXPECTED


def test_toc_fill_attached(sample):
    document = sample.clone
    toc = TOC("Table des matières")
    document.body.append(toc)
    toc.fill()
    toc_lines = get_toc_lines(toc)
    assert toc_lines == SAMPLE_EXPECTED


def test_repr_empty():
    toc = TOC("Table des matières")
    assert repr(toc) == "<TOC tag=text:table-of-content>"


def test_str_empty():
    toc = TOC("Table des matières")
    assert "Table des matières" in str(toc)


def test_repr(sample):
    toc = TOC("Table des matières")
    toc.fill(sample)
    assert repr(toc) == "<TOC tag=text:table-of-content>"


def test_str(sample):
    toc = TOC("Table des matières")
    toc.fill(sample)
    result = str(toc)
    for line in SAMPLE_EXPECTED:
        assert line in result
