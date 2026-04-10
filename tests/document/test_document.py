# Copyright 2018-2026 Jérôme Dumonteil
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
#          Luis Belmar-Letelier <luis@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
from importlib import resources as rso
from io import BytesIO
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from odfdo.annotation import Annotation
from odfdo.const import (
    ODF_CONTENT,
    ODF_EXTENSIONS,
    ODF_MANIFEST,
    ODF_MANIFEST_RDF,
    ODF_META,
    ODF_SETTINGS,
)
from odfdo.content import Content
from odfdo.document import Document, _get_part_class
from odfdo.element import Element
from odfdo.frame import Frame
from odfdo.header import Header
from odfdo.image import DrawFillImage, DrawImage
from odfdo.manifest import Manifest
from odfdo.master_page import StyleMasterPage
from odfdo.meta import Meta
from odfdo.note import Note
from odfdo.paragraph import Paragraph
from odfdo.settings import Settings
from odfdo.style import Style
from odfdo.style_base import StyleBase
from odfdo.table import Table
from odfdo.utils.blob import Blob
from odfdo.xmlpart import XmlPart


def _copied_template(tmp_path, template):
    src = rso.files("odfdo.templates") / template
    dest = tmp_path / template
    dest.write_bytes(src.read_bytes())
    return dest


def test_non_existing(samples):
    with pytest.raises(IOError):
        Document(samples("notexisting"))


def test_text_template(tmp_path):
    template = _copied_template(tmp_path, "text.ott")
    print(template)
    assert Document.new(template)


def test_spreadsheet_template(tmp_path):
    template = _copied_template(tmp_path, "spreadsheet.ots")
    assert Document.new(template)


def test_presentation_template(tmp_path):
    template = _copied_template(tmp_path, "presentation.otp")
    assert Document.new(template)


def test_drawing_template(tmp_path):
    template = _copied_template(tmp_path, "drawing.otg")
    assert Document.new(template)


def test_mimetype(tmp_path):
    template = _copied_template(tmp_path, "drawing.otg")
    document = Document.new(template)
    mimetype = document.mimetype
    assert "template" not in mimetype
    manifest = document.get_part(ODF_MANIFEST)
    media_type = manifest.get_media_type("/")
    assert "template" not in media_type


def test_bad_type():
    with pytest.raises(IOError):
        Document.new("foobar")


def test_text_type():
    document = Document("text")
    assert document.mimetype == ODF_EXTENSIONS["odt"]


def test_text_type_2():
    document = Document("texte")
    assert document.mimetype == ODF_EXTENSIONS["odt"]


def test_text_type_3():
    document = Document("odt")
    assert document.mimetype == ODF_EXTENSIONS["odt"]


def test_spreadsheet_type():
    document = Document.new("spreadsheet")
    assert document.mimetype == ODF_EXTENSIONS["ods"]


def test_spreadsheet_type_2():
    document = Document.new("tableur")
    assert document.mimetype == ODF_EXTENSIONS["ods"]


def test_spreadsheet_type_3():
    document = Document.new("ods")
    assert document.mimetype == ODF_EXTENSIONS["ods"]


def test_presentation_type():
    document = Document("presentation")
    assert document.mimetype == ODF_EXTENSIONS["odp"]


def test_presentation_type_2():
    document = Document("odp")
    assert document.mimetype == ODF_EXTENSIONS["odp"]


def test_drawing_type():
    document = Document.new("drawing")
    assert document.mimetype == ODF_EXTENSIONS["odg"]


def test_drawing_type_2():
    document = Document.new("odg")
    assert document.mimetype == ODF_EXTENSIONS["odg"]


def test_drawing_type_3():
    document = Document.new("graphics")
    assert document.mimetype == ODF_EXTENSIONS["odg"]


def test_drawing_type_4():
    document = Document.new("graphic")
    assert document.mimetype == ODF_EXTENSIONS["odg"]


def test_case_filesystem(samples):
    assert Document(samples("example.odt"))


def test_case_get_mimetype(samples):
    document = Document(samples("example.odt"))
    assert document.mimetype == ODF_EXTENSIONS["odt"]


def test_case_get_content(samples):
    document = Document(samples("example.odt"))
    content = document.get_part(ODF_CONTENT)
    assert isinstance(content, Content)


def test_case_get_meta(samples):
    document = Document(samples("example.odt"))
    meta = document.get_part(ODF_META)
    assert isinstance(meta, Meta)


def test_case_get_manifest(samples):
    document = Document(samples("example.odt"))
    manifest = document.get_part(ODF_MANIFEST)
    assert isinstance(manifest, Manifest)


def test_case_get_settings(samples):
    document = Document(samples("example.odt"))
    settings = document.get_part(ODF_SETTINGS)
    assert isinstance(settings, Settings)


def test_case_get_body(samples):
    document = Document(samples("example.odt"))
    body = document.body
    assert body.tag == "office:text"


def test_case_clone_body_none(samples):
    document = Document(samples("example.odt"))
    _dummy = document.body
    clone = document.clone
    # new body cache should be empty
    assert clone._Document__body is None


def test_case_clone_xmlparts_empty(samples):
    document = Document(samples("example.odt"))
    clone = document.clone
    # new xmlparts cache should be empty
    assert clone._Document__xmlparts == {}


def test_case_clone_same_content(samples):
    document = Document(samples("example.odt"))
    s_orig = document.body.serialize()
    clone = document.clone
    s_clone = clone.body.serialize()
    assert s_clone == s_orig


def test_case_clone_different_changes_1(samples):
    document = Document(samples("example.odt"))
    s_orig = document.body.serialize()
    clone = document.clone
    clone.body.append(Paragraph("some text"))
    s_clone = clone.body.serialize()
    assert s_clone != s_orig


