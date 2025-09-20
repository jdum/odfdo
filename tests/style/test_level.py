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
    yield Style("list")


def test_get_level_style(style):
    level_style = style.get_level_style(1)
    assert level_style is None


def test_set_level_style(style):
    style.set_level_style(1, num_format="1")
    level_style = style.get_level_style(1)
    assert level_style is not None


def test_set_level_style_number_missing_format(style):
    with pytest.raises(ValueError):
        style.set_level_style(1)


def test_set_level_style_number(style):
    level_style = style.set_level_style(1, num_format="1")
    assert isinstance(level_style, Style)
    expected = '<text:list-level-style-number text:level="1" fo:num-format="1"/>'
    assert level_style.serialize() == expected


def test_set_level_style_bullet(style):
    level_style = style.set_level_style(2, bullet_char="·")
    assert isinstance(level_style, Style)
    expected = '<text:list-level-style-bullet text:level="2" text:bullet-char="·"/>'
    assert level_style.serialize() == expected


def test_set_level_style_image(style):
    level_style = style.set_level_style(3, url="bullet.png")
    assert isinstance(level_style, Style)
    expected = '<text:list-level-style-image text:level="3" xlink:href="bullet.png"/>'
    assert level_style.serialize() == expected


def test_set_level_style_full(style):
    level_style = style.set_level_style(
        3,
        num_format="1",
        prefix=" ",
        suffix=".",
        display_levels=3,
        start_value=2,
        style="MyList",
    )
    expected = (
        "<text:list-level-style-number "
        'text:level="3" fo:num-format="1" '
        'style:num-prefix=" " style:num-suffix="." '
        'text:display-levels="3" text:start-value="2" '
        'text:style-name="MyList"/>'
    )
    assert level_style.serialize() == expected


def test_set_level_style_clone(style):
    level_1 = style.set_level_style(1, num_format="1")
    level_2 = style.set_level_style(2, display_levels=2, clone=level_1)
    expected = (
        "<text:list-level-style-number "
        'text:level="2" fo:num-format="1" '
        'text:display-levels="2"/>'
    )
    assert level_2.serialize() == expected
