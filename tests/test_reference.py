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
from odfdo.reference import ReferenceMark, ReferenceMarkEnd, ReferenceMarkStart

ZOE = "你好 Zoé"


@pytest.fixture
def body1(samples) -> Iterable[Element]:
    document = Document(samples("bookmark.odt")).clone
    yield document.body


@pytest.fixture
def body2(samples) -> Iterable[Element]:
    document = Document(samples("base_text.odt")).clone
    yield document.body


def test_create_reference_mark():
    reference_mark = ReferenceMark(ZOE)
    expected = f'<text:reference-mark text:name="{ZOE}"/>'
    assert reference_mark.serialize() == expected


def test_create_reference_mark_str():
    reference_mark = ReferenceMark(ZOE)
    assert str(reference_mark) == ""


def test_create_reference_mark_start():
    reference_mark_start = ReferenceMarkStart(ZOE)
    expected = f'<text:reference-mark-start text:name="{ZOE}"/>'
    assert reference_mark_start.serialize() == expected


def test_create_reference_mark_end():
    reference_mark_end = ReferenceMarkEnd(ZOE)
    expected = f'<text:reference-mark-end text:name="{ZOE}"/>'
    assert reference_mark_end.serialize() == expected


def test_get_reference_mark_single(body1):
    para = body1.get_paragraph()
    reference_mark = ReferenceMark(ZOE)
    para.append(reference_mark)
    get = body1.get_reference_mark_single(name=ZOE)
    expected = f'<text:reference-mark text:name="{ZOE}"/>'
    assert get.serialize() == expected


def test_get_reference_mark_single_list(body1):
    para = body1.get_paragraph()
    reference_mark = ReferenceMark(ZOE)
    para.append(reference_mark)
    get = body1.get_reference_marks_single()[0]
    expected = f'<text:reference-mark text:name="{ZOE}"/>'
    assert get.serialize() == expected


def test_get_reference_mark_start(body1):
    para = body1.get_paragraph()
    reference_mark_start = ReferenceMarkStart(ZOE)
    para.append(reference_mark_start)
    get = body1.get_reference_mark_start(name=ZOE)
    expected = f'<text:reference-mark-start text:name="{ZOE}"/>'
    assert get.serialize() == expected


def test_get_reference_mark_start_list(body1):
    result = body1.get_reference_mark_starts()
    assert len(result) == 1
    element = result[0]
    expected = '<text:reference-mark-start text:name="Nouvelle référence"/>'
    assert element.serialize() == expected


def test_get_reference_mark_end(body1):
    para = body1.get_paragraph()
    reference_mark_end = ReferenceMarkEnd(ZOE)
    para.append(reference_mark_end)
    get = body1.get_reference_mark_end(name=ZOE)
    expected = f'<text:reference-mark-end text:name="{ZOE}"/>'
    assert get.serialize() == expected


def test_get_reference_mark_end_list(body1):
    result = body1.get_reference_mark_ends()
    assert len(result) == 1
    element = result[0]
    expected = '<text:reference-mark-end text:name="Nouvelle référence"/>'
    assert element.serialize() == expected


def test_get_referenced_1_odf(body2):
    para = body2.get_paragraph(content="of the second title")
    para.set_reference_mark("one", content="paragraph of the second title")
    ref = body2.get_reference_mark(name="one")
    referenced = ref.get_referenced()
    expected = (
        '<office:text><text:p text:style-name="Text_20_body">'
        "paragraph of the second title</text:p></office:text>"
    )
    assert referenced.serialize() == expected


def test_get_referenced_1_xml(body2):
    para = body2.get_paragraph(content="of the second title")
    para.set_reference_mark("one", content="paragraph of the second title")
    ref = body2.get_reference_mark(name="one")
    referenced = ref.get_referenced(as_xml=True)
    expected = (
        '<office:text><text:p text:style-name="Text_20_body">'
        "paragraph of the second title</text:p></office:text>"
    )
    assert referenced == expected


def test_get_referenced_1_list(body2):
    para = body2.get_paragraph(content="of the second title")
    para.set_reference_mark("one", content="paragraph of the second title")
    ref = body2.get_reference_mark(name="one")
    referenced = ref.get_referenced(as_list=True)
    assert isinstance(referenced, list)
    assert len(referenced) == 1
    expected = (
        '<text:p text:style-name="Text_20_body">paragraph of the second title</text:p>'
    )
    assert referenced[0].serialize() == expected


def test_get_referenced_multi_odf(body2):
    para = body2.get_paragraph(content="of the second title")
    para.set_reference_mark("one", content=para)
    para.set_reference_mark("two", position=(0, 7))
    ref = body2.get_reference_mark(name="two")
    referenced = ref.get_referenced()
    expected = (
        "<office:text>"
        '<text:p text:style-name="Text_20_body">'
        "This is"
        "</text:p></office:text>"
    )
    assert referenced.serialize() == expected


def test_get_referenced_multi_xml_dirty(body2):
    para = body2.get_paragraph(content="of the second title")
    para.set_reference_mark("one", content=para)
    para.set_reference_mark("two", position=(0, 7))
    ref = body2.get_reference_mark(name="one")
    referenced = ref.get_referenced(as_xml=True, clean=False)
    expected = (
        "<office:text>"
        '<text:p text:style-name="Text_20_body">'
        '<text:reference-mark-start text:name="two"/>'
        'This is<text:reference-mark-end text:name="two"/>'
        " the first paragraph of the second title."
        "</text:p>"
        "</office:text>"
    )
    assert referenced == expected


def test_get_referenced_multi_xml_clean(body2):
    para = body2.get_paragraph(content="of the second title")
    para.set_reference_mark("one", content=para)
    para.set_reference_mark("two", position=(0, 7))
    ref = body2.get_reference_mark(name="one")
    referenced = ref.get_referenced(as_xml=True, clean=True)
    expected = (
        "<office:text>"
        '<text:p text:style-name="Text_20_body">'
        "This is"
        " the first paragraph of the second title."
        "</text:p>"
        "</office:text>"
    )
    assert referenced == expected


def test_get_referenced_mix_xml(body2):
    para = body2.get_paragraph()
    para.set_reference_mark("one", content="first paragraph.")
    para.set_reference_mark("two", position=(0, 17))
    ref = body2.get_reference_mark(name="two")
    referenced = ref.get_referenced(as_xml=True)
    expected = (
        "<office:text>"
        '<text:p text:style-name="Text_20_body">'
        "This is the first"
        "</text:p>"
        "</office:text>"
    )
    assert referenced == expected


def test_get_referenced_header(body2):
    head = body2.get_header()
    head.set_reference_mark("one", content=head)
    ref = body2.get_reference_mark(name="one")
    referenced = ref.get_referenced(as_xml=True)
    expected = (
        "<office:text>"
        '<text:h text:style-name="Heading_20_1" '
        'text:outline-level="1">'
        '<text:span text:style-name="T1">'
        "odfdo"
        "</text:span>"
        " Test Case Document"
        "</text:h>"
        "</office:text>"
    )
    assert referenced == expected


def test_get_referenced_no_header(body2):
    head = body2.get_header()
    head.set_reference_mark("one", content=head)
    ref = body2.get_reference_mark(name="one")
    referenced = ref.get_referenced(as_xml=True, no_header=True)
    expected = (
        "<office:text><text:p>"
        '<text:span text:style-name="T1">'
        "odfdo"
        "</text:span> "
        "Test Case Document"
        "</text:p>"
        "</office:text>"
    )
    assert referenced == expected