def test_case_clone_different_unchanged_1(samples):
    document = Document(samples("example.odt"))
    s_orig = document.body.serialize()
    clone = document.clone
    clone.body.append(Paragraph("some text"))
    s_after = document.body.serialize()
    assert s_after == s_orig


def test_case_clone_different_unchanged_2(samples):
    document = Document(samples("example.odt"))
    clone = document.clone
    clone.body.append(Paragraph("some text"))
    s_clone1 = clone.body.serialize()
    document.body.append(Paragraph("new text"))
    s_clone2 = clone.body.serialize()
    assert s_clone1 == s_clone2


def test_case_save_nogenerator(tmp_path, samples):
    document = Document(samples("example.odt"))
    temp = BytesIO()
    document.save(temp)
    temp.seek(0)
    new = Document(temp)
    generator = new.get_part(ODF_META).get_generator()
    assert generator.startswith("odfdo")


def test_case_save_generator(samples):
    document = Document(samples("example.odt"))
    document.get_part(ODF_META).set_generator("toto")
    temp = BytesIO()
    document.save(temp)
    temp.seek(0)
    new = Document(temp)
    generator = new.get_part(ODF_META).get_generator()
    assert generator == "toto"


def test_repr_empty():
    document = Document()
    assert repr(document) == "<Document type=text path=None>"


def test_repr_text(samples):
    document = Document(samples("example.odt"))
    assert "example.odt" in repr(document)


def test_repr_spreadsheet(samples):
    document = Document(samples("simple_table.ods"))
    result = repr(document)
    assert "type=spreadsheet" in result
    assert "simple_table.ods" in result


def test_str_empty():
    document = Document()
    document.body.clear()
    assert str(document) == ""


def test_str_text(samples):
    document = Document(samples("example.odt"))
    result = str(document)
    assert "odfdo Test Case Document" in result
    assert "This is the second paragraph" in result
    assert "First paragraph[*] of the second section" in result


def test_str_spreadsheet(samples):
    document = Document(samples("simple_table.ods"))
    result = str(document)
    assert "1 1 1 2 3 3 3" in result
    assert "A float" in result
    assert "3.14" in result


def test_document_meta_error():
    doc = Document(None)
    doc.container = None
    with pytest.raises(ValueError, match="Empty Container"):
        _ = doc.meta


def test_settings_property():
    doc = Document("text")
    assert doc.settings is not None


def test_document_settings_error():
    doc = Document(None)
    doc.container = None
    with pytest.raises(ValueError, match="Empty Container"):
        _ = doc.settings


def test_document_styles_error():
    doc = Document(None)
    doc.container = None
    with pytest.raises(ValueError, match="Empty Container"):
        _ = doc.styles


def test_document_manifest_error():
    doc = Document(None)
    doc.container = None
    with pytest.raises(ValueError, match="Empty Container"):
        _ = doc.manifest


def test_document_get_type_no_container():
    doc = Document(None)
    doc.container = None
    with pytest.raises(ValueError, match="Empty Container"):
        doc.get_type()


def test_mimetype_setter_text_template():
    doc = Document("text")
    doc.mimetype = "application/vnd.oasis.opendocument.text-template"
    assert doc.mimetype == "application/vnd.oasis.opendocument.text-template"


def test_document_mimetype_property_error():
    doc = Document("text")
    doc.container = None
    with pytest.raises(ValueError, match="Empty Container"):
        _ = doc.mimetype


def test_document_get_formatted_text_spreadsheet():
    doc = Document("spreadsheet")
    table = Table("T1")
    table.set_value("A1", "cell1")
    doc.body.append(table)
    res = doc.get_formatted_text()
    assert "cell1" in res


def test_document_get_formatted_text_rst():
    doc = Document("text")
    p = Paragraph("test")
    doc.body.append(p)
    res = doc.get_formatted_text(rst_mode=True)
    assert "test" in res


def test_document_get_formatted_text_complex():
    doc = Document("text")
    p = Paragraph("test")

    # Footnote
    fn = Note("footnote", note_id="fn1")
    fn.note_body = Paragraph("note content")
    p.append(fn)

    # Annotation
    ann = Annotation("ann1", creator="me")
    ann.note_body = Paragraph("ann content")
    p.append(ann)

    doc.body.append(p)

    # Endnote
    en = Note("endnote", note_id="en1")
    en.note_body = Paragraph("endnote content")
    p2 = Paragraph("p2")
    p2.append(en)
    doc.body.append(p2)

    # Image for RST mode
    img = DrawImage("Pictures/test.png")
    frame = Frame.image_frame(img, width="10cm", height="10cm")
    doc.body.append(frame)

    res = doc.get_formatted_text()
    assert "test" in res
    assert "note content" in res
    assert "ann content" in res
    assert "endnote content" in res

    res_rst = doc.get_formatted_text(rst_mode=True)
    assert ".. [#]" in res_rst
    assert ".. image::" in res_rst
    assert ":width:" in res_rst
    assert ":height:" in res_rst


def test_document_get_formatted_text_not_implemented():
    doc = Document("text")
    with patch.object(Document, "get_type", return_value="formula"):
        with pytest.raises(NotImplementedError, match="not supported yet"):
            doc.get_formatted_text()


def test_document_del_part_success():
    doc = Document("text")
    doc.container.set_part("some/part", b"data")
    doc.del_part("some/part")
    with pytest.raises(ValueError, match="is deleted"):
        doc.get_part("some/part")


