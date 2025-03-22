# Copyright 2018-2025 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com

import subprocess
import sys
from pathlib import Path

from odfdo.scripts import styles

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


def test_base(samples):
    source = str(samples("base_text.odt"))
    params = [source]
    out, _err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    print(out)
    assert b"common used:y family:graphic" in out
    assert b"auto   used:y family:section" in out


def test_base_auto(samples):
    source = str(samples("base_text.odt"))
    params = ["-a", source]
    out, _err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert b"auto   used:y family:drawing-page parent: name:Mdp1" in out
    assert b"common used" not in out


def test_base_common(samples):
    source = str(samples("base_text.odt"))
    params = ["-c", source]
    out, _err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert b"auto   used" not in out
    assert b"common used" in out


def test_base_properties(samples):
    source = str(samples("base_text.odt"))
    params = ["-p", source]
    out, _err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert b"- style:layout-grid-lines: 20" in out
    assert b"- style:text-underline-color: font-color" in out


def test_base_auto_properties(samples):
    source = str(samples("base_text.odt"))
    params = ["-ap", source]
    out, _err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert b"- style:layout-grid-lines: 20" in out
    assert b"- style:text-underline-color: font-color" not in out


def test_base_common_properties(samples):
    source = str(samples("base_text.odt"))
    params = ["-cp", source]
    out, _err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert b"- style:text-underline-color: font-color" in out
    assert b"- style:layout-grid-lines: 20" not in out


def test_delete_fail(samples):
    source = str(samples("base_text.odt"))
    params = ["-d", source]
    _out, err, exitcode = run_params_bytes(params)
    assert exitcode == 1
    assert b"Error: Will not delete in-place" in err


def test_delete_to_stdout(samples):
    source = str(samples("base_text.odt"))
    params = ["-d", "-o", "-", source]
    out, err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert b"23 styles removed (0 error, 0 warning)" in err
    assert len(out) > 8000


def test_delete_to_file(tmp_path, samples):
    source = str(samples("base_text.odt"))
    dest = tmp_path / "test_deleted.odt"
    params = ["-d", "-o", f"{dest}", source]
    _out, err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert b"23 styles removed (0 error, 0 warning)" in err
    assert dest.is_file()


def test_show_to_file(tmp_path, samples):
    source = str(samples("base_text.odt"))
    dest = tmp_path / "styles.txt"
    params = ["-o", f"{dest}", source]
    out, _err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert not out.strip()
    assert dest.is_file()


def test_show_to_file2(tmp_path, samples):
    source = str(samples("base_text.odt"))
    dest = tmp_path / "styles2.txt"
    params = ["-o", f"{dest}", source]
    _out, _err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    content = dest.read_text()
    assert "common used:y family:graphic" in content
    assert "auto   used:y family:text" in content


def test_show_odp(samples):
    source = str(samples("background.odp"))
    params = [source]
    out, _err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert b"common used:y family:presentation" in out
    assert b"auto   used:n family:presentation" in out


def test_show_odp2(samples):
    source = str(samples("example.odp"))
    params = [source]
    out, _err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert b"common used:y family:presentation" in out
    assert b"auto   used:n family:presentation" in out


def test_merge(tmp_path, samples):
    source = str(samples("base_text.odt"))
    source_styles = str(samples("lpod_styles.odt"))
    dest = tmp_path / "styles_text.odt"
    params = ["-m", source_styles, "-o", f"{dest}", source]
    out, err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert b"Done (0 error, 0 warning)" in err
    assert not out.strip()
    assert dest.is_file()


def test_merge_prez(tmp_path, samples):
    source = str(samples("example.odp"))
    source_styles = str(samples("background.odp"))
    dest = tmp_path / "styles_text.odp"
    params = ["-m", source_styles, "-o", f"{dest}", source]
    _out, err, exitcode = run_params_bytes(params)
    assert exitcode == 0
    assert b"Done (0 error, 0 warning)" in err
