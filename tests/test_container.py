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
#          Luis Belmar-Letelier <luis@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>

from os.path import isfile, join

import pytest

from odfdo.const import (
    FOLDER,
    ODF_CONTENT,
    ODF_EXTENSIONS,
    ODF_MANIFEST,
    ODF_META,
    ODF_SETTINGS,
    ODF_STYLES,
    ODF_TEXT,
    ZIP,
)
from odfdo.container import Container
from odfdo.utils import to_bytes


def test_filesystem(samples):
    path = samples("example.odt")
    container = Container()
    container.open(path)
    mimetype = container.get_part("mimetype")
    umimetype = container.mimetype
    assert mimetype == to_bytes(ODF_EXTENSIONS["odt"])
    assert umimetype == ODF_EXTENSIONS["odt"]


def test_get_part_xml(samples):
    container = Container()
    container.open(samples("example.odt"))
    content = container.get_part(ODF_CONTENT)
    assert b"<office:document-content" in content


def test_get_part_mimetype(samples):
    container = Container()
    container.open(samples("example.odt"))
    mimetype = container.get_part("mimetype")
    umimetype = container.mimetype
    assert mimetype == to_bytes(ODF_EXTENSIONS["odt"])
    assert umimetype == ODF_EXTENSIONS["odt"]


def test_mimetype_setter(samples):
    container = Container()
    container.open(samples("example.odt"))
    container.mimetype = ODF_EXTENSIONS["odt"]
    assert container.mimetype == ODF_EXTENSIONS["odt"]


def test_set_part(samples):
    container = Container()
    container.open(samples("example.odt"))
    path = join("Pictures", "a.jpg")
    data = to_bytes("JFIFIThinéééékImAnImage")
    container.set_part(path, data)
    assert container.get_part(path) == data


def test_del_part(samples):
    container = Container()
    container.open(samples("example.odt"))
    # Not a realistic test
    path = "content"
    container.del_part(path)
    with pytest.raises(ValueError):
        container.get_part(path)


def test_save_zip(tmp_path, samples):
    """TODO: 2 cases
    1. from ZIP to ZIP
    2. from "flat" to ZIP
    """
    container = Container()
    container.open(samples("example.odt"))
    container.save(tmp_path / "example.odt")
    new_container = Container()
    new_container.open(tmp_path / "example.odt")
    mimetype = new_container.get_part("mimetype")
    assert mimetype == to_bytes(ODF_EXTENSIONS["odt"])


def test_save_folder(tmp_path, samples):
    container = Container()
    container.open(samples("example.odt"))
    path1 = tmp_path / "example.odt"
    container.save(str(path1), packaging=FOLDER)
    path = tmp_path / "example.odt.folder" / "mimetype"
    assert isfile(path)
    path = tmp_path / "example.odt.folder" / "content.xml"
    assert isfile(path)
    path = tmp_path / "example.odt.folder" / "meta.xml"
    assert isfile(path)
    path = tmp_path / "example.odt.folder" / "styles.xml"
    assert isfile(path)
    path = tmp_path / "example.odt.folder" / "settings.xml"
    assert isfile(path)


def test_save_folder_pathlib(tmp_path, samples):
    container = Container()
    container.open(samples("example.odt"))
    path1 = tmp_path / "example.odt"
    container.save(path1, packaging=FOLDER)
    path = tmp_path / "example.odt.folder" / "mimetype"
    assert isfile(path)
    path = tmp_path / "example.odt.folder" / "content.xml"
    assert isfile(path)
    path = tmp_path / "example.odt.folder" / "meta.xml"
    assert isfile(path)
    path = tmp_path / "example.odt.folder" / "styles.xml"
    assert isfile(path)
    path = tmp_path / "example.odt.folder" / "settings.xml"
    assert isfile(path)


def test_save_folder_to_zip(tmp_path, samples):
    container = Container()
    container.open(samples("example.odt"))
    path1 = tmp_path / "example.odt"
    container.save(path1, packaging=FOLDER)
    path = tmp_path / "example.odt.folder" / "mimetype"
    assert isfile(path)
    new_container = Container()
    new_container.open(tmp_path / "example.odt.folder")
    path2 = tmp_path / "example_bis.odt"
    new_container.save(path2, packaging=ZIP)
    new_container_zip = Container()
    new_container_zip.open(path2)
    mimetype = new_container_zip.get_part("mimetype")
    assert mimetype == to_bytes(ODF_EXTENSIONS["odt"])


def test_load_folder(tmp_path, samples):
    container = Container()
    container.open(samples("example.odt"))
    path1 = tmp_path / "example_f.odt"
    container.save(path1, packaging=FOLDER)
    new_container = Container()
    new_container.open(tmp_path / "example_f.odt.folder")
    content = new_container.get_part(ODF_CONTENT)
    assert b"<office:document-content" in content
    mimetype = new_container.get_part("mimetype")
    assert mimetype == to_bytes(ODF_EXTENSIONS["odt"])
    path = join("Pictures", "a.jpg")
    data = to_bytes("JFIFIThiééénkImA §ççànImage")
    new_container.set_part(path, data)
    assert new_container.get_part(path) == to_bytes(data)
    # Not a realistic test
    path = "content"
    new_container.del_part(path)
    with pytest.raises(ValueError):
        new_container.get_part(path)


def test_repr_empty():
    container = Container()
    assert repr(container) == "<Container type= path=None>"


def test_str_empty():
    container = Container()
    assert str(container) == repr(container)


def test_repr(samples):
    container = Container()
    container.open(samples("example.odt"))
    result = repr(container)
    assert result.startswith("<Container type=application/vnd.oasis.opendocument.text")
    assert " path=" in result
    assert result.endswith("example.odt>")


def test_str(samples):
    container = Container()
    container.open(samples("example.odt"))
    assert str(container) == repr(container)


def test_default_manifest_rdf():
    container = Container()
    assert "rdf:RDF" in container.default_manifest_rdf


def test_manifest_rdf_0(tmp_path, samples):
    base = Container()
    base.open(samples("example.odt"))
    content = base.get_part(ODF_CONTENT)
    styles = base.get_part(ODF_STYLES)
    container = Container()
    container.set_part(ODF_CONTENT, content)
    container.set_part(ODF_STYLES, styles)
    container.mimetype = ODF_TEXT
    expected = {ODF_CONTENT, ODF_STYLES, "mimetype"}
    assert set(container.parts) == expected


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
    path = tmp_path / "example.odt"
    container.save(path, packaging=ZIP)
    new_container = Container()
    new_container.open(path)
    mimetype = new_container.get_part("mimetype")
    assert mimetype.decode() == ODF_TEXT


def test_manifest_rdf_3(tmp_path, samples):
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
    path = tmp_path / "example.odt"
    container.save(path, packaging=ZIP)
    new_container = Container()
    new_container.open(path)
    content2 = new_container.get_part(ODF_CONTENT)
    assert content2 == content
