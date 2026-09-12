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
# Authors (offdo project): jerome.dumonteil@gmail.com
# The odfdo project is a derivative work of the lpod-python project:
# https://github.com/lpod/lpod-python
from __future__ import annotations

from decimal import Decimal

import pytest

from odfdo.document import Document
from odfdo.table import Table


def test_document_to_dict_all_tables(samples):
    doc = Document(samples("store_table.ods"))
    result = doc.to_dict()
    assert "product" in result
    assert "store" in result
    assert result["product"]["reference"] == ["ref01", "ref02", "ref03"]
    assert result["store"]["reference"] == ["ref01", "ref02", "ref03"]


def test_document_to_dict_specific_table_by_name(samples):
    doc = Document(samples("store_table.ods"))
    result = doc.to_dict(table="product")
    assert result == {
        "reference": ["ref01", "ref02", "ref03"],
        "color": ["white", "blue", "red"],
        "price": [10, Decimal("20.5"), Decimal("25.75")],
    }


def test_document_to_dict_specific_table_by_index(samples):
    doc = Document(samples("store_table.ods"))
    result = doc.to_dict(table=0)
    assert result["reference"] == ["ref01", "ref02", "ref03"]


def test_document_to_dict_table_not_found(samples):
    doc = Document(samples("store_table.ods"))
    with pytest.raises(KeyError, match="not found in document"):
        doc.to_dict(table="nonexistent")


def test_document_to_dict_table_index_out_of_range(samples):
    doc = Document(samples("store_table.ods"))
    with pytest.raises(IndexError, match="out of range"):
        doc.to_dict(table=99)


def test_document_to_dict_orient_list(samples):
    doc = Document(samples("store_table.ods"))
    result = doc.to_dict(orient="list")
    assert "product" in result
    assert "store" in result
    assert result["product"]["reference"] == ["ref01", "ref02", "ref03"]


def test_document_to_dict_invalid_orient(samples):
    doc = Document(samples("store_table.ods"))
    with pytest.raises(ValueError, match="Invalid orient parameter"):
        doc.to_dict(orient="bogus")
    with pytest.raises(ValueError, match="Invalid orient parameter"):
        doc.to_dict(orient="dict")


def test_document_to_dict_orient_matrix(samples):
    doc = Document(samples("store_table.ods"))
    result = doc.to_dict(orient="matrix")
    assert "product" in result
    assert "store" in result
    assert result["product"][0] == ["reference", "color", "price"]


def test_document_to_dict_unnamed_tables():
    doc = Document("spreadsheet")
    doc.body.clear()
    t1 = Table()
    t1.set_value("A1", "v1")
    t2 = Table()
    t2.set_value("A1", "v2")
    doc.body.append(t1)
    doc.body.append(t2)
    result = doc.to_dict()
    assert "Sheet1" in result
    assert "Sheet2" in result


def test_document_from_dict_empty():
    doc = Document.from_dict({})
    tables = doc.body.tables
    assert len(tables) == 1
    assert tables[0].name == "Sheet1"
    assert tables[0].shape == (0, 0)


def test_document_from_dict_empty_with_custom_name():
    doc = Document.from_dict({}, table_name="Custom")
    tables = doc.body.tables
    assert len(tables) == 1
    assert tables[0].name == "Custom"


def test_document_from_dict_columnar():
    data = {"col1": [1, 2], "col2": [3, 4]}
    doc = Document.from_dict(data)
    tables = doc.body.tables
    assert len(tables) == 1
    assert tables[0].name == "Sheet1"
    assert list(tables[0].iter_values(complete=True)) == [
        ["col1", "col2"],
        [1, 3],
        [2, 4],
    ]


def test_document_from_dict_records():
    data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    doc = Document.from_dict(data)
    tables = doc.body.tables
    assert len(tables) == 1
    assert tables[0].name == "Sheet1"
    assert list(tables[0].iter_values(complete=True)) == [
        ["a", "b"],
        [1, 2],
        [3, 4],
    ]


def test_document_from_dict_single_matrix():
    data = {"MyMatrix": [["a", "b"], [1, 2]]}
    doc = Document.from_dict(data)
    tables = doc.body.tables
    assert len(tables) == 1
    assert tables[0].name == "MyMatrix"
    assert list(tables[0].iter_values(complete=True)) == [
        ["a", "b"],
        [1, 2],
    ]


def test_document_from_dict_single_matrix_with_table_name_override():
    data = {"MyMatrix": [["a", "b"], [1, 2]]}
    doc = Document.from_dict(data, table_name="CustomMatrix")
    tables = doc.body.tables
    assert len(tables) == 1
    assert tables[0].name == "CustomMatrix"
    assert list(tables[0].iter_values(complete=True)) == [
        ["a", "b"],
        [1, 2],
    ]


def test_document_from_dict_single_matrix_empty():
    data = {"EmptyMatrix": []}
    doc = Document.from_dict(data)
    tables = doc.body.tables
    assert len(tables) == 1
    assert tables[0].name == "EmptyMatrix"
    assert tables[0].shape == (0, 0)


def test_document_from_dict_multi_sheet_dict():
    data = {
        "SheetA": {"c1": [10]},
        "SheetB": {"c2": [20]},
    }
    doc = Document.from_dict(data)
    tables = doc.body.tables
    assert len(tables) == 2
    assert tables[0].name == "SheetA"
    assert tables[1].name == "SheetB"


def test_document_from_dict_multi_sheet_records():
    data = {
        "SheetA": [{"c1": 10}],
        "SheetB": [{"c2": 20}],
    }
    doc = Document.from_dict(data)
    tables = doc.body.tables
    assert len(tables) == 2
    assert tables[0].name == "SheetA"
    assert tables[1].name == "SheetB"


def test_document_from_dict_multi_sheet_matrix():
    data = {
        "SheetA": [["c1"], [10]],
        "SheetB": [["c2"], [20]],
    }
    doc = Document.from_dict(data)
    tables = doc.body.tables
    assert len(tables) == 2
    assert tables[0].name == "SheetA"
    assert tables[1].name == "SheetB"


def test_document_from_dict_unnamed_multi_sheets():
    data = {
        "": {"c1": [1]},
        "SheetA": {"c2": [2]},
    }
    doc = Document.from_dict(data)
    tables = doc.body.tables
    assert len(tables) == 2
    assert tables[0].name == "Sheet1"
    assert tables[1].name == "SheetA"


def test_document_from_dict_duplicate_sheet_names():
    data = {
        "": {"c1": [1]},
        "Sheet1": {"c2": [2]},
    }
    doc = Document.from_dict(data)
    tables = doc.body.tables
    assert len(tables) == 2
    assert tables[0].name == "Sheet1"
    assert tables[1].name == "Sheet12"


def test_document_from_dict_with_language():
    doc = Document.from_dict({"a": [1]}, language="fr-FR")
    assert doc.language == "fr-FR"


def test_document_from_dict_invalid_type():
    with pytest.raises(TypeError, match="data must be a dict or list of dicts"):
        Document.from_dict(12345)  # type: ignore[arg-type]


def test_document_to_dict_include_hidden(samples):
    doc = Document(samples("store_table.ods"))
    doc.set_table_displayed(1, False)
    assert len(doc.to_dict(include_hidden=False)) == 1
    assert len(doc.to_dict(include_hidden=True)) == 2