def test_document_del_part_no_container():
    doc = Document("text")
    doc.container = None
    with pytest.raises(ValueError, match="Empty Container"):
        doc.del_part("some/part")


def test_document_del_part_mandatory():
    doc = Document("text")
    with pytest.raises(ValueError, match="is mandatory"):
        doc.del_part("content")


def test_document_set_part_no_container():
    doc = Document("text")
    doc.container = None
    with pytest.raises(ValueError, match="Empty Container"):
        doc.set_part("some/part", b"data")


def test_document_get_parts_no_container_property():
    doc = Document("text")
    doc.container = None
    with pytest.raises(ValueError, match="Empty Container"):
        _a = doc.parts


def test_document_new_invalid_template():
    with pytest.raises(FileNotFoundError):
        Document.new("invalid")


def test_document_new_path(tmp_path):
    doc1 = Document("text")
    path = tmp_path / "template.ott"
    doc1.save(path)
    doc2 = Document.new(path)
    assert doc2.container is not None


def test_document_save_no_container():
    doc = Document("text")
    doc.container = None
    with pytest.raises(ValueError, match="Empty Container"):
        doc.save("test.odt")


def test_document_save_invalid_packaging():
    doc = Document("text")
    with pytest.raises(ValueError, match="not supported"):
        doc.save("test.odt", packaging="invalid")


def test_document_save_pretty_caching():
    doc = Document("text")
    doc.get_part("content")
    with patch.object(doc.container, "save"):
        doc.save("test.odt", pretty=True)


def test_document_check_manifest_rdf():
    doc = Document("text")
    doc.manifest.set_media_type(ODF_MANIFEST_RDF, "application/rdf+xml")
    doc._check_manifest_rdf()
    assert ODF_MANIFEST_RDF in doc.container.parts

    doc.manifest.del_full_path(ODF_MANIFEST_RDF)
    doc.container.set_part(ODF_MANIFEST_RDF, b"<rdf/>")
    doc._check_manifest_rdf()
    with pytest.raises(ValueError, match="is deleted"):
        doc.get_part(ODF_MANIFEST_RDF)


def test_document_delete_styles():
    doc = Document("text")

    p = Paragraph("test", style="s1")
    doc.body.append(p)
    doc.insert_style(Style("paragraph", name="s1"))

    mock_style = MagicMock(spec=StyleBase)
    type(mock_style).name = PropertyMock(side_effect=AttributeError)
    mock_style2 = MagicMock(spec=StyleBase)
    type(mock_style2).name = PropertyMock(return_value=None)

    with patch.object(Document, "get_styles", return_value=[mock_style, mock_style2]):
        doc.delete_styles()

    deleted = doc.delete_styles()
    assert deleted > 0
    assert p.style is None


def test_document_copy_image_from_document():
    doc1 = Document("text")
    doc2 = Document("text")
    doc1.container.set_part("Pictures/test.png", b"data")
    doc1.manifest.add_full_path("Pictures/test.png", "image/png")
    doc2._copy_image_from_document(doc1, "Pictures/test.png")
    assert doc2.get_part("Pictures/test.png") == b"data"
    assert doc2.manifest.get_media_type("Pictures/test.png") == "image/png"


def test_document_merge_styles_from():
    doc1 = Document("text")
    doc2 = Document("text")
    s1 = Style("paragraph", name="style1")
    doc1.insert_style(s1)
    doc2.merge_styles_from(doc1)
    assert doc2.get_style("paragraph", "style1") is not None


def test_document_merge_styles_from_complex():
    doc1 = Document("text")
    doc2 = Document("text")
    s1 = Style("paragraph", name="auto1")
    doc1.insert_style(s1, automatic=True)
    s2 = StyleMasterPage("master1", page_layout="pl1")
    doc1.insert_style(s2)
    s3 = Style("font-face", font_name="font1")
    doc1.insert_style(s3)

    mock_style = MagicMock(spec=StyleBase)
    type(mock_style).family = PropertyMock(return_value=None)

    mock_style2 = MagicMock(spec=StyleBase)
    type(mock_style2).family = PropertyMock(return_value="paragraph")
    type(mock_style2).parent = PropertyMock(return_value=None)

    with patch.object(Document, "get_styles", return_value=[mock_style, mock_style2]):
        doc2.merge_styles_from(doc1)

    doc2.merge_styles_from(doc1)
    assert doc2.get_style("paragraph", "auto1") is not None
    assert doc2.get_style("master-page", "master1") is not None
    assert doc2.get_style("font-face", "font1") is not None


def test_document_add_page_break_style():
    doc = Document("text")
    doc.add_page_break_style()
    assert doc.get_style("paragraph", "odfdopagebreak") is not None
    doc.add_page_break_style()


def test_document_get_table():
    doc = Document("spreadsheet")
    table = Table("T1")
    doc.body.append(table)
    assert doc._get_table("T1").name == "T1"
    assert doc._get_table(0) is not None
    with pytest.raises(TypeError, match="must be int or str"):
        doc._get_table(None)


def test_document_get_cell_style_properties():
    doc = Document("spreadsheet")
    table = Table("T1")
    table.set_value("A1", "val")
    doc.body.append(table)
    assert doc.get_cell_style_properties("T1", "A1") == {}
    s1 = Style("table-cell", name="s1", background_color="#ff0000")
    doc.insert_style(s1)
    table.get_cell("A1", clone=False).style = "s1"
    props = doc.get_cell_style_properties("T1", "A1")
    assert props.get("fo:background-color") == "#ff0000"


