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

from odfdo.document import Document

# from odfdo.element import Element
from odfdo.user_field_declaration import UserFieldDecl, UserFieldDecls

ZOE = "你好 Zoé"
CHAMP = "Champêtre"


@pytest.fixture
def document(samples) -> Iterable[Document]:
    document = Document(samples("variable.odt"))
    yield document


def test_user_field_decls_class():
    field = UserFieldDecls()
    assert isinstance(field, UserFieldDecls)


def test_user_field_decl_class():
    field = UserFieldDecl()
    assert isinstance(field, UserFieldDecl)


def test_user_field_decl_set_value():
    field = UserFieldDecl(name="field_name")
    field.set_value(42)
    assert field.get_value() == 42


def test_create_user_field_decl():
    user_field_decl = UserFieldDecl(ZOE, 42)
    expected = (
        f'<text:user-field-decl text:name="{ZOE}" '
        'office:value-type="float" calcext:value-type="float" '
        'office:value="42" calcext:value="42"/>'
    )
    assert user_field_decl.serialize() == expected


def test_get_user_field_decl(document):
    body = document.body
    user_field_decl = body.get_user_field_decl(CHAMP)
    expected = (
        '<text:user-field-decl office:value-type="float" '
        f'office:value="1" text:name="{CHAMP}"/>'
    )
    assert user_field_decl.serialize() == expected
