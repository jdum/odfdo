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

from odfdo.document import Document
from odfdo.style import Style


@pytest.fixture
def document(samples) -> Iterable[Document]:
    yield Document(samples("example.odt"))


def test_insert_common_style(document):
    style = Style("paragraph", "MyStyle")
    document.insert_style(style)
    inserted_style = document.get_style("paragraph", "MyStyle")

    assert style.serialize() == inserted_style.serialize()


def test_insert_default_style(document):
    style = Style("paragraph", "MyStyle")
    document.insert_style(style, default=True)
    inserted_style = document.get_style("paragraph")
    expected = '<style:default-style style:family="paragraph"/>'
    assert inserted_style.serialize() == expected


def test_insert_automatic_style(document):
    style = Style("paragraph")
    document.insert_style(style, automatic=True)
    assert style.name is not None


def test_insert_style_name_as_argument(document):
    style = Style("paragraph")
    arg_name = "some_name"
    returned_name = document.insert_style(style, name=arg_name, automatic=True)
    assert style.name is not None
    assert returned_name == arg_name


def test_insert_style_from_string(document):
    style_str = (
        '<style:style style:name="style_as_str" '
        'style:family="paragraph">'
        "<style:text-properties "
        'fo:background-color="#ff0000" '
        'fo:color="#0000ff"/>'
        "</style:style>"
    )
    returned_name = document.insert_style(style_str, automatic=True)
    assert returned_name == "style_as_str"
    read_style = document.get_style("paragraph", "style_as_str")
    assert read_style.serialize() in (
        (
            '<style:style style:name="style_as_str" '
            'style:family="paragraph">'
            "<style:text-properties "
            'fo:background-color="#ff0000" '
            'fo:color="#0000ff"/>'
            "</style:style>"
        ),
        (
            '<style:style style:name="style_as_str" '
            'style:family="paragraph">'
            '<style:text-properties fo:color="#0000ff" '
            'fo:background-color="#ff0000"/>'
            "</style:style>"
        ),
        (
            '<style:style style:family="paragraph" '
            'style:name="style_as_str">'
            "<style:text-properties "
            'fo:background-color="#ff0000" '
            'fo:color="#0000ff"/>'
            "</style:style>"
        ),
    )


def test_insert_with_error(document):
    style = Style("paragraph", "MyStyle")
    with pytest.raises(AttributeError):
        document.insert_style(
            style=style,
            automatic=True,
            default=True,
        )


def test_insert_master_page_style(document):
    style = Style("master-page", "MyPageStyle")
    document.insert_style(style)
    inserted_style = document.get_style("master-page", "MyPageStyle")
    assert style.serialize() == inserted_style.serialize()
