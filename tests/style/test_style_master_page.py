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

from odfdo.element import Element
from odfdo.master_page import (
    StyleFooter,
    StyleFooterLeft,
    StyleHeader,
    StyleHeaderLeft,
    StyleMasterPage,
)
from odfdo.style import Style


def test_create_style_master_page():
    style = StyleMasterPage()
    expected = "<style:master-page/>"
    assert style.serialize() == expected


def test_create_style_master_page_deprecated():
    style = Style("master-page")
    expected = "<style:master-page/>"
    assert style.serialize() == expected


def test_create_style_master_page_from_tag():
    style = Element.from_tag("<style:master-page/>")
    expected = "<style:master-page/>"
    assert isinstance(style, StyleMasterPage)
    assert style.serialize() == expected


def test_create_style_header():
    style = StyleHeader()
    expected = "<style:header/>"
    assert style.serialize() == expected


def test_style_header_repr():
    style = StyleHeader()
    expected = "<StyleHeader>"
    assert repr(style) == expected


def test_style_header_display():
    style = StyleHeader()
    assert style.display


def test_create_style_header_true():
    style = StyleHeader(display=True)
    expected = "<style:header/>"
    assert style.serialize() == expected


def test_create_style_header_false():
    style = StyleHeader(display=False)
    expected = '<style:header style:display="false"/>'
    assert style.serialize() == expected
    assert not style.display


def test_style_header_display_false():
    style = StyleHeader()
    style.display = False
    expected = '<style:header style:display="false"/>'
    assert style.serialize() == expected
    assert not style.display


def test_style_header_display_false_none():
    style = StyleHeader()
    style.display = None
    expected = '<style:header style:display="false"/>'
    assert style.serialize() == expected
    assert not style.display


def test_style_header_display_false_str():
    style = StyleHeader()
    style.display = "false"
    expected = '<style:header style:display="false"/>'
    assert style.serialize() == expected
    assert not style.display


def test_header_from_tag():
    style = Element.from_tag("<style:header/>")
    assert isinstance(style, StyleHeader)


def test_header_from_tag_false():
    style = Element.from_tag('<style:header style:display="false"/>')
    assert not style.display


def test_create_style_header_left():
    style = StyleHeaderLeft()
    expected = "<style:header-left/>"
    assert style.serialize() == expected


def test_style_header_left_repr():
    style = StyleHeaderLeft()
    expected = "<StyleHeaderLeft>"
    assert repr(style) == expected


def test_style_header_left_display():
    style = StyleHeaderLeft()
    assert style.display


def test_create_style_header_left_false():
    style = StyleHeaderLeft(display=False)
    expected = '<style:header-left style:display="false"/>'
    assert style.serialize() == expected
    assert not style.display


def test_header_left_from_tag():
    style = Element.from_tag("<style:header-left/>")
    assert isinstance(style, StyleHeaderLeft)


def test_create_style_footer():
    style = StyleFooter()
    expected = "<style:footer/>"
    assert style.serialize() == expected


def test_style_footer_repr():
    style = StyleFooter()
    expected = "<StyleFooter>"
    assert repr(style) == expected


def test_style_footer_display():
    style = StyleFooter()
    assert style.display


def test_create_style_footer_false():
    style = StyleFooter(display=False)
    expected = '<style:footer style:display="false"/>'
    assert style.serialize() == expected
    assert not style.display


def test_footer_from_tag():
    style = Element.from_tag("<style:footer/>")
    assert isinstance(style, StyleFooter)


def test_create_style_footer_left():
    style = StyleFooterLeft()
    expected = "<style:footer-left/>"
    assert style.serialize() == expected


def test_style_footer_left_repr():
    style = StyleFooterLeft()
    expected = "<StyleFooterLeft>"
    assert repr(style) == expected


def test_style_footer_left_display():
    style = StyleFooterLeft()
    assert style.display


def test_create_style_footer_left_false():
    style = StyleFooterLeft(display=False)
    expected = '<style:footer-left style:display="false"/>'
    assert style.serialize() == expected
    assert not style.display


def test_footer_left_from_tag():
    style = Element.from_tag("<style:footer-left/>")
    assert isinstance(style, StyleFooterLeft)
