# Copyright 2018-2025 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com

import platform
import subprocess
import sys
from pathlib import Path

from odfdo.scripts import to_csv

SCRIPT = Path(to_csv.__file__)


def run_params(params: list):
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
    _out, err, exitcode = run_params(params)
    assert exitcode == 1
    if platform.system() != "Windows":
        assert b"timeout" in err


def test_version():
    params = ["--version"]
    out, _err, exitcode = run_params(params)
    assert exitcode == 0
    assert b"odfdo-to-csv v3" in out


def test_no_file():
    params = ["-i", "none_file"]
    _out, err, exitcode = run_params(params)
    assert exitcode == 1
    assert b"FileNotFoundError" in err


def test_to_csv_1(samples):
    source = samples("simple_table.ods")
    params = ["-i", source]
    out, _err, exitcode = run_params(params)
    assert exitcode == 0
    assert out == (
        b"1,1,1,2,3,3,3\r\n1,1,1,2,3,3,3\r\n1,1,1,2,3,3,3\r\n1,2,3,4,5,6,7\r\n"
    )


def test_to_csv_2(samples):
    source = samples("simple_table.ods")
    params = ["-u", "-i", source]
    out, _err, exitcode = run_params(params)
    assert exitcode == 0
    print(repr(out))
    assert out == (
        b'"1","1","1","2","3","3","3"\n'
        b'"1","1","1","2","3","3","3"\n'
        b'"1","1","1","2","3","3","3"\n'
        b'"1","2","3","4","5","6","7"\n'
    )


def test_to_csv_3(samples):
    source = samples("simple_table.ods")
    params = ["-u", "-i", source, "-t", "Example2"]
    out, _err, exitcode = run_params(params)
    assert exitcode == 0
    print(repr(out))
    assert out == b'""\n'


def test_to_csv_4(samples):
    source = samples("simple_table.ods")
    params = ["-u", "-i", source, "-t", "Example3"]
    out, _err, exitcode = run_params(params)
    assert exitcode == 0
    print(repr(out))
    assert out == b'"A float","3.14"\n"A date","1975-05-07 00:00:00"\n'


def test_to_csv_raise(samples):
    source = samples("simple_table.ods")
    params = ["-u", "-i", source, "-t", "oops"]
    _out, err, exitcode = run_params(params)
    assert exitcode == 1
    assert b"ValueError" in err
