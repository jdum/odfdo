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

import json
import platform
import subprocess
import sys
from pathlib import Path

import pytest

from odfdo.scripts import to_json
from odfdo.scripts.to_json import main as main_script
from odfdo.scripts.to_json import main_to_json, parse_cli_args

SCRIPT = Path(to_json.__file__)


def run_params(params: list):
    command = [sys.executable, SCRIPT] + params
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_to_json_no_param():
    params = []
    _out, err, exitcode = run_params(params)
    assert exitcode == 1
    if platform.system() != "Windows":
        assert b"timeout" in err


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Fails on Windows due to stdin/output capture conflict.",
)
def test_to_json_2_no_param_on_main_function(monkeypatch):
    with pytest.raises(ValueError) as result:
        monkeypatch.setattr(sys, "argv", [])
        main_script()
        assert result.value.code >= 1


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Fails on Windows due to stdin/output capture conflict.",
)
def test_to_json_2_no_param():
    with pytest.raises(ValueError) as result:
        params = parse_cli_args([])
        main_to_json(params)
        assert result.value.code >= 1


def test_to_json_2_version(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--version"])
        assert result.value.code == 0
    captured = capsys.readouterr()

    assert "odfdo-to-json v3" in captured.out


def test_to_json_2_help(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--help"])
        assert result.value.code == 0
    captured = capsys.readouterr()

    assert "Export one or all" in captured.out


def test_to_json_2_no_file():
    params = parse_cli_args(["-i", "none_file"])
    with pytest.raises(FileNotFoundError) as result:
        main_to_json(params)
        assert result.value.code >= 1


def test_to_json_basic(capsys, samples):
    source = samples("legacy_content.ods")
    params = parse_cli_args(["-i", str(source)])
    expected = {
        "Employees": [["Name", "Country"], ["Alice", "USA"], ["Gaël", "France"]],
        "Figures": [["Number", "Bool"], [1, True], [-2, False], [3.14, ""]],
    }

    main_to_json(params)
    captured = capsys.readouterr()

    data = json.loads(captured.out)
    assert data == expected


def test_to_json_basic_pretty(capsys, samples):
    source = samples("legacy_content.ods")
    params = parse_cli_args(["-i", str(source), "--pretty"])
    expected = {
        "Employees": [["Name", "Country"], ["Alice", "USA"], ["Gaël", "France"]],
        "Figures": [["Number", "Bool"], [1, True], [-2, False], [3.14, ""]],
    }

    main_to_json(params)
    captured = capsys.readouterr()

    data = json.loads(captured.out)
    assert data == expected


def test_to_json_single_table(capsys, samples):
    source = samples("legacy_content.ods")
    params = parse_cli_args(["-i", str(source), "-t", "Employees", "--pretty"])
    expected = {
        "Employees": [["Name", "Country"], ["Alice", "USA"], ["Gaël", "France"]],
    }

    main_to_json(params)
    captured = capsys.readouterr()

    data = json.loads(captured.out)
    assert data == expected


def test_to_json_output_file(samples, tmp_path):
    source = samples("legacy_content.ods")
    out_file = tmp_path / "out.json"
    params = parse_cli_args(["-i", str(source), "-o", str(out_file), "--pretty"])
    expected = {
        "Employees": [["Name", "Country"], ["Alice", "USA"], ["Gaël", "France"]],
        "Figures": [["Number", "Bool"], [1, True], [-2, False], [3.14, ""]],
    }

    main_to_json(params)

    assert out_file.exists()
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data == expected


def test_to_json_table_not_found(samples):
    source = samples("legacy_content.ods")
    params = parse_cli_args(["-i", str(source), "-t", "NonExistentTable"])
    with pytest.raises(ValueError, match="Table 'NonExistentTable' not found"):
        main_to_json(params)


def test_to_json_single_table_output_file(samples, tmp_path):
    source = samples("legacy_content.ods")
    out_file = tmp_path / "table.json"
    params = parse_cli_args(["-i", str(source), "-t", "Employees", "-o", str(out_file)])
    expected = {
        "Employees": [["Name", "Country"], ["Alice", "USA"], ["Gaël", "France"]],
    }

    main_to_json(params)

    assert out_file.exists()
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data == expected


def test_to_json_simple_table_1(capsys, samples):
    source = samples("simple_table.ods")
    params = parse_cli_args(["-i", str(source), "--pretty"])

    main_to_json(params)
    captured = capsys.readouterr()

    data = json.loads(captured.out)
    assert "Example1" in data
    assert "Example2" in data
    assert "Example3" in data
    assert data["Example1"][0] == [1, 1, 1, 2, 3, 3, 3]


def test_to_json_simple_table_example2(capsys, samples):
    source = samples("simple_table.ods")
    params = parse_cli_args(["-i", str(source), "-t", "Example2", "--pretty"])

    main_to_json(params)
    captured = capsys.readouterr()

    data = json.loads(captured.out)
    assert "Example2" in data
    assert "Example1" not in data


def test_to_json_simple_table_example3(capsys, samples):
    source = samples("simple_table.ods")
    params = parse_cli_args(["-i", str(source), "-t", "Example3", "--pretty"])

    main_to_json(params)
    captured = capsys.readouterr()

    data = json.loads(captured.out)
    assert "Example3" in data
    assert data["Example3"] == [["A float", 3.14], ["A date", "1975-05-07"]]


def test_to_json_simple_table_raise(samples):
    source = samples("simple_table.ods")
    params = parse_cli_args(["-i", str(source), "-t", "oops"])

    with pytest.raises(ValueError):
        main_to_json(params)


def test_to_json_styled_table(capsys, samples):
    source = samples("styled_table.ods")
    params = parse_cli_args(["-i", str(source), "--pretty"])

    main_to_json(params)
    captured = capsys.readouterr()

    data = json.loads(captured.out)
    assert "Feuille1" in data
    assert len(data["Feuille1"]) == 7
    assert data["Feuille1"][0] == [1, 2, 3, 4]


def test_to_json_unstriped(capsys, samples):
    source = samples("unstriped.ods")
    params = parse_cli_args(["-i", str(source), "--pretty"])

    main_to_json(params)
    captured = capsys.readouterr()

    data = json.loads(captured.out)
    assert "Sheet1" in data
    assert "Sheet2" in data
    assert len(data["Sheet1"]) == 4
    assert len(data["Sheet2"]) == 5


def test_to_json_big_ods(capsys, samples):
    source = samples("big.ods")
    params = parse_cli_args(["-i", str(source)])

    main_to_json(params)
    captured = capsys.readouterr()

    data = json.loads(captured.out)
    assert "Feuille1" in data
    assert len(data["Feuille1"]) == 20100
    assert data["Feuille1"][0] == [1]
    assert data["Feuille1"][-1] == [20000]


def test_to_json_hidden_table_default(capsys, samples):
    source = samples("minimal_hidden.ods")
    params = parse_cli_args(["-i", str(source)])

    main_to_json(params)
    captured = capsys.readouterr()

    data = json.loads(captured.out)
    assert "Tab 1" in data
    assert "Tab 2" not in data


def test_to_json_hidden_table_flag_d(capsys, samples):
    source = samples("minimal_hidden.ods")
    params = parse_cli_args(["-i", str(source), "-d"])

    main_to_json(params)
    captured = capsys.readouterr()

    data = json.loads(captured.out)
    assert "Tab 1" in data
    assert "Tab 2" in data


def test_to_json_hidden_table_flag_hidden(capsys, samples):
    source = samples("minimal_hidden.ods")
    params = parse_cli_args(["-i", str(source), "--hidden"])

    main_to_json(params)
    captured = capsys.readouterr()

    data = json.loads(captured.out)
    assert "Tab 1" in data
    assert "Tab 2" in data


def test_to_json_hidden_single_table_without_flag(samples):
    source = samples("minimal_hidden.ods")
    params = parse_cli_args(["-i", str(source), "-t", "Tab 2"])

    with pytest.raises(ValueError):
        main_to_json(params)


def test_to_json_hidden_single_table_with_flag(capsys, samples):
    source = samples("minimal_hidden.ods")
    params = parse_cli_args(["-i", str(source), "-t", "Tab 2", "-d"])

    main_to_json(params)
    captured = capsys.readouterr()

    data = json.loads(captured.out)
    assert "Tab 2" in data
