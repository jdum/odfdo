# Copyright 2018-2024 Jérôme Dumonteil
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
from pathlib import Path

import pytest

from odfdo.document import Document

SAMPLES = Path(__file__).parent / "samples"


@pytest.fixture
def document() -> Iterable:
    doc = Document("odt")
    doc.body.clear()
    yield doc


def test_add_file_non_exists(document):
    with pytest.raises(FileNotFoundError):
        document.add_file("non exists")


def test_add_file_manifest(document):
    document.add_file(SAMPLES / "image.png")
    manifest = document.manifest
    paths = manifest.get_path_medias()
    assert ("Pictures/ceddccf10506d07cc0990639e79f8c72.png", "image/png") in paths


def test_add_file_get_part(document):
    png = SAMPLES / "image.png"
    document.add_file(png)
    expected = png.read_bytes()
    container = document.container
    content = container.get_part("Pictures/ceddccf10506d07cc0990639e79f8c72.png")
    assert content == expected
