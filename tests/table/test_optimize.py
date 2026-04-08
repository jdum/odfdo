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

from odfdo.row import Row
from odfdo.table import Table


def test_optimize_width():
    table = Table("TestTable")
    table.set_value("A1", "content")
    table.set_value("A2", "content")
    table.set_value("B1", "content")
    table.set_value("E10", None)
    table.optimize_width()
    assert table.width == 2
    assert table.height >= 2


def test_optimize_width_many_empty_rows():
    table = Table("Test")
    table.set_value("A1", "v1")
    # append 3 empty rows
    table.append_row(Row())
    table.append_row(Row())
    table.append_row(Row())
    # Should keep one empty row
    table.optimize_width()
    assert table.height == 2


def test_optimize_width_all_empty():
    table = Table("Empty")
    table.append_row(Row())
    table.append_row(Row())
    # count == self.height (2)
    table.optimize_width()
    assert table.height == 1


def test_optimize_width_cols_internal():
    table = Table("Test", width=2, height=1)
    # width=2 creates columns.
    table.optimize_width()
    assert table.width == 2


def test_optimize_width_length_internal():
    table = Table("Test")
    table.set_value("A1", "v1")
    table.optimize_width()
    assert table.width == 1


def test_optimize_width_all_empty_try_except():
    table = Table("Empty")
    table.optimize_width()
    assert table.height == 0
