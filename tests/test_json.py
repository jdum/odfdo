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
    json_str = doc.to_json()
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

    res = doc.to_json(path_or_file=output_path)
    assert res is None
    assert output_path.exists()

    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert "Employees" in data
    assert "Figures" in data


def test_table_to_json(samples):
    doc = Document(samples("legacy_content.ods"))
    table = doc.body.tables[0]
    json_str = table.to_json()
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

    res = table.to_json(path_or_file=output_path)
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
    t4 = Table("Table1")
    t4.set_value("A1", 4)
    t5 = Table("Table1")
    t5.set_value("A1", 5)

    doc.body.append(t1)
    doc.body.append(t2)
    doc.body.append(t3)
    doc.body.append(t4)
    doc.body.append(t5)

    js_str = doc.to_json()
    assert js_str is not None
    data = json.loads(js_str)
    assert "Sheet1" in data
    assert "Sheet2" in data
    assert "Sheet3" in data
    assert "Table1" in data
    assert "Table12" in data
    assert data["Sheet1"] == [[1]]
    assert data["Sheet2"] == [[2]]
    assert data["Sheet3"] == [[3]]
    assert data["Table1"] == [[4]]
    assert data["Table12"] == [[5]]


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


def test_table_to_json_custom_object_no_name():
    class CustomObj:
        def __str__(self):
            return "custom_val"

    table = Table()
    with patch.object(
        type(table), "values", new_callable=PropertyMock, return_value=[[CustomObj()]]
    ):
        js_str = table.to_json()
        assert js_str is not None
        data = json.loads(js_str)
        assert data["Sheet1"] == [["custom_val"]]


def test_table_from_json_empty_dict():
    table1 = Table.from_json({})
    assert table1.name == "Sheet1"
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
    t1 = doc.body.get_table(name="Sheet1")
    assert t1 is not None
    assert t1.values == [["A", "B"], [1, 2]]
    t2 = doc.body.get_table(name="Sheet2")
    assert t2 is not None
    assert t2.values == [["C", "D"], [3, 4]]


def test_document_from_json_string():
    json_str = json.dumps({"Data": [["Col1", "Col2"], [10, True]]})
    doc = Document.from_json(json_str)
    t = doc.body.get_table(name="Data")
    assert t is not None
    assert t.values == [["Col1", "Col2"], [10, True]]


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
    with pytest.raises(
        TypeError, match="JSON content must be a string, Path, dict or list"
    ):
        Document.from_json(123)  # type: ignore[arg-type]
    with pytest.raises(
        TypeError, match="JSON content must be a string, Path, dict or list"
    ):
        Document.from_json(None)  # type: ignore[arg-type]


def test_document_from_json_list():
    rows = [["Header1", "Header2"], [10, 20]]
    doc = Document.from_json(rows, table_name="CustomTable")
    assert len(doc.body.tables) == 1
    t = doc.body.tables[0]
    assert t.name == "CustomTable"
    assert t.values == [["Header1", "Header2"], [10, 20]]


def test_document_from_json_list_no_name():
    rows = [["Header1", "Header2"], [10, 20]]
    doc = Document.from_json(rows)
    assert len(doc.body.tables) == 1
    t = doc.body.tables[0]
    assert t.name == "Sheet1"
    assert t.values == [["Header1", "Header2"], [10, 20]]


def test_document_from_json_list_json_str():
    json_str = '[["ColA", "ColB"], ["X", "Y"]]'
    doc = Document.from_json(json_str, table_name="ListTable")
    assert len(doc.body.tables) == 1
    t = doc.body.tables[0]
    assert t.name == "ListTable"
    assert t.values == [["ColA", "ColB"], ["X", "Y"]]


def test_document_from_json_primitive_json_str():
    with pytest.raises(TypeError, match="JSON document content must be a dictionary"):
        Document.from_json("123")
    with pytest.raises(TypeError, match="JSON document content must be a dictionary"):
        Document.from_json('"string_value"')
    with pytest.raises(TypeError, match="JSON document content must be a dictionary"):
        Document.from_json("true")


