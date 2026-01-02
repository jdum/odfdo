# Copyright 2018-2026 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com
from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

import pytest

from odfdo.document import Document
from odfdo.scripts import replace
from odfdo.scripts.replace import main as main_script
from odfdo.scripts.replace import main_replace, parse_cli_args

SCRIPT = Path(replace.__file__)


def run_params(params: list):
    command = [sys.executable, SCRIPT] + params
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_replace_no_param():
    params = []
    _out, err, exitcode = run_params(params)
    assert exitcode == 2
    assert b"usage:" in err
    assert b"odfdo-replace: error: the following arguments are required" in err


# direct access to internal function


def test_replace_2_no_param_on_main_function(monkeypatch):
    with pytest.raises(SystemExit) as result:
        monkeypatch.setattr(sys, "argv", [])
        main_script()
        assert result.value.code >= 1


def test_replace_2_no_param():
    with pytest.raises(SystemExit) as result:
        params = parse_cli_args([])
        main_replace(params)
        assert result.value.code >= 1


def test_replace_2_version(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--version"])
        assert result.value.code == 0
    captured = capsys.readouterr()

    assert "odfdo-replace v3" in captured.out


def test_replace_2_help(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--help"])
        assert result.value.code == 0
    captured = capsys.readouterr()

    assert "pattern replacement" in captured.out


def test_replace_2_no_file():
    params = parse_cli_args(
        ["-i", "none_file1", "-o", "none_file2", "pattern", "replacement"]
    )

    with pytest.raises(SystemExit) as result:
        main_replace(params)
        assert result.value.code >= 1


def test_replace_2_base_on_main_function(capsysbinary, monkeypatch, samples):
    source = str(samples("base_text.odt"))
    monkeypatch.setattr(sys, "argv", ["odfdo-replace", "-i", source, "odfdo", "FOO"])

    main_script()
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    assert document.body.search("FOO") is not None


def test_replace_2_base(capsysbinary, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args(["-i", source, "odfdo", "FOO"])

    main_replace(params)
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    assert document.body.search("FOO") is not None


def test_replace_2_not_here(capsysbinary, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args(["-i", source, "not here", "FOO"])

    main_replace(params)
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    assert document.body.search("FOO") is None


def test_replace_2_para(capsysbinary, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args(["-i", source, "paragraph", "FOO"])

    main_replace(params)
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    assert document.body.search("odfdo") is not None
    assert document.body.search("FOO") is not None
    assert document.body.search("paragraph") is None


def test_replace_2_formatted_1(capsysbinary, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args(["-f", "-i", source, "paragraph", "FOO"])

    main_replace(params)
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    assert document.body.search("odfdo") is not None
    assert document.body.search("FOO") is not None
    assert document.body.search("paragraph") is None


def test_replace_2_formatted_2(capsysbinary, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args(["-i", source, "paragraph", "FOO\nBAR"])

    main_replace(params)
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    assert len(document.body.get_elements("//text:line-break")) == 0
    assert document.body.search("odfdo") is not None
    assert document.body.search("FOO") is not None
    assert document.body.search("BAR") is not None
    assert document.body.search("paragraph") is None


def test_replace_2_formatted_3(capsysbinary, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args(["-f", "-i", source, "paragraph", "FOO\n\nBAR"])

    main_replace(params)
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    assert len(document.body.get_elements("//text:line-break")) == 14
    assert document.body.search("odfdo") is not None
    assert document.body.search("FOO") is not None
    assert document.body.search("BAR") is not None
    assert document.body.search("paragraph") is None
