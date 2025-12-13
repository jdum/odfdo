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

# from collections.abc import Iterable

# import pytest

# from odfdo.document import Document
# from odfdo.element import Element
from odfdo.variable_declaration import (
    VarDecl,
    VarDecls,
)

ZOE = "你好 Zoé"


# @pytest.fixture
# def document(samples) -> Iterable[Document]:
#     document = Document(samples("variable.odt"))
#     yield document


def test_var_decls_class():
    variable = VarDecls()
    assert isinstance(variable, VarDecls)


def test_var_decl_class():
    variable = VarDecl()
    assert isinstance(variable, VarDecl)


def test_create_variable_decl():
    variable_decl = VarDecl(ZOE, "float")
    assert variable_decl.serialize() in (
        (f'<text:variable-decl text:name="{ZOE}" office:value-type="float"/>'),
        (f'<text:variable-decl office:value-type="float" text:name="{ZOE}"/>'),
    )
