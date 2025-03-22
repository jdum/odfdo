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

from collections.abc import Iterable
from decimal import Decimal

import pytest

from odfdo.const import ODF_CONTENT
from odfdo.container import Container
from odfdo.element import Element
from odfdo.table import Table
from odfdo.xmlpart import XmlPart


@pytest.fixture
def chart_container(samples) -> Iterable[Container]:
    container = Container()
    container.open(samples("chart.odt"))
    yield container


def test_get_element_list(chart_container):
    content_part = XmlPart(ODF_CONTENT, chart_container)
    elements = content_part.get_elements("//text:p")
    assert len(elements) == 4


def test_get_body(chart_container):
    content_part = XmlPart(ODF_CONTENT, chart_container)
    body = content_part.body
    assert body.tag == "office:text"


def test_parts(chart_container):
    parts = chart_container.get_parts()
    assert "mimetype" in parts
    assert "content.xml" in parts
    assert "Object 1/content.xml" in parts


def test_parts_property(chart_container):
    parts = chart_container.parts
    assert "mimetype" in parts
    assert "content.xml" in parts
    assert "Object 1/content.xml" in parts


def test_content_chart(chart_container):
    obj = XmlPart("Object 1/content.xml", chart_container)
    body = obj.body
    assert body is not None
    assert isinstance(body, Element)


def test_rows_columns(chart_container):
    obj = XmlPart("Object 1/content.xml", chart_container)
    body = obj.body
    table = body.get_table(0)
    assert isinstance(table, Table)
    print(table.serialize(pretty=True))
    assert table.width == 4
    assert table.height == 5


def test_read_values(chart_container):
    obj = XmlPart("Object 1/content.xml", chart_container)
    body = obj.body
    table = body.get_table(0)
    values = table.get_values()
    # remove "NaN" results:
    values[1][1] = None
    values[2][1] = None
    values[3][1] = None
    values[4][1] = None
    assert values[0] == [None, "", "Column 2", "Column 3"]
    assert values[1] == ["Row 1", None, 10, 20]
    assert values[2] == ["Row 2", None, 30, 40]
    assert values[3] == ["Row 3", None, 50, 360]
    assert values[4] == ["Row 4", None, Decimal("9.02"), Decimal("6.2")]


def test_change_value(chart_container):
    obj = XmlPart("Object 1/content.xml", chart_container)
    body = obj.body
    table = body.get_table(0)
    table.set_value("A2", "row1 changed")
    table.set_value("D3", 4000)
    values = table.get_values()
    # remove "NaN" results:
    values[1][1] = None
    values[2][1] = None
    values[3][1] = None
    values[4][1] = None
    assert values[0] == [None, "", "Column 2", "Column 3"]
    assert values[1] == ["row1 changed", None, 10, 20]
    assert values[2] == ["Row 2", None, 30, 4000]
    assert values[3] == ["Row 3", None, 50, 360]
    assert values[4] == ["Row 4", None, Decimal("9.02"), Decimal("6.2")]
