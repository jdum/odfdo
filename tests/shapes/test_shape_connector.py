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
from __future__ import annotations

from collections.abc import Iterable

import pytest

from odfdo import Element
from odfdo.document import Document
from odfdo.draw_page import DrawPage
from odfdo.paragraph import Paragraph
from odfdo.shapes import ConnectorShape, EllipseShape, RectangleShape


@pytest.fixture
def body(samples) -> Iterable[Element]:
    document = Document(samples("base_shapes.odg"))
    yield document.body


def test_create_connector():
    page = DrawPage("Page1")
    rectangle = RectangleShape(
        size=("10cm", "20cm"), position=("3cm", "4cm"), draw_id="rectangle"
    )
    ellipse = EllipseShape(
        size=("31cm", "32cm"), position=("35cm", "45cm"), draw_id="ellipse"
    )
    connector = ConnectorShape(
        connected_shapes=(rectangle, ellipse), glue_points=(1, 2)
    )
    page.append(rectangle)
    page.append(ellipse)
    page.append(connector)
    expected = (
        '<draw:page draw:id="Page1">'
        '<draw:rect draw:id="rectangle" '
        'svg:height="20cm" '
        'svg:width="10cm" '
        'svg:x="3cm" '
        'svg:y="4cm">'
        "</draw:rect>"
        '<draw:ellipse draw:id="ellipse" '
        'svg:height="32cm" '
        'svg:width="31cm" '
        'svg:x="35cm" '
        'svg:y="45cm">'
        "</draw:ellipse>"
        "<draw:connector "
        'draw:end-glue-point="2" '
        'draw:end-shape="ellipse" '
        'draw:start-glue-point="1" '
        'draw:start-shape="rectangle">'
        "</draw:connector>"
        "</draw:page>"
    )
    assert page._canonicalize() == expected


def test_get_draw_connector_list(body):
    page = body.get_draw_page()
    connectors = page.get_draw_connectors()
    assert len(connectors) == 1


def test_get_draw_connector_list_regex(body):
    page = body.get_draw_page()
    connectors = page.get_draw_connectors(content="Con")
    assert len(connectors) == 1


def test_get_draw_connector_list_draw_style(body):
    page = body.get_draw_page()
    connectors = page.get_draw_connectors(draw_style="gr4")
    assert len(connectors) == 0


def test_get_draw_connector_list_draw_text_style(body):
    page = body.get_draw_page()
    connectors = page.get_draw_connectors(draw_text_style="P1")
    assert len(connectors) == 1


def test_get_draw_connector_by_content(body):
    page = body.get_draw_page()
    connector = page.get_draw_connector(content="ecteur")
    expected = (
        '<draw:connector draw:end-glue-point="2" '
        'draw:end-shape="id2" '
        'draw:layer="layout" '
        'draw:start-glue-point="1" '
        'draw:start-shape="id1" '
        'draw:style-name="gr1" '
        'draw:text-style-name="P1" '
        'svg:d="M11000 8000h1250v1001h3250v-501" '
        'svg:viewBox="0 0 4501 1002" '
        'svg:x1="11cm" '
        'svg:x2="15.5cm" '
        'svg:y1="8cm" '
        'svg:y2="8.5cm">'
        '<text:p text:style-name="P1">'
        "Connecteur"
        "</text:p>"
        "</draw:connector>"
    )
    print(connector._canonicalize())
    assert connector._canonicalize() == expected


def test_get_draw_connector_by_id(body):
    page = body.get_draw_page()
    connector = ConnectorShape(draw_id="an id")
    page.append(connector)
    connector = page.get_draw_connector(id="an id")
    expected = '<draw:connector draw:id="an id"></draw:connector>'
    assert connector._canonicalize() == expected


def test_get_draw_orphans_connector(body):
    # page = body.get_draw_page()
    orphan_connector = ConnectorShape()
    orphan_connector.append(Paragraph("Orphan c"))
    body.append(orphan_connector)
    connectors = body.get_orphan_draw_connectors()
    assert len(connectors) == 1
