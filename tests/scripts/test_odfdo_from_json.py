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
# https://github.com/lpod/lpod-pythonfrom __future__ import annotations
from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

from odfdo.document import Document
from odfdo.scripts import from_json
from odfdo.scripts.from_json import main as main_script
from odfdo.scripts.from_json import main_from_json, parse_cli_args
from odfdo.table import Table

SCRIPT = Path(from_json.__file__)


def run_params(params: list):
    command = [sys.executable, SCRIPT] + params
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_from_json_no_param():
    params = []
    _out, _err, exitcode = run_params(params)
    assert exitcode == 1


def test_from_json_2_no_param_on_main_function(monkeypatch):
    with pytest.raises(Exception) as result:
        monkeypatch.setattr(sys, "argv", [])
        main_script()
        assert result.value.code >= 1


def test_from_json_2_no_param(monkeypatch):
    with pytest.raises(Exception) as result:
        params = parse_cli_args([])
        main_from_json(params)
        assert result.value.code >= 1


def test_from_json_2_version(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--version"])
        assert result.value.code == 0
    captured = capsys.readouterr()
    assert "odfdo-from-json v" in captured.out


def test_from_json_2_help(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--help"])
        assert result.value.code == 0
    captured = capsys.readouterr()
    assert "Create an ODS" in captured.out


def test_from_json_2_no_file():
    params = parse_cli_args(["-i", "none_file"])
    with pytest.raises(FileNotFoundError):
        main_from_json(params)


def test_from_json_basic(capsysbinary, tmp_path):
    data = {"Sheet1": [["Name", "Score"], ["Alice", 100], ["Bob", 95]]}
    json_path = tmp_path / "data.json"
    json_path.write_text(json.dumps(data), encoding="utf-8")

    params = parse_cli_args(["-i", str(json_path)])
    main_from_json(params)

    captured = capsysbinary.readouterr()
    content = io.BytesIO(captured.out)
    doc = Document(content)
    content.close()

    table = doc.body.get_table(name="Sheet1")
    assert table is not None
    assert table.values == [["Name", "Score"], ["Alice", 100], ["Bob", 95]]


def test_from_json_output_file(tmp_path):
    data = {"Sheet1": [["A", "B"], [1, 2]]}
    json_path = tmp_path / "data.json"
    json_path.write_text(json.dumps(data), encoding="utf-8")
    out_ods = tmp_path / "out.ods"

    params = parse_cli_args(["-i", str(json_path), "-o", str(out_ods)])
    main_from_json(params)

    assert out_ods.exists()
    doc = Document(out_ods)
    table = doc.body.get_table(name="Sheet1")
    assert table is not None
    assert table.values == [["A", "B"], [1, 2]]


def test_from_json_dict_import(capsysbinary, tmp_path):
    json_data = {
        "Employees": [["Name", "Country"], ["Alice", "USA"]],
        "Figures": [["Number", "Bool"], [1, True]],
    }
    input_file = tmp_path / "data.json"
    input_file.write_text(json.dumps(json_data), encoding="utf-8")

    params = parse_cli_args(["-i", str(input_file)])
    main_from_json(params)

    captured = capsysbinary.readouterr()
    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()

    assert len(document.body.tables) == 2
    assert document.body.tables[0].name == "Employees"
    assert document.body.tables[1].name == "Figures"
    assert document.body.tables[0].values == [["Name", "Country"], ["Alice", "USA"]]


def test_from_json_list_import(capsysbinary, tmp_path):
    json_data = [["Col1", "Col2"], [100, 200]]
    input_file = tmp_path / "list_data.json"
    input_file.write_text(json.dumps(json_data), encoding="utf-8")

    params = parse_cli_args(["-i", str(input_file)])
    main_from_json(params)

    captured = capsysbinary.readouterr()
    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()

    assert len(document.body.tables) == 1
    table = document.body.tables[0]
    assert table.name == "Table"
    assert table.values == [["Col1", "Col2"], [100, 200]]


def test_from_json_sample_text1(capsysbinary, samples, tmp_path):
    source_csv = samples("text1.csv")
    table_csv = Table.from_csv(source_csv.read_text(), name="table")
    json_path = tmp_path / "text1.json"
    table_csv.to_json(path_or_file=json_path)

    params = parse_cli_args(["-i", str(json_path)])
    main_from_json(params)
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    table = document.body.tables[0]
    assert table.name == "table"
    assert table.get_row_values(0) == ["foo1", "foo2"]
    assert table.get_row_values(1) == [1, 2]


def test_from_json_sample_text2(capsysbinary, samples, tmp_path):
    source_csv = samples("text2.csv")
    table_csv = Table.from_csv(source_csv.read_text(), name="sheet")
    json_path = tmp_path / "text2.json"
    table_csv.to_json(path_or_file=json_path)

    params = parse_cli_args(["-i", str(json_path)])
    main_from_json(params)
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    table = document.body.tables[0]
    assert table.get_row_values(1)[:2] == [1, 2]
