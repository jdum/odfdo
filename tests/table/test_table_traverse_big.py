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
# Authors: Jerome Dumonteil <jerome.dumonteil@itaapy.com>

from collections.abc import Iterable

import pytest

from odfdo.document import Document
from odfdo.table import _XP_ROW_IDX, Table


@pytest.fixture
def table(samples) -> Iterable[Table]:
    document = Document(samples("big.ods"))
    yield document.body.tables[0]  # type: ignore


def test_count_height(table):
    assert table.height == 20100


def test_get_row_0(table):
    row = table.get_row(0)
    assert row.get_values() == [1]
    assert row.y == 0


def test_get_row_5099(table):
    row = table.get_row(5099)
    assert row.get_values() == [5100]
    assert row.y == 5099
    assert row.repeated in (None, 1)


def test_get_row_5100(table):
    row = table.get_row(5100)
    assert row.get_values() == ["same"]
    assert row.y == 5100
    assert row.repeated == 100


def test_get_row_5199(table):
    row = table.get_row(5199)
    assert row.get_values() == ["same"]
    assert row.y == 5199
    assert row.repeated == 100


def test_get_row_5200(table):
    row = table.get_row(5200)
    assert row.get_values() == [5101]
    assert row.y == 5200
    assert row.repeated in (None, 1)


def test_get_row_raw_5100(table):
    row = table._get_element_idx2(_XP_ROW_IDX, 5100)
    assert row.get_values() == ["same"]
    assert row.y is None
    assert row.repeated == 100


def test_get_row_raw_5101(table):
    row = table._get_element_idx2(_XP_ROW_IDX, 5101)
    print(row.serialize())
    assert row.get_values() == [5101]
    assert row.y is None
    assert row.repeated in (None, 1)


def test_get_row_raw_20099(table):
    row = table.get_row(20099)
    assert row.get_values() == [20000]
    assert row.y == 20099
    assert row.repeated in (None, 1)


def test_get_row_raw_20100(table):
    row = table.get_row(20100)
    assert row.get_values() == []
    assert row.y == 20100
    assert row.repeated in (None, 1)


def test_traverse_all(table):
    counter = 0
    for _row in table.traverse():
        counter += 1
    assert counter == 20100


def test_traverse_1(table):
    counter = 0
    for _row in table.traverse(0, 10000):
        counter += 1
    assert counter == 10001


def test_traverse_2(table):
    counter = 0
    for _row in table.traverse(1000, 50000):
        counter += 1
    assert counter == 19100


def test_traverse_3(table):
    counter = 0
    for _row in table.traverse(19000, 20000):
        counter += 1
    assert counter == 1001


def test_traverse_4(table):
    counter = 0
    for _row in table.traverse(19000, 19000):
        counter += 1
    assert counter == 1


def test_traverse_5(table):
    counter = 0
    for _row in table.traverse(10, 9):
        counter += 1
    assert counter == 0
