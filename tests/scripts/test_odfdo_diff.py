# Copyright 2018-2026 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from odfdo.scripts import diff
from odfdo.scripts.diff import main as main_script
from odfdo.scripts.diff import main_diff, parse_cli_args

SCRIPT = Path(diff.__file__)


def run_params(params: list):
    command = [sys.executable, SCRIPT] + params
    proc = subprocess.Popen(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_diff_no_param():
    params = []
    _out, err, exitcode = run_params(params)
    assert exitcode == 2
    assert "odfdo-diff: error" in err
    assert "usage" in err


# direct access to internal function


def test_diff_2_no_param_on_main_function(monkeypatch, capsys):
    with pytest.raises(SystemExit) as result:
        monkeypatch.setattr(sys, "argv", [])
        main_script()
        assert result.type is SystemExit
        assert result.value.code >= 1
    captured = capsys.readouterr()

    assert "usage" in captured.err


def test_diff_2_no_param(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args([])
        assert result.type is SystemExit
        assert result.value.code >= 1
    captured = capsys.readouterr()

    assert "usage" in captured.err


def test_diff_2_no_file(capsys):
    params = parse_cli_args(["none_file1", "none_file2"])

    with pytest.raises(SystemExit) as result:
        main_diff(params)
        assert result.type is SystemExit
        assert result.value.code == 1
    captured = capsys.readouterr()

    assert "Show a diff" in captured.out


def test_diff_2_no_file_on_main_function(monkeypatch, capsys):
    with pytest.raises(SystemExit) as result:
        monkeypatch.setattr(sys, "argv", ["odfdo-diff", "none_file1", "none_file2"])
        main_script()
        assert result.type is SystemExit
        assert result.value.code == 1
    captured = capsys.readouterr()

    assert "Show a diff" in captured.out


def test_diff_2_bad_format(capsys, samples):
    params = parse_cli_args(
        [f"{samples('test_diff1.odt')}", f"{samples('background.odp')}"]
    )

    with pytest.raises(SystemExit) as result:
        main_diff(params)
        assert result.type is SystemExit
        assert result.value.code == 1
    captured = capsys.readouterr()

    assert "Show a diff" in captured.out
    assert "Error: odfdo-diff requires input documents of type text" in captured.out


def test_diff_2_diff(capsys, samples):
    params = parse_cli_args(
        [f"{samples('test_diff1.odt')}", f"{samples('test_diff2.odt')}"]
    )

    main_diff(params)
    captured = capsys.readouterr()

    assert "test_diff1.odt" in captured.out
    assert "test_diff2.odt" in captured.out
    assert "\n-content A\n" in captured.out
    assert "\n+content B\n" in captured.out


def test_diff_2_ndiff(capsys, samples):
    params = parse_cli_args(
        ["-n", f"{samples('test_diff1.odt')}", f"{samples('test_diff2.odt')}"]
    )

    main_diff(params)
    captured = capsys.readouterr()

    assert "test_diff1.odt" not in captured.out
    assert "\n- content A\n" in captured.out
    assert "\n+ content B\n" in captured.out


def test_diff_2_diff_same(capsys, samples):
    params = parse_cli_args(
        [f"{samples('test_diff1.odt')}", f"{samples('test_diff1.odt')}"]
    )

    main_diff(params)
    captured = capsys.readouterr()

    assert not captured.out.strip()