def test_document_get_cell_style_properties_branches():
    doc = Document("spreadsheet")
    table = Table("T1")
    table.set_value("A1", "val")
    doc.body.append(table)

    assert doc.get_cell_style_properties("NonExistent", "A1") == {}

    s_row = Style("table-row", name="sr1")
    s_row.set_properties(area="table-cell", background_color="#0000FF")
    doc.insert_style(s_row)
    table.get_row(0, clone=False).style = "sr1"
    props = doc.get_cell_style_properties("T1", "A1")
    assert props.get("fo:background-color") == "#0000FF"

    table.get_row(0, clone=False).style = None
    s1 = Style("table-cell", name="s1", background_color="#FF0000")
    doc.insert_style(s1)
    col = table.get_column(0)
    col.default_cell_style = "s1"
    table.set_column(0, col)
    props = doc.get_cell_style_properties("T1", "A1")
    assert props.get("fo:background-color") == "#FF0000"

    col = table.get_column(0)
    col.default_cell_style = None
    table.set_column(0, col)
    assert doc.get_cell_style_properties("T1", "A1") == {}

    with patch.object(Table, "get_column", side_effect=ValueError):
        assert doc.get_cell_style_properties("T1", "A1") == {}


def test_document_get_cell_background_color():
    doc = Document("spreadsheet")
    table = Table("T1")
    table.set_value("A1", "val")
    doc.body.append(table)
    assert doc.get_cell_background_color("T1", "A1") == "#ffffff"
    s1 = Style("table-cell", name="s1", background_color="#ff0000")
    doc.insert_style(s1)
    table.get_cell("A1", clone=False).style = "s1"
    assert doc.get_cell_background_color("T1", "A1") == "#ff0000"


def test_document_get_table_style():
    doc = Document("spreadsheet")
    table = Table("T1")
    doc.body.append(table)
    assert doc.get_table_style("NonExistent") is None
    s1 = Style("table", name="st1")
    doc.insert_style(s1)
    table.style = "st1"
    assert doc.get_table_style("T1").name == "st1"


def test_document_get_table_displayed():
    doc = Document("spreadsheet")
    table = Table("T1")
    doc.body.append(table)
    assert doc.get_table_displayed("T1") is True
    doc.set_table_displayed("T1", False)
    assert doc.get_table_displayed("T1") is False

    table.style = None
    assert doc.get_table_displayed("T1") is True


def test_document_unique_style_name():
    doc = Document("text")
    name1 = doc._unique_style_name("base")
    assert name1 == "base_0"
    doc.insert_style(Style("paragraph", name="base_0"))
    name2 = doc._unique_style_name("base")
    assert name2 == "base_1"


def test_document_set_table_displayed():
    doc = Document("spreadsheet")
    table = Table("T1")
    doc.body.append(table)
    doc.set_table_displayed("T1", False)
    style = doc.get_table_style("T1")
    assert style.get_properties()["table:display"] == "false"
    doc.set_table_displayed("T1", True)
    style = doc.get_table_style("T1")  # Get the NEW style
    assert style.get_properties()["table:display"] == "true"


def test_document_language():
    doc = Document("text")
    doc.language = "fr-FR"
    assert doc.language == "fr-FR"
    with pytest.raises(TypeError, match=r"RFC3066"):
        doc.language = "invalid"


def test_document_get_parent_style():
    doc = Document("text")
    s1 = Style("paragraph", name="parent")
    s2 = Style("paragraph", name="child", parent_style="parent")
    doc.insert_style(s1)
    doc.insert_style(s2)
    assert doc.get_parent_style(s2).name == "parent"
    assert doc.get_parent_style(s1) is None


def test_document_get_list_style():
    doc = Document("text")
    ls = Style("list", name="ls1")
    doc.insert_style(ls)
    s1 = Style("paragraph", name="s1")
    s1.set_attribute("style:list-style-name", "ls1")
    doc.insert_style(s1)
    assert doc.get_list_style(s1).name == "ls1"


def test_document_set_automatic_name():
    doc = Document("text")
    s1 = Style("paragraph")
    doc._set_automatic_name(s1, "paragraph")
    assert s1.name.startswith("odfdo_auto_")
    doc.insert_style(s1, automatic=True)
    s2 = Style("paragraph")
    doc._set_automatic_name(s2, "paragraph")
    assert s2.name != s1.name


def test_document_show_styles():
    doc = Document("text")
    s1 = Style("paragraph", name="s1", color="red")
    s1.set_properties(area="paragraph", writing_mode="lr-tb")
    doc.insert_style(s1)
    s2 = DrawFillImage(name="img1")
    doc.insert_style(s2)
    s3 = Style("text", name="auto1")
    doc.insert_style(s3, automatic=True)
    res = doc.show_styles(properties=True)
    assert "s1" in res
    assert "img1" in res
    assert "auto1" in res
    assert "writing-mode" in res


def test_document_pseudo_style_attribute():
    doc = Document("text")
    s1 = Style("paragraph", name="s1", display_name="Display S1")
    res = doc._pseudo_style_attribute(s1, "name")
    assert res == "s1"
    res = doc._pseudo_style_attribute(s1, "display_name")
    assert res == "Display S1"
    res = doc._pseudo_style_attribute(s1, "invalid")
    assert res == ""


def test_document_get_formated_meta():
    doc = Document("text")
    res = doc.get_formated_meta()
    assert "Creation date" in res


def test_document_to_markdown():
    doc = Document("text")
    doc.body.append(Element.from_tag("<text:p>test markdown</text:p>"))
    res = doc.to_markdown()
    assert "test markdown" in res

    doc2 = Document("spreadsheet")
    with pytest.raises(NotImplementedError):
        doc2.to_markdown()


