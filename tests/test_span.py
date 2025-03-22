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
from odfdo.document import Document
from odfdo.paragraph import Span


@pytest.fixture
def body(samples) -> Iterable[Element]:
    document = Document(samples("span_style.odt"))
    yield document.body


def test_create_span():
    span = Span("my text", style="my_style")
    expected = '<text:span text:style-name="my_style">my text</text:span>'
    assert span.serialize() == expected


def test_create_span_naive_spaces():
    span = Span("my text   ", style="my_style")
    expected = (
        '<text:span text:style-name="my_style">my text<text:s text:c="3"/></text:span>'
    )
    assert span.serialize() == expected


def test_create_span_naive_spaces_no_format():
    span = Span("my text   ", style="my_style", formatted=False)
    expected = '<text:span text:style-name="my_style">my text </text:span>'
    assert span.serialize() == expected


def test_get_span_list(body):
    result = body.get_spans()
    assert len(result) == 2
    element = result[0]
    expected = '<text:span text:style-name="T1">moustache</text:span>'
    assert element.serialize() == expected


def test_get_span_list_property(body):
    result = body.spans
    assert len(result) == 2
    element = result[0]
    expected = '<text:span text:style-name="T1">moustache</text:span>'
    assert element.serialize() == expected


def test_get_span_list_style(body):
    result = body.get_spans(style="T2")
    assert len(result) == 1
    element = result[0]
    expected = '<text:span text:style-name="T2">rouge</text:span>'
    assert element.serialize() == expected


def test_get_span(body):
    span = body.get_span(position=1)
    expected = '<text:span text:style-name="T2">rouge</text:span>'
    assert span.serialize() == expected


def test_get_span_str(body):
    span = body.get_span(position=1)
    assert str(span) == "rouge"


def test_insert_span(body):
    span = Span("my text", "my_style")
    paragraph = body.get_paragraph(position=0)
    paragraph.append(span)
    read_span = paragraph.get_span(position=-1)
    assert read_span.serialize() == span.serialize()


def test_insert_span_line_break(body):
    span = Span("my text\nmultiline", "my_style")
    paragraph = body.get_paragraph(position=0)
    paragraph.append(span)
    read_span = paragraph.get_span(position=-1)
    assert read_span.serialize() == span.serialize()
    assert "text:line-break" in read_span.serialize()
    assert read_span.inner_text == "my text\nmultiline"


def test_insert_span_line_break_no_format(body):
    span = Span("my text\nmultiline", "my_style", formatted=False)
    paragraph = body.get_paragraph(position=0)
    paragraph.append(span)
    read_span = paragraph.get_span(position=-1)
    assert read_span.serialize() == span.serialize()
    assert "text:line-break" not in read_span.serialize()
    assert read_span.inner_text == "my text multiline"
