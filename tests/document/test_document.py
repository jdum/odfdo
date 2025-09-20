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
#          Luis Belmar-Letelier <luis@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>

from importlib import resources as rso
from io import BytesIO

import pytest

from odfdo.const import ODF_CONTENT, ODF_EXTENSIONS, ODF_MANIFEST, ODF_META
from odfdo.content import Content
from odfdo.document import Document
from odfdo.manifest import Manifest
from odfdo.meta import Meta
from odfdo.paragraph import Paragraph


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