def test_document_add_file(tmp_path):
    doc = Document("text")
    f = tmp_path / "test.txt"
    f.write_text("content")
    path = doc.add_file(f)
    assert "Pictures/" in path

    buf = BytesIO(b"content2")
    buf.name = "test2.txt"
    doc.add_file(buf)


def test_document_clone():
    doc = Document("text")
    # Add a dummy XmlPart to test setattr loop
    doc.dummy_part = XmlPart("dummy", doc.container)
    doc2 = doc.clone
    assert doc2 is not doc
    assert doc2.get_type() == doc.get_type()
    assert hasattr(doc2, "dummy_part")
    assert doc2.dummy_part is not doc.dummy_part


def test_check_manifest_rdf_no_container():
    doc = Document()
    doc.container = None
    # Should return early
    doc._check_manifest_rdf()


def test_show_styles_no_name_style():
    doc = Document("text")
    style_mock = MagicMock(spec=Style)
    style_mock.tag = "style:style"
    style_mock.name = ""  # instead of None to avoid MagicMock in join
    style_mock.family = "paragraph"
    style_mock.parent = None  # is_auto False
    style_mock.attributes = {}
    style_mock.children = []
    # Mocking for _pseudo_style_attribute
    style_mock.display_name = ""
    style_mock.parent_style = ""

    with patch.object(Document, "get_styles", return_value=[style_mock]):
        res = doc.show_styles()
        assert "family:paragraph" in res


def test_delete_styles_name_none():
    doc = Document("text")
    style_mock = MagicMock(spec=Style)
    style_mock.name = None
    with patch.object(Document, "get_styles", return_value=[style_mock]):
        # Should skip style with name None (now via if not name:)
        assert doc.delete_styles() == 0


def test_get_parts_no_container():
    doc = Document()
    doc.container = None
    with pytest.raises(ValueError, match="Empty Container"):
        doc.get_parts()


def test_get_type_invalid_mimetype():
    doc = Document()
    doc.container = MagicMock()
    # Mimetype without dot
    doc.container.mimetype = "text"
    assert doc.get_type() == "text"


def test_content_property_none():
    doc = Document("text")
    with patch.object(Document, "get_part", return_value=None):
        with pytest.raises(ValueError, match="Empty Content"):
            _ = doc.content


def test_meta_property_none():
    doc = Document("text")
    with patch.object(Document, "get_part", return_value=None):
        with pytest.raises(ValueError, match="Empty Meta"):
            _ = doc.meta


def test_styles_property_none():
    doc = Document("text")
    with patch.object(Document, "get_part", return_value=None):
        with pytest.raises(ValueError, match="Empty Styles"):
            _ = doc.styles


def test_get_parent_style_none():
    doc = Document("text")
    assert doc.get_parent_style(None) is None


def test_get_list_style_none():
    doc = Document("text")
    assert doc.get_list_style(None) is None


def test_get_list_style_no_attr():
    doc = Document("text")
    style = Element.from_tag("style:style")
    assert doc.get_list_style(style) is None


def test_get_list_style_no_name_branch():
    doc = Document("text")
    style = Style("paragraph", name="MyStyle")
    style.set_attribute("style:list-style-name", "")
    assert doc.get_list_style(style) is None


def test_show_styles_drawfillimage_branch():
    doc = Document("text")
    fill = DrawFillImage("myfill", "Pictures/img.png")
    # DrawFillImage is usually inserted in office:styles (common)
    doc.insert_style(fill)
    res = doc.show_styles()
    assert "myfill" in res
    # The family for DrawFillImage should be "" in show_styles
    assert "family: " in res


def test_copy_image_from_document_not_bytes():
    doc1 = Document("text")
    doc2 = Document("text")
    with patch.object(Document, "get_part", return_value="not bytes"):
        doc2._copy_image_from_document(doc1, "path")
        assert "path" not in doc2.parts


def test_merge_styles_from_no_name_attr():
    doc1 = Document("text")
    doc2 = Document("text")
    style = Element.from_tag("style:style")
    style.set_attribute("style:family", "paragraph")
    doc1.content.get_element("//office:automatic-styles").append(style)
    doc2.merge_styles_from(doc1)


def test_merge_styles_from_stylename_none():
    doc1 = Document("text")
    doc2 = Document("text")
    style = Style("paragraph")
    doc1.content.get_element("//office:automatic-styles").append(style)
    doc2.merge_styles_from(doc1)


def test_get_style_properties_style_none():
    doc = Document("text")
    assert doc.get_style_properties("paragraph", "NONEXISTENT") is None


def test_get_cell_style_properties_row_style_none():
    doc = Document("spreadsheet")
    sheet = doc.body.get_table(0)
    row = sheet.get_row(0)
    row.style = None
    props = doc.get_cell_style_properties(0, (0, 0))
    assert isinstance(props, dict)


def test_get_cell_style_properties_column_style_none():
    doc = Document("spreadsheet")
    sheet = doc.body.get_table(0)
    col = sheet.get_column(0)
    col.default_cell_style = None
    props = doc.get_cell_style_properties(0, (0, 0))
    assert props == {}


def test_mimetype_empty_container_old():
    doc = Document()
    doc.container = None
    with pytest.raises(ValueError, match="Empty Container"):
        _ = doc.mimetype
    with pytest.raises(ValueError, match="Empty Container"):
        doc.mimetype = "application/vnd.oasis.opendocument.text"


def test_meta_empty_or_invalid():
    doc = Document("text")
    doc.get_part = MagicMock(return_value=None)
    with pytest.raises(ValueError, match="Empty Meta"):
        _ = doc.meta


def test_manifest_empty_or_invalid():
    doc = Document("text")
    doc.get_part = MagicMock(return_value=None)
    with pytest.raises(ValueError, match="Empty Manifest"):
        _ = doc.manifest


