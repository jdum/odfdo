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
from __future__ import annotations

from collections.abc import Iterable

import pytest

from odfdo.const import ODF_CONTENT
from odfdo.container import Container
from odfdo.content import Content
from odfdo.style import Style


@pytest.fixture
def example_container(samples) -> Iterable[Container]:
    container = Container()
    container.open(samples("example.odt"))
    yield container


@pytest.fixture
def content(example_container) -> Iterable[Content]:
    yield Content(ODF_CONTENT, example_container)


def test_content_class(content):
    assert isinstance(content, Content)


def test_content_str(content):
    assert str(content) == str(content.body)


def test_get_style_contexts_font_face(content):
    ctxs = content._get_style_contexts("font-face")
    assert len(ctxs) == 1
    assert ctxs[0].tag == "office:font-face-decls"


def test_get_style_contexts_other(content):
    ctxs = content._get_style_contexts("paragraph")
    assert len(ctxs) == 2
    assert ctxs[0].tag == "office:font-face-decls"
    assert ctxs[1].tag == "office:automatic-styles"


def test_get_style_contexts_none(content):
    ctxs = content._get_style_contexts(None)
    assert len(ctxs) == 2
    assert ctxs[0].tag == "office:font-face-decls"
    assert ctxs[1].tag == "office:automatic-styles"


def test_get_styles_all(content):
    styles = content.get_styles()
    assert len(styles) > 0
    tags = {s.tag for s in styles}
    assert "style:font-face" in tags
    assert "style:style" in tags


def test_get_styles_family(content):
    styles = content.get_styles(family="paragraph")
    assert len(styles) > 0
    for s in styles:
        assert s.get_attribute("style:family") == "paragraph"


def test_get_style_by_name(content):
    # P1 should exist in example.odt
    style = content.get_style("paragraph", "P1")
    assert style is not None
    assert style.get_attribute("style:name") == "P1"
    assert style.get_attribute("style:family") == "paragraph"


def test_get_style_font_face(content):
    # Liberation Serif should exist
    style = content.get_style("font-face", "Liberation Serif")
    assert style is not None
    assert style.tag == "style:font-face"
    assert style.get_attribute("style:name") == "Liberation Serif"


def test_get_style_not_found(content):
    style = content.get_style("paragraph", "nonexistent_style_name")
    assert style is None


def test_get_style_by_element(content):
    style = content.get_style("paragraph", "P1")
    assert style is not None
    result = content.get_style("paragraph", style)
    assert result is style


def test_get_style_by_display_name(content):
    # Let's add a style with a display name to test this
    new_style = Style("paragraph", name="MyStyle", display_name="Friendly Name")
    content.get_element("//office:automatic-styles").append(new_style)

    style = content.get_style("paragraph", display_name="Friendly Name")
    assert style is not None
    assert style.get_attribute("style:name") == "MyStyle"
    assert style.get_attribute("style:display-name") == "Friendly Name"


def test_get_styles_missing_context(example_container):
    # Create a content part with missing styles elements
    content = Content(ODF_CONTENT, example_container)
    # Remove font-face-decls and automatic-styles
    ffd = content.get_element("//office:font-face-decls")
    if ffd:
        ffd.delete()
    aus = content.get_element("//office:automatic-styles")
    if aus:
        aus.delete()

    styles = content.get_styles()
    assert len(styles) == 0

    style = content.get_style("paragraph", "P1")
    assert style is None
