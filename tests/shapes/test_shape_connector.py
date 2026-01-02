# Copyright 2018-2026 Jérôme Dumonteil
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


@pytest.fixture
def connector() -> Iterable[ConnectorShape]:
    shape1 = RectangleShape(draw_id="31")
    shape2 = RectangleShape(draw_id="32")
    shape = ConnectorShape(
        name="some name",
        style="style name",
        text_style="text style",
        draw_id="draw_id",
        layer="layer",
        connected_shapes=(shape1, shape2),
        glue_points=("100", "200"),
        p1=("1cm", "2cm"),
        p2=("3cm", "4cm"),
        line_skew="5",
        svg_d="6",
        view_box="view box",
        presentation_class="pres class",
        presentation_style="pres style",
        caption_id="capid",
        class_names="class1",
        transform="tr1",
        z_index=4,
        end_cell_address="x10",
        end_x="10",
        end_y="20",
        table_background=True,
        anchor_type="page",
        anchor_page=42,
        xml_id="xmlid",
    )
    shape.svg_title = "title"
    yield shape


def test_connectorshape_minimal():
    shape = ConnectorShape()
    assert shape._canonicalize() == "<draw:connector></draw:connector>"


def test_connectorshape_class():
    shape = Element.from_tag("<draw:connector/>")
    assert isinstance(shape, ConnectorShape)


def test_connectorshape_connected_shapes_1(connector):
    assert connector.connected_shapes == ("31", "32")


def test_connectorshape_connected_shapes_2(connector):
    assert connector.start_shape == "31"


def test_connectorshape_connected_shapes_3(connector):
    assert connector.end_shape == "32"


def test_connectorshape_connected_shapes_4(connector):
    connector.connected_shapes = None
    assert connector.connected_shapes == (None, None)


def test_connectorshape_glue_points_1(connector):
    assert connector.glue_points == ("100", "200")


def test_connectorshape_glue_points_2(connector):
    assert connector.start_glue_point == "100"


def test_connectorshape_glue_points_3(connector):
    assert connector.end_glue_point == "200"


def test_connectorshape_glue_points_4(connector):
    connector.glue_points = None
    assert connector.glue_points == (None, None)


def test_connectorshape_p1_1(connector):
    assert connector.p1 == ("1cm", "2cm")


def test_connectorshape_p1_2(connector):
    assert connector.x1 == "1cm"


def test_connectorshape_p1_3(connector):
    assert connector.y1 == "2cm"


def test_connectorshape_p1_4(connector):
    connector.p1 = None
    assert connector.p1 == (None, None)


def test_connectorshape_p2_1(connector):
    assert connector.p2 == ("3cm", "4cm")


def test_connectorshape_p2_2(connector):
    assert connector.x2 == "3cm"


def test_connectorshape_p2_3(connector):
    assert connector.y2 == "4cm"


def test_connectorshape_p2_4(connector):
    connector.p2 = None
    assert connector.p2 == (None, None)


def test_connectorshape_draw_type_1(connector):
    assert connector.draw_type == "standard"


def test_connectorshape_draw_type_2(connector):
    connector.draw_type = "curve"
    assert connector.draw_type == "curve"


def test_connectorshape_draw_type_3(connector):
    with pytest.raises(TypeError):
        connector.draw_type = "bad"


def test_connectorshape_draw_type_4():
    connector = ConnectorShape(draw_type="line")
    assert connector.draw_type == "line"


def test_create_connectorshape():
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


def test_page_get_draw_connector_list(body):
    page = body.get_draw_page()
    connectors = page.get_draw_connectors()
    assert len(connectors) == 1


def test_page_get_draw_connector_list_regex(body):
    page = body.get_draw_page()
    connectors = page.get_draw_connectors(content="Con")
    assert len(connectors) == 1


def test_page_get_draw_connector_list_draw_style(body):
    page = body.get_draw_page()
    connectors = page.get_draw_connectors(draw_style="gr4")
    assert len(connectors) == 0


def test_page_get_draw_connector_list_draw_text_style(body):
    page = body.get_draw_page()
    connectors = page.get_draw_connectors(draw_text_style="P1")
    assert len(connectors) == 1


def test_page_get_draw_connector_by_content(body):
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
    assert connector._canonicalize() == expected


def test_page_get_draw_connector_by_id(body):
    page = body.get_draw_page()
    connector = ConnectorShape(draw_id="an id")
    page.append(connector)
    connector = page.get_draw_connector(id="an id")
    expected = '<draw:connector draw:id="an id"></draw:connector>'
    assert connector._canonicalize() == expected


def test_page_get_draw_orphans_connector(body):
    # page = body.get_draw_page()
    orphan_connector = ConnectorShape()
    orphan_connector.append(Paragraph("Orphan c"))
    body.append(orphan_connector)
    connectors = body.get_orphan_draw_connectors()
    assert len(connectors) == 1