def test_settings_empty_or_invalid():
    doc = Document("text")
    doc.get_part = MagicMock(return_value=None)
    with pytest.raises(ValueError, match="Empty settings part"):
        _ = doc.settings


def test_to_markdown_invalid_type():
    doc = Document("spreadsheet")
    with pytest.raises(
        NotImplementedError, match="Type of document 'spreadsheet' not supported yet"
    ):
        doc.to_markdown()


def test_add_binary_part_empty_container_old():
    doc = Document()
    doc.container = None
    blob = Blob.from_io(BytesIO(b"content"))
    with pytest.raises(ValueError, match="Empty Container"):
        doc._add_binary_part(blob)


def test_add_file_empty_container_old():
    doc = Document()
    doc.container = None
    with pytest.raises(ValueError, match="Empty Container"):
        doc.add_file(BytesIO(b"content"))


def test_clone_empty_container_old():
    doc = Document()
    doc.container = None
    with pytest.raises(ValueError, match="Empty Container"):
        _ = doc.clone


def test_get_parent_style_no_family():
    doc = Document("text")
    style = Style("paragraph", name="MyStyle")
    style.family = None
    assert doc.get_parent_style(style) is None


def test_get_parent_style_no_parent():
    doc = Document("text")
    style = Style("paragraph", name="MyStyle")
    assert doc.get_parent_style(style) is None


def test_get_list_style_no_name():
    doc = Document("text")
    style = Style("paragraph", name="MyStyle")
    assert doc.get_list_style(style) is None


def test_set_automatic_name_no_name_attr_old():
    doc = Document("text")
    element = Element.from_tag("dc:title")
    doc._set_automatic_name(element, "paragraph")
    assert not hasattr(element, "name")


def test_show_styles_flags_old():
    doc = Document("text")
    res = doc.show_styles(automatic=False)
    assert "auto" not in res
    res = doc.show_styles(common=False)
    assert "common" not in res
    res = doc.show_styles(automatic=False, common=False)
    assert res == ""


def test_delete_styles_mixed_old():
    doc = Document("text")
    style1 = Style("paragraph", name="USED")
    doc.insert_style(style1, automatic=False)
    p = Paragraph("test", style="USED")
    doc.body.append(p)
    count = doc.delete_styles()
    assert count >= 1
    assert p.get_attribute("text:style-name") is None
    assert doc.get_style("paragraph", "USED") is None


def test_add_page_break_style_existing_old():
    doc = Document("text")
    doc.add_page_break_style()
    doc.add_page_break_style()
    assert doc.get_style("paragraph", "odfdopagebreak") is not None


def test_get_table_invalid_type_old():
    doc = Document("spreadsheet")
    with pytest.raises(TypeError, match="Table parameter must be int or str"):
        doc._get_table(None)


def test_save_pretty_xml_old_old():
    doc = Document("text")
    out = BytesIO()
    doc.save(out, packaging="xml", pretty=True)
    assert b"<office:document" in out.getvalue()


def test_check_manifest_rdf_missing_part_old_old():
    doc = Document("text")
    doc.manifest.add_full_path("manifest.rdf", "application/rdf+xml")
    doc._check_manifest_rdf()
    assert "manifest.rdf" in doc.container.parts


def test_merge_styles_from_different_containers_old():
    doc1 = Document("text")
    doc2 = Document("text")
    style = Style("paragraph", name="P1")
    doc1.content.get_element("//office:automatic-styles").append(style)
    doc2.merge_styles_from(doc1)
    assert doc2.content.get_style("paragraph", "P1") is not None


def test_merge_styles_from_master_page_with_image_old():
    doc1 = Document("text")
    doc2 = Document("text")
    master_page = Element.from_tag("style:master-page")
    master_page.set_attribute("style:name", "MyMaster")
    doc1.styles.get_element("//office:master-styles").append(master_page)
    img_path = "Pictures/test.png"
    img_content = b"fake image"
    doc1.set_part(img_path, img_content)
    doc1.manifest.add_full_path(img_path, "image/png")
    img = DrawImage(url=img_path)
    master_page.append(img)
    doc2.merge_styles_from(doc1)
    assert doc2.get_part(img_path) == img_content


def test_merge_styles_from_draw_fill_image_old_old():
    doc1 = Document("text")
    doc2 = Document("text")
    img_path = "Pictures/test_fill.png"
    img_content = b"fake fill image"
    doc1.set_part(img_path, img_content)
    doc1.manifest.add_full_path(img_path, "image/png")
    fill_image = DrawFillImage(name="MyFill", url=img_path)
    doc1.styles.get_element("//office:styles").append(fill_image)
    doc2.merge_styles_from(doc1)
    assert doc2.get_part(img_path) == img_content


def test_insert_style_font_face_decls_old_old():
    doc = Document("text")
    font_face = Element.from_tag("style:font-face")
    font_face.set_attribute("style:name", "MyFont")
    doc.content.get_element("//office:font-face-decls").append(font_face)
    doc.insert_style(font_face)
    assert doc.get_style("font-face", "MyFont") is not None


def test_merge_styles_from_content_automatic_old_old():
    doc1 = Document("text")
    doc2 = Document("text")
    style = Style("paragraph", name="P1")
    doc1.content.get_element("//office:automatic-styles").append(style)
    doc2.merge_styles_from(doc1)
    assert doc2.content.get_style("paragraph", "P1") is not None


