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
from odfdo.style import Style
from odfdo.styles import Styles


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


def test_get_styles_master_page(styles):
    style_list = styles.get_styles(family="master-page")
    assert len(style_list) == 1


def test_styles_get_master_pages(styles):
    style_list = styles.get_master_pages()
    assert len(style_list) == 1
    assert isinstance(style_list[0], Style)


def test_styles_get_master_page(styles):
    style = styles.get_master_page(0)
    assert isinstance(style, Style)


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
