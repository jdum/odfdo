# Copyright 2018-2025 Jérôme Dumonteil
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

from odfdo import Table
from odfdo.document import Document


@pytest.fixture
def table(samples) -> Iterable[Table]:
    # simpletable :
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1   2	3	4	5	6	7
    document = Document(samples("simple_table.ods"))
    yield document.body.get_table(name="Example1")


@pytest.fixture
def table3(samples) -> Iterable[Table]:
    # simpletable :
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1   2	3	4	5	6	7
    document = Document(samples("simple_table.ods"))
    yield document.body.get_table(name="Example3")


def test_str_sample1(table):
    result = str(table)
    assert "1 1 1 2 3 3 3" in result
    assert "1 2 3 4 5 6 7" in result


def test_str_sample3(table3):
    result = str(table3)
    assert '"A float"' in result
    assert "3.14" in result
