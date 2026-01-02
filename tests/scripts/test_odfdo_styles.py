# Copyright 2018-2026 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from odfdo.scripts import styles
from odfdo.scripts.styles import main as main_script
from odfdo.scripts.styles import main_styles, parse_cli_args

SCRIPT = Path(styles.__file__)


def run_params_bytes(params):
    command = [sys.executable, SCRIPT] + params
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_styles_no_param():
    params = []
    out, err, exitcode = run_params_bytes(params)
    print(out, err, exitcode)
    assert exitcode == 2
    assert b"odfdo-styles: error: the following arguments" in err
    assert b"usage" in err


# direct access to internal function


def test_styles_2_no_param_on_main_function(monkeypatch):
    with pytest.raises(SystemExit) as result:
        monkeypatch.setattr(sys, "argv", [])
        main_script()
        assert result.value.code >= 1


def test_styles_2_no_param():
    with pytest.raises(SystemExit) as result:
        params = parse_cli_args([])
        main_styles(params)
        assert result.value.code >= 1


def test_styles_2_version(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--version"])
        assert result.value.code == 0
    captured = capsys.readouterr()

    assert "odfdo-styles v3" in captured.out


def test_styles_2_help(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--help"])
        assert result.value.code == 0
    captured = capsys.readouterr()

    assert "Manipulate styles within" in captured.out


def test_styles_2_no_file():
    params = parse_cli_args(["none_file"])

    with pytest.raises(SystemExit) as result:
        main_styles(params)
        assert result.value.code >= 1


def test_styles_2_base_on_main_function(capsys, monkeypatch, samples):
    source = str(samples("base_text.odt"))
    monkeypatch.setattr(sys, "argv", ["odfdo-styles", source])

    main_script()
    captured = capsys.readouterr()

    assert "common used:y family:graphic" in captured.out
    assert "auto   used:y family:section" in captured.out


def test_styles_2_base(capsys, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args([source])

    main_styles(params)
    captured = capsys.readouterr()

    assert "common used:y family:graphic" in captured.out
    assert "auto   used:y family:section" in captured.out


def test_styles_2_base_auto(capsys, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args(["-a", source])

    main_styles(params)
    captured = capsys.readouterr()

    assert "auto   used:y family:drawing-page parent: name:Mdp1" in captured.out
    assert "common used" not in captured.out


def test_styles_2_base_common(capsys, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args(["-c", source])

    main_styles(params)
    captured = capsys.readouterr()

    assert "auto   used" not in captured.out
    assert "common used" in captured.out


def test_styles_2_base_properties(capsys, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args(["-p", source])

    main_styles(params)
    captured = capsys.readouterr()

    assert "- style:layout-grid-lines: 20" in captured.out
    assert "- style:text-underline-color: font-color" in captured.out


def test_styles_2_base_auto_properties(capsys, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args(["-ap", source])

    main_styles(params)
    captured = capsys.readouterr()

    assert "- style:layout-grid-lines: 20" in captured.out
    assert "- style:text-underline-color: font-color" not in captured.out


def test_styles_2_base_common_properties(capsys, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args(["-cp", source])

    main_styles(params)
    captured = capsys.readouterr()

    assert "- style:text-underline-color: font-color" in captured.out
    assert "- style:layout-grid-lines: 20" not in captured.out


def test_styles_2_delete_fail(capsys, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args(["-d", source])

    with pytest.raises(SystemExit) as result:
        main_styles(params)
        assert result.value.code >= 1
    captured = capsys.readouterr()

    assert "Error: Will not delete in-place" in captured.err


def test_styles_2_delete_to_stdout(capsysbinary, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args(["-d", "-o", "-", source])

    main_styles(params)
    captured = capsysbinary.readouterr()

    assert b"27 styles removed (0 error, 0 warning)" in captured.err
    assert len(captured.out) > 8000


def test_styles_2_delete_to_file(tmp_path, capsys, samples):
    source = str(samples("base_text.odt"))
    dest = tmp_path / "test_deleted.odt"
    params = parse_cli_args(["-d", "-o", f"{dest}", source])

    main_styles(params)
    captured = capsys.readouterr()

    assert "27 styles removed (0 error, 0 warning)" in captured.err
    assert dest.is_file()


def test_styles_2_show_to_file(tmp_path, capsys, samples):
    source = str(samples("base_text.odt"))
    dest = tmp_path / "styles.txt"
    params = parse_cli_args(["-o", f"{dest}", source])

    main_styles(params)
    captured = capsys.readouterr()

    assert not captured.out.strip()
    assert dest.is_file()


def test_styles_2_show_to_file2(tmp_path, samples):
    source = str(samples("base_text.odt"))
    dest = tmp_path / "styles2.txt"
    params = parse_cli_args(["-o", f"{dest}", source])

    main_styles(params)

    content = dest.read_text()
    assert "common used:y family:graphic" in content
    assert "auto   used:y family:text" in content


def test_styles_2_show_odp(capsys, samples):
    source = str(samples("background.odp"))
    params = parse_cli_args([source])

    main_styles(params)
    captured = capsys.readouterr()

    assert "common used:y family:presentation" in captured.out
    assert "auto   used:n family:presentation" in captured.out


def test_styles_2_show_odp2(capsys, samples):
    source = str(samples("example.odp"))
    params = parse_cli_args([source])

    main_styles(params)
    captured = capsys.readouterr()

    assert "common used:y family:presentation" in captured.out
    assert "auto   used:n family:presentation" in captured.out


def test_styles_2_merge(tmp_path, capsys, samples):
    source = str(samples("base_text.odt"))
    source_styles = str(samples("lpod_styles.odt"))
    dest = tmp_path / "styles_text.odt"
    params = parse_cli_args(["-m", source_styles, "-o", f"{dest}", source])

    main_styles(params)
    captured = capsys.readouterr()

    assert "Done (0 error, 0 warning)" in captured.err
    assert not captured.out.strip()
    assert dest.is_file()


def test_styles_2_merge_prez(tmp_path, capsys, samples):
    source = str(samples("example.odp"))
    source_styles = str(samples("background.odp"))
    dest = tmp_path / "styles_text.odp"
    params = parse_cli_args(["-m", source_styles, "-o", f"{dest}", source])

    main_styles(params)
    captured = capsys.readouterr()

    assert "Done (0 error, 0 warning)" in captured.err
