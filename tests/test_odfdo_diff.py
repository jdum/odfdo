# Copyright 2018-2023 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com

import shlex
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "odfdo" / "scripts" / "diff.py"
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
    assert "Show a diff" in out


def test_no_file():
    params = "none_file1 none_file2"
    out, err, exitcode = run_params(params)
    assert exitcode == 1
    assert "Show a diff" in out


def test_bad_format():
    params = f"{SAMPLES/'test_odf.odt'} {SAMPLES/'background.odp'}"
    out, err, exitcode = run_params(params)
    assert exitcode == 1
    assert "Show a diff" in out
    assert "documents of type text" in out


def test_diff():
    params = f"{SAMPLES/'test_odf.odt'} {SAMPLES/'test2_odf.odt'}"
    out, err, exitcode = run_params(params)
    assert exitcode == 0
    assert "test_odf.odt" in out
    assert "test2_odf.odt" in out
    assert "\n-xxxx\n+yyyyy\n" in out


def test_ndiff():
    params = f"-n {SAMPLES/'test_odf.odt'} {SAMPLES/'test2_odf.odt'}"
    out, err, exitcode = run_params(params)
    assert exitcode == 0
    assert "test_odf.odt" not in out
    assert "\n- xxxx\n+ yyyyy\n" in out
