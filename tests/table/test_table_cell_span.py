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
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>

from collections.abc import Iterable

import pytest

from odfdo.document import Document
from odfdo.table import Table


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
def table2(samples) -> Iterable[Table]:
    # simpletable :
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1   2	3	4	5	6	7
    document = Document(samples("simple_table.ods"))
    table = document.body.get_table(name="Example1")
    table2 = table.clone
    table2.set_value("a1", "a")
    table2.set_value("b1", "b")
    table2.set_value("d1", "d")
    table2.set_value("b2", "")
    table2.set_value("c2", "C")
    table2.set_value("d2", "")
    yield table2


def test_span_bad1(table):
    assert table.set_span("a1:a1") is False


def test_span_sp1(table):
    table.set_span("a1:a2")
    # span change only display
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    for coord in ("a1", "a2"):
        assert table.get_cell(coord).is_spanned() is True
    for coord in ("b1", "b2", "a3"):
        assert table.get_cell(coord).is_spanned() is False
    assert table.set_span("a1:a2") is False
    assert table.del_span("a1:a2") is True
    assert table.del_span("a1:a2") is False
    for coord in ("a1", "a2"):
        assert table.get_cell(coord).is_spanned() is False


def test_span_sp1_merge(table2):
    table = table2
    table.set_span("a1:a2", merge=True)
    # span change only display
    assert table.get_values() == [
        ["a 1", "b", 1, "d", 3, 3, 3],
        [None, "", "C", "", 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    for coord in ("a1", "a2"):
        assert table.get_cell(coord).is_spanned() is True
    for coord in ("b1", "b2", "a3"):
        assert table.get_cell(coord).is_spanned() is False
    assert table.set_span("a1:a2") is False
    assert table.del_span("a1:a2") is True
    assert table.del_span("a1:a2") is False
    for coord in ("a1", "a2"):
        assert table.get_cell(coord).is_spanned() is False


def test_span_sp2(table):
    zone = "a1:b3"
    table.set_span(zone)
    # span change only display
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [True, True, False, False, False, False, False],
        [True, True, False, False, False, False, False],
        [True, True, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]


def test_span_sp2_property(table):
    zone = "a1:b3"
    table.set_span(zone)
    # span change only display
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [True, True, False, False, False, False, False],
        [True, True, False, False, False, False, False],
        [True, True, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]


def test_span_sp2_merge(table2):
    table = table2
    zone = "a1:b3"
    table.set_span(zone, merge=True)
    # span change only display
    assert table.get_values() == [
        ["a b 1 1 1", None, 1, "d", 3, 3, 3],
        [None, None, "C", "", 3, 3, 3],
        [None, None, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [True, True, False, False, False, False, False],
        [True, True, False, False, False, False, False],
        [True, True, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]


def test_span_sp2_merge_property(table2):
    table = table2
    zone = "a1:b3"
    table.set_span(zone, merge=True)
    # span change only display
    assert table.get_values() == [
        ["a b 1 1 1", None, 1, "d", 3, 3, 3],
        [None, None, "C", "", 3, 3, 3],
        [None, None, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [True, True, False, False, False, False, False],
        [True, True, False, False, False, False, False],
        [True, True, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]


def test_span_sp3(table):
    zone = "c1:c3"
    table.set_span(zone)
    # span change only display
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, True, False, False, False, False],
        [False, False, True, False, False, False, False],
        [False, False, True, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]


def test_span_sp3_property(table):
    zone = "c1:c3"
    table.set_span(zone)
    # span change only display
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, True, False, False, False, False],
        [False, False, True, False, False, False, False],
        [False, False, True, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]


# table 2
# [[u'a', u'b', 1, u'd', 3, 3, 3],
# [1, u'', u'C', u'', 3, 3, 3],
# [1, 1, 1, 2, 3, 3, 3],
# [1, 2, 3, 4, 5, 6, 7]])


def test_span_sp3_merge(table2):
    table = table2
    zone = "c1:c3"
    table.set_span(zone, merge=True)
    # span change only display
    assert table.get_values() == [
        ["a", "b", "1 C 1", "d", 3, 3, 3],
        [1, "", None, "", 3, 3, 3],
        [1, 1, None, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, True, False, False, False, False],
        [False, False, True, False, False, False, False],
        [False, False, True, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]


def test_span_sp3_merge_property(table2):
    table = table2
    zone = "c1:c3"
    table.set_span(zone, merge=True)
    # span change only display
    assert table.get_values() == [
        ["a", "b", "1 C 1", "d", 3, 3, 3],
        [1, "", None, "", 3, 3, 3],
        [1, 1, None, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, True, False, False, False, False],
        [False, False, True, False, False, False, False],
        [False, False, True, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]


def test_span_sp4(table):
    zone = "g1:g4"
    table.set_span(zone)
    # span change only display
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, True],
        [False, False, False, False, False, False, True],
        [False, False, False, False, False, False, True],
        [False, False, False, False, False, False, True],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]


def test_span_sp4_property(table):
    zone = "g1:g4"
    table.set_span(zone)
    # span change only display
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, True],
        [False, False, False, False, False, False, True],
        [False, False, False, False, False, False, True],
        [False, False, False, False, False, False, True],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]


def test_span_sp42(table2):
    table = table2
    zone = "g1:g4"
    table.set_span(zone, merge=True)
    # span change only display
    assert table.get_values() == [
        ["a", "b", 1, "d", 3, 3, "3 3 3 7"],
        [1, "", "C", "", 3, 3, None],
        [1, 1, 1, 2, 3, 3, None],
        [1, 2, 3, 4, 5, 6, None],
    ]
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, True],
        [False, False, False, False, False, False, True],
        [False, False, False, False, False, False, True],
        [False, False, False, False, False, False, True],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]


