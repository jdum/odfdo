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

from collections.abc import Iterable

import pytest

from odfdo.const import ODF_CONTENT
from odfdo.container import Container
from odfdo.style import Style
from odfdo.xmlpart import XmlPart


@pytest.fixture
def style_element(samples) -> Iterable[Style]:
    container = Container(samples("example.odt"))
    content_part = XmlPart(ODF_CONTENT, container)
    query = '//style:style[@style:family="paragraph"][1]'
    yield content_part.get_element(query)


def test_odf_style(style_element):
    assert isinstance(style_element, Style)


def test_get_style_properties(style_element):
    style = style_element
    properties = style.get_properties()
    assert isinstance(properties, dict)
    assert len(properties) == 12
    assert properties["fo:margin-left"] == "0cm"


def test_get_style_properties_area(style_element):
    style = style_element
    properties = style.get_properties(area="text")
    assert isinstance(properties, dict)
    assert len(properties) == 1
    assert properties["fo:hyphenate"] == "false"


def test_get_style_properties_bad_element(samples):
    container = Container(samples("example.odt"))
    content_part = XmlPart(ODF_CONTENT, container)
    paragraph_element = content_part.get_element("//text:p[1]")
    with pytest.raises(AttributeError):
        paragraph_element.get_properties()


def test_get_style_properties_bad_area(style_element):
    style = style_element
    properties = style.get_properties(area="toto")
    assert properties is None


def test_set_style_properties(style_element):
    style = style_element
    style.set_properties({"fo:color": "#f00"})
    properties = style.get_properties()
    assert len(properties) == 13
    assert properties["fo:color"] == "#f00"


def test_set_style_properties_area(style_element):
    style = style_element
    style.set_properties({"fo:color": "#f00"}, area="text")
    properties = style.get_properties(area="text")
    assert len(properties) == 2
    assert properties["fo:color"] == "#f00"


def test_set_style_properties_new_area(style_element):
    style = style_element
    properties = style.get_properties(area="chart")
    assert properties is None
    style.set_properties({"fo:color": "#f00"}, area="chart")
    properties = style.get_properties(area="chart")
    assert len(properties) == 1
    assert properties["fo:color"] == "#f00"


def test_del_style_properties(style_element):
    style = style_element
    style.del_properties(["fo:margin-left"])
    properties = style.get_properties()
    assert len(properties) == 11
    with pytest.raises(KeyError):
        _dummy = properties["fo:margin-left"]


def test_del_style_properties_bad_area(style_element):
    style = style_element
    with pytest.raises(ValueError):
        style.del_properties(area="foobar")
