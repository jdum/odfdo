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

import pytest

from odfdo.const import ODF_STYLES
from odfdo.document import Document
from odfdo.element import Element
from odfdo.master_page import (
    StyleFooter,
    StyleFooterLeft,
    StyleHeader,
    StyleHeaderLeft,
    StyleMasterPage,
)
from odfdo.paragraph import Paragraph
from odfdo.style import Style
from odfdo.styles import Styles


@pytest.fixture
def styles(samples) -> Iterable[Styles]:
    document = Document(samples("example.odt"))
    yield document.get_part(ODF_STYLES)


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


def test_read_master_page(styles):
    mp = styles.get_master_page(0)
    assert isinstance(mp, StyleMasterPage)


def test_read_master_page_attr(styles):
    mp = styles.get_master_page(0)
    # <style:master-page style:name="Standard"
    # style:page-layout-name="Mpm1"/>
    assert mp.name == "Standard"
    assert mp.display_name is None
    assert mp.page_layout == "Mpm1"
    assert mp.next_style is None
    assert mp.draw_style_name is None


def test_master_page_family(styles):
    mp = styles.get_master_page(0)
    assert mp.family == "master-page"


def test_master_page_set_family(styles):
    mp = styles.get_master_page(0)
    mp.family = "oops"
    assert mp.family == "master-page"


def test_master_page_repr(styles):
    mp = styles.get_master_page(0)
    assert repr(mp) == "<StyleMasterPage family=master-page name=Standard>"


def test_master_page_create_attr():
    mp = StyleMasterPage(
        name="Std2",
        display_name="Standard 2",
        page_layout="PL1",
        next_style="Std3",
        draw_style_name="dsn",
    )
    assert mp.serialize() == (
        "<style:master-page "
        'style:name="Std2" '
        'style:display-name="Standard 2" '
        'style:page-layout-name="PL1" '
        'style:next-style-name="Std3" '
        'draw:style-name="dsn"/>'
    )


def test_master_page_get_page_header(styles):
    mp = styles.get_master_page(0)
    ph = mp.get_page_header()
    assert ph is None


def test_master_page_get_page_footer(styles):
    mp = styles.get_master_page(0)
    pf = mp.get_page_footer()
    assert pf is None


def test_master_page_set_page_header_1(styles):
    mp = styles.get_master_page(0)
    ph = mp.get_page_header()
    assert ph is None
    mp.set_page_header("text header")
    result = mp.get_page_header()
    assert len(result.children) == 1
    para = result.children[0]
    assert isinstance(para, Paragraph)
    assert str(para) == "text header\n"


def test_master_page_set_page_header_2(styles):
    mp = styles.get_master_page(0)
    mp.set_page_header("text header")
    mp.set_page_header("text header other")
    result = mp.get_page_header()
    assert len(result.children) == 1
    para = result.children[0]
    assert isinstance(para, Paragraph)
    assert str(para) == "text header other\n"


def test_master_page_set_page_header_page_header(styles):
    ph = StyleHeader()
    ph.append(Paragraph("some header"))
    mp = styles.get_master_page(0)
    mp.set_page_header(ph)
    result = mp.get_page_header()
    assert len(result.children) == 1
    para = result.children[0]
    assert isinstance(para, Paragraph)
    assert str(para) == "some header\n"


def test_master_page_set_page_header_list(styles):
    p1 = Paragraph("paragraph 1")
    p2 = Paragraph("paragraph 2")
    mp = styles.get_master_page(0)
    mp.set_page_header([p1, p2])
    result = mp.get_page_header()
    assert len(result.children) == 2
    para1 = result.children[0]
    assert isinstance(para1, Paragraph)
    assert str(para1) == "paragraph 1\n"
    para2 = result.children[1]
    assert isinstance(para2, Paragraph)
    assert str(para2) == "paragraph 2\n"


def test_master_page_set_page_header_list_bad(styles):
    p1 = Paragraph("paragraph 1")
    p2 = Paragraph("paragraph 2")
    mp = styles.get_master_page(0)
    mp.set_page_header([p1, ["ignore"], p2])
    result = mp.get_page_header()
    assert len(result.children) == 2
    para1 = result.children[0]
    assert isinstance(para1, Paragraph)
    assert str(para1) == "paragraph 1\n"
    para2 = result.children[1]
    assert isinstance(para2, Paragraph)
    assert str(para2) == "paragraph 2\n"


def test_master_page_set_page_footer_1(styles):
    mp = styles.get_master_page(0)
    pf = mp.get_page_footer()
    assert pf is None
    mp.set_page_footer("text footer")
    result = mp.get_page_footer()
    assert len(result.children) == 1
    para = result.children[0]
    assert isinstance(para, Paragraph)
    assert str(para) == "text footer\n"
