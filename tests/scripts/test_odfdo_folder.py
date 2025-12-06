# Copyright 2018-2025 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com
from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path

import pytest

from odfdo import Document
from odfdo.scripts import folder
from odfdo.scripts.folder import main as main_script
from odfdo.scripts.folder import main_convert_folder, parse_cli_args

SCRIPT = Path(folder.__file__)


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


def test_folder_no_param():
    params = []
    out, err, exitcode = run_params(params)
    print(out, err, exitcode)
    assert exitcode == 2
    assert "odfdo-folder: error: the following arguments are required" in err
    assert "usage" in err


# direct access to internal function


def test_folder_2_no_param_on_main_function(monkeypatch):
    with pytest.raises(SystemExit) as result:
        monkeypatch.setattr(sys, "argv", [])
        main_script()
        assert result.value.code >= 1


@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="Fails on Windows due to stdin/output capture conflict.",
)
def test_folder_2_no_param():
    with pytest.raises(SystemExit) as result:
        params = parse_cli_args([])
        main_convert_folder(params)
        assert result.value.code >= 1


def test_folder_2_version(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--version"])
        assert result.value.code == 0
    captured = capsys.readouterr()

    assert "odfdo-folder v3" in captured.out


def test_folder_2_help(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--help"])
        assert result.value.code == 0
    captured = capsys.readouterr()

    assert "Convert a standard ODF file" in captured.out


def test_folder_2_no_file_on_main(monkeypatch):
    with pytest.raises(SystemExit) as result:
        monkeypatch.setattr(sys, "argv", ["xxx", "none_file"])
        main_script()
        assert result.value.code >= 1


def test_folder_2_no_file():
    params = parse_cli_args(["none_file"])
    with pytest.raises(SystemExit) as result:
        main_convert_folder(params)
        assert result.value.code >= 1


def test_folder_2_1(capsys, tmp_path, samples):
    source = samples("test_diff1.odt")
    document_src = Document(source)
    tmp_source = tmp_path / "test.odt"
    document_src.save(tmp_source)
    assert tmp_source.exists()
    params = parse_cli_args([str(tmp_source)])
    main_convert_folder(params)
    captured = capsys.readouterr()
    print(captured.out)
    print(captured.err)
    path = tmp_path / "test.odt.folder"
    assert path.is_dir()


def test_folder_2_2(tmp_path, samples):
    source = samples("test_diff1.odt")
    document_src = Document(source)
    tmp_source = tmp_path / "test.odt"
    document_src.save(tmp_source)
    params1 = parse_cli_args([str(tmp_source)])
    main_convert_folder(params1)
    tmp_source.unlink()
    assert not tmp_source.exists()
    params2 = parse_cli_args([str(tmp_path / "test.odt.folder")])
    main_convert_folder(params2)
    assert tmp_source.exists()
