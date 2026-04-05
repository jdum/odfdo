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
# Authors: Hervé Cauwelier <herve@itaapy.com>
from __future__ import annotations

from collections.abc import Iterable
from typing import cast

import pytest

from odfdo.const import ODF_CONTENT, ODF_STYLES
from odfdo.content import Content
from odfdo.document import Document
from odfdo.element import Element
from odfdo.style import Style


@pytest.fixture
def content(samples) -> Iterable[Content]:
    document = Document(samples("span_style.odt"))
    content = cast(Content, document.get_part(ODF_CONTENT))
    yield content


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

    expected = (
        "<style:style "
        'style:family="paragraph" style:name="style1">'
        "<style:text-properties "
        'fo:background-color="#ff0000" fo:color="#0000ff">'
        "</style:text-properties>"
        "</style:style>"
    )
    assert read_style._canonicalize() == expected


def test_get_styles_none(content):
    styles = content.get_styles(family=None)
    assert len(styles) == 7


def test_get_styles_nonexistent(content):
    with pytest.raises(ValueError, match="Unknown family"):
        content.get_styles(family="nonexistent")


def test_get_style_not_found(content):
    style = content.get_style("paragraph", "nonexistent")
    assert style is None


def test_get_style_by_element(content):
    style = content.get_style("paragraph", "P1")
    read_style = content.get_style("paragraph", style)
    assert read_style == style


def test_get_style_by_element_error(content):
    element = Element.from_tag("<text:p/>")
    with pytest.raises(ValueError, match="Not a odf_style"):
        content.get_style("paragraph", element)


def test_get_style_by_display_name(content):
    style = content.get_style("paragraph", "P1")
    style.set_attribute("style:display-name", "My Display Name")
    read_style = content.get_style("paragraph", display_name="My Display Name")
    assert read_style._canonicalize() == style._canonicalize()


def test_get_style_no_family(content):
    # get font face by name (it has style:name but no style:family)
    style = content.get_style("", "Liberation Serif")
    assert style.tag == "style:font-face"


def test_get_style_no_family_draw_name():
    # Test matching draw:name when family is empty
    container = Element.from_tag("<office:styles/>")
    # draw:fill-image uses draw:name
    tag = '<draw:fill-image draw:name="img1" xlink:href="url1" />'
    img = Element.from_tag(tag)
    container.append(img)

    style = container.get_style("", "img1")
    assert style.tag == "draw:fill-image"
    assert style.get_attribute("draw:name") == "img1"


def test_get_style_no_family_display_name():
    # Test matching display-name when family is empty
    container = Element.from_tag("<office:styles/>")
    tag = '<style:style style:name="s1" style:display-name="Display 1" />'
    s = Element.from_tag(tag)
    container.append(s)

    style = container.get_style("", display_name="Display 1")
    assert style.get_attribute("style:name") == "s1"


def test_get_style_no_family_first():
    # Test getting first style when family and names are empty
    container = Element.from_tag("<office:styles/>")
    tag1 = '<style:style style:name="s1" />'
    tag2 = '<style:style style:name="s2" />'
    container.append(Element.from_tag(tag1))
    container.append(Element.from_tag(tag2))

    style = container.get_style("")
    assert style.get_attribute("style:name") == "s1"


def test_get_style_default_by_family(samples):
    document = Document(samples("example.odt"))
    styles_part = document.get_part(ODF_STYLES)
    # Testing get_style(family, name=None) which should return default style
    style = styles_part.get_style("paragraph")
    assert style.tag == "style:default-style"
    assert style.get_attribute("style:family") == "paragraph"


def test_get_styles_all_no_family(samples):
    document = Document(samples("example.odt"))
    styles_part = document.get_part(ODF_STYLES)
    styles = styles_part.get_styles()  # family="" by default
    assert len(styles) > 0
    # Should include default styles, markers, fill-images etc.
    tags = {s.tag for s in styles}
    assert "style:default-style" in tags
