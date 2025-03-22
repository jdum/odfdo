# Copyright 2018-2025 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com

import subprocess
import sys
from pathlib import Path

from odfdo.scripts import diff

SCRIPT = Path(diff.__file__)


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


def test_no_param():
    params = []
    _out, err, exitcode = run_params(params)
    assert exitcode == 2
    assert "odfdo-diff: error" in err
    assert "usage" in err


def test_no_file():
    params = ["none_file1", "none_file2"]
    out, _err, exitcode = run_params(params)
    assert exitcode == 1
    assert "Show a diff" in out


def test_bad_format(samples):
    print(samples("test_diff1.odt"))
    print(samples)
    params = [f"{samples('test_diff1.odt')}", f"{samples('background.odp')}"]
    out, _err, exitcode = run_params(params)
    assert exitcode == 1
    assert "Show a diff" in out
    assert "Error: odfdo-diff requires input documents of type text" in out


def test_diff(samples):
    params = [f"{samples('test_diff1.odt')}", f"{samples('test_diff2.odt')}"]
    out, _err, exitcode = run_params(params)
    assert exitcode == 0
    assert "test_diff1.odt" in out
    assert "test_diff2.odt" in out
    assert "\n-content A\n" in out
    assert "\n+content B\n" in out


def test_ndiff(samples):
    params = ["-n", f"{samples('test_diff1.odt')}", f"{samples('test_diff2.odt')}"]
    out, _err, exitcode = run_params(params)
    assert exitcode == 0
    assert "test_diff1.odt" not in out
    assert "\n- content A\n" in out
    assert "\n+ content B\n" in out


def test_diff_same(samples):
    params = [f"{samples('test_diff1.odt')}", f"{samples('test_diff1.odt')}"]
    out, _err, exitcode = run_params(params)
    assert exitcode == 0
    assert not out.strip()
