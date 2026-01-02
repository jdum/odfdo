# Copyright 2018-2026 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from odfdo.document import Document
from odfdo.scripts import meta_print
from odfdo.scripts.meta_print import main as main_script
from odfdo.scripts.meta_print import main_meta_print, parse_cli_args

SCRIPT = Path(meta_print.__file__)
SOURCE = "user_fields.odt"


def run_params(params: list):
    command = [sys.executable, SCRIPT] + params
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_meta_print_no_param():
    params = []
    out, _err, exitcode = run_params(params)
    assert exitcode == 1
    assert b"usage:" in out
    assert b"Error:" in out


# direct access to internal function


def test_meta_print_2_no_param_on_main_function(monkeypatch, capsys):
    with pytest.raises(SystemExit) as result:
        monkeypatch.setattr(sys, "argv", [])
        main_script()
        assert result.type is SystemExit
        assert result.value.code >= 1
    captured = capsys.readouterr()

    assert "usage" in captured.out


def test_meta_print_2_no_param(capsys):
    params = parse_cli_args([])

    with pytest.raises(SystemExit) as result:
        main_meta_print(params)
        assert result.type is SystemExit
        assert result.value.code == 1
    captured = capsys.readouterr()

    assert "usage" in captured.out


def test_meta_print_2_no_file(capsys):
    params = parse_cli_args(["-i", "none_file1", "-o", "none_file2"])

    with pytest.raises(SystemExit) as result:
        main_meta_print(params)
        assert result.type is SystemExit
        assert result.value.code == 1
    captured = capsys.readouterr()

    assert "usage" in captured.out
    assert "FileNotFoundError" in captured.out


def test_meta_2_print_language(capsys, samples):
    source = str(samples(SOURCE))
    params = parse_cli_args(["-l", "-i", source])

    main_meta_print(params)
    captured = capsys.readouterr()

    assert "Default style language: fr-FR" in captured.out
    assert "Statistic:" in captured.out


def test_meta_print_2_odf_version(capsys, samples):
    source = str(samples(SOURCE))
    params = parse_cli_args(["-v", "-i", source])

    main_meta_print(params)
    captured = capsys.readouterr()

    assert "OpenDocument format version: 1.3" in captured.out
    assert "Statistic:" in captured.out


def test_meta_print_2_text(capsys, samples):
    source = str(samples(SOURCE))
    params = parse_cli_args(["-i", source])

    main_meta_print(params)
    captured = capsys.readouterr()

    assert "Creation date:" in captured.out
    assert "Statistic:" in captured.out
    assert "Object count:" in captured.out


def test_meta_print_2_json(capsys, samples):
    source = str(samples(SOURCE))
    params = parse_cli_args(["-j", "-i", source])

    main_meta_print(params)
    captured = capsys.readouterr()

    assert "meta:creation-date" in captured.out
    assert "dc:date" in captured.out
    assert "meta:table-count" in captured.out
    assert "meta:generator" in captured.out
    assert "meta:initial-creator" in captured.out


def test_meta_print_2_json_save(tmp_path, samples):
    source = str(samples(SOURCE))
    dest = tmp_path / "json_data.json"
    params = parse_cli_args(["-j", "-i", source, "-o", str(dest)])

    main_meta_print(params)

    result = dest.read_text(encoding="utf8")
    assert "meta:creation-date" in result
    assert "dc:date" in result
    assert "meta:table-count" in result
    assert "meta:generator" in result
    assert "meta:initial-creator" in result


def test_meta_print_2_text_from_stdin(monkeypatch, capsys, samples):
    mock_document = Document(samples(SOURCE))

    def mock_read_document(input_path: str | None):
        assert input_path is None
        return mock_document

    monkeypatch.setattr("odfdo.scripts.meta_print.read_document", mock_read_document)

    params = parse_cli_args([])

    main_meta_print(params)
    captured = capsys.readouterr()

    assert "Creation date:" in captured.out
    assert "Statistic:" in captured.out
    assert "Object count:" in captured.out
