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

from odfdo.const import ODF_STYLES
from odfdo.document import Document
from odfdo.element import Element
from odfdo.page_layout import StylePageLayout
from odfdo.styles import Styles


@pytest.fixture
def styles(samples) -> Iterable[Styles]:
    document = Document(samples("example.odt"))
    yield document.get_part(ODF_STYLES)


def test_style_page_layout_create():
    spl = StylePageLayout()
    assert spl.serialize() == "<style:page-layout/>"


def test_style_page_layout_from_tag():
    spl = Element.from_tag("<style:page-layout/>")
    assert isinstance(spl, StylePageLayout)


def test_style_page_layout_repr():
    spl = Element.from_tag("<style:page-layout/>")
    assert repr(spl) == "<StylePageLayout family=page-layout name=None>"


def test_get_style_page_layout(styles):
    auto = styles.office_automatic_styles
    spl = auto.page_layouts[0]
    assert isinstance(spl, StylePageLayout)


def test_get_style_page_layout_name(styles):
    auto = styles.office_automatic_styles
    spl = auto.page_layouts[0]
    assert spl.name == "Mpm1"


def test_get_style_page_layout_family(styles):
    auto = styles.office_automatic_styles
    spl = auto.page_layouts[0]
    assert spl.family == "page-layout"


def test_get_style_page_layout_set_family_unchanged(styles):
    auto = styles.office_automatic_styles
    spl = auto.page_layouts[0]
    spl.family = "unchanged"
    assert spl.family == "page-layout"


def test_get_style_page_layout_page_usage(styles):
    auto = styles.office_automatic_styles
    spl = auto.page_layouts[0]
    usage = spl.page_usage
    assert usage == "all"


def test_get_style_page_layout_get_properties(styles):
    auto = styles.office_automatic_styles
    spl = auto.page_layouts[0]
    props = spl.get_properties()
    expected = {
        "fo:page-width": "20.999cm",
        "fo:page-height": "29.699cm",
        "style:num-format": "1",
        "style:print-orientation": "portrait",
        "fo:margin-top": "2cm",
        "fo:margin-bottom": "2cm",
        "fo:margin-left": "2cm",
        "fo:margin-right": "2cm",
        "style:writing-mode": "lr-tb",
        "style:layout-grid-color": "#c0c0c0",
        "style:layout-grid-lines": "20",
        "style:layout-grid-base-height": "0.706cm",
        "style:layout-grid-ruby-height": "0.353cm",
        "style:layout-grid-mode": "none",
        "style:layout-grid-ruby-below": "false",
        "style:layout-grid-print": "false",
        "style:layout-grid-display": "false",
        "style:footnote-max-height": "0cm",
        "style:footnote-sep": {
            "style:width": "0.018cm",
            "style:distance-before-sep": "0.101cm",
            "style:distance-after-sep": "0.101cm",
            "style:line-style": "none",
            "style:adjustment": "left",
            "style:rel-width": "25%",
            "style:color": "#000000",
        },
    }
    assert props == expected


def test_get_style_page_layout_get_header_style(styles):
    auto = styles.office_automatic_styles
    spl = auto.page_layouts[0]
    style = spl.get_header_style()
    assert style.tag == "style:header-style"


def test_get_style_page_layout_get_footer_style(styles):
    auto = styles.office_automatic_styles
    spl = auto.page_layouts[0]
    style = spl.get_footer_style()
    assert style.tag == "style:footer-style"


# def test_set_style_page_layout(styles):
#     new_oms = OfficeMasterStyles()
#     styles.office_master_styles = new_oms
#     oms = styles.office_master_styles
#     assert isinstance(oms, OfficeMasterStyles)
#     assert len(oms.children) == 0