def test_document_from_json_primitive_path(tmp_path):
    p = tmp_path / "primitive.json"
    p.write_text("123", encoding="utf-8")
    with pytest.raises(TypeError, match="JSON document content must be a dictionary"):
        Document.from_json(p)


def test_document_from_json_long_string_oserror():
    long_str = "{" + "a" * 1000 + "}"
    with pytest.raises(json.JSONDecodeError):
        Document.from_json(long_str)


def test_serialize_table_rows_trailing_none_and_empty_rows():
    table = Table("TrailingTest")
    with patch.object(
        type(table),
        "values",
        new_callable=PropertyMock,
        return_value=[
            [1, 2, None, None],
            [None, None, None, None],
            [None, None],
        ],
    ):
        rows = table._serialize_table_rows()
        assert rows == [[1, 2]]


def test_serialize_table_rows_all_none_rows():
    table = Table("EmptyTest")
    with patch.object(
        type(table),
        "values",
        new_callable=PropertyMock,
        return_value=[
            [None, None],
            [None, None],
        ],
    ):
        rows = table._serialize_table_rows()
        assert rows == []


def test_document_roundtrip_legacy_content(samples):
    doc_orig = Document(samples("legacy_content.ods"))
    json_str = doc_orig.to_json()
    assert json_str is not None

    data = json.loads(json_str)
    new_doc = Document.from_json(data)

    assert len(new_doc.body.tables) == 2
    assert new_doc.body.tables[0].name == "Employees"
    assert new_doc.body.tables[1].name == "Figures"
    assert new_doc.body.tables[0].values == doc_orig.body.tables[0].values


def test_document_roundtrip_large_ods(samples):
    doc_orig = Document(samples("large_ods.ods"))
    json_str = doc_orig.to_json()
    assert json_str is not None

    data = json.loads(json_str)
    assert len(data) == 3
    assert "Sheet1" in data
    assert "Sheet2" in data
    assert "Sheet3" in data
    assert len(data["Sheet1"]) == 5000
    assert len(data["Sheet2"]) == 5000
    assert len(data["Sheet3"]) == 5000

    new_doc = Document.from_json(data)
    assert len(new_doc.body.tables) == 3
    for orig_table, new_table in zip(doc_orig.body.tables, new_doc.body.tables, strict=True):
        assert new_table.name == orig_table.name
        assert new_table.size == orig_table.size
        assert new_table.values == orig_table.values


def test_document_to_json_styled_table(samples):
    doc = Document(samples("styled_table.ods"))
    json_str = doc.to_json()
    assert json_str is not None
    data = json.loads(json_str)

    assert "Feuille1" in data
    assert "Feuille2" in data
    assert "Feuille 3 3" in data

    rows_feuille1 = data["Feuille1"]
    assert len(rows_feuille1) == 7
    assert rows_feuille1[0] == [1, 2, 3, 4]
    assert rows_feuille1[6] == [4, 5, 6, 7]
    assert data["Feuille2"] == [["val2"]]
    assert data["Feuille 3 3"] == [["val3"]]


def test_document_to_json_unstriped(samples):
    doc = Document(samples("unstriped.ods"))
    json_str = doc.to_json()
    assert json_str is not None
    data = json.loads(json_str)

    assert "Sheet1" in data
    assert "Sheet2" in data

    assert data["Sheet1"] == [
        [1],
        [None, 2],
        [None, None, 3],
        [None, None, None, 4],
    ]
    assert data["Sheet2"] == [
        [],
        [None, 2],
        [None, None, 3],
        [None, None, None, 4],
        [None, None, None, None, 5, 6],
    ]


def test_document_to_json_big_ods(samples):
    doc = Document(samples("big.ods"))
    json_str = doc.to_json()
    assert json_str is not None
    data = json.loads(json_str)

    assert "Feuille1" in data
    rows = data["Feuille1"]
    assert len(rows) == 20100
    assert rows[0] == [1]
    assert rows[1] == [2]
    assert rows[-1] == [20000]


