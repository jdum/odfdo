# Copyright 2018-2025 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com
from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path

import pytest

from odfdo.scripts import to_csv
from odfdo.scripts.to_csv import main as main_script
from odfdo.scripts.to_csv import main_to_csv, parse_cli_args

SCRIPT = Path(to_csv.__file__)


def run_params(params: list):
    command = [sys.executable, SCRIPT] + params
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_to_csv_no_param():
    params = []
    _out, err, exitcode = run_params(params)
    assert exitcode == 1
    if platform.system() != "Windows":
        assert b"timeout" in err


# direct access to internal function


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Fails on Windows due to stdin/output capture conflict.",
)
def test_to_csv_2_no_param_on_main_function(monkeypatch):
    with pytest.raises(ValueError) as result:
        monkeypatch.setattr(sys, "argv", [])
        main_script()
        assert result.value.code >= 1


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Fails on Windows due to stdin/output capture conflict.",
)
def test_to_csv_2_no_param():
    with pytest.raises(ValueError) as result:
        params = parse_cli_args([])
        main_to_csv(params)
        assert result.value.code >= 1


def test_to_csv_2_version(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--version"])
        assert result.value.code == 0
    captured = capsys.readouterr()

    assert "odfdo-to-csv v3" in captured.out


def test_to_csv_2_help(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--help"])
        assert result.value.code == 0
    captured = capsys.readouterr()

    assert "Export a table from" in captured.out


def test_to_csv_2_no_file():
    params = parse_cli_args(["-i", "none_file"])
    with pytest.raises(FileNotFoundError) as result:
        main_to_csv(params)
        assert result.value.code >= 1


def test_to_csv_2_1(capsys, samples):
    source = samples("simple_table.ods")
    params = parse_cli_args(["-i", str(source)])

    main_to_csv(params)
    captured = capsys.readouterr()

    assert captured.out == (
        "1,1,1,2,3,3,3\r\n1,1,1,2,3,3,3\r\n1,1,1,2,3,3,3\r\n1,2,3,4,5,6,7\r\n"
    )


def test_to_csv_2_2(capsys, samples):
    source = samples("simple_table.ods")
    params = parse_cli_args(["-u", "-i", str(source)])

    main_to_csv(params)
    captured = capsys.readouterr()

    assert captured.out == (
        '"1","1","1","2","3","3","3"\n'
        '"1","1","1","2","3","3","3"\n'
        '"1","1","1","2","3","3","3"\n'
        '"1","2","3","4","5","6","7"\n'
    )


def test_to_csv_2_3(capsys, samples):
    source = samples("simple_table.ods")
    params = parse_cli_args(["-u", "-i", str(source), "-t", "Example2"])

    main_to_csv(params)
    captured = capsys.readouterr()

    assert captured.out == '""\n'


def test_to_csv_2_4(capsys, samples):
    source = samples("simple_table.ods")
    params = parse_cli_args(["-u", "-i", str(source), "-t", "Example3"])

    main_to_csv(params)
    captured = capsys.readouterr()

    assert captured.out == '"A float","3.14"\n"A date","1975-05-07 00:00:00"\n'


def test_to_csv_2_raise(samples):
    source = samples("simple_table.ods")
    params = parse_cli_args(["-u", "-i", str(source), "-t", "oops"])

    with pytest.raises(ValueError) as result:
        main_to_csv(params)
        assert result.value.code >= 1


def test_to_csv_2_raise_type(samples):
    source = samples("base_text.odt")
    params = parse_cli_args(["-u", "-i", str(source), "-t", "oops"])

    with pytest.raises(TypeError) as result:
        main_to_csv(params)
        assert result.value.code >= 1
