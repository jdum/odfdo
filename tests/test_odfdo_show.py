# Copyright 2018-2023 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com

import shlex
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "odfdo" / "scripts" / "show.py"
SAMPLES = Path(__file__).parent / "samples"


def run_params(params):
    command = shlex.split(f"python {SCRIPT} {params}")
    proc = subprocess.Popen(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_no_param():
    params = ""
    out, err, exitcode = run_params(params)
    print(out, err, exitcode)
    assert exitcode == 1
    assert "Dump text from an OpenDocument" in out


def test_help():
    params = "--help"
    out, err, exitcode = run_params(params)
    print(out, err, exitcode)
    assert exitcode == 0
    assert "Dump text from an OpenDocument" in out


def test_no_file():
    params = "none_file"
    out, err, exitcode = run_params(params)
    assert exitcode == 1
    assert "FileNotFoundError" in out


def test_base():
    source = SAMPLES / "base_text.odt"
    params = f"{source}"
    out, err, exitcode = run_params(params)
    assert exitcode == 0
    assert "This is the second paragraph." in out


def test_no_text():
    source = SAMPLES / "base_text.odt"
    params = f"-n {source}"
    out, err, exitcode = run_params(params)
    assert exitcode == 0
    assert not out.strip()


def test_meta():
    source = SAMPLES / "base_text.odt"
    params = f"-nm {source}"
    out, err, exitcode = run_params(params)
    assert exitcode == 0
    assert "This is the second paragraph." not in out
    assert "Keyword: These are the keywords" in out
    assert "Generator: LibreOffice" in out


def test_style():
    source = SAMPLES / "base_text.odt"
    params = f"-s {source}"
    out, err, exitcode = run_params(params)
    assert exitcode == 0
    assert "This is the second paragraph." in out
    assert "used:y family:paragraph" in out


def test_style_no_text():
    source = SAMPLES / "base_text.odt"
    params = f"-ns {source}"
    out, err, exitcode = run_params(params)
    assert exitcode == 0
    assert "This is the second paragraph." not in out
    assert "used:y family:paragraph" in out


def test_style_rst():
    source = SAMPLES / "base_text.odt"
    params = f"-r {source}"
    out, err, exitcode = run_params(params)
    assert exitcode == 0
    assert "Level 2 Title\n=============" in out


def test_style_ods():
    source = SAMPLES / "styled_table.ods"
    params = f"{source}"
    out, err, exitcode = run_params(params)
    assert exitcode == 0
    assert "1,2,3,4" in out


def test_not_style_ods():
    source = SAMPLES / "styled_table.ods"
    params = f"-n {source}"
    out, err, exitcode = run_params(params)
    assert exitcode == 0
    assert "1,2,3,4" not in out


def test_unsupported():
    source = SAMPLES / "base_shapes.odg "
    params = f"{source}"
    out, err, exitcode = run_params(params)
    assert exitcode == 1
    assert "format 'graphics' is not supported" in err


def test_folder_unsupported(tmp_path):
    source = SAMPLES / "base_shapes.odg"
    dest = tmp_path / "test_show"
    params = f"-o {dest} {source}"
    out, err, exitcode = run_params(params)
    assert exitcode == 1
    assert "format 'graphics' is not supported" in err


def test_folder_text(tmp_path):
    source = SAMPLES / "base_text.odt"
    dest = tmp_path / "test_show"
    params = f"-o {dest} {source}"
    out, err, exitcode = run_params(params)
    assert exitcode == 0
    assert dest.is_dir()
    assert (dest / "meta.txt").is_file()
    assert (dest / "styles.txt").is_file()
    assert (dest / "content.rst").is_file()
    assert not (dest / "Pictures").exists()


def test_folder_image(tmp_path):
    source = SAMPLES / "background.odp"
    dest = tmp_path / "test_show"
    params = f"-o {dest} {source}"
    out, err, exitcode = run_params(params)
    assert exitcode == 0
    assert dest.is_dir()
    assert (dest / "meta.txt").is_file()
    assert (dest / "styles.txt").is_file()
    assert (dest / "content.rst").is_file()
    assert (dest / "Pictures").is_dir()
    assert (
        dest / "Pictures" / "100000000000032000000258B4CA95580695A322.jpg"
    ).is_file()


def test_folder_ods(tmp_path):
    source = SAMPLES / "styled_table.ods"
    dest = tmp_path / "test_show_ods"
    params = f"-o {dest} {source}"
    out, err, exitcode = run_params(params)
    assert exitcode == 0
    assert dest.is_dir()
    assert (dest / "meta.txt").is_file()
    assert (dest / "styles.txt").is_file()
    assert (dest / "Feuille1.csv").is_file()
    assert (dest / "Feuille2.csv").is_file()