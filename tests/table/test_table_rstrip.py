# Copyright 2018-2026 Jérôme Dumonteil
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
from typing import cast

import pytest

from odfdo.document import Document
from odfdo.row import Row
from odfdo.table import Table


@pytest.fixture
def table(samples) -> Iterable[Table]:
    # simpletable :
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1   2	3	4	5	6	7
    document = Document(samples("simple_table.ods"))
    yield cast(Table, document.body.get_table(name="Example1"))


@pytest.fixture
def styled_table(samples) -> Iterable[Table]:
    document = Document(samples("styled_table.ods"))
    yield cast(Table, document.body.get_table(name="Feuille1"))


@pytest.fixture
def unstriped_table_1(samples) -> Iterable[Table]:
    document = Document(samples("unstriped.ods"))
    yield cast(Table, document.body.get_table(name="Sheet1"))


@pytest.fixture
def unstriped_table_2(samples) -> Iterable[Table]:
    document = Document(samples("unstriped.ods"))
    yield cast(Table, document.body.get_table(name="Sheet2"))


def test_table_rstrip_unstriped_table_1(unstriped_table_1):
    unstriped_table_1.rstrip()
    assert unstriped_table_1.size[0] > 1000
    assert unstriped_table_1.size[1] > 1000


def test_table_rstrip_unstriped_table_1_gg(unstriped_table_1):
    unstriped_table_1.rstrip(aggressive=True)
    assert unstriped_table_1.size == (4, 4)


def test_table_rstrip_unstriped_table_2(unstriped_table_2):
    unstriped_table_2.rstrip()
    assert unstriped_table_2.size[0] == 6
    assert unstriped_table_2.size[1] == 5


def test_table_rstrip_styled_table(styled_table):
    styled_table.rstrip()
    assert styled_table.size == (5, 9)


def test_table_rstrip_1(table):
    table.rstrip()
    result = list(table.iter_values(complete=True))
    assert result == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]


def test_table_rstrip_2(table):
    col = table.columns[6]
    col.repeated = 4
    table.set_column(6, col)
    result = list(table.iter_values(complete=True))
    assert result == [
        [1, 1, 1, 2, 3, 3, 3, None, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None, None],
        [1, 2, 3, 4, 5, 6, 7, None, None, None],
    ]


def test_table_rstrip_3(table):
    col = table.columns[6]
    col.repeated = 4
    table.set_column(6, col)
    table.rstrip()
    result = list(table.iter_values(complete=True))
    assert result == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]


def test_table_rstrip_4(table):
    col = table.columns[6]
    col.repeated = 4
    table.set_column(6, col)
    row = Row()
    row.set_values([10, 20, 30, 40, 50, 60, 70, 80, 90])
    table.append(row)
    result = list(table.iter_values(complete=True))
    assert result == [
        [1, 1, 1, 2, 3, 3, 3, None, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None, None],
        [1, 2, 3, 4, 5, 6, 7, None, None, None],
        [10, 20, 30, 40, 50, 60, 70, 80, 90, None],
    ]


def test_table_rstrip_5():
    table = Table("empty")
    expected = table.serialize()
    table.rstrip()
    result = table.serialize()
    assert result == expected
