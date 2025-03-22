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

from odfdo.style import Style


@pytest.fixture
def style() -> Iterable[Style]:
    yield Style("paragraph")


def test_bad_family():
    style = Style("master-page")
    pytest.raises(TypeError, style.set_background)


def test_color(style):
    style.set_background(color="#abcdef")
    expected = (
        '<style:style style:family="paragraph">'
        "<style:paragraph-properties "
        'fo:background-color="#abcdef"/>'
        "</style:style>"
    )
    assert style.serialize() == expected


def test_image(style):
    style.set_background(url="Pictures/toto")
    expected = (
        '<style:style style:family="paragraph">'
        "<style:paragraph-properties "
        'fo:background-color="transparent">'
        "<style:background-image "
        'xlink:href="Pictures/toto" '
        'style:position="center"/>'
        "</style:paragraph-properties>"
        "</style:style>"
    )
    assert style.serialize() == expected


def test_image_full(style):
    style.set_background(
        url="Pictures/toto",
        position="top left",
        repeat="no-repeat",
        opacity=50,
        filter="myfilter",
    )
    expected = (
        '<style:style style:family="paragraph">'
        "<style:paragraph-properties "
        'fo:background-color="transparent">'
        "<style:background-image "
        'xlink:href="Pictures/toto" '
        'style:position="top left" '
        'style:repeat="no-repeat" '
        'draw:opacity="50" '
        'style:filter-name="myfilter"/>'
        "</style:paragraph-properties>"
        "</style:style>"
    )
    assert style.serialize() == expected
