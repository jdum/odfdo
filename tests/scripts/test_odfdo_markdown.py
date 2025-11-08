# Copyright 2018-2025 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from odfdo.scripts import to_markdown
from odfdo.scripts.to_markdown import main as main_script
from odfdo.scripts.to_markdown import main_to_md, parse_cli_args

SCRIPT = Path(to_markdown.__file__)


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


def test_to_md_no_param():
    params = []
    out, _err, exitcode = run_params(params)
    assert exitcode == 1
    assert "usage:" in out


# direct access to internal function


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Fails on Windows due to stdin/output capture conflict.",
)
def test_to_md_2_no_param_on_main_function(monkeypatch):
    with pytest.raises(ValueError) as result:
        monkeypatch.setattr(sys, "argv", [])
        main_script()
        assert result.value.code >= 1


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Fails on Windows due to stdin/output capture conflict.",
)
def test_to_md_2_no_param():
    with pytest.raises(ValueError) as result:
        params = parse_cli_args([])
        main_to_md(params)
        assert result.value.code >= 1


def test_to_md_2_version(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--version"])
        assert result.value.code == 0
    captured = capsys.readouterr()

    assert "odfdo-markdown v3" in captured.out


def test_to_md_2_help(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--help"])
        assert result.value.code == 0
    captured = capsys.readouterr()

    assert "document in markdown format" in captured.out


def test_to_md_2_no_file():
    params = parse_cli_args(["none_file"])
    with pytest.raises(FileNotFoundError) as result:
        main_to_md(params)
        assert result.value.code >= 1


def test_to_md_2_md_osq_bad(samples):
    source = samples("simple_table.ods")
    params = parse_cli_args([str(source)])

    with pytest.raises(NotImplementedError) as result:
        main_to_md(params)
        assert result.value.code >= 1


def test_to_md_2_example(capsys, samples):
    source = samples("example.odt")
    params = parse_cli_args([str(source)])

    main_to_md(params)
    captured = capsys.readouterr()

    assert "odfdo Test Case Document" in captured.out
    assert "First paragraph" in captured.out