def test_json_export_numeric_and_boolean_types():
    table = Table("NumbersAndBools")
    row = Row()
    row.set_value(0, 0)
    row.set_value(1, 100)
    row.set_value(2, -42)
    row.set_value(3, 0.0)
    row.set_value(4, 3.14159)
    row.set_value(5, -0.001)
    row.set_value(6, Decimal("100.50"))
    row.set_value(7, Decimal("42"))
    row.set_value(8, True)
    row.set_value(9, False)
    table.append_row(row)

    json_str = table.to_json()
    assert json_str is not None
    data = json.loads(json_str)
    row_data = data["NumbersAndBools"][0]

    assert row_data[0] == 0
    assert isinstance(row_data[0], int)
    assert row_data[1] == 100
    assert isinstance(row_data[1], int)
    assert row_data[2] == -42
    assert isinstance(row_data[2], int)

    assert row_data[3] == 0.0
    assert row_data[4] == 3.14159
    assert isinstance(row_data[4], float)
    assert row_data[5] == -0.001

    assert row_data[6] == 100.5
    assert row_data[7] == 42
    assert isinstance(row_data[7], int)

    assert row_data[8] is True
    assert isinstance(row_data[8], bool)
    assert row_data[9] is False
    assert isinstance(row_data[9], bool)


def test_json_export_date_and_datetime_types():
    table = Table("DatesTable")
    row = Row()
    row.set_value(0, date(2000, 1, 1))
    row.set_value(1, date(2026, 12, 31))
    row.set_value(2, datetime(2026, 8, 14, 15, 30, 45))
    row.set_value(3, datetime(2030, 5, 10, 8, 0, 0))
    table.append_row(row)

    json_str = table.to_json()
    assert json_str is not None
    data = json.loads(json_str)
    row_data = data["DatesTable"][0]

    assert row_data[0] == "2000-01-01"
    assert row_data[1] == "2026-12-31"
    assert row_data[2] == "2026-08-14T15:30:45"
    assert row_data[3] == "2030-05-10T08:00:00"


def test_json_export_duration_timedelta_types():
    table = Table("TimeTable")
    row = Row()
    row.set_value(0, timedelta(seconds=45))
    row.set_value(1, timedelta(minutes=30))
    row.set_value(2, timedelta(hours=5, minutes=12, seconds=34))
    row.set_value(3, timedelta(days=1, hours=2, minutes=3))
    table.append_row(row)

    json_str = table.to_json()
    assert json_str is not None
    data = json.loads(json_str)
    row_data = data["TimeTable"][0]

    assert row_data[0] == "PT00H00M45S"
    assert row_data[1] == "PT00H30M00S"
    assert row_data[2] == "PT05H12M34S"
    assert row_data[3] == "PT26H03M00S"


def test_json_import_all_primitive_types():
    json_data = {
        "ImportTable": [
            [
                "hello",
                123,
                45.67,
                True,
                False,
                "2026-08-14T12:00:00",
                "2:15:00",
                None,
            ]
        ]
    }
    json_str = json.dumps(json_data)
    table = Table.from_json(json_str)

    assert table.name == "ImportTable"
    row = table.rows[0]
    assert row.get_cell(0).value == "hello"
    assert row.get_cell(0).type == "string"

    assert row.get_cell(1).value == 123

    assert row.get_cell(2).value == Decimal("45.67")

    assert row.get_cell(3).value is True
    assert row.get_cell(3).type == "boolean"

    assert row.get_cell(4).value is False
    assert row.get_cell(4).type == "boolean"

    assert row.get_cell(5).value == datetime(2026, 8, 14, 12, 0, 0)
    assert row.get_cell(5).type == "date"

    assert row.get_cell(6).value == timedelta(hours=2, minutes=15)
    assert row.get_cell(6).type == "time"

    assert row.get_cell(7).value is None


