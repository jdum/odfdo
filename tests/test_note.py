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
from odfdo.list import List
from odfdo.note import Note
from odfdo.paragraph import Paragraph


@pytest.fixture
def document(samples) -> Iterable[Document]:
    document = Document(samples("note.odt"))
    yield document


def test_note_class():
    note = Note()
    assert isinstance(note, Note)


def test_note_minimal_tag():
    note = Element.from_tag('<text:note text:note-class="footnote"/>')
    assert isinstance(note, Note)


def test_note_empty_citation():
    note = Note()
    assert note.citation == ""


def test_note_empty_citation_without_tag():
    note = Element.from_tag('<text:note text:note-class="footnote"/>')
    assert note.citation == ""


def test_note_empty_citation_without_tag_setter_inactif():
    note = Element.from_tag('<text:note text:note-class="footnote"/>')
    note.citation = "no place to store this"
    assert note.citation == ""


def test_note_empty_body():
    note = Note()
    assert note.note_body == ""


def test_note_empty_body_without_tag():
    note = Element.from_tag('<text:note text:note-class="footnote"/>')
    assert note.note_body == ""


def test_note_empty_body_without_tag_setter_inactif():
    note = Element.from_tag('<text:note text:note-class="footnote"/>')
    note.note_body = "no place to store this"
    assert note.note_body == ""


def test_note_body_setter():
    note = Note()
    note.note_body = "initial"
    assert note.note_body == "initial"
    note.note_body = None
    assert note.note_body == ""


def test_note_body_setter_element():
    content = Paragraph("content")
    note = Note()
    note.note_body = "initial"
    assert note.note_body == "initial"
    note.note_body = content
    assert str(note.note_body) == "content"


def test_note_body_setter_wrong_type():
    note = Note()
    with pytest.raises(TypeError):
        note.note_body = []


def test_note_check_valid_no_class_0():
    note = Element.from_tag("<text:note/>")
    with pytest.raises(ValueError):
        note.check_validity()


def test_note_check_valid_no_class_1():
    note = Element.from_tag('<text:note text:note-class=""/>')
    with pytest.raises(ValueError):
        note.check_validity()


def test_note_check_valid_no_class_2():
    note = Element.from_tag('<text:note text:note-class="wrong"/>')
    with pytest.raises(ValueError):
        note.check_validity()


def test_note_check_valid_no_id_0():
    note = Element.from_tag('<text:note text:note-class="footnote"/>')
    with pytest.raises(ValueError):
        note.check_validity()


def test_note_check_valid_no_id_1():
    note = Element.from_tag('<text:note text:note-class="footnote"  text:id=""/>')
    with pytest.raises(ValueError):
        note.check_validity()


def test_note_check_valid_no_citation_0():
    note = Element.from_tag('<text:note text:note-class="footnote" text:id="note1"/>')
    with pytest.raises(ValueError):
        note.check_validity()


def test_note_check_valid_no_citation_1():
    note = Element.from_tag(
        '<text:note text:note-class="footnote" text:id="note1">'
        "<text:note-citation></text:note-citation></text:note>"
    )
    with pytest.raises(ValueError):
        note.check_validity()


def test_note_check_valid_no_body_0():
    note = Element.from_tag(
        '<text:note text:note-class="footnote" text:id="note1">'
        "<text:note-citation>Some citation</text:note-citation></text:note>"
    )
    assert note.check_validity() is None


def test_note_check_valid_no_body_1():
    note = Element.from_tag(
        '<text:note text:note-class="footnote" text:id="note1">'
        "<text:note-citation>Some citation</text:note-citation>"
        "<text:note-body></text:note-body>"
        "</text:note>"
    )
    assert note.check_validity() is None


def test_note_str_no_citation():
    note = Element.from_tag(
        '<text:note text:note-class="footnote" text:id="note1">'
        "<text:note-citation></text:note-citation>"
        "<text:note-body>"
        '<text:p text:style-name="Standard">'
        "a footnote"
        "</text:p>"
        "</text:note-body>"
        "</text:note>"
    )
    assert str(note) == "a footnote"


def test_create_note1():
    # With an odf_element
    note_body = Paragraph("a footnote", style="Standard")
    note = Note(note_id="note1", citation="1", body=note_body)
    expected = (
        '<text:note text:note-class="footnote" text:id="note1">'
        "<text:note-citation>1</text:note-citation>"
        "<text:note-body>"
        '<text:p text:style-name="Standard">'
        "a footnote"
        "</text:p>"
        "</text:note-body>"
        "</text:note>"
    )
    assert note.serialize() == expected


def test_create_note1_str():
    # With an odf_element
    note_body = Paragraph("a footnote", style="Standard")
    note = Note(note_id="note1", citation="1", body=note_body)
    expected = "1. a footnote"
    assert str(note) == expected


def test_create_note2():
    # With an unicode object
    note = Note(note_id="note1", citation="1", body="a footnote")
    expected = (
        '<text:note text:note-class="footnote" text:id="note1">'
        "<text:note-citation>1</text:note-citation>"
        "<text:note-body>"
        "<text:p>"
        "a footnote"
        "</text:p>"
        "</text:note-body>"
        "</text:note>"
    )
    assert note.serialize() == expected


