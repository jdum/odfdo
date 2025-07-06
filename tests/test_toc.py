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
from odfdo.element import Element
from odfdo.style import Style
from odfdo.toc import TOC, IndexTitle, TabStopStyle

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


def test_index_title_class():
    title = IndexTitle()
    assert isinstance(title, IndexTitle)


def test_index_title_style():
    title = IndexTitle(style="Standard", xml_id="abc")
    assert isinstance(title, IndexTitle)


def test_tab_stop_style_class():
    element = TabStopStyle()
    assert isinstance(element, TabStopStyle)


def test_tab_stop_style_class_from_tag():
    element = Element.from_tag("<style:tab-stop/>")
    assert isinstance(element, Style)


def test_tab_stop_style_argsg():
    element = TabStopStyle(
        style_type="right",
        leader_style="dotted",
        leader_text=".",
        style_char="Standard",
        leader_color="#000",
        leader_text_style="dotted",
        leader_type="Standard",
        leader_width="1cm",
        style_position="default",
    )
    assert isinstance(element, TabStopStyle)


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


def test_toc_args():
    toc = TOC(
        title="Table des matières", name="table", style="Standard", protected=False
    )
    assert "Table des matières" in str(toc)


def test_toc_no_title_bad_args():
    toc = TOC(title="")
    assert "Table des matières" not in str(toc)


def test_toc_create_toc_source_args():
    element = TOC.create_toc_source(
        title="title",
        outline_level=2,
        title_style="Standard",
        entry_style="Standard_%s",
    )
    assert str(element) == "title"


def test_toc_create_toc_source_bad_args():
    element = TOC.create_toc_source(
        title="title",
        outline_level=2,
        title_style="",
        entry_style="",
    )
    assert str(element) == "title"


def test_get_formatted_text(sample):
    toc = TOC("Table des matières")
    toc.fill(sample)
    result = toc.get_formatted_text()
    assert result.startswith("Table des matières\n1. Level 1")


def test_get_formatted_text_ctx(sample):
    toc = TOC("Table des matières")
    toc.fill(sample)
    ctx = {"rst_mode": True}
    result = toc.get_formatted_text(ctx)
    assert result == "\n.. contents::\n\n"


def test_outline_level():
    toc = TOC("Table des matières")
    result = toc.outline_level
    assert result == 0


def test_outline_level_no_source():
    toc = TOC("Table des matières")
    source = toc.get_element("text:table-of-content-source")
    source.delete()
    result = toc.outline_level
    assert result is None


def test_set_outline_level():
    toc = TOC("Table des matières")
    toc.outline_level = 2
    result = toc.outline_level
    assert result == 2


def test_set_outline_level_no_source():
    toc = TOC("Table des matières")
    source = toc.get_element("text:table-of-content-source")
    source.delete()
    toc.outline_level = 2
    result = toc.outline_level
    assert result == 2


def test_set_some_body():
    toc = TOC("Table des matières")
    toc.body = Element.from_tag("text:index-body")
    assert toc.body.serialize() == "<text:index-body/>"


def test_set_none_body():
    toc = TOC("Table des matières")
    toc.body = None
    assert toc.body.serialize() == "<text:index-body/>"


def test_set_toc_title_1():
    toc = TOC("Table des matières")
    source = toc.get_element("text:table-of-content-source")
    source.delete()
    toc.set_toc_title("new title")
    assert str(toc).startswith("new title")


def test_set_toc_title_2():
    toc = TOC("Table des matières")
    toc.set_toc_title("new title")
    assert str(toc).startswith("new title")


def test_set_toc_title_3():
    toc = TOC("Table des matières")
    toc.set_toc_title("new title", style="Standard")
    assert str(toc).startswith("new title")


def test_set_toc_title_4():
    toc = TOC("Table des matières")
    index_title = toc.body.get_element(IndexTitle._tag)
    index_title.clear()
    toc.set_toc_title("new title", style="Standard")
    assert str(toc).startswith("new title")


def test_set_toc_title_5():
    toc = TOC("Table des matières")
    index_title = toc.body.get_element(IndexTitle._tag)
    index_title.clear()
    toc.set_toc_title(
        "new title",
        style="Standard",
        text_style="Standard",
    )
    assert str(toc).startswith("new title")


def test_get_title_1():
    toc = TOC("Table des matières")
    result = toc.get_title()
    assert result == "Table des matières"


def test_get_title_2():
    toc = TOC("Table des matières")
    toc.body.delete()
    result = toc.get_title()
    assert result == ""


def test_get_title_3():
    toc = TOC("Table des matières")
    index_title = toc.body.get_element(IndexTitle._tag)
    index_title.delete()
    result = toc.get_title()
    assert result == ""
