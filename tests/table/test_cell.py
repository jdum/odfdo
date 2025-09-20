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

from odfdo.cell import Cell

EURO = "€"


@pytest.fixture
def cell() -> Iterable[Cell]:
    yield Cell(1, repeated=3, style="ce5")


def test_cell_repr_not_in_table(cell):
    assert repr(cell) == "<Cell x=None y=None>"


def test_get_cell_value(cell):
    assert cell.get_value() == 1
    assert cell.get_value(get_type=True) == (1, "float")


def test_set_cell_value(cell):
    cell.set_value(EURO)
    assert cell.get_value() == EURO
    assert cell.type == "string"
    assert cell.get_value(get_type=True) == (EURO, "string")


def test_get_cell_type(cell):
    assert cell.type == "float"
    cell.set_value(EURO)
    assert cell.type == "string"


def test_get_cell_type_percentage():
    cell = Cell(90, cell_type="percentage")
    assert cell.type == "percentage"
    assert cell.get_value(get_type=True) == (90, "percentage")


def test_get_cell_type_percentage_2(cell):
    cell.type = "percentage"
    assert cell.type == "percentage"
    assert cell.get_value(get_type=True) == (1, "percentage")


def test_set_cell_type(cell):
    cell.type = "time"
    assert cell.type == "time"


def test_set_cell_type_date(cell):
    cell.type = "date"
    assert cell.type == "date"


def test_get_cell_currency():
    cell = Cell(123, cell_type="currency", currency="EUR")
    assert cell.currency == "EUR"
    assert cell.type == "currency"
    assert cell.get_value(get_type=True) == (123, "currency")


def test_set_cell_currency():
    cell = Cell(123, cell_type="currency", currency="EUR")
    cell.currency = "CHF"
    assert cell.currency == "CHF"


def test_get_cell_repeated(cell):
    assert cell.repeated == 3


def test_set_cell_repeated(cell):
    cell.repeated = 99
    assert cell.repeated == 99
    cell.repeated = 1
    assert cell.repeated is None
    cell.repeated = 2
    assert cell.repeated == 2
    cell.repeated = None
    assert cell.repeated is None


def test_get_cell_style(cell):
    assert cell.style == "ce5"
    cell.style = "something blue"
    assert cell.style == "something blue"
    cell.style = None
    assert cell.style is None


def test_set_cell_style(cell):
    cell.style = "ce2"
    assert cell.style == "ce2"
    cell.style = None
    assert cell.style is None


def test_set_cell_formula(cell):
    cell.formula = "any string"
    assert cell.formula == "any string"
    cell.formula = None
    assert cell.formula is None


def test_set_cell_formula_2(cell):
    cell.set_value(4, formula="4")
    assert cell.value == 4
    assert cell.formula == "4"
