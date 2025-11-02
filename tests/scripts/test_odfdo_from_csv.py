# Copyright 2018-2025 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com
from __future__ import annotations

import io
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest

from odfdo.document import Document
from odfdo.scripts import from_csv
from odfdo.scripts.from_csv import main as main_script
from odfdo.scripts.from_csv import main_from_csv, parse_cli_args

SCRIPT = Path(from_csv.__file__)


def run_params(params: list):
    command = [sys.executable, SCRIPT] + params
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_from_csv_no_param():
    params = []
    _out, _err, exitcode = run_params(params)
    assert exitcode == 1


# direct access to internal function


def test_from_csv_2_no_param_on_main_function(monkeypatch):
    with pytest.raises(Exception) as result:
        monkeypatch.setattr(sys, "argv", [])
        main_script()
        assert result.value.code >= 1


def test_from_csv_2_no_param(monkeypatch):
    with pytest.raises(Exception) as result:
        params = parse_cli_args([])
        main_from_csv(params)
        assert result.value.code >= 1


def test_from_csv_2_version(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--version"])
        assert result.value.code == 0
    captured = capsys.readouterr()

    assert "odfdo-from-csv v3" in captured.out


def test_from_csv_2_no_file():
    params = parse_cli_args(["-i", "none_file"])

    with pytest.raises(FileNotFoundError) as result:
        main_from_csv(params)
        assert result.value.code == 1


def test_from_csv_2_text1(capsysbinary, samples):
    source = samples("text1.csv")
    params = parse_cli_args(["-i", str(source)])

    main_from_csv(params)
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    table = document.body.tables[0]
    assert table.name == "table"
    assert table.get_row_values(0) == ["foo1", "foo2"]
    assert table.get_row_values(1) == [1, 2]


def test_from_csv_2_text2(capsysbinary, samples):
    source = samples("text2.csv")
    params = parse_cli_args(["-i", str(source), "-t", "sheet"])

    main_from_csv(params)
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    table = document.body.tables[0]
    assert table.name == "sheet"
    # buggy windows envirnment not beeing utf-8:
    deci_bug = "dÃ©cimal"
    # to fix: 'dÃ©cimal'.encode('latin1').decode()
    case1 = ["foo1", "foo2", "txt content", "décimal"]
    case2 = ["foo1", "foo2", "txt content", deci_bug]
    assert table.get_row_values(0) in (case1, case2)
    assert table.get_row_values(1) == [1, 2, "some text with, comma", Decimal("-3.14")]
    assert table.get_row_values(2) == [3, 4, "text with space", Decimal("0.01")]
