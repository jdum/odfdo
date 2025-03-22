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

from collections.abc import Iterable
from os.path import isfile

import pytest

from odfdo.const import (
    FOLDER,
    ODF_CONTENT,
    ODF_MANIFEST,
    ODF_MANIFEST_RDF,
    ODF_META,
    ODF_SETTINGS,
    ODF_STYLES,
    ODF_TEXT,
    ZIP,
)
from odfdo.container import Container
from odfdo.document import Document


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