def test_get_formatted_text_images_rst_old_old():
    doc = Document("text")
    result = []
    context = {
        "images": [
            ("ref1", "file1.png", ("10cm", "5cm")),
            ("ref2", "file2.png", (None, None)),
        ],
        "annotations": [],
        "endnotes": [],
    }
    doc._get_formatted_text_images(result, context, rst_mode=True)
    res_str = "".join(result)
    assert ".. ref1 image:: file1.png" in res_str
    assert ":width: 10cm" in res_str
    assert ":height: 5cm" in res_str
    assert ".. ref2 image:: file2.png" in res_str
    assert "width" not in res_str.split("file2.png")[-1]


def test_set_automatic_name_index_parsing_old_old():
    doc = Document("text")
    style1 = Style("paragraph", name="odfdo_auto_abc")
    doc.content.get_element("//office:automatic-styles").append(style1)
    style2 = Style("paragraph", name="NewStyle")
    doc._set_automatic_name(style2, "paragraph")
    assert style2.name == "odfdo_auto_1"


def test_show_styles_with_properties_old_old():
    doc = Document("text")
    style = Style("paragraph", name="P_PROPS")
    style.set_properties(area="paragraph", align="center")
    doc.styles.get_element("//office:styles").append(style)
    p = Paragraph("test", style="P_PROPS")
    doc.body.append(p)
    res = doc.show_styles(properties=True)
    assert "P_PROPS" in res
    assert "fo:text-align: center" in res


def test_merge_styles_from_duplicate_old_old():
    doc1 = Document("text")
    doc2 = Document("text")
    style1 = Style("paragraph", name="P_DUP")
    style1.set_properties(area="text", color="#111111")
    doc1.styles.get_element("//office:styles").append(style1)
    style2 = Style("paragraph", name="P_DUP")
    style2.set_properties(area="text", color="#222222")
    doc2.styles.get_element("//office:styles").append(style2)
    doc2.merge_styles_from(doc1)
    res_style = doc2.get_style("paragraph", "P_DUP")
    assert res_style.get_properties(area="text")["fo:color"] == "#111111"


def test_get_parent_style_not_found_old_old():
    doc = Document("text")
    style = Style("paragraph", name="MyStyle", parent_style="NonExistent")
    assert doc.get_parent_style(style) is None


def test_get_list_style_not_found_old_old():
    doc = Document("text")
    style = Style("paragraph", name="MyStyle")
    style.list_style_name = "NonExistent"
    assert doc.get_list_style(style) is None


def test_get_styles_family_bytes_old_old():
    doc = Document("text")
    styles = doc.get_styles(family=b"paragraph")
    assert len(styles) > 0


def test_get_styled_elements_all_old_old():
    doc = Document("text")
    elements = doc.get_styled_elements()
    assert len(elements) > 0


def test_delete_styles_attribute_error_old_old():
    doc = Document("text")
    style = MagicMock()
    type(style).name = property(
        lambda x: exec('raise AttributeError("no name")'),  # noqa: S102
    )
    orig_get_styles = doc.get_styles
    doc.get_styles = MagicMock(return_value=orig_get_styles() + [style])
    res = doc.delete_styles()
    assert isinstance(res, int)


def test_copy_image_from_document_invalid_content_old_old():
    doc1 = Document("text")
    doc2 = Document("text")
    doc1.get_part = MagicMock(return_value=None)
    doc2._copy_image_from_document(doc1, "Pictures/none.png")
    assert "Pictures/none.png" not in doc2.container.parts


def test_merge_styles_from_no_name_old_old():
    doc1 = Document("text")
    doc2 = Document("text")
    style = Element.from_tag("style:style")
    style.set_attribute("style:family", "paragraph")
    doc1.styles.get_element("//office:styles").append(style)
    doc2.merge_styles_from(doc1)
    assert doc2.styles.get_style("paragraph", None) is not None


def test_merge_styles_from_wrong_upper_container_old_old():
    doc1 = Document("text")
    doc2 = Document("text")
    style = Style("paragraph", name="P_WRONG")
    wrong_container = Element.from_tag("office:body")
    wrong_container.append(style)
    doc1.get_styles = MagicMock(return_value=[style])
    with pytest.raises(NotImplementedError):
        doc2.merge_styles_from(doc1)


def test_save_pretty_zip_old_old():
    doc = Document("text")
    out = BytesIO()
    doc.save(out, packaging="zip", pretty=True)
    from zipfile import ZipFile

    with ZipFile(out) as z:
        content = z.read("content.xml")
        assert b"\n" in content


def test_get_parts_empty_container_old_old():
    doc = Document()
    doc.container = None
    with pytest.raises(ValueError, match="Empty Container"):
        doc.get_parts()


def test_get_type_all_old_old():
    for mimetype, expected in [
        ("application/vnd.oasis.opendocument.text", "text"),
        ("application/vnd.oasis.opendocument.spreadsheet", "spreadsheet"),
    ]:
        doc = Document()
        doc.container = MagicMock()
        doc.container.mimetype = mimetype
        assert doc.get_type() == expected


def test_get_formatted_text_footnotes_non_rst_old_old():
    doc = Document("text")
    result = []
    context = {
        "footnotes": [("1", "note 1")],
        "annotations": [],
        "images": [],
        "endnotes": [],
    }
    doc._get_formatted_text_footnotes(result, context, rst_mode=False)
    assert "note 1" in "".join(result)


def test_get_formatted_text_footnotes_non_rst():
    doc = Document("text")
    result = []
    context = {
        "footnotes": [("1", "citation")],
        "annotations": [],
        "images": [],
        "endnotes": [],
    }
    doc._get_formatted_text_footnotes(result, context, rst_mode=False)
    assert "----\n" in "".join(result)
    assert "[1] citation\n" in "".join(result)


