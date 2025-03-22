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

from odfdo import Element
from odfdo.const import ODF_CONTENT
from odfdo.document import Document
from odfdo.style import Style


@pytest.fixture
def content(samples) -> Iterable[Element]:
    document = Document(samples("span_style.odt"))
    yield document.get_part(ODF_CONTENT)


def test_get_styles(content):
    styles = content.get_styles()
    assert len(styles) == 7


def test_get_styles_family(content):
    styles = content.get_styles(family="paragraph")
    assert len(styles) == 2


def test_get_style_automatic(content):
    style = content.get_style("paragraph", "P1")
    assert style is not None


def test_insert_style(content):
    style = Style(
        "paragraph",
        "style1",
        area="text",
        **{"fo:color": "#0000ff", "fo:background-color": "#ff0000"},
    )
    auto_styles = content.get_element("//office:automatic-styles")
    auto_styles.append(style)
    read_style = content.get_style("paragraph", "style1")
    assert read_style.serialize() in (
        (
            '<style:style style:name="style1" '
            'style:family="paragraph">'
            "<style:text-properties "
            'fo:background-color="#ff0000" '
            'fo:color="#0000ff"/>'
            "</style:style>"
        ),
        (
            '<style:style style:name="style1" '
            'style:family="paragraph">'
            '<style:text-properties fo:color="#0000ff" '
            'fo:background-color="#ff0000"/>'
            "</style:style>"
        ),
        (
            '<style:style style:family="paragraph" '
            'style:name="style1">'
            "<style:text-properties "
            'fo:background-color="#ff0000" '
            'fo:color="#0000ff"/>'
            "</style:style>"
        ),
    )
