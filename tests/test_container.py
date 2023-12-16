# Copyright 2018-2023 Jérôme Dumonteil
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

from importlib import resources as rso
from os.path import isfile, join
from pathlib import Path

import pytest

from odfdo.const import ODF_CONTENT, ODF_EXTENSIONS
from odfdo.container import Container
from odfdo.utils import to_bytes

SAMPLES = Path(__file__).parent / "samples"


def _copied_template(tmp_path, template):
    src = rso.files("odfdo.templates") / template
    dest = tmp_path / template
    dest.write_bytes(src.read_bytes())
    return dest


def test_bad_template():
    with pytest.raises(OSError):
        Container.new(SAMPLES / "notexisting")


def test_text_template(tmp_path):
    template = _copied_template(tmp_path, "text.ott")
    container = Container.new(template)
    mimetype = container.get_part("mimetype")
    umimetype = container.mimetype
    assert mimetype == to_bytes(ODF_EXTENSIONS["odt"])
    assert umimetype == ODF_EXTENSIONS["odt"]


def test_spreadsheet_template(tmp_path):
    template = _copied_template(tmp_path, "spreadsheet.ots")
    container = Container.new(template)
    mimetype = container.get_part("mimetype")
    umimetype = container.mimetype
    assert mimetype == to_bytes(ODF_EXTENSIONS["ods"])
    assert umimetype == ODF_EXTENSIONS["ods"]


def test_presentation_template(tmp_path):
    template = _copied_template(tmp_path, "presentation.otp")
    container = Container.new(template)
    mimetype = container.get_part("mimetype")
    umimetype = container.mimetype
    assert mimetype == to_bytes(ODF_EXTENSIONS["odp"])
    assert umimetype == ODF_EXTENSIONS["odp"]


def test_drawing_template(tmp_path):
    template = _copied_template(tmp_path, "drawing.otg")
    container = Container.new(template)
    mimetype = container.get_part("mimetype")
    umimetype = container.mimetype
    assert mimetype == to_bytes(ODF_EXTENSIONS["odg"])
    assert umimetype == ODF_EXTENSIONS["odg"]


def test_bad_type():
    with pytest.raises(IOError):
        Container.new("foobar")


def test_bad_type2():
    with pytest.raises(ValueError):
        Container.new(object)


def test_bad_type3():
    with pytest.raises(ValueError):
        Container.new(None)


def test_text_type():
    container = Container.new("text")
    mimetype = container.get_part("mimetype")
    umimetype = container.mimetype
    assert mimetype == to_bytes(ODF_EXTENSIONS["odt"])
    assert umimetype == ODF_EXTENSIONS["odt"]


def test_spreadsheet_type():
    container = Container.new("spreadsheet")
    mimetype = container.get_part("mimetype")
    umimetype = container.mimetype
    assert mimetype == to_bytes(ODF_EXTENSIONS["ods"])
    assert umimetype == ODF_EXTENSIONS["ods"]


def test_presentation_type():
    container = Container.new("presentation")
    mimetype = container.get_part("mimetype")
    umimetype = container.mimetype
    assert mimetype == to_bytes(ODF_EXTENSIONS["odp"])
    assert umimetype == ODF_EXTENSIONS["odp"]


def test_drawing_type():
    container = Container.new("drawing")
    mimetype = container.get_part("mimetype")
    umimetype = container.mimetype
    assert mimetype == to_bytes(ODF_EXTENSIONS["odg"])
    assert umimetype == ODF_EXTENSIONS["odg"]


def test_filesystem():
    path = SAMPLES / "example.odt"
    container = Container()
    container.open(path)
    mimetype = container.get_part("mimetype")
    umimetype = container.mimetype
    assert mimetype == to_bytes(ODF_EXTENSIONS["odt"])
    assert umimetype == ODF_EXTENSIONS["odt"]


def test_clone():
    container = Container.new("text")
    clone = container.clone
    assert clone.path is None


def test_get_part_xml():
    container = Container()
    container.open(SAMPLES / "example.odt")
    content = container.get_part(ODF_CONTENT)
    assert b"<office:document-content" in content


def test_get_part_mimetype():
    container = Container()
    container.open(SAMPLES / "example.odt")
    mimetype = container.get_part("mimetype")
    umimetype = container.mimetype
    assert mimetype == to_bytes(ODF_EXTENSIONS["odt"])
    assert umimetype == ODF_EXTENSIONS["odt"]


def test_mimetype_setter():
    container = Container()
    container.open(SAMPLES / "example.odt")
    container.mimetype = ODF_EXTENSIONS["odt"]
    assert container.mimetype == ODF_EXTENSIONS["odt"]


def test_set_part():
    container = Container()
    container.open(SAMPLES / "example.odt")
    path = join("Pictures", "a.jpg")
    data = to_bytes("JFIFIThinéééékImAnImage")
    container.set_part(path, data)
    assert container.get_part(path) == data


def test_del_part():
    container = Container()
    container.open(SAMPLES / "example.odt")
    # Not a realistic test
    path = "content"
    container.del_part(path)
    with pytest.raises(ValueError):
        container.get_part(path)


def test_save_zip(tmp_path):
    """TODO: 2 cases
    1. from "zip" to "zip"
    2. from "flat" to "zip"
    """
    container = Container()
    container.open(SAMPLES / "example.odt")
    container.save(tmp_path / "example.odt")
    new_container = Container()
    new_container.open(tmp_path / "example.odt")
    mimetype = new_container.get_part("mimetype")
    assert mimetype == to_bytes(ODF_EXTENSIONS["odt"])


def test_save_folder(tmp_path):
    container = Container()
    container.open(SAMPLES / "example.odt")
    path1 = tmp_path / "example.odt"
    container.save(str(path1), packaging="folder")
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


def test_save_folder_pathlib(tmp_path):
    container = Container()
    container.open(SAMPLES / "example.odt")
    path1 = tmp_path / "example.odt"
    container.save(path1, packaging="folder")
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


def test_save_folder_to_zip(tmp_path):
    container = Container()
    container.open(SAMPLES / "example.odt")
    path1 = tmp_path / "example.odt"
    container.save(path1, packaging="folder")
    path = tmp_path / "example.odt.folder" / "mimetype"
    assert isfile(path)
    new_container = Container()
    new_container.open(tmp_path / "example.odt.folder")
    path2 = tmp_path / "example_bis.odt"
    new_container.save(path2, packaging="zip")
    new_container_zip = Container()
    new_container_zip.open(path2)
    mimetype = new_container_zip.get_part("mimetype")
    assert mimetype == to_bytes(ODF_EXTENSIONS["odt"])


def test_load_folder(tmp_path):
    container = Container()
    container.open(SAMPLES / "example.odt")
    path1 = tmp_path / "example_f.odt"
    container.save(path1, packaging="folder")
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


def test_repr():
    container = Container()
    container.open(SAMPLES / "example.odt")
    result = repr(container)
    assert result.startswith("<Container type=application/vnd.oasis.opendocument.text")
    assert " path=" in result
    assert result.endswith("amples/example.odt>")


def test_str():
    container = Container()
    container.open(SAMPLES / "example.odt")
    assert str(container) == repr(container)
