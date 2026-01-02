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

from collections.abc import Iterable

import pytest

from odfdo.const import ODF_STYLES
from odfdo.document import Document
from odfdo.style import Style
from odfdo.style_utils import (
    _check_background_support,
    _check_opacity,
    _check_position,
    _check_repeat,
    _erase_background,
    _map_key,
    _set_background,
    _set_background_color,
    _set_background_image,
)
from odfdo.styles import Styles


@pytest.fixture
def styles(samples) -> Iterable[Styles]:
    document = Document(samples("example.odt"))
    yield document.get_part(ODF_STYLES)


def test_check_background_support():
    assert _check_background_support("text") is None


def test_check_background_support_raise():
    with pytest.raises(TypeError):
        _check_background_support("oops")


def test_check_position_none():
    assert _check_position(None) is None


def test_check_position():
    assert _check_position("center") is None


def test_check_position_raise_1():
    with pytest.raises(ValueError):
        _check_position(" ")


def test_check_position_raise_2():
    with pytest.raises(ValueError):
        _check_position("oops")


def test_check_repeat_none():
    assert _check_repeat(None) is None


def test_check_repeat():
    assert _check_repeat("repeat") is None


def test_check_repeat_raise_1():
    with pytest.raises(ValueError):
        _check_repeat(" ")


def test_check_repeat_raise_2():
    with pytest.raises(ValueError):
        _check_repeat("oops")


def test_check_opacity_none():
    assert _check_opacity(None) is None


def test_check_opacity_int():
    assert _check_opacity(50) is None


def test_check_opacity_str():
    assert _check_opacity("50") is None


def test_check_opacity_raise_1():
    with pytest.raises(ValueError):
        _check_opacity("oops")


def test_check_opacity_raise_2():
    with pytest.raises(ValueError):
        _check_opacity(-1)


def test_check_opacity_raise_3():
    with pytest.raises(ValueError):
        _check_opacity(999)


def test_check_opacity_raise_4():
    with pytest.raises(ValueError):
        _check_opacity("-1")


def test_check_opacity_raise_5():
    with pytest.raises(ValueError):
        _check_opacity("999")


def test_find_page_layout(styles):
    auto = styles.office_automatic_styles
    layouts = auto.get_elements("style:page-layout")
    lay = layouts[0]
    assert lay.name == "Mpm1"


def test_erase_background(styles):
    auto = styles.office_automatic_styles
    layouts = auto.get_elements("style:page-layout")
    lay = layouts[0]
    assert _erase_background(lay) is None


def test_erase_background_2(styles):
    auto = styles.office_automatic_styles
    layouts = auto.get_elements("style:page-layout")
    lay = layouts[0]
    properties = lay.get_element("style:page-layout-properties")
    properties.delete()
    assert _erase_background(lay) is None


def test_set_background_color_1(styles):
    auto = styles.office_automatic_styles
    layouts = auto.get_elements("style:page-layout")
    lay = layouts[0]
    assert _set_background_color(lay, "#FFFFFF") is None


def test_erase_background_3(styles):
    auto = styles.office_automatic_styles
    layouts = auto.get_elements("style:page-layout")
    lay = layouts[0]
    _set_background_color(lay, "#FFFFFF")
    assert _erase_background(lay) is None


def test_set_background_image_1(styles):
    auto = styles.office_automatic_styles
    layouts = auto.get_elements("style:page-layout")
    lay = layouts[0]
    assert (
        _set_background_image(lay, "http://example.com/aaa", None, None, None, None)
        is None
    )


def test_erase_background_4(styles):
    auto = styles.office_automatic_styles
    layouts = auto.get_elements("style:page-layout")
    lay = layouts[0]
    _set_background_image(lay, "http://example.com/aaa", None, None, None, None)
    assert _erase_background(lay) is None


def test_set_background_color_2(styles):
    auto = styles.office_automatic_styles
    layouts = auto.get_elements("style:page-layout")
    lay = layouts[0]
    _set_background_image(lay, "http://example.com/aaa", None, None, None, None)
    assert _set_background_color(lay, "#FFFFFF") is None


def test_set_background_image_2(styles):
    auto = styles.office_automatic_styles
    layouts = auto.get_elements("style:page-layout")
    lay = layouts[0]
    _set_background_image(lay, "http://example.com/aaa", None, None, None, None)
    assert (
        _set_background_image(lay, "http://example.com/bbb", None, None, None, None)
        is None
    )


def test_set_background_1(styles):
    auto = styles.office_automatic_styles
    layouts = auto.get_elements("style:page-layout")
    lay = layouts[0]
    _set_background_image(lay, "http://example.com/aaa", None, None, None, None)
    assert _set_background(lay, None, None, None, None, None, None) is None


def test_set_background_text_style(styles):
    style = Style("text", name="name", area="text")
    with pytest.raises(TypeError):
        _set_background(style, None, "http://example.com/aaa", None, None, None, None)


def test_map_key_known():
    key = "chart:angle-offset"
    odf_key = _map_key(key)
    assert odf_key == key


def test_map_key_mapped_col():
    key = "display"
    odf_key = _map_key(key)
    assert odf_key == "text:display"


def test_map_key_mapped_no_mapped_no_col():
    key = "db:apply-command"
    odf_key = _map_key(key)
    assert odf_key == key


def test_map_key_mapped_no_mapped_no_col_not_known():
    key = "ooops"
    odf_key = _map_key(key)
    assert odf_key is None


def test_map_key_mapped_no_mapped_no_col_known():
    key = "border-left"
    odf_key = _map_key(key)
    assert odf_key == "fo:border-left"