def test_span_sp42_property(table2):
    table = table2
    zone = "g1:g4"
    table.set_span(zone, merge=True)
    # span change only display
    assert table.get_values() == [
        ["a", "b", 1, "d", 3, 3, "3 3 3 7"],
        [1, "", "C", "", 3, 3, None],
        [1, 1, 1, 2, 3, 3, None],
        [1, 2, 3, 4, 5, 6, None],
    ]
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, True],
        [False, False, False, False, False, False, True],
        [False, False, False, False, False, False, True],
        [False, False, False, False, False, False, True],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]


def test_span_sp5(table):
    zone = "a3:c4"
    table.set_span(zone)
    # span change only display
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [True, True, True, False, False, False, False],
        [True, True, True, False, False, False, False],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]


def test_span_sp5_property(table):
    zone = "a3:c4"
    table.set_span(zone)
    # span change only display
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [True, True, True, False, False, False, False],
        [True, True, True, False, False, False, False],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]


def test_span_sp5_merge(table2):
    table = table2
    zone = "a3:c4"
    table.set_span(zone, merge=True)
    # span change only display
    assert table.get_values() == [
        ["a", "b", 1, "d", 3, 3, 3],
        [1, "", "C", "", 3, 3, 3],
        ["1 1 1 1 2 3", None, None, 2, 3, 3, 3],
        [None, None, None, 4, 5, 6, 7],
    ]
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [True, True, True, False, False, False, False],
        [True, True, True, False, False, False, False],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]


def test_span_sp5_merge_property(table2):
    table = table2
    zone = "a3:c4"
    table.set_span(zone, merge=True)
    # span change only display
    assert table.get_values() == [
        ["a", "b", 1, "d", 3, 3, 3],
        [1, "", "C", "", 3, 3, 3],
        ["1 1 1 1 2 3", None, None, 2, 3, 3, 3],
        [None, None, None, 4, 5, 6, 7],
    ]
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [True, True, True, False, False, False, False],
        [True, True, True, False, False, False, False],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]


def test_span_sp6(table):
    zone = "b3:f3"
    table.set_span(zone)
    # span change only display
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, True, True, True, True, True, False],
        [False, False, False, False, False, False, False],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]


def test_span_sp6_property(table):
    zone = "b3:f3"
    table.set_span(zone)
    # span change only display
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, True, True, True, True, True, False],
        [False, False, False, False, False, False, False],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]


