# Copyright 2018-2025 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from odfdo.scripts import show
from odfdo.scripts.show import main as main_script
from odfdo.scripts.show import main_show, parse_cli_args

SCRIPT = Path(show.__file__)


def run_params(params: list):
    command = [sys.executable, SCRIPT, *params]
    proc = subprocess.Popen(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_show_no_param():
    params = []
    _out, err, exitcode = run_params(params)
    assert exitcode == 2
    assert "odfdo-show: error: the following arguments" in err
    assert "usage" in err


# direct access to internal function


def test_show_2_no_param_on_main_function(monkeypatch):
    with pytest.raises(SystemExit) as result:
        monkeypatch.setattr(sys, "argv", [])
        main_script()
        assert result.value.code >= 1


def test_show_2_no_param():
    with pytest.raises(SystemExit) as result:
        params = parse_cli_args([])
        main_show(params)
        assert result.value.code >= 1


def test_show_2_version(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--version"])
        assert result.value.code == 0
    captured = capsys.readouterr()

    assert "odfdo-show v3" in captured.out


def test_show_2_help(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--help"])
        assert result.value.code == 0
    captured = capsys.readouterr()

    assert "Dump text from an OpenDocument" in captured.out


def test_show_2_no_file():
    params = parse_cli_args(["none_file"])

    with pytest.raises(SystemExit) as result:
        main_show(params)
        assert result.value.code >= 1


def test_show_2_base_on_main_function(capsys, monkeypatch, samples):
    source = str(samples("base_text.odt"))
    monkeypatch.setattr(sys, "argv", ["odfdo-replace", source])

    main_script()
    captured = capsys.readouterr()

    assert "This is the second paragraph." in captured.out


def test_show_2_base(capsys, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args([source])

    main_show(params)
    captured = capsys.readouterr()

    assert "This is the second paragraph." in captured.out


def test_show_2_no_text(capsys, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args(["-n", source])

    main_show(params)
    captured = capsys.readouterr()

    assert not captured.out.strip()


def test_show_2_meta(capsys, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args(["-nm", source])

    main_show(params)
    captured = capsys.readouterr()

    assert "This is the second paragraph." not in captured.out
    assert "Keyword: These are the keywords" in captured.out
    assert "Generator: LibreOffice" in captured.out


def test_show_2_style(capsys, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args(["-s", source])

    main_show(params)
    captured = capsys.readouterr()

    assert "This is the second paragraph." in captured.out
    assert "used:y family:paragraph" in captured.out


def test_show_2_style_no_text(capsys, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args(["-ns", source])

    main_show(params)
    captured = capsys.readouterr()

    assert "This is the second paragraph." not in captured.out
    assert "used:y family:paragraph" in captured.out


def test_show_2_style_rst(capsys, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args(["-r", source])

    main_show(params)
    captured = capsys.readouterr()

    assert "Level 2 Title\n=============" in captured.out


def test_show_2_style_ods(capsys, samples):
    source = str(samples("styled_table.ods"))
    params = parse_cli_args([source])

    main_show(params)
    captured = capsys.readouterr()

    assert "1,2,3,4" in captured.out


def test_show_2_not_style_ods(capsys, samples):
    source = str(samples("styled_table.ods"))
    params = parse_cli_args(["-n", source])

    main_show(params)
    captured = capsys.readouterr()

    assert "1,2,3,4" not in captured.out


def test_show_2_unsupported(capsys, samples):
    source = str(samples("base_shapes.odg"))
    params = parse_cli_args([source])

    with pytest.raises(SystemExit) as result:
        main_show(params)
        assert result.value.code >= 1
    captured = capsys.readouterr()

    assert "format 'graphics' is not supported" in captured.err


def test_show_2_folder_unsupported(tmp_path, capsys, samples):
    source = str(samples("base_shapes.odg"))
    dest = tmp_path / "test_show"
    params = parse_cli_args(["-o", str(dest), source])

    with pytest.raises(SystemExit) as result:
        main_show(params)
        assert result.value.code >= 1
    captured = capsys.readouterr()

    assert "format 'graphics' is not supported" in captured.err


def test_show_2_folder_text(tmp_path, samples):
    source = str(samples("base_text.odt"))
    dest = tmp_path / "test_show"
    params = parse_cli_args(["-o", str(dest), source])

    main_show(params)

    assert dest.is_dir()
    assert (dest / "meta.txt").is_file()
    assert (dest / "styles.txt").is_file()
    assert (dest / "content.rst").is_file()
    assert not (dest / "Pictures").exists()


def test_show_2_folder_image(tmp_path, samples):
    source = str(samples("background.odp"))
    dest = tmp_path / "test_show"
    params = parse_cli_args(["-o", str(dest), source])

    main_show(params)

    assert dest.is_dir()
    assert (dest / "meta.txt").is_file()
    assert (dest / "styles.txt").is_file()
    assert (dest / "content.rst").is_file()
    assert (dest / "Pictures").is_dir()
    assert (
        dest / "Pictures" / "100000000000032000000258B4CA95580695A322.jpg"
    ).is_file()


def test_show_2_folder_ods(tmp_path, samples):
    source = str(samples("styled_table.ods"))
    dest = tmp_path / "test_show_ods"
    params = parse_cli_args(["-o", str(dest), source])

    main_show(params)

    assert dest.is_dir()
    assert (dest / "meta.txt").is_file()
    assert (dest / "styles.txt").is_file()
    assert (dest / "Feuille1.csv").is_file()
    assert (dest / "Feuille2.csv").is_file()
