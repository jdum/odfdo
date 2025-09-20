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

import base64
import io

from odfdo.document import Blob


def test_blob_null():
    blob = Blob()
    assert blob.content == b""
    assert blob.name == ""
    assert blob.mime_type == ""


def test_blob_png(samples):
    png = samples("image.png")
    blob = Blob.from_path(png)
    assert blob.name == "ceddccf10506d07cc0990639e79f8c72.png"
    assert blob.mime_type == "image/png"


def test_blob_png_content(samples):
    png = samples("image.png")
    expected = png.read_bytes()
    blob = Blob.from_path(png)
    assert blob.content == expected


def test_blob_png_str(samples):
    png = str(samples("image.png"))
    blob = Blob.from_path(png)
    assert blob.name == "ceddccf10506d07cc0990639e79f8c72.png"
    assert blob.mime_type == "image/png"


def test_blob_png_content_str(samples):
    png = samples("image.png")
    expected = png.read_bytes()
    blob = Blob.from_path(str(png))
    assert blob.content == expected


def test_blob_jpg(samples):
    png = samples("image2.jpg")
    blob = Blob.from_path(png)
    assert blob.name == "b011604234764865b75f7dbd903992de.jpg"
    assert blob.mime_type == "image/jpeg"


def test_blob_jpg_content(samples):
    png = samples("image2.jpg")
    expected = png.read_bytes()
    blob = Blob.from_path(png)
    assert blob.content == expected


def test_blob_io(samples):
    png = samples("image.png")
    with io.BytesIO() as bytes_content:
        bytes_content.write(png.read_bytes())
        bytes_content.seek(0)
        blob = Blob.from_io(bytes_content)
    assert blob.name == "ceddccf10506d07cc0990639e79f8c72"
    assert blob.mime_type == "application/octet-stream"


def test_blob_io_content(samples):
    png = samples("image.png")
    expected = png.read_bytes()
    with io.BytesIO() as bytes_content:
        bytes_content.write(png.read_bytes())
        bytes_content.seek(0)
        blob = Blob.from_io(bytes_content)
    assert blob.content == expected


def test_blob_b64(samples):
    png = samples("image.png")
    content = png.read_bytes()
    b64string = base64.standard_b64encode(content)
    blob = Blob.from_base64(b64string, "image/png")
    assert blob.name == "ceddccf10506d07cc0990639e79f8c72"
    assert blob.mime_type == "image/png"


def test_blob_b64_content(samples):
    png = samples("image.png")
    content = png.read_bytes()
    b64string = base64.standard_b64encode(content)
    blob = Blob.from_base64(b64string, "image/png")
    assert blob.content == content
