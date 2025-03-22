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
#          David Versmisse <david.versmisse@itaapy.com>

from collections.abc import Iterable

import pytest

from odfdo.const import ODF_MANIFEST, ODF_PRESENTATION
from odfdo.document import Document
from odfdo.manifest import Manifest

IMG_PATH = "Pictures/100002010000012C00000042188DCB81589D2C10.png"


@pytest.fixture
def base_manifest(samples) -> Iterable[Manifest]:
    document = Document(samples("frame_image.odp"))
    yield document.get_part(ODF_MANIFEST)


def test_get_manifest(base_manifest):
    assert isinstance(base_manifest, Manifest)


def test_get_path_list(base_manifest):
    results = base_manifest.get_paths()
    assert len(results) == 9


def test_get_path_media_list(base_manifest):
    results = base_manifest.get_path_medias()
    assert len(results) == 9
    root = results[0]
    assert root == ("/", ODF_PRESENTATION)


def test_get_media_type_root(base_manifest):
    assert base_manifest.get_media_type("/") == ODF_PRESENTATION


def test_get_media_type_directory(base_manifest):
    assert base_manifest.get_media_type("Pictures/") is None


def test_get_media_type_other(base_manifest):
    assert base_manifest.get_media_type(IMG_PATH) == "image/png"


def test_get_media_type_missing(base_manifest):
    assert base_manifest.get_media_type("LpOD") is None


def test_set_media_type(base_manifest):
    assert base_manifest.get_media_type(IMG_PATH) == "image/png"
    base_manifest.set_media_type(IMG_PATH, "image/jpeg")
    assert base_manifest.get_media_type(IMG_PATH) == "image/jpeg"


def test_set_media_type_missing(base_manifest):
    with pytest.raises(KeyError):
        base_manifest.set_media_type("LpOD", "")


def test_add_full_path(base_manifest):
    assert base_manifest.get_media_type("LpOD") is None
    base_manifest.add_full_path("LpOD", "")
    assert base_manifest.get_media_type("LpOD") == ""


def test_add_full_path_existing(base_manifest):
    assert base_manifest.get_media_type(IMG_PATH) == "image/png"
    base_manifest.add_full_path(IMG_PATH, "image/jpeg")
    assert base_manifest.get_media_type(IMG_PATH) == "image/jpeg"


def test_del_full_path(base_manifest):
    assert base_manifest.get_media_type(IMG_PATH) == "image/png"
    base_manifest.del_full_path(IMG_PATH)
    assert base_manifest.get_media_type(IMG_PATH) is None


def test_repr(base_manifest):
    assert repr(base_manifest) == "<Manifest part_name=META-INF/manifest.xml>"


def test_str(base_manifest):
    assert str(base_manifest) == repr(base_manifest)
