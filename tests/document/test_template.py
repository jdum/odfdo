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


import pytest

from odfdo.const import ODF_EXTENSIONS
from odfdo.document import container_from_template
from odfdo.utils import to_bytes


def test_bad_template():
    with pytest.raises(FileNotFoundError):
        container_from_template("notexisting")


def test_text_template(tmp_path):
    container = container_from_template("text")
    mimetype = container.get_part("mimetype")
    umimetype = container.mimetype
    assert mimetype == to_bytes(ODF_EXTENSIONS["odt"])
    assert umimetype == ODF_EXTENSIONS["odt"]


def test_spreadsheet_template(tmp_path):
    container = container_from_template("spreadsheet")
    mimetype = container.get_part("mimetype")
    umimetype = container.mimetype
    assert mimetype == to_bytes(ODF_EXTENSIONS["ods"])
    assert umimetype == ODF_EXTENSIONS["ods"]


def test_presentation_template(tmp_path):
    container = container_from_template("presentation")
    mimetype = container.get_part("mimetype")
    umimetype = container.mimetype
    assert mimetype == to_bytes(ODF_EXTENSIONS["odp"])
    assert umimetype == ODF_EXTENSIONS["odp"]


def test_drawing_template(tmp_path):
    container = container_from_template("drawing")
    mimetype = container.get_part("mimetype")
    umimetype = container.mimetype
    assert mimetype == to_bytes(ODF_EXTENSIONS["odg"])
    assert umimetype == ODF_EXTENSIONS["odg"]


def test_bad_type():
    with pytest.raises(FileNotFoundError):
        container_from_template("foobar")


def test_bad_type2():
    with pytest.raises(TypeError):
        container_from_template(object)


def test_bad_type3():
    with pytest.raises(TypeError):
        container_from_template(None)


def test_text_type():
    container = container_from_template("text")
    mimetype = container.get_part("mimetype")
    umimetype = container.mimetype
    assert mimetype == to_bytes(ODF_EXTENSIONS["odt"])
    assert umimetype == ODF_EXTENSIONS["odt"]


def test_spreadsheet_type():
    container = container_from_template("spreadsheet")
    mimetype = container.get_part("mimetype")
    umimetype = container.mimetype
    assert mimetype == to_bytes(ODF_EXTENSIONS["ods"])
    assert umimetype == ODF_EXTENSIONS["ods"]


def test_presentation_type():
    container = container_from_template("presentation")
    mimetype = container.get_part("mimetype")
    umimetype = container.mimetype
    assert mimetype == to_bytes(ODF_EXTENSIONS["odp"])
    assert umimetype == ODF_EXTENSIONS["odp"]


def test_drawing_type():
    container = container_from_template("drawing")
    mimetype = container.get_part("mimetype")
    umimetype = container.mimetype
    assert mimetype == to_bytes(ODF_EXTENSIONS["odg"])
    assert umimetype == ODF_EXTENSIONS["odg"]


def test_clone():
    container = container_from_template("text")
    clone = container.clone
    assert clone.path is None