def test_get_formatted_text_images_call_via_header():
    doc = Document("text")
    header = Header(1, "Title")
    img = DrawImage(url="Pictures/test.png")
    frame = Frame.image_frame(img, size=("1cm", "1cm"))
    header.append(frame)
    doc.body.append(header)
    res = doc.get_formatted_text(rst_mode=True)
    assert ".. |img1| image:: Pictures/test.png" in res


def test_check_manifest_rdf_extra_in_parts_old_old():
    doc = Document("text")
    doc.manifest.get_media_type = MagicMock(return_value=None)
    doc.container.get_parts = MagicMock(return_value=[ODF_MANIFEST_RDF, "mimetype"])
    doc.container.del_part = MagicMock()
    doc._check_manifest_rdf()
    doc.container.del_part.assert_called_with(ODF_MANIFEST_RDF)


def test_get_style_with_style_base_old_old():
    doc = Document("text")
    style = Style("paragraph", name="MyStyle")
    assert doc.get_style("paragraph", style) is style


def test_get_style_default_old_old():
    doc = Document("text")
    style = doc.get_style("paragraph", None)
    assert style is not None
    assert style.tag == "style:default-style"


def test_set_automatic_name_with_existing_indices_old_old():
    doc = Document("text")
    style1 = Style("paragraph", name="odfdo_auto_10")
    doc.content.get_element("//office:automatic-styles").append(style1)
    style2 = Style("paragraph", name="NewStyle")
    doc._set_automatic_name(style2, "paragraph")
    assert style2.name == "odfdo_auto_11"


def test_delete_styles_with_attributes_old_old():
    doc = Document("text")
    p = Paragraph("test", style="Standard")
    doc.body.append(p)
    doc.delete_styles()
    assert p.get_attribute("text:style-name") is None


def test_get_part_none_old_old():
    doc = Document("text")
    doc.container.get_part = MagicMock(return_value=None)
    res = doc.get_part("non_existent_raw_part")
    assert res is None


def test_get_table_style_old_old():
    doc = Document("spreadsheet")
    style = doc.get_table_style(0)
    assert style is not None
    assert style.family == "table"


def test_get_table_displayed_old_old():
    doc = Document("spreadsheet")
    assert doc.get_table_displayed(0) is True


def test_set_table_displayed_old_old():
    doc = Document("spreadsheet")
    doc.set_table_displayed(0, False)
    assert doc.get_table_displayed(0) is False


def test_get_cell_style_properties_cell_old_old():
    doc = Document("spreadsheet")
    sheet = doc.body.get_table(0)
    style = Style("table-cell", name="cellstyle")
    style.set_properties(area="table-cell", background_color="#112233")
    doc.insert_style(style, automatic=False)
    sheet.set_value((0, 0), value="", style="cellstyle")
    res_props = doc.get_cell_style_properties(0, (0, 0))
    assert res_props.get("fo:background-color") == "#112233"


def test_get_cell_style_properties_column_old_old():
    doc = Document("spreadsheet")
    sheet = doc.body.get_table(0)
    column = sheet.get_column(0)
    column.default_cell_style = "colstyle"
    sheet.set_column(0, column)
    style = Style("table-cell", name="colstyle")
    style.set_properties(area="table-cell", background_color="#654321")
    doc.insert_style(style, automatic=False)
    cell = sheet.get_cell((0, 0))
    cell.style = None
    sheet.set_cell((0, 0), cell)
    row = sheet.get_row(0)
    row.style = None
    sheet.set_row(0, row)
    res_props = doc.get_cell_style_properties(0, (0, 0))
    assert res_props.get("fo:background-color") == "#654321"


def test_get_set_language_old_old():
    doc = Document("text")
    doc.language = "fr-FR"
    assert doc.language == "fr-FR"
    assert doc.meta.language == "fr-FR"
    with pytest.raises(TypeError, match="Language must be"):
        doc.language = "invalid"


def test_save_pretty_xml_runtime_error():
    doc = Document("text")
    _ = doc.meta

    def mock_get_part_class(path):
        if path == "settings.xml":
            return None
        return _get_part_class(path)

    with patch("odfdo.document._get_part_class", side_effect=mock_get_part_class):
        out = BytesIO()
        with pytest.raises(RuntimeError, match="Should never happen"):
            doc.save(out, pretty=True)


def test_save_pretty_none_xmlparts_1():
    doc = Document("text")
    doc._Document__xmlparts[ODF_CONTENT] = None
    out = BytesIO()
    doc.save(out, pretty=True)
    assert out.getvalue() != b""


def test_save_not_pretty_none_xmlparts_2():
    doc = Document("text")
    doc._Document__xmlparts[ODF_CONTENT] = None
    out = BytesIO()
    doc.save(out, pretty=False)
    assert out.getvalue() != b""


def test_save_xmlparts_path_known():
    doc = Document("text")
    _ = doc.content
    _ = doc.meta
    _ = doc.styles
    _ = doc.settings
    out = BytesIO()
    doc.save(out, pretty=True)
    assert out.getvalue() != b""


def test_save_container_get_part_none():
    doc = Document("text")
    valid_meta = (
        b"<office:document-meta xmlns:office="
        b'"urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
        b'xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" '
        b'office:version="1.2">'
        b"<office:meta>"
        b"<meta:generator/>"
        b"</office:meta>"
        b"</office:document-meta>"
    )

    def side_effect(path):
        if path == "settings.xml":
            return None
        if path == "meta.xml":
            return valid_meta
        return b"<xml/>"

    with patch.object(doc.container, "get_part", side_effect=side_effect):
        out = BytesIO()
        doc.save(out, pretty=True)
    assert out.getvalue() != b""
