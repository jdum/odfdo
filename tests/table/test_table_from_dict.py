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

from decimal import Decimal
from typing import TYPE_CHECKING, cast

import pytest

from odfdo.document import Document
from odfdo.table import Table

if TYPE_CHECKING:
    from collections.abc import Iterable


@pytest.fixture
def product(samples) -> Iterable[Table]:
    # product table:
    #   reference   color   price
    #   ref01       white   10
    #   ref02       blue    20.5
    #   ref03       red     25.75
    document = Document(samples("store_table.ods"))
    yield cast("Table", document.body.get_table(name="product"))


EXPECTED_VALUES = [
    ["reference", "color", "price"],
    ["ref01", "white", 10],
    ["ref02", "blue", Decimal("20.5")],
    ["ref03", "red", Decimal("25.75")],
]


def test_from_dict_columnar(product):
    data = product.to_dict()
    table = Table.from_dict(data, name="copy")
    assert table.name == "copy"
    assert table.shape == (4, 3)
    assert list(table.iter_values(complete=True)) == EXPECTED_VALUES


def test_from_dict_records(product):
    data = product.to_dict(orient="records")
    table = Table.from_dict(data, name="copy")
    assert table.name == "copy"
    assert table.shape == (4, 3)
    assert list(table.iter_values(complete=True)) == EXPECTED_VALUES


def test_from_dict_matrix(product):
    data = product.to_dict(orient="matrix")
    table = Table.from_dict(data)
    # table name is taken from the matrix dict key
    assert table.name == "product"
    assert table.shape == (4, 3)
    assert list(table.iter_values(complete=True)) == EXPECTED_VALUES


def test_from_dict_matrix_name_override(product):
    data = product.to_dict(orient="matrix")
    table = Table.from_dict(data, name="renamed")
    assert table.name == "renamed"
    assert table.shape == (4, 3)


def test_from_dict_default_name():
    table = Table.from_dict({"a": [1, 2]})
    assert table.name == "Table"
    assert list(table.iter_values(complete=True)) == [["a"], [1], [2]]


def test_from_dict_guess_type():
    data = {"value": ["1", "2.5", "x"]}
    table = Table.from_dict(data, name="guessed", guess_type=True)
    assert list(table.iter_values(complete=True)) == [
        ["value"],
        [1],
        [Decimal("2.5")],
        ["x"],
    ]


def test_from_dict_keep_strings():
    data = {"value": ["1", "2.5", "x"]}
    table = Table.from_dict(data, name="strings")
    assert list(table.iter_values(complete=True)) == [
        ["value"],
        ["1"],
        ["2.5"],
        ["x"],
    ]


def test_from_dict_scalar_column_value():
    data = {"a": [1, 2], "b": 3}
    table = Table.from_dict(data, name="scalar")
    assert list(table.iter_values(complete=True)) == [
        ["a", "b"],
        [1, 3],
        [2, None],
    ]


def test_from_dict_uneven_columns():
    data = {"a": [1, 2, 3], "b": [4]}
    table = Table.from_dict(data, name="uneven")
    assert list(table.iter_values(complete=True)) == [
        ["a", "b"],
        [1, 4],
        [2, None],
        [3, None],
    ]


def test_from_dict_empty_dict():
    table = Table.from_dict({}, name="empty")
    assert table.name == "empty"
    assert table.shape == (0, 0)


def test_from_dict_empty_list():
    table = Table.from_dict([], name="empty")
    assert table.name == "empty"
    assert table.shape == (0, 0)


def test_from_dict_bad_type():
    with pytest.raises(TypeError, match="data must be a dict or list of dicts"):
        Table.from_dict("not a dict")  # type: ignore[arg-type]


def test_from_dict_list_of_non_dicts():
    with pytest.raises(TypeError, match="List elements must be dictionaries"):
        Table.from_dict([1, 2, 3])  # type: ignore[list-item]


def test_from_dict_store_json_roundtrip(samples):
    document = Document(samples("store_table.ods"))
    store = cast("Table", document.body.get_table(name="store"))
    data = store.to_dict(mode="json")
    table = Table.from_dict(data, name="store_copy")
    assert list(table.iter_values(complete=True)) == [
        ["reference", "quantity", "available", "date"],
        ["ref01", 10, True, "2026-12-25"],
        ["ref02", 5, True, "2026-12-24"],
        ["ref03", 0, False, "2026-12-23"],
    ]


def test_from_dict_matrix_empty_list():
    table = Table.from_dict({"Sheet1": []})
    assert table.name == "Sheet1"
    assert table.shape == (0, 0)


def test_from_dict_matrix_guess_type():
    data = {"MyMatrix": [["1", "2.5"], ["10", "x"]]}
    table = Table.from_dict(data, guess_type=True)
    assert table.name == "MyMatrix"
    assert list(table.iter_values(complete=True)) == [
        [1, Decimal("2.5")],
        [10, "x"],
    ]


def test_from_dict_records_guess_type():
    data = [{"num": "1", "val": "2.5"}, {"num": "10", "val": "3.75"}]
    table = Table.from_dict(data, name="rec_guess", guess_type=True)
    assert list(table.iter_values(complete=True)) == [
        ["num", "val"],
        [1, Decimal("2.5")],
        [10, Decimal("3.75")],
    ]


def test_from_dict_records_keep_strings():
    data = [{"num": "1", "val": "2.5"}]
    table = Table.from_dict(data, name="rec_str", guess_type=False)
    assert list(table.iter_values(complete=True)) == [
        ["num", "val"],
        ["1", "2.5"],
    ]


def test_from_dict_records_subsequent_non_dict():
    with pytest.raises(TypeError, match="List elements must be dictionaries"):
        Table.from_dict([{"a": 1}, 42])  # type: ignore[list-item]


def test_from_dict_records_disjoint_keys():
    data = [{"a": 1}, {"b": 2, "a": 3}]
    table = Table.from_dict(data, name="disjoint")
    assert list(table.iter_values(complete=True)) == [
        ["a", "b"],
        [1, None],
        [3, 2],
    ]


def test_from_dict_columns_empty_lists():
    data = {"col1": [], "col2": []}
    table = Table.from_dict(data, name="empty_cols")
    assert list(table.iter_values(complete=True)) == [
        ["col1", "col2"],
    ]


def test_from_dict_columns_tuples():
    data = {"a": (1, 2), "b": (3, 4)}
    table = Table.from_dict(data, name="tuples")
    assert list(table.iter_values(complete=True)) == [
        ["a", "b"],
        [1, 3],
        [2, 4],
    ]


def test_from_dict_default_name_empty():
    t_dict = Table.from_dict({})
    assert t_dict.name == "Table"
    t_list = Table.from_dict([])
    assert t_list.name == "Table"

