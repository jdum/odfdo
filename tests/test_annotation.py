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
from datetime import datetime

import pytest

from odfdo.document import Document
from odfdo.element import Element
from odfdo.note import Annotation, AnnotationEnd
from odfdo.paragraph import Paragraph


@pytest.fixture
def document(samples) -> Iterable[Document]:
    document = Document(samples("note.odt"))
    yield document


def test_get_office_names_0():
    doc = Document()
    assert doc.body.get_office_names() == []


def test_get_office_names_1(document):
    assert document.body.get_office_names() == []


def test_get_office_names_2(document):
    annotation = Annotation(
        "Some annotation",
        creator="John Doe",
        date=datetime(2025, 6, 7, 12, 00, 00),
    )
    document.body.append(annotation)
    assert document.body.get_office_names() == ["__Fieldmark__lpod_1"]


def test_get_office_names_3(document):
    annotation1 = Annotation(
        "Some annotation 1",
        creator="John Doe",
        date=datetime(2025, 6, 7, 12, 00, 00),
        parent=document.body,
    )
    document.body.append(annotation1)
    annotation2 = Annotation(
        "Some annotation 1",
        creator="John Doe",
        date=datetime(2025, 6, 7, 12, 00, 00),
        parent=document.body,
    )
    document.body.append(annotation2)
    assert set(document.body.get_office_names()) == {
        "__Fieldmark__lpod_1",
        "__Fieldmark__lpod_2",
    }


def test_annotation_class():
    annotation = Annotation()
    assert isinstance(annotation, Annotation)


def test_annotation_minimal_tag():
    annotation = Element.from_tag("<office:annotation/>")
    assert isinstance(annotation, Annotation)


def test_annotation_with_name():
    annotation = Annotation(name="some name")
    assert annotation.name == "some name"


def test_annotation_set_dc_creator():
    annotation = Annotation()
    name = "John Doe"
    annotation.dc_creator = name
    assert annotation.dc_creator == name


def test_annotation_set_dc_date():
    annotation = Annotation()
    dt = datetime(2024, 12, 25, 12, 0, 0)
    annotation.dc_date = dt
    assert annotation.dc_date == dt


def test_annotation_set_note_body_str():
    annotation = Annotation()
    content = "Some string content"
    annotation.note_body = content
    assert annotation.note_body == content


def test_annotation_set_note_body_element():
    annotation = Annotation()
    content = Paragraph("Some element content")
    annotation.note_body = content
    assert annotation.note_body == str(content).strip()


def test_annotation_set_note_body_wrong_type():
    annotation = Annotation()
    with pytest.raises(TypeError):
        annotation.note_body = []


def test_annotation_start():
    annotation = Annotation()
    assert annotation.start == annotation


def test_annotation_end():
    annotation = Annotation()
    assert annotation.end is None


def test_annotation_end_minimal():
    annotation = Element.from_tag("<office:annotation/>")
    assert annotation.end is None


def test_annotation_end_when_body(document):
    body = document.body
    annotation = body.get_annotations()[0]
    assert annotation.end is None


def test_annotation_get_annotated_none(document):
    body = document.body
    annotation = body.get_annotations()[0]
    result = annotation.get_annotated()
    assert result is None


def test_annotation_get_annotated_str(document):
    body = document.body
    annotation = body.get_annotations()[0]
    result = annotation.get_annotated(as_text=True)
    assert result == ""


