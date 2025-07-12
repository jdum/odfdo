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

from odfdo.table import Cell
from odfdo.user_field import UserFieldDecl
from odfdo.variable import VarSet

ZOE = "你好 Zoé"


def test_get_with_cell():
    cell = Cell(42)
    assert cell.get_value() == 42


def test_get_with_variable():
    variable_set = VarSet(ZOE, 42)
    assert variable_set.get_value() == 42


def test_get_with_user_field():
    user_field_decl = UserFieldDecl(ZOE, 42)
    assert user_field_decl.get_value() == 42


def test_with_cell():
    cell = Cell(42)
    cell.set_value(ZOE)
    expected = (
        '<table:table-cell office:value-type="string" '
        'calcext:value-type="string" '
        f'office:string-value="{ZOE}">'
        "<text:p>"
        f"{ZOE}"
        "</text:p>"
        "</table:table-cell>"
    )
    assert cell.serialize() == expected


def test_with_variable():
    variable_set = VarSet(ZOE, 42)
    variable_set.set_value(ZOE)
    expected = (
        '<text:variable-set office:value-type="string" '
        'calcext:value-type="string" '
        f'office:string-value="{ZOE}" text:name="{ZOE}" '
        'text:display="none">'
        f"{ZOE}"
        "</text:variable-set>"
    )
    assert variable_set.serialize() == expected


def test_with_user_field():
    user_field_decl = UserFieldDecl(ZOE, 42)
    user_field_decl.set_value(ZOE)
    expected = (
        '<text:user-field-decl office:value-type="string" '
        'calcext:value-type="string" '
        'office:string-value="%s" text:name="%s"/>'
    ) % ((ZOE,) * 2)
    assert user_field_decl.serialize() == expected
