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

from odfdo.const import ODF_CONTENT
from odfdo.content import Content
from odfdo.document import Document


@pytest.fixture
def base_content(samples) -> Iterable[Content]:
    document = Document(samples("base_text.odt"))
    yield document.get_part(ODF_CONTENT)


def test_get_content(base_content):
    assert isinstance(base_content, Content)


def test_get_body(base_content):
    body = base_content.body
    assert body.tag == "office:text"


def test_get_styles(base_content):
    result = base_content.get_styles()
    assert len(result) == 5


def test_get_styles_family(base_content):
    result = base_content.get_styles("font-face")
    assert len(result) == 3


def test_get_style(base_content):
    style = base_content.get_style("section", "Sect1")
    assert style.name == "Sect1"
    assert style.family == "section"


def test_get_style_2(base_content):
    # trst a missing context
    ctx = base_content.get_element("//office:font-face-decls")
    ctx.delete()
    style = base_content.get_style("section", "Sect1")
    assert style.family == "section"


def test_repr(base_content):
    assert repr(base_content) == "<Content part_name=content.xml>"


def test_str(base_content):
    result = str(base_content)
    assert "odfdo Test Case Document" in result
    assert "This is a paragraph with a named style" in result
