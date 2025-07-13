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

from collections.abc import Iterable

import pytest

from odfdo import Element
from odfdo.const import FOLDER
from odfdo.document import Document
from odfdo.element import NEXT_SIBLING
from odfdo.frame import Frame
from odfdo.image import DrawFillImage, DrawImage

IMG_PATH = "Pictures/100002010000012C00000042188DCB81589D2C10.png"


@pytest.fixture
def sample_body(samples) -> Iterable[Element]:
    document = Document(samples("frame_image.odp"))
    yield document.body


def test__draw_fill_image_class():
    dfi = DrawFillImage()
    assert isinstance(dfi, DrawFillImage)


def test_create_image():
    image = DrawImage(IMG_PATH)
    expected = (
        f'<draw:image xlink:href="{IMG_PATH}" xlink:type="simple" '
        'xlink:show="embed" xlink:actuate="onLoad"/>'
    )
    assert image.serialize() == expected


def test_get_image_list(sample_body):
    result = sample_body.get_images()
    assert len(result) == 1
    element = result[0]
    assert element.url == IMG_PATH


def test_get_image_list_property(sample_body):
    result = sample_body.images
    assert len(result) == 1
    element = result[0]
    assert element.url == IMG_PATH


def test_get_image_by_name(sample_body):
    element = sample_body.get_image(name="odfdo")
    assert element.url == IMG_PATH


def test_get_image_by_position(sample_body):
    element = sample_body.get_image(position=0)
    assert element.url == IMG_PATH


def test_get_image_by_path(sample_body):
    element = sample_body.get_image(url=".png")
    assert element.url == IMG_PATH


def test_insert_image(tmp_path, samples):
    document = Document(samples("frame_image.odp"))
    body = document.body
    path = "a/path"
    image = DrawImage(path)
    frame = Frame("Image Frame", size=("0cm", "0cm"), style="Graphics")
    frame.append(image)
    body.get_frame().parent.insert(frame, NEXT_SIBLING)
    element = body.get_image(name="Image Frame")
    assert element.url == path
    element = body.get_image(position=1)
    tmp_file = tmp_path / "frame_image.odp"
    document.save(tmp_file, packaging=FOLDER)
    assert element.url == path


def test_repr(sample_body):
    element = sample_body.get_image(name="odfdo")
    assert repr(element) == "<DrawImage tag=draw:image>"


def test_str(sample_body):
    element = sample_body.get_image(name="odfdo")
    assert str(element) == "\n"  # a pragraph ends with '\n'
