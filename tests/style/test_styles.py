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
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>

from collections.abc import Iterable

import pytest

from odfdo.const import ODF_STYLES
from odfdo.document import Document
from odfdo.element import Element
from odfdo.master_page import StyleMasterPage
from odfdo.style import Style
from odfdo.styles import OfficeMasterStyles, Styles


@pytest.fixture
def styles(samples) -> Iterable[Styles]:
    document = Document(samples("example.odt"))
    yield document.get_part(ODF_STYLES)


def test_styles_class(styles):
    assert isinstance(styles, Styles)


def test_create_style():
    style = Style("paragraph", "style1")
    assert style.serialize() in (
        ('<style:style style:name="style1" style:family="paragraph"/>'),
        ('<style:style style:family="paragraph" style:name="style1"/>'),
    )


def test_get_styles(styles):
    style_list = styles.get_styles()
    assert len(style_list) == 20


def test_get_styles_paragraph(styles):
    style_list = styles.get_styles(family="paragraph")
    assert len(style_list) == 10


def test_get_styles_paragraph_wrong(styles):
    with pytest.raises(ValueError):
        styles.get_styles(family="not_a_family")


def test_get_styles_master_page(styles):
    style_list = styles.get_styles(family="master-page")
    assert len(style_list) == 1


def test_styles_get_master_pages(styles):
    style_list = styles.get_master_pages()
    assert len(style_list) == 1
    assert isinstance(style_list[0], StyleMasterPage)


def test_styles_get_master_page(styles):
    style = styles.get_master_page(0)
    assert isinstance(style, StyleMasterPage)


def test_styles_get_master_page_none(styles):
    style = styles.get_master_page(5)
    assert style is None


def test_get_style_automatic(styles):
    style = styles.get_style("page-layout", "Mpm1")
    assert style is not None


def test_get_style_named(styles):
    style = styles.get_style("paragraph", "Heading_20_1")
    assert style.display_name == "Heading 1"


def test_get_style_display_name(styles):
    style = styles.get_style("paragraph", display_name="Text body")
    assert style.name == "Text_20_body"


def test_insert_style(styles):
    styles = styles.clone
    style = Style(
        "paragraph",
        name="style1",
        area="text",
        **{"fo:color": "#0000ff", "fo:background-color": "#ff0000"},
    )
    context = styles.get_element("//office:styles")
    context.append(style)
    read_style = styles.get_style("paragraph", "style1")
    assert read_style.serialize() in (
        (
            '<style:style style:name="style1" '
            'style:family="paragraph">'
            '<style:text-properties fo:background-color="#ff0000" '
            'fo:color="#0000ff"/>'
            "</style:style>"
        ),
        '<style:style style:family="paragraph" '
        'style:name="style1">'
        "<style:text-properties "
        'fo:background-color="#ff0000" '
        'fo:color="#0000ff"/>'
        "</style:style>",
    )


def test_bad_set_language(styles):
    styles = styles.clone
    with pytest.raises(TypeError):
        styles.set_default_styles_language_country("wrong")


def test_language(styles):
    assert styles.default_language == "fr-FR"


def test_language_no_default_style(styles):
    styles = styles.clone
    defaults = styles.get_elements("//style:default-style")
    for elem in defaults:
        elem.delete()
    assert styles.default_language == ""


def test_office_master_styles_create():
    oms = OfficeMasterStyles()
    assert oms.serialize() == "<office:master-styles/>"


def test_office_master_styles_from_tag():
    oms = Element.from_tag("<office:master-styles/>")
    assert isinstance(oms, OfficeMasterStyles)


def test_get_office_master_styles(styles):
    oms = styles.office_master_styles
    assert isinstance(oms, OfficeMasterStyles)
    assert len(oms.children) == 1


def test_set_office_master_styles(styles):
    new_oms = OfficeMasterStyles()
    styles.office_master_styles = new_oms
    oms = styles.office_master_styles
    assert isinstance(oms, OfficeMasterStyles)
    assert len(oms.children) == 0


def test_set_office_master_styles_no_eixts(styles):
    current = styles.office_master_styles
    current.delete()
    new_oms = OfficeMasterStyles()
    styles.office_master_styles = new_oms
    oms = styles.office_master_styles
    assert isinstance(oms, OfficeMasterStyles)
    assert len(oms.children) == 0
