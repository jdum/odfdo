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

from collections.abc import Iterable

import pytest

from odfdo import Element
from odfdo.document import Document
from odfdo.table import Table


@pytest.fixture
def body(samples) -> Iterable[Element]:
    document = Document(samples("simple_table.ods"))
    yield document.body


@pytest.fixture
def table(samples) -> Iterable[Table]:
    # simpletable :
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1   2	3	4	5	6	7
    document = Document(samples("simple_table.ods"))
    yield document.body.get_table(name="Example1")


def test_table_empty():
    table = Table("empty")
    table.transpose()
    assert table.get_values() == []


def test_table_empty_2():
    table = Table("empty", 3, 2)
    table.transpose()
    assert table.get_values() == [
        [None, None],
        [None, None],
        [None, None],
    ]


def test_table_empty_3():
    table = Table("empty", 3, 2)
    table.transpose((0, 0, 1, 1))
    assert table.get_values() == [
        [None, None, None],
        [None, None, None],
    ]


# simpletable :
#   1	1	1	2	3	3	3
#   1	1	1	2	3	3	3
#   1	1	1	2	3	3	3
#   1   2	3	4	5	6	7


def test_table_transpose(table):
    table.transpose()
    assert table.get_values() == [
        [1, 1, 1, 1],
        [1, 1, 1, 2],
        [1, 1, 1, 3],
        [2, 2, 2, 4],
        [3, 3, 3, 5],
        [3, 3, 3, 6],
        [3, 3, 3, 7],
    ]


def test_table_transpose_1(table):
    coord = (None, None, None, None)
    table.transpose(coord)
    result = list(table.iter_values(complete=True))
    assert result == [
        [1, 1, 1, 1, None, None, None],
        [1, 1, 1, 2, None, None, None],
        [1, 1, 1, 3, None, None, None],
        [2, 2, 2, 4, None, None, None],
        [3, 3, 3, 5, None, None, None],
        [3, 3, 3, 6, None, None, None],
        [3, 3, 3, 7, None, None, None],
    ]


def test_table_transpose_2(table):
    table.transpose("A1:G1")
    assert table.get_values() == [
        [1, None, None, None, None, None, None],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [2, 2, 3, 4, 5, 6, 7],
        [3, None, None, None, None, None, None],
        [3, None, None, None, None, None, None],
        [3, None, None, None, None, None, None],
    ]


def test_table_transpose_3(table):
    table.delete_row(3)
    table.delete_row(2)
    table.delete_row(1)
    table.transpose()
    assert table.get_values() == [[1], [1], [1], [2], [3], [3], [3]]


def test_table_transpose_3c(table):
    table.delete_column(6)
    table.delete_column(5)
    table.delete_column(4)
    table.delete_column(3)
    table.delete_column(2)
    table.delete_column(1)
    table.transpose()
    assert table.get_values() == [[1, 1, 1, 1]]


def test_table_transpose_4(table):
    table.transpose("F2:F4")
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3, None],
        [1, 1, 1, 2, 3, 3, 3, 6],
        [1, 1, 1, 2, 3, None, 3, None],
        [1, 2, 3, 4, 5, None, 7, None],
    ]
