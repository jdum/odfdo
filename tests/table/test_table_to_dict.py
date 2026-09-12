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

from datetime import date
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


@pytest.fixture
def store(samples) -> Iterable[Table]:
    # store table:
    #   reference   quantity    available   date
    #   ref01       10          True        2026-12-25
    #   ref02       5           True        2026-12-24
    #   ref03       0           False       2026-12-23
    document = Document(samples("store_table.ods"))
    yield cast("Table", document.body.get_table(name="store"))


def test_to_dict_default(product):
    result = product.to_dict()
    assert result == {
        "reference": ["ref01", "ref02", "ref03"],
        "color": ["white", "blue", "red"],
        "price": [10, Decimal("20.5"), Decimal("25.75")],
    }


def test_to_dict_orient_list(product):
    result = product.to_dict(orient="list")
    assert result == {
        "reference": ["ref01", "ref02", "ref03"],
        "color": ["white", "blue", "red"],
        "price": [10, Decimal("20.5"), Decimal("25.75")],
    }


def test_to_dict_records(product):
    result = product.to_dict(orient="records")
    assert result == [
        {"reference": "ref01", "color": "white", "price": 10},
        {"reference": "ref02", "color": "blue", "price": Decimal("20.5")},
        {"reference": "ref03", "color": "red", "price": Decimal("25.75")},
    ]


def test_to_dict_matrix(product):
    result = product.to_dict(orient="matrix")
    assert result == {
        "product": [
            ["reference", "color", "price"],
            ["ref01", "white", 10],
            ["ref02", "blue", Decimal("20.5")],
            ["ref03", "red", Decimal("25.75")],
        ]
    }


def test_to_dict_header_false(product):
    result = product.to_dict(header=False)
    assert result == {
        "0": ["reference", "ref01", "ref02", "ref03"],
        "1": ["color", "white", "blue", "red"],
        "2": ["price", 10, Decimal("20.5"), Decimal("25.75")],
    }


def test_to_dict_json_mode(product):
    result = product.to_dict(mode="json")
    assert result == {
        "reference": ["ref01", "ref02", "ref03"],
        "color": ["white", "blue", "red"],
        "price": [10, 20.5, 25.75],
    }


def test_to_dict_no_decimal(product):
    result = product.to_dict(no_decimal=True)
    assert result["price"] == [10, 20.5, 25.75]


def test_to_dict_lstrip():
    table = Table("T", width=3, height=3)
    table.set_value((2, 2), "x")
    result = table.to_dict(orient="matrix")
    assert result == {"T": [[], [], [None, None, "x"]]}
    result = table.to_dict(orient="matrix", lstrip=True)
    assert result == {"T": [["x"]]}


def test_to_dict_invalid_orient(product):
    with pytest.raises(ValueError, match="Invalid orient parameter"):
        product.to_dict(orient="bogus")
    with pytest.raises(ValueError, match="Invalid orient parameter"):
        product.to_dict(orient="dict")


def test_to_dict_duplicate_headers():
    table = Table("dup", width=2, height=2)
    table.set_value((0, 0), "a")
    table.set_value((1, 0), "a")
    table.set_value((0, 1), 1)
    table.set_value((1, 1), 2)
    assert table.to_dict() == {"a": [1], "a2": [2]}
    assert table.to_dict(orient="records") == [{"a": 1, "a2": 2}]


def test_to_dict_unnamed_header():
    table = Table("unnamed", width=3, height=2)
    table.set_value((0, 0), "a")
    table.set_value((2, 0), "b")
    table.set_value((0, 1), 1)
    table.set_value((1, 1), 2)
    table.set_value((2, 1), 3)
    assert table.to_dict() == {"a": [1], "Unnamed: 1": [2], "b": [3]}
    assert table.to_dict(orient="records") == [{"a": 1, "Unnamed: 1": 2, "b": 3}]


def test_to_dict_empty_table():
    table = Table("empty")
    assert table.to_dict() == {}
    assert table.to_dict(orient="records") == []
    assert table.to_dict(orient="matrix") == {"empty": []}


def test_to_dict_store_types(store):
    result = store.to_dict(orient="records")
    assert result == [
        {
            "reference": "ref01",
            "quantity": 10,
            "available": True,
            "date": date(2026, 12, 25),
        },
        {
            "reference": "ref02",
            "quantity": 5,
            "available": True,
            "date": date(2026, 12, 24),
        },
        {
            "reference": "ref03",
            "quantity": 0,
            "available": False,
            "date": date(2026, 12, 23),
        },
    ]


def test_to_dict_store_json_mode(store):
    result = store.to_dict(mode="json")
    assert result["date"] == ["2026-12-25", "2026-12-24", "2026-12-23"]
    assert result["available"] == [True, True, False]


def test_to_dict_records_header_false(product):
    result = product.to_dict(orient="records", header=False)
    assert result == [
        {"0": "reference", "1": "color", "2": "price"},
        {"0": "ref01", "1": "white", "2": 10},
        {"0": "ref02", "1": "blue", "2": Decimal("20.5")},
        {"0": "ref03", "1": "red", "2": Decimal("25.75")},
    ]


def test_to_dict_matrix_unnamed_table():
    table = Table()
    table.set_value("A1", "hello")
    result = table.to_dict(orient="matrix")
    assert result == {"Sheet1": [["hello"]]}


def test_to_dict_headers_only():
    table = Table("headers_only", width=2, height=1)
    table.set_value("A1", "col_a")
    table.set_value("B1", "col_b")
    assert table.to_dict() == {"col_a": [], "col_b": []}
    assert table.to_dict(orient="records") == []


def test_to_dict_ragged_rows():
    table = Table("ragged", width=3, height=3)
    table.set_value("A1", "h1")
    table.set_value("B1", "h2")
    table.set_value("C1", "h3")
    table.set_value("A2", 1)
    table.set_value("B2", 2)
    # C2 left empty / missing
    table.set_value("A3", 3)
    assert table.to_dict() == {
        "h1": [1, 3],
        "h2": [2, None],
        "h3": [None, None],
    }
    assert table.to_dict(orient="records") == [
        {"h1": 1, "h2": 2, "h3": None},
        {"h1": 3, "h2": None, "h3": None},
    ]


def test_to_dict_no_date_option(store):
    result = store.to_dict(no_date=True)
    assert result["date"] == ["2026-12-25", "2026-12-24", "2026-12-23"]


def test_to_dict_no_nan_option():
    table = Table("nan_table", width=3, height=2)
    table.set_value("A1", "h1")
    table.set_value("B1", "h2")
    table.set_value("C1", "h3")
    table.set_value("A2", float("nan"))
    table.set_value("B2", float("inf"))
    table.set_value("C2", 123)
    result = table.to_dict(no_nan=True)
    assert result == {"h1": [None], "h2": [None], "h3": [123]}
