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

from odfdo.column import Column


@pytest.fixture
def column() -> Iterable[Column]:
    yield Column(default_cell_style="ce5", repeated=7, style="co1")


def test_get_column_default_cell_style(column):
    assert column.get_default_cell_style() == "ce5"


def test_get_column_default_cell_style_property(column):
    assert column.default_cell_style == "ce5"


def test_set_column_default_cell_style(column):
    column.set_default_cell_style("ce2")
    assert column.get_default_cell_style() == "ce2"
    column.set_default_cell_style(None)
    assert column.get_default_cell_style() is None


def test_set_column_default_cell_style_property(column):
    column.default_cell_style = "ce2"
    assert column.default_cell_style == "ce2"
    column.default_cell_style = None
    assert column.default_cell_style is None


def test_get_column_repeated(column):
    assert column.repeated == 7


def test_set_column_repeated(column):
    column.repeated = 99
    assert column.repeated == 99
    column.repeated = 1
    assert column.repeated is None
    column.repeated = 2
    assert column.repeated == 2
    column.repeated = None
    assert column.repeated is None


def test_get_column_style(column):
    assert column.style == "co1"


def test_set_column_style(column):
    column.style = "co2"
    assert column.style == "co2"
    column.style = None
    assert column.style is None