def test_insert_annotation_with_end():
    text = "It's like you're in a cave."
    creator = "Plato"
    date = datetime(2025, 6, 7)
    annotation = Annotation(text, creator=creator, date=date)
    paragraph = Paragraph("Un paragraphe")
    paragraph.insert_annotation(annotation, after="para")
    paragraph.insert_annotation_end(annotation, after="graphe")
    expected = (
        "<text:p>Un para"
        '<office:annotation office:name="__Fieldmark__lpod_1">'
        "<text:p>It's like you're in a cave.</text:p>"
        "<dc:creator>Plato</dc:creator><dc:date>2025-06-07T00:00:00</dc:date>"
        "</office:annotation>"
        "graphe"
        '<office:annotation-end office:name="__Fieldmark__lpod_1"/>'
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_insertget_long_annotated():
    text = "It's like you're in a cave."
    creator = "Plato"
    date = datetime(2025, 6, 7)
    annotation = Annotation(text, creator=creator, date=date)
    paragraph = Paragraph("Un paragraphe")
    paragraph.insert_annotation(annotation, after="para")
    paragraph.insert_annotation_end(annotation, after="graphe")
    result = annotation.get_annotated()
    assert len(result) == 1
    assert isinstance(result[0], Paragraph)


def test_insertget_long_annotated_str():
    text = "It's like you're in a cave."
    creator = "Plato"
    date = datetime(2025, 6, 7)
    annotation = Annotation(text, creator=creator, date=date)
    paragraph = Paragraph("Un paragraphe")
    paragraph.insert_annotation(annotation, after="para")
    paragraph.insert_annotation_end(annotation, after="graphe")
    result = annotation.get_annotated(as_text=True)
    assert result == "graphe\n\n"


def test_insertget_short_delete():
    text = "It's like you're in a cave."
    creator = "Plato"
    date = datetime(2025, 6, 7)
    annotation = Annotation(text, creator=creator, date=date)
    paragraph = Paragraph("Un paragraphe")
    paragraph.insert_annotation(annotation, after="para")
    annotation.delete()
    annotations = paragraph.get_annotations()
    assert annotations == []


def test_insertget_long_delete():
    text = "It's like you're in a cave."
    creator = "Plato"
    date = datetime(2025, 6, 7)
    annotation = Annotation(text, creator=creator, date=date)
    paragraph = Paragraph("Un paragraphe")
    paragraph.insert_annotation(annotation, after="para")
    paragraph.insert_annotation_end(annotation, after="graphe")
    annotation.delete()
    annotations = paragraph.get_annotations()
    assert annotations == []
    annotations_end = paragraph.get_annotation_ends()
    assert annotations_end == []


def test_annotation_check_valid_no_note_body_0():
    annotation = Element.from_tag("<office:annotation/>")
    with pytest.raises(ValueError):
        annotation.check_validity()


def test_annotation_check_valid_no_note_body_1():
    annotation = Annotation()
    with pytest.raises(ValueError):
        annotation.check_validity()


def test_annotation_check_valid_no_dc_creator():
    annotation = Annotation("Some body")
    with pytest.raises(ValueError):
        annotation.check_validity()


def test_annotation_check_valid_no_dc_date():
    annotation = Annotation("Some body", creator="John")
    annotation.dc_date = None
    assert annotation.check_validity() is None


def test_annotation_check_valid_no_dc_date_2():
    annotation = Annotation("Some body", creator="John")
    to_del = annotation.get_element("//dc:date")
    annotation.delete(to_del)
    assert annotation.check_validity() is None


def test_create_annotation():
    # Create
    annotation = Annotation(
        "Lost Dialogs",
        creator="Plato",
        date=datetime(2009, 6, 22, 17, 18, 42),
    )
    expected = (
        '<office:annotation office:name="__Fieldmark__lpod_1">'
        "<text:p>"
        "Lost Dialogs"
        "</text:p>"
        "<dc:creator>Plato</dc:creator>"
        "<dc:date>2009-06-22T17:18:42</dc:date>"
        "</office:annotation>"
    )
    assert annotation.serialize() == expected


def test_create_annotation_str():
    # Create
    annotation = Annotation(
        "Lost Dialogs",
        creator="Plato",
        date=datetime(2009, 6, 22, 17, 18, 42),
    )
    expected = "Lost Dialogs\nPlato 2009-06-22 17:18:42"
    assert str(annotation) == expected


def test_get_annotation_list(document):
    body = document.body
    annotations = body.get_annotations()
    assert len(annotations) == 1
    annotation = annotations[0]
    creator = annotation.dc_creator
    assert creator == "Auteur inconnu"
    date = annotation.dc_date
    assert date == datetime(2009, 8, 3, 12, 9, 45)
    text = annotation.text_content
    expected = "Sauf qu'il est commenté !"
    assert text == expected


def test_get_annotation_list_properties_creator(document):
    body = document.body
    annotations = body.get_annotations()
    annotation = annotations[0]
    creator = annotation.creator
    assert creator == "Auteur inconnu"


def test_get_annotation_list_properties_date(document):
    body = document.body
    annotations = body.get_annotations()
    annotation = annotations[0]
    date = annotation.date
    assert date == datetime(2009, 8, 3, 12, 9, 45)


def test_get_annotation_list_author(document):
    body = document.body
    creator = "Auteur inconnu"
    annotations = body.get_annotations(creator=creator)
    assert len(annotations) == 1


def test_get_annotation_list_bad_author(document):
    body = document.body
    creator = "Plato"
    annotations = body.get_annotations(creator=creator)
    assert len(annotations) == 0


def test_get_annotation_list_start_date(document):
    body = document.body
    start_date = datetime(2009, 8, 1, 0, 0, 0)
    annotations = body.get_annotations(start_date=start_date)
    assert len(annotations) == 1


def test_get_annotation_list_bad_start_date(document):
    body = document.body
    start_date = datetime(2009, 9, 1, 0, 0, 0)
    annotations = body.get_annotations(start_date=start_date)
    assert len(annotations) == 0


def test_get_annotation_list_end_date(document):
    body = document.body
    end_date = datetime(2009, 9, 1, 0, 0, 0)
    annotations = body.get_annotations(end_date=end_date)
    assert len(annotations) == 1


def test_get_annotation_list_bad_end_date(document):
    body = document.body
    end_date = datetime(2009, 8, 1, 0, 0, 0)
    annotations = body.get_annotations(end_date=end_date)
    assert len(annotations) == 0


def test_get_annotation_list_start_date_end_date(document):
    body = document.body
    start_date = datetime(2009, 8, 1, 0, 0, 0)
    end_date = datetime(2009, 9, 1, 0, 0, 0)
    annotations = body.get_annotations(start_date=start_date, end_date=end_date)
    assert len(annotations) == 1


def test_get_annotation_list_bad_start_date_end_date(document):
    body = document.body
    start_date = datetime(2009, 5, 1, 0, 0, 0)
    end_date = datetime(2009, 6, 1, 0, 0, 0)
    annotations = body.get_annotations(start_date=start_date, end_date=end_date)
    assert len(annotations) == 0


def test_get_annotation_list_author_start_date_end_date(document):
    body = document.body
    creator = "Auteur inconnu"
    start_date = datetime(2009, 8, 1, 0, 0, 0)
    end_date = datetime(2009, 9, 1, 0, 0, 0)
    annotations = body.get_annotations(
        creator=creator, start_date=start_date, end_date=end_date
    )
    assert len(annotations) == 1


def test_get_annotation_list_bad_author_start_date_end_date(document):
    body = document.body
    creator = "Plato"
    start_date = datetime(2009, 6, 1, 0, 0, 0)
    end_date = datetime(2009, 7, 1, 0, 0, 0)
    annotations = body.get_annotations(
        creator=creator, start_date=start_date, end_date=end_date
    )
    assert len(annotations) == 0


def test_get_annotation_list_author_bad_start_date_end_date(document):
    body = document.body
    creator = "Auteur inconnu"
    start_date = datetime(2009, 6, 23, 0, 0, 0)
    end_date = datetime(2009, 7, 1, 0, 0, 0)
    annotations = body.get_annotations(
        creator=creator, start_date=start_date, end_date=end_date
    )
    assert len(annotations) == 0


def test_insert_annotation():
    text = "It's like you're in a cave."
    creator = "Plato"
    date = datetime(2009, 8, 19)
    annotation = Annotation(text, creator=creator, date=date)
    paragraph = Paragraph("Un paragraphe")
    paragraph.insert_annotation(annotation, after="para")
    expected = (
        "<text:p>Un para"
        '<office:annotation office:name="__Fieldmark__lpod_1">'
        "<text:p>It's like you're in a cave.</text:p>"
        "<dc:creator>Plato</dc:creator>"
        "<dc:date>2009-08-19T00:00:00</dc:date>"
        "</office:annotation>"
        "graphe</text:p>"
    )
    assert paragraph.serialize() == expected


def test_annotation_end_class():
    with pytest.raises(ValueError):
        AnnotationEnd()


def test_annotation_end_class_1():
    annotation_end = AnnotationEnd(name="some name")
    assert isinstance(annotation_end, AnnotationEnd)


def test_annotation_end_minimal_tag():
    annotation_end = Element.from_tag("<office:annotation-end/>")
    assert isinstance(annotation_end, AnnotationEnd)


def test_annotation_end_from_annotation_start():
    text = "It's like you're in a cave."
    creator = "Plato"
    date = datetime(2025, 6, 7)
    annotation = Annotation(text, creator=creator, date=date)
    paragraph = Paragraph("Un paragraphe")
    paragraph.insert_annotation(annotation, after="para")
    annotation_end = paragraph.insert_annotation_end(annotation, after="graphe")
    assert annotation_end.start.name == annotation.name


def test_annotation_end_from_annotation_end():
    text = "It's like you're in a cave."
    creator = "Plato"
    date = datetime(2025, 6, 7)
    annotation = Annotation(text, creator=creator, date=date)
    paragraph = Paragraph("Un paragraphe")
    paragraph.insert_annotation(annotation, after="para")
    annotation_end = paragraph.insert_annotation_end(annotation, after="graphe")
    assert annotation_end.end == annotation_end