def test_json_roundtrip_all_types():
    table = Table("RoundtripTable")
    row = Row()
    row.set_value(0, "Sample")
    row.set_value(1, 999)
    row.set_value(2, 12.34)
    row.set_value(3, Decimal("50.25"))
    row.set_value(4, True)
    row.set_value(5, False)
    row.set_value(6, datetime(2026, 8, 14, 10, 20, 30))
    row.set_value(7, timedelta(hours=1, minutes=45))
    table.append_row(row)

    json_str = table.to_json()
    assert json_str is not None

    table_reimported = Table.from_json(json_str)
    assert table_reimported.name == "RoundtripTable"

    row_reimported = table_reimported.rows[0]
    assert row_reimported.get_cell(0).value == "Sample"
    assert row_reimported.get_cell(0).type == "string"

    assert row_reimported.get_cell(1).value == 999
    assert row_reimported.get_cell(2).value == Decimal("12.34")
    assert row_reimported.get_cell(3).value == Decimal("50.25")

    assert row_reimported.get_cell(4).value is True
    assert row_reimported.get_cell(4).type == "boolean"
    assert row_reimported.get_cell(5).value is False
    assert row_reimported.get_cell(5).type == "boolean"

    assert row_reimported.get_cell(6).value == datetime(2026, 8, 14, 10, 20, 30)
    assert row_reimported.get_cell(6).type == "date"

    assert row_reimported.get_cell(7).value == timedelta(hours=1, minutes=45)
    assert row_reimported.get_cell(7).type == "time"


def test_document_to_json_hidden_table(samples):
    doc = Document(samples("minimal_hidden.ods"))

    # Default: hidden tables omitted
    json_default = doc.to_json()
    assert json_default is not None
    data_default = json.loads(json_default)
    assert "Tab 1" in data_default
    assert "Tab 2" not in data_default

    # include_hidden=True: hidden tables included
    json_hidden = doc.to_json(include_hidden=True)
    assert json_hidden is not None
    data_hidden = json.loads(json_hidden)
    assert "Tab 1" in data_hidden
    assert "Tab 2" in data_hidden


def test_table_to_json_nan_inf_replaced_with_none():
    table = Table("FloatSpecial")
    table.set_value((0, 0), float("nan"))
    table.set_value((1, 0), float("inf"))
    table.set_value((2, 0), float("-inf"))
    table.set_value((3, 0), 10.5)

    json_str = table.to_json()
    assert json_str is not None
    data = json.loads(json_str)

    # Standard JSON replaces NaN, INF, -INF with null (None in Python)
    assert data["FloatSpecial"] == [
        [None, None, None, 10.5],
    ]


def test_document_to_json_nan_inf_replaced_with_none():
    doc = Document("spreadsheet")
    table = doc.body.tables[0]
    table.set_value((0, 0), "Header")
    table.set_value((1, 0), float("nan"))
    table.set_value((2, 0), float("inf"))
    table.set_value((3, 0), Decimal("nan"))

    json_str = doc.to_json()
    assert json_str is not None
    data = json.loads(json_str)

    assert data["Feuille1"] == [
        ["Header"],
    ]


def test_serialize_table_rows_all_types_and_nan_branches():
    class DummyObj:
        def __str__(self):
            return "dummy"

    row_input = [
        None,
        "text",
        42,
        True,
        False,
        float("nan"),
        float("inf"),
        float("-inf"),
        3.14159,
        Decimal("nan"),
        Decimal("inf"),
        Decimal("-inf"),
        Decimal("100"),
        Decimal("2.718"),
        datetime(2026, 1, 1, 12, 0, 0),
        date(2026, 1, 1),
        timedelta(hours=2),
        DummyObj(),
        None,
    ]

    table = Table("FullBranchCoverage")
    with patch.object(
        type(table),
        "values",
        new_callable=PropertyMock,
        return_value=[row_input, [None, None]],
    ):
        result = table._serialize_table_rows()

    assert result == [
        [
            None,
            "text",
            42,
            True,
            False,
            None,
            None,
            None,
            3.14159,
            None,
            None,
            None,
            100,
            2.718,
            "2026-01-01T12:00:00",
            "2026-01-01",
            "PT02H00M00S",
            "dummy",
        ]
    ]
