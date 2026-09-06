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

from odfdo.utils.unify_name import NameUnifyer


def test_init_default():
    unifyer = NameUnifyer()
    assert unifyer.base_name == "Sheet"
    assert unifyer.seen == set()


def test_init_custom_base():
    unifyer = NameUnifyer("Table")
    assert unifyer.base_name == "Table"
    assert unifyer.seen == set()


def test_unique_first_time():
    unifyer = NameUnifyer()
    assert unifyer.unique("Sheet") == "Sheet"
    assert unifyer.unique("Other") == "Other"
    assert unifyer.seen == {"Sheet", "Other"}


def test_unique_duplicates():
    unifyer = NameUnifyer()
    assert unifyer.unique("Sheet") == "Sheet"
    assert unifyer.unique("Sheet") == "Sheet2"
    assert unifyer.unique("Sheet") == "Sheet3"
    assert unifyer.unique("Sheet") == "Sheet4"
    assert unifyer.seen == {"Sheet", "Sheet2", "Sheet3", "Sheet4"}


def test_unique_collision_skip():
    unifyer = NameUnifyer()
    assert unifyer.unique("Data") == "Data"
    assert unifyer.unique("Data2") == "Data2"
    # Next duplicate of Data should skip Data2 and become Data3
    assert unifyer.unique("Data") == "Data3"
    assert unifyer.unique("Data") == "Data4"
    assert unifyer.seen == {"Data", "Data2", "Data3", "Data4"}


def test_unique_empty_name_default_base():
    unifyer = NameUnifyer()
    assert unifyer.unique("") == "Sheet1"
    assert unifyer.unique("") == "Sheet2"
    assert unifyer.unique("") == "Sheet3"
    assert unifyer.seen == {"Sheet1", "Sheet2", "Sheet3"}


def test_unique_empty_name_default_custom():
    unifyer = NameUnifyer("Table")
    assert unifyer.unique() == "Table1"
    assert unifyer.unique() == "Table2"
    assert unifyer.unique() == "Table3"
    assert unifyer.seen == {"Table1", "Table2", "Table3"}


def test_unique_empty_name_custom_base():
    unifyer = NameUnifyer(base_name="Grid")
    assert unifyer.unique("") == "Grid1"
    assert unifyer.unique() == "Grid2"
    assert unifyer.unique("") == "Grid3"
    assert unifyer.seen == {"Grid1", "Grid2", "Grid3"}


def test_unique_mixed_sequence():
    unifyer = NameUnifyer()
    names = ["A", "B", "A", "A2", "A", "", ""]
    expected = ["A", "B", "A2", "A22", "A3", "Sheet1", "Sheet2"]
    result = [unifyer.unique(name) for name in names]
    assert result == expected
