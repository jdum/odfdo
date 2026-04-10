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
from collections.abc import Iterable
from io import BytesIO
from os.path import isfile
from pathlib import Path
from unittest.mock import patch

import pytest

from odfdo.const import (
    FOLDER,
    ODF_CONTENT,
    ODF_MANIFEST,
    ODF_MANIFEST_NAME,
    ODF_MANIFEST_RDF,
    ODF_META,
    ODF_SETTINGS,
    ODF_STYLES,
    ODF_TEXT,
    ZIP,
)
from odfdo.container import Container
from odfdo.content import Content
from odfdo.document import (
    Document,
    _get_part_class,
    _get_part_path,
)
from odfdo.manifest import Manifest
from odfdo.meta import Meta
from odfdo.settings import Settings
from odfdo.styles import Styles


@pytest.fixture
def document() -> Iterable:
    doc = Document("odt")
    doc.body.clear()
    yield doc


def test_add_file_non_exists(document):
    with pytest.raises(FileNotFoundError):
        document.add_file("non exists")


def test_add_file_manifest(document, samples):
    document.add_file(samples("image.png"))
    manifest = document.manifest
    paths = manifest.get_path_medias()
    assert ("Pictures/ceddccf10506d07cc0990639e79f8c72.png", "image/png") in paths


def test_add_file_get_part(document, samples):
    png = samples("image.png")
    document.add_file(png)
    expected = png.read_bytes()
    container = document.container
    content = container.get_part("Pictures/ceddccf10506d07cc0990639e79f8c72.png")
    assert content == expected


def test_add_manifest_rdf_1(tmp_path, samples):
    base = Container()
    base.open(samples("example.odt"))
    content = base.get_part(ODF_CONTENT)
    styles = base.get_part(ODF_STYLES)
    meta = base.get_part(ODF_META)
    settings = base.get_part(ODF_SETTINGS)
    manifest = base.get_part(ODF_MANIFEST)
    container = Container()
    container.set_part(ODF_CONTENT, content)
    container.set_part(ODF_STYLES, styles)
    container.set_part(ODF_META, meta)
    container.set_part(ODF_SETTINGS, settings)
    container.set_part(ODF_MANIFEST, manifest)
    container.mimetype = ODF_TEXT
    document = Document("odt")
    document.container = container
    path = tmp_path / "example.odt"
    document.save(path, packaging=ZIP)
    new_container = Container()
    new_container.open(path)
    rdf = new_container.get_part(ODF_MANIFEST_RDF)
    assert rdf.decode() == new_container.default_manifest_rdf


def test_manifest_rdf_2(tmp_path, samples):
    base = Container()
    base.open(samples("example.odt"))
    content = base.get_part(ODF_CONTENT)
    styles = base.get_part(ODF_STYLES)
    meta = base.get_part(ODF_META)
    settings = base.get_part(ODF_SETTINGS)
    manifest = base.get_part(ODF_MANIFEST)
    container = Container()
    container.set_part(ODF_CONTENT, content)
    container.set_part(ODF_STYLES, styles)
    container.set_part(ODF_META, meta)
    container.set_part(ODF_SETTINGS, settings)
    container.set_part(ODF_MANIFEST, manifest)
    container.mimetype = ODF_TEXT
    document = Document("odt")
    document.container = container
    path = tmp_path / "example.odt"
    document.save(path, packaging=FOLDER)
    path_m = tmp_path / "example.odt.folder" / "mimetype"
    assert isfile(path_m)
    path_c = tmp_path / "example.odt.folder" / ODF_CONTENT
    assert isfile(path_c)
    path_s = tmp_path / "example.odt.folder" / ODF_STYLES
    assert isfile(path_s)
    path_m = tmp_path / "example.odt.folder" / ODF_META
    assert isfile(path_m)
    path_se = tmp_path / "example.odt.folder" / ODF_SETTINGS
    assert isfile(path_se)
    path_m1 = tmp_path / "example.odt.folder" / ODF_MANIFEST
    assert isfile(path_m1)
    path_m2 = tmp_path / "example.odt.folder" / ODF_MANIFEST_RDF
    assert isfile(path_m2)


def test_get_part_path():
    assert _get_part_path("content") == ODF_CONTENT
    assert _get_part_path("meta") == ODF_META
    assert _get_part_path("settings") == ODF_SETTINGS
    assert _get_part_path("styles") == ODF_STYLES
    assert _get_part_path("manifest") == ODF_MANIFEST
    assert _get_part_path("other") == "other"


def test_get_part_class():
    assert _get_part_class(ODF_CONTENT) == Content
    assert _get_part_class(ODF_META) == Meta
    assert _get_part_class(ODF_SETTINGS) == Settings
    assert _get_part_class(ODF_STYLES) == Styles
    assert _get_part_class(ODF_MANIFEST_NAME) == Manifest
    assert _get_part_class("other.xml") is None


def test_document_init_bytes():
    doc = Document(b"text")
    assert doc.container is not None


def test_document_init_path(tmp_path):
    # Create a dummy ODT file
    doc1 = Document("text")
    path = tmp_path / "test.odt"
    doc1.save(path)
    doc2 = Document(str(path))
    assert doc2.container is not None
    assert doc2.path == path


def test_document_init_container():
    container = Container()
    doc = Document(container)
    assert doc.container is container


def test_document_init_bytesio():
    doc1 = Document("text")
    buf = BytesIO()
    doc1.save(buf)
    buf.seek(0)
    doc2 = Document(buf)
    assert doc2.container is not None


def test_document_init_none():
    doc = Document(None)
    assert doc.container is not None
    assert doc.container.path is None


def test_document_init_error():
    with pytest.raises(TypeError, match="Unknown Document source type"):
        Document(123)


def test_document_repr():
    doc = Document("text")
    assert "Document" in repr(doc)
    assert "type=text" in repr(doc)


def test_document_str_not_implemented():
    doc = Document("text")
    with patch.object(Document, "get_formatted_text", side_effect=NotImplementedError):
        res = str(doc)
        assert len(res) >= 0


def test_document_path_property():
    doc = Document("text")
    doc.path = "new/path"
    assert doc.path == Path("new/path")
    doc.container = None
    assert doc.path is None
    doc.path = "other/path"  # returns safely


def test_document_get_parts_no_container():
    doc = Document("text")
    doc.container = None
    with pytest.raises(ValueError, match="Empty Container"):
        doc.get_parts()


def test_document_get_part_non_xml():
    doc = Document("text")
    doc.container.set_part("Pictures/test.png", b"data")
    res = doc.get_part("Pictures/test.png")
    assert res == b"data"


def test_document_get_part_xml_cached():
    doc = Document("text")
    p1 = doc.get_part("content")
    p2 = doc.get_part("content")
    assert p1 is p2


def test_document_get_part_no_container():
    doc = Document("text")
    doc.container = None
    with pytest.raises(ValueError, match="Empty Container"):
        doc.get_part("content")
