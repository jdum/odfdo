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
import io
from collections.abc import Iterable

import pytest

from odfdo import Document, Frame, Paragraph


@pytest.fixture
def doc_xml(samples) -> Iterable:
    doc = Document("odt")
    doc.body.clear()
    img_url = doc.add_file(samples("image.png"))
    image_frame = Frame.image_frame(
        img_url,
        size=("6cm", "4cm"),
        position=("5cm", "10cm"),
    )
    paragraph = Paragraph()
    paragraph.append(image_frame)
    doc.body.append(paragraph)
    with io.BytesIO() as bytes_content:
        doc.save(bytes_content, packaging="xml")
        xml_content = bytes_content.getvalue()
    yield xml_content.decode()


def test_save_xml_header(doc_xml):
    assert doc_xml.startswith('<?xml version="1.0" encoding="UTF-8"?>')


def test_save_xml_header_2(doc_xml):
    assert (
        'office:version="1.2" office:mimetype="application/vnd.oasis.opendocument.text">'
        in doc_xml
    )


def test_save_xml_header_meta(doc_xml):
    assert "<office:meta>" in doc_xml
    assert "    <meta:creation-date>" in doc_xml


def test_save_xml_settings(doc_xml):
    assert "<office:settings>" in doc_xml
    assert "<office:font-face-decls>" in doc_xml


def test_save_xml_styles(doc_xml):
    assert "  <office:styles>" in doc_xml
    assert "<office:font-face-decls>" in doc_xml
    assert "  </office:master-styles>" in doc_xml
    assert "<office:scripts/>" in doc_xml


def test_save_xml_content_1(doc_xml):
    assert "  <office:body>" in doc_xml
    assert "    <office:text>" in doc_xml


def test_save_xml_content_2(doc_xml):
    assert "  <office:body>" in doc_xml
    assert (
        '<text:p><draw:frame svg:width="6cm" svg:height="4cm" draw:z-index="0" '
        'svg:x="5cm" svg:y="10cm" text:anchor-type="paragraph">'
    ) in doc_xml


def test_save_xml_content_3(doc_xml):
    assert (
        """<office:body>\n    <office:text>\n      <text:p><draw:frame svg:width="6cm" svg:height="4cm" draw:z-index="0" svg:x="5cm" svg:y="10cm" text:anchor-type="paragraph">\n          <draw:image draw:mime-type="None">\n            <office:binary-data>iVBORw0KGgoAAAANSUhEUgAAAQEAAACWCAIAAABRmqrlAAA\n             gAElEQVR42sy9WbNl13Emlrn23me881BzFVAAAQICAYiSKFJqWU1Ft4ZWh93q6AjZc\n             jjkB3dH2yF32B1hh/vF0WH7wREOv/lFP6LpoEJPDskaqHATpCgQ4NAFEFUACjXeeTj\n             nnmEPmX5Ya2Xm2qcIVBVAUZeMwq17b91z9t5rrcz88vu+xBf+xXMAgIwAzAgAAAwAA\n             AjIwIgIzAwQPkFEZv8D/qcQgIEBkAH8nwQA6IjDX+XrjMiAxEDgCJDANQjMiOgQ0QE\n             6xPAXRAfh88VPEJ0DQEQHLnwLAcE5ROeyHF2OWeZc7lyGLndZji5zLnNZ7tABEwEzE\n             zMQEDExEwMTM5P/FhMQ+y8AMYP/GQImYgAK3/P/FpiIgBqmBpqGqQEmoAaoZiKgBpo\n             GuGEiaOJXqAFuuGkg/pWpAarlr0ANE4FzDh26zKFD5xAzlyGg/ys6f9X+v+ET5wbzH\n             AGA/bNADI8RgPzTC8/I+S8TICAAuBxdjlg4V6ArHBbgCuc6iDm6wmUdhwW6wrkOYOF\n             c7rIOxq84V6DrOHQAfvUQMDETQgPcINcMDXINXCPXTBVyDVwBl8g1UIl665kYiInYP\n             wD2n5C/0ez/JPvDzEwEFJ4kNEThJ4mponnZVHVTVvW8pLJuyqopAQEY/J8Y7gtwuCH\n             +1iCzX/1hHwCwv2PM7O8VAyMgyO1Ffw/9BgD0X407IWwn9j/FGF7c/2v/Hvwbkt+F8\n             szis4q/DhEQ/Y+A7lH5xfKkARAZEBH92wmf+u3rHGLc5uxfhRniZuZ4f+J7jHvXX17\n             c9AjE/ivEHL/jP+N4IPhfDPItAGZk8lcWXpb8QvVvwX8Rw7+INzxcQrgN4XaZ2x6/7\n """
        in doc_xml
    )


def test_save_xml_content_4(doc_xml):
    assert (
        """hkbURB7PoCAhFR0bz/EXZ7JPVMSkBEgml5zuMUwo1moOKorWguyVhzeISVkKDbCxGN\n             UzWNqnRGbIfMI8bzeWyjgUs47CfqaNil6wJJrkPIBFi/SiwnhpJEuFmx2vNjm6BSoO\n             jw2AcUXtrC57rMOFUA1nEsXwy0DS836Bex0zmEW4c2MxYWmnZlk7TbO8psQCkFYqbm\n             bfGRioTF7e1k0LzdTRyXRrpPQ/aapClaKORetzz3eOB4BNm4iKyWaw5ihB4xIcAr4F\n             RbDmJyJm+Spui8eRW2TUR3uB2qGIbcneOLjyjZMNgvQnKAH/t6cmjLN+Bctd1Xy2mu\n             wFrh2O8FEukiITFzIiwFlq9c51gMoWIifw3Ge2aEHd+GkwAAAAASUVORK5CYII=\n            </office:binary-data>\n          </draw:image>\n        </draw:frame>\n      </text:p>\n    </office:text>\n  </office:body>\n</office:document>\n"""
        in doc_xml
    )
