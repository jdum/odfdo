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
from odfdo.reference import (
    Reference,
    ReferenceMark,
    ReferenceMarkEnd,
    ReferenceMarkStart,
    remove_all_reference_marks,
    remove_reference_mark,
    strip_references,
)

ZOE = "你好 Zoé"


@pytest.fixture
def body1(samples) -> Iterable[Element]:
    document = Document(samples("bookmark.odt")).clone
    yield document.body


@pytest.fixture
def body2(samples) -> Iterable[Element]:
    document = Document(samples("base_text.odt")).clone
    yield document.body


def test_reference_class():
    ref = Reference()
    assert isinstance(ref, Reference)


def test_reference_args():
    ref = Reference(name="refname", ref_format="chapter")
    assert ref.name == "refname"
    assert ref.ref_format == "chapter"


def test_reference_args_default():
    ref = Reference(name="refname")
    assert ref.ref_format == "page"


def test_reference_args_default_none():
    # incomplete content:
    ref = Element.from_tag("<text:reference-ref/>")
    assert isinstance(ref, Reference)
    assert ref.ref_format is None


def test_reference_update(body1):
    marks = body1.get_reference_mark_starts()
    mark = marks[0]
    ref_name = mark.name
    ref = Reference(name=ref_name, ref_format="text")
    body1.append(ref)  # required
    mark_start = body1.get_reference_mark(name=ref_name)
    # same mark as before
    assert isinstance(mark_start, ReferenceMarkStart)
    ref_text = mark_start.referenced_text()
    expected = "Élise"
    assert ref_text == expected
    assert ref.text == ""
    ref.update()
    assert ref.text == expected


def test_reference_update_not(body1):
    marks = body1.get_reference_mark_starts()
    mark = marks[0]
    ref_name = mark.name
    ref = Reference(name=ref_name, ref_format="page")
    body1.append(ref)  # required
    mark_start = body1.get_reference_mark(name=ref_name)
    # same mark as before
    assert isinstance(mark_start, ReferenceMarkStart)
    ref_text = mark_start.referenced_text()
    expected = "Élise"
    assert ref_text == expected
    assert ref.text == ""
    ref.update()
    # only update for 'text' format
    assert ref.text == ""


def test_reference_update_not_bad(body1):
    ref_name = "bad name"
    ref = Reference(name=ref_name, ref_format="text")
    body1.append(ref)  # required
    mark_start = body1.get_reference_mark(name=ref_name)
    # same mark as before
    assert mark_start is None
    assert ref.text == ""
    ref.update()
    assert ref.text == ""


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


def test_get_reference_mark_end_referenced(body1):
    para = body1.get_paragraph()
    reference_mark_end = ReferenceMarkEnd(ZOE)
    para.append(reference_mark_end)
    ref_end = body1.get_reference_mark_end(name=ZOE)
    assert ref_end.referenced_text() == ""


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


def test_get_referenced_empty():
    ref = ReferenceMarkStart()
    with pytest.raises(ValueError):
        ref.get_referenced()


def test_reference_delete(body2):
    head = body2.get_header()
    head.set_reference_mark("one", content=head)
    ref = body2.get_reference_mark(name="one")
    ref.delete()
    ref2 = body2.get_reference_mark(name="one")
    assert ref2 is None


def test_strip_references(body1):
    marks = body1.get_reference_mark_starts()
    mark = marks[0]
    ref_name = mark.name
    ref = Reference(name=ref_name, ref_format="text")
    body1.append(ref)
    refs = body1.get_references()
    assert len(refs) == 1
    strip_references(body1)
    assert not body1.get_references()


def test_remove_all_reference_marks(body1):
    marks = body1.get_reference_mark_starts()
    assert len(marks) == 1
    remove_all_reference_marks(body1)
    assert not body1.get_reference_mark_starts()


def test_remove_reference_mark_1(body1):
    remove_reference_mark(body1, 0)
    assert not body1.get_reference_mark_starts()


def test_remove_reference_mark_2(body1):
    remove_reference_mark(body1, name="Nouvelle référence")
    assert not body1.get_reference_mark_starts()


def test_remove_reference_mark_3(body1):
    remove_reference_mark(body1, name="wrong")
    assert len(body1.get_reference_mark_starts()) == 1
