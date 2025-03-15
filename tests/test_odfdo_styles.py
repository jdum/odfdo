# Copyright 2018-2025 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "src" / "odfdo" / "scripts" / "styles.py"
SAMPLES = Path(__file__).parent / "samples"


def run_params_bytes(params):
    command = [sys.executable, SCRIPT] + params
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_no_param():
    params = []
    out, err, exitcode = run_params_bytes(params)
    print(out, err, exitcode)
    assert exitcode == 2
    assert b"odfdo-styles: error: the following arguments" in err
    assert b"usage" in err


def test_help():
    params = ["--help"]
    out, err, exitcode = run_params_bytes(params)
    print(out, err, exitcode)
    assert exitcode == 0
    assert b"to manipulate styles" in out


def test_no_file():
    params = ["none_file"]
    out, _err, exitcode = run_params_bytes(params)
    assert exitcode == 1
    assert b"FileNotFoundError" in out


def test_base():
    source = SAMPLES / "base_text.odt"
    params = [f"{source}"]
    out, _err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    print(out)
    assert b"common used:y family:graphic" in out
    assert b"auto   used:y family:section" in out


def test_base_auto():
    source = SAMPLES / "base_text.odt"
    params = ["-a", f"{source}"]
    out, _err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert b"auto   used:y family:drawing-page parent: name:Mdp1" in out
    assert b"common used" not in out


def test_base_common():
    source = SAMPLES / "base_text.odt"
    params = ["-c", f"{source}"]
    out, _err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert b"auto   used" not in out
    assert b"common used" in out


def test_base_properties():
    source = SAMPLES / "base_text.odt"
    params = ["-p", f"{source}"]
    out, _err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert b"- style:layout-grid-lines: 20" in out
    assert b"- style:text-underline-color: font-color" in out


def test_base_auto_properties():
    source = SAMPLES / "base_text.odt"
    params = ["-ap", f"{source}"]
    out, _err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert b"- style:layout-grid-lines: 20" in out
    assert b"- style:text-underline-color: font-color" not in out


def test_base_common_properties():
    source = SAMPLES / "base_text.odt"
    params = ["-cp", f"{source}"]
    out, _err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert b"- style:text-underline-color: font-color" in out
    assert b"- style:layout-grid-lines: 20" not in out


def test_delete_fail():
    source = SAMPLES / "base_text.odt"
    params = ["-d", f"{source}"]
    _out, err, exitcode = run_params_bytes(params)
    assert exitcode == 1
    assert b"Error: Will not delete in-place" in err


def test_delete_to_stdout():
    source = SAMPLES / "base_text.odt"
    params = ["-d", "-o", "-", f"{source}"]
    out, err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert b"23 styles removed (0 error, 0 warning)" in err
    assert len(out) > 8000


def test_delete_to_file(tmp_path):
    source = SAMPLES / "base_text.odt"
    dest = tmp_path / "test_deleted.odt"
    params = ["-d", "-o", f"{dest}", f"{source}"]
    _out, err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert b"23 styles removed (0 error, 0 warning)" in err
    assert dest.is_file()


def test_show_to_file(tmp_path):
    source = SAMPLES / "base_text.odt"
    dest = tmp_path / "styles.txt"
    params = ["-o", f"{dest}", f"{source}"]
    out, _err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert not out.strip()
    assert dest.is_file()


def test_show_to_file2(tmp_path):
    source = SAMPLES / "base_text.odt"
    dest = tmp_path / "styles2.txt"
    params = ["-o", f"{dest}", f"{source}"]
    _out, _err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    content = dest.read_text()
    assert "common used:y family:graphic" in content
    assert "auto   used:y family:text" in content


def test_show_odp():
    source = SAMPLES / "background.odp"
    params = [f"{source}"]
    out, _err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert b"common used:y family:presentation" in out
    assert b"auto   used:n family:presentation" in out


def test_show_odp2():
    source = SAMPLES / "example.odp"
    params = [f"{source}"]
    out, _err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert b"common used:y family:presentation" in out
    assert b"auto   used:n family:presentation" in out


def test_merge(tmp_path):
    source = SAMPLES / "base_text.odt"
    source_styles = SAMPLES / "lpod_styles.odt"
    dest = tmp_path / "styles_text.odt"
    params = ["-m", f"{source_styles}", "-o", f"{dest}", f"{source}"]
    out, err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert b"Done (0 error, 0 warning)" in err
    assert not out.strip()
    assert dest.is_file()


def test_merge_prez(tmp_path):
    source = SAMPLES / "example.odp"
    source_styles = SAMPLES / "background.odp"
    dest = tmp_path / "styles_text.odp"
    params = ["-m", f"{source_styles}", "-o", f"{dest}", f"{source}"]
    _out, err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert b"Done (0 error, 0 warning)" in err