def test_span_sp6_2zone(table):
    zone = "b3:f3"
    table.set_span(zone)
    # span change only display
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, True, True, True, True, True, False],
        [False, False, False, False, False, False, False],
    ]
    zone2 = "a2:a4"
    table.set_span(zone2)
    # span change only display
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [True, False, False, False, False, False, False],
        [True, True, True, True, True, True, False],
        [True, False, False, False, False, False, False],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [True, False, False, False, False, False, False],
        [True, False, False, False, False, False, False],
        [True, False, False, False, False, False, False],
    ]
    assert table.del_span(zone2) is True
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]


def test_span_sp6_2zone_property(table):
    zone = "b3:f3"
    table.set_span(zone)
    # span change only display
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, True, True, True, True, True, False],
        [False, False, False, False, False, False, False],
    ]
    zone2 = "a2:a4"
    table.set_span(zone2)
    # span change only display
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
    ]
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [True, False, False, False, False, False, False],
        [True, True, True, True, True, True, False],
        [True, False, False, False, False, False, False],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [True, False, False, False, False, False, False],
        [True, False, False, False, False, False, False],
        [True, False, False, False, False, False, False],
    ]
    assert table.del_span(zone2) is True
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
    ]


def test_span_bigger(table):
    zone = "e2:i4"
    table.set_span(zone)
    # span change only display
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None],
        [1, 2, 3, 4, 5, 6, 7, None, None],
    ]
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, True, True, True, True, True],
        [False, False, False, False, True, True, True, True, True],
        [False, False, False, False, True, True, True, True, True],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False, False, False],
    ]


def test_span_bigger_property(table):
    zone = "e2:i4"
    table.set_span(zone)
    # span change only display
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None],
        [1, 2, 3, 4, 5, 6, 7, None, None],
    ]
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, True, True, True, True, True],
        [False, False, False, False, True, True, True, True, True],
        [False, False, False, False, True, True, True, True, True],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False, False, False],
    ]


def test_span_bigger_merge(table):
    zone = "f4:f5"
    table.set_span(zone, merge=True)
    # span change only display
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
        [None, None, None, None, None, None, None],
    ]
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, True, False],
        [False, False, False, False, False, True],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False],
    ]


def test_span_bigger_merge_property(table):
    zone = "f4:f5"
    table.set_span(zone, merge=True)
    # span change only display
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
        [None, None, None, None, None, None, None],
    ]
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, True, False],
        [False, False, False, False, False, True],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False],
    ]


def test_span_bigger_outside(table):
    zone = "g6:i7"
    table.set_span(zone)
    # span change only display
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None],
        [1, 2, 3, 4, 5, 6, 7, None, None],
        [None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None],
    ]
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [],
        [False, False, False, False, False, False, True, True, True],
        [False, False, False, False, False, False, True, True, True],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [],
        [False, False, False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False, False, False],
    ]


def test_span_bigger_outside_property(table):
    zone = "g6:i7"
    table.set_span(zone)
    # span change only display
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None],
        [1, 2, 3, 4, 5, 6, 7, None, None],
        [None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None],
    ]
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [],
        [False, False, False, False, False, False, True, True, True],
        [False, False, False, False, False, False, True, True, True],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [],
        [False, False, False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False, False, False],
    ]


def test_span_bigger_outside_merge(table):
    zone = "g6:i7"
    table.set_span(zone, merge=True)
    # span change only display
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None],
        [1, 2, 3, 4, 5, 6, 7, None, None],
        [None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None],
    ]
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [],
        [False, False, False, False, False, False, True, True, True],
        [False, False, False, False, False, False, True, True, True],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.get_cells():
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [],
        [False, False, False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False, False, False],
    ]


def test_span_bigger_outside_merge_property(table):
    zone = "g6:i7"
    table.set_span(zone, merge=True)
    # span change only display
    assert table.get_values() == [
        [1, 1, 1, 2, 3, 3, 3, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None],
        [1, 1, 1, 2, 3, 3, 3, None, None],
        [1, 2, 3, 4, 5, 6, 7, None, None],
        [None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None],
    ]
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [],
        [False, False, False, False, False, False, True, True, True],
        [False, False, False, False, False, False, True, True, True],
    ]
    assert table.del_span(zone) is True
    res = []
    for r in table.cells:
        test_row = []
        for cell in r:
            test_row.append(cell.is_spanned())
        res.append(test_row)
    assert res == [
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [],
        [False, False, False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False, False, False],
    ]