def test_get_note(document):
    body = document.body
    note = body.get_note(note_id="ftn1")
    assert note.tag == "text:note"


def test_get_note_list(document):
    body = document.body
    notes = body.get_notes()
    assert len(notes) == 2


def test_get_note_list_footnote(document):
    body = document.body
    notes = body.get_notes(note_class="footnote")
    assert len(notes) == 1


def test_get_note_list_endnote(document):
    body = document.body
    notes = body.get_notes(note_class="endnote")
    assert len(notes) == 1


def test_get_note_by_id(document):
    body = document.body
    note = body.get_note(note_id="ftn1")
    expected = (
        '<text:note text:id="ftn1" text:note-class="footnote">\n'
        "  <text:note-citation>1</text:note-citation>\n"
        "  <text:note-body>\n"
        '    <text:p text:style-name="Footnote">'
        "C'est-à-dire l'élément "
        "« text:p ».</text:p>\n"  # noqa: RUF001
        "  </text:note-body>\n"
        "</text:note>\n"
    )
    assert note.serialize(pretty=True) == expected


def test_get_note_by_class_footnote(document):
    body = document.body
    footnotes = body.get_notes(note_class="footnote")
    footnote = footnotes[0]
    expected = (
        '<text:note text:id="ftn1" text:note-class="footnote">\n'
        "  <text:note-citation>1</text:note-citation>\n"
        "  <text:note-body>\n"
        '    <text:p text:style-name="Footnote">'
        "C'est-à-dire l'élément "
        "« text:p ».</text:p>\n"  # noqa: RUF001
        "  </text:note-body>\n"
        "</text:note>\n"
    )
    assert footnote.serialize(pretty=True) == expected


def test_get_note_by_class_endnote(document):
    body = document.body
    endnotes = body.get_notes(note_class="endnote")
    endnote = endnotes[0]
    expected = (
        '<text:note text:id="ftn2" text:note-class="endnote">\n'
        "  <text:note-citation>i</text:note-citation>\n"
        "  <text:note-body>\n"
        '    <text:p text:style-name="Endnote">Les apparences '
        "sont trompeuses !</text:p>\n"
        "  </text:note-body>\n"
        "</text:note>\n"
    )
    assert endnote.serialize(pretty=True) == expected


def test_insert_note():
    note = Note(note_id="note1", citation="1", body="élément pertubateur")
    paragraph = Paragraph("Un paragraphe")
    paragraph.insert_note(note, after="para")
    expected = (
        "<text:p>Un para"
        '<text:note text:note-class="footnote" '
        'text:id="note1">'
        "<text:note-citation>1</text:note-citation>"
        "<text:note-body>"
        "<text:p>élément pertubateur</text:p>"
        "</text:note-body>"
        "</text:note>"
        "graphe</text:p>"
    )
    assert paragraph.serialize() == expected


def test_insert_note_inside_span():
    note = Note(note_id="note1", citation="1", body="élément pertubateur")
    data = "<text:p>Un <text:span>para</text:span>graphe</text:p>"
    paragraph = Element.from_tag(data)
    paragraph.insert_note(note, after="para")
    expected = (
        "<text:p>Un <text:span>para"
        '<text:note text:note-class="footnote" '
        'text:id="note1">'
        "<text:note-citation>1</text:note-citation>"
        "<text:note-body>"
        "<text:p>élément pertubateur</text:p>"
        "</text:note-body>"
        "</text:note>"
        "</text:span>graphe</text:p>"
    )
    assert paragraph.serialize() == expected


def test_insert_note_after_span():
    note = Note(note_id="note1", citation="1", body="élément pertubateur")
    data = "<text:p>Un <text:span>para</text:span>graphe.</text:p>"
    paragraph = Element.from_tag(data)
    paragraph.insert_note(note, after="graphe")
    expected = (
        "<text:p>Un <text:span>para</text:span>graphe"
        '<text:note text:note-class="footnote" '
        'text:id="note1">'
        "<text:note-citation>1</text:note-citation>"
        "<text:note-body>"
        "<text:p>élément pertubateur</text:p>"
        "</text:note-body>"
        "</text:note>"
        ".</text:p>"
    )
    assert paragraph.serialize() == expected


def test_get_formatted_text(document):
    body = document.body
    paragraph = body.get_element("//text:p")
    list_with_note = List()
    list_with_note.append_item(paragraph)
    body.append(list_with_note)
    expected = (
        "- Un paragraphe[1] d'apparence(i) banale[*].\n"
        "----\n"
        "[1] C'est-à-dire l'élément « text:p ».\n"  # noqa: RUF001
        "\n"
        "----\n"
        "[*] Sauf qu'il est commenté !\n"
        "\n"
        "========\n"
        "(i) Les apparences sont trompeuses !\n"
    )
    assert document.get_formatted_text() == expected
