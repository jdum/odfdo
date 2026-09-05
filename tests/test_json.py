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
import json
from datetime import date, datetime, timedelta
from decimal import Decimal
from textwrap import dedent
from unittest.mock import PropertyMock, patch

import pytest

from odfdo.document import Document
from odfdo.row import Row
from odfdo.table import Table


def test_document_to_json_ods(samples):
    doc = Document(samples("legacy_content.ods"))
    json_str = doc.to_json(pretty=True)
    assert json_str is not None
    data = json.loads(json_str)

    assert "Employees" in data
    assert "Figures" in data
    assert data["Employees"] == [
        ["Name", "Country"],
        ["Alice", "USA"],
        ["Gaël", "France"],
    ]
    assert data["Figures"] == [
        ["Number", "Bool"],
        [1, True],
        [-2, False],
        [3.14, ""],
    ]


def test_document_to_json_odt(samples):
    doc = Document(samples("table.odt"))
    json_str = doc.to_json()
    assert json_str is not None
    data = json.loads(json_str)

    assert "Tableau1" in data
    assert "Tableau2" in data
    assert len(data["Tableau1"]) == 5
    assert len(data["Tableau2"]) == 3


def test_document_to_json_file(samples, tmp_path):
    doc = Document(samples("legacy_content.ods"))
    output_path = tmp_path / "output.json"

    res = doc.to_json(path_or_file=output_path, pretty=True)
    assert res is None
    assert output_path.exists()

    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert "Employees" in data
    assert "Figures" in data


def test_table_to_json(samples):
    doc = Document(samples("legacy_content.ods"))
    table = doc.body.tables[0]
    json_str = table.to_json(pretty=True)
    assert json_str is not None
    data = json.loads(json_str)

    assert data == {
        "Employees": [
            ["Name", "Country"],
            ["Alice", "USA"],
            ["Gaël", "France"],
        ]
    }


def test_table_to_json_file(samples, tmp_path):
    doc = Document(samples("legacy_content.ods"))
    table = doc.body.tables[0]
    output_path = tmp_path / "table.json"

    res = table.to_json(path_or_file=output_path, pretty=True)
    assert res is None
    assert output_path.exists()

    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert "Employees" in data


def test_table_from_json_dict():
    json_data = {"Sheet1": [["A", "B"], [1, 2]]}
    table = Table.from_json(json_data)
    assert table.name == "Sheet1"
    assert table.values == [["A", "B"], [1, 2]]


def test_table_from_json_list():
    rows = [["X", "Y"], [10, 20]]
    table = Table.from_json(rows, name="CustomTable")
    assert table.name == "CustomTable"
    assert table.values == [["X", "Y"], [10, 20]]


def test_table_from_json_string():
    json_str = json.dumps({"Data": [["col1", "col2"], [1.5, True]]})
    table = Table.from_json(json_str)
    assert table.name == "Data"
    assert table.values == [["col1", "col2"], [Decimal("1.5"), True]]


def test_json_serialization_data_types():
    table = Table("Some table")
    row = Row()
    row.set_value(0, "text")
    row.set_value(1, 42)
    row.set_value(2, 3.14)
    row.set_value(3, Decimal("99.99"))
    row.set_value(4, True)
    row.set_value(5, date(2026, 8, 15))
    row.set_value(6, datetime(2026, 8, 15, 14, 30))
    row.set_value(7, timedelta(hours=2))
    table.append_row(row)

    expected = dedent("""\
        {
          "Some table": [
            ["text", 42, 3.14, 99.99, true, "2026-08-15", "2026-08-15T14:30:00", "PT02H00M00S"]
          ]
        }
    """).strip()

    json_str = table.to_json(pretty=True)
    print(json_str)
    assert json_str.strip() == expected

    data = json.loads(json_str)

    row_data = data["Some table"][0]
    assert row_data[0] == "text"
    assert row_data[1] == 42
    assert row_data[2] == 3.14
    assert row_data[3] == 99.99
    assert row_data[4] is True
    assert row_data[5] == "2026-08-15"
    assert row_data[6] == "2026-08-15T14:30:00"
    assert row_data[7] == "PT02H00M00S"


def test_document_to_json_duplicate_table_names():
    doc = Document.new("text")
    t1 = Table()
    t1.set_value("A1", 1)
    t2 = Table()
    t2.set_value("A1", 2)
    t3 = Table()
    t3.set_value("A1", 3)
    t4 = Table("Sheet1")
    t4.set_value("A1", 4)
    t5 = Table("Sheet1")
    t5.set_value("A1", 5)

    doc.body.append(t1)
    doc.body.append(t2)
    doc.body.append(t3)
    doc.body.append(t4)
    doc.body.append(t5)

    js_str = doc.to_json()
    assert js_str is not None
    data = json.loads(js_str)
    assert "Table" in data
    assert "Table_2" in data
    assert "Table_3" in data
    assert "Sheet1" in data
    assert "Sheet1_2" in data
    assert data["Table"] == [[1]]
    assert data["Table_2"] == [[2]]
    assert data["Table_3"] == [[3]]
    assert data["Sheet1"] == [[4]]
    assert data["Sheet1_2"] == [[5]]


def test_table_to_json_custom_object():
    class CustomObj:
        def __str__(self):
            return "custom_val"

    table = Table("CustomTable")
    with patch.object(
        type(table), "values", new_callable=PropertyMock, return_value=[[CustomObj()]]
    ):
        js_str = table.to_json()
        assert js_str is not None
        data = json.loads(js_str)
        assert data["CustomTable"] == [["custom_val"]]


def test_table_from_json_empty_dict():
    table1 = Table.from_json({})
    assert table1.name == "Table"
    assert table1.values == []

    table2 = Table.from_json({}, name="EmptySheet")
    assert table2.name == "EmptySheet"
    assert table2.values == []


def test_table_from_json_invalid_type():
    with pytest.raises(TypeError):
        Table.from_json(123)

    with pytest.raises(TypeError):
        Table.from_json("123")


def test_document_from_json_dict():
    data = {
        "Sheet1": [["A", "B"], [1, 2]],
        "Sheet2": [["C", "D"], [3, 4]],
    }
    doc = Document.from_json(data)
    assert len(doc.body.tables) >= 2
    table1 = doc.body.get_table(name="Sheet1")
    assert table1 is not None
    assert table1.values == [["A", "B"], [1, 2]]
    table2 = doc.body.get_table(name="Sheet2")
    assert table2 is not None
    assert table2.values == [["C", "D"], [3, 4]]


def test_document_from_json_string():
    json_str = json.dumps({"Data": [["Col1", "Col2"], [10, True]]})
    doc = Document.from_json(json_str)
    table = doc.body.get_table(name="Data")
    assert table is not None
    assert table.values == [["Col1", "Col2"], [10, True]]


def test_document_from_json_path_and_filename(tmp_path):
    data = {"Info": [["Key", "Val"], ["Version", 1]]}
    file_path = tmp_path / "doc_data.json"
    file_path.write_text(json.dumps(data), encoding="utf-8")

    # Test with Path object
    doc1 = Document.from_json(file_path)
    assert doc1.body.get_table(name="Info") is not None

    # Test with string path to file
    doc2 = Document.from_json(str(file_path))
    assert doc2.body.get_table(name="Info") is not None


def test_document_from_json_invalid_types():
    with pytest.raises(TypeError):
        Document.from_json(123)  # type: ignore[arg-type]


def test_document_from_json_long_string_oserror():
    long_str = "{" + "a" * 1000 + "}"
    with pytest.raises(json.JSONDecodeError):
        Document.from_json(long_str)
