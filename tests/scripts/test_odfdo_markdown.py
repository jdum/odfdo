# Copyright 2018-2025 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com

import subprocess
import sys
from pathlib import Path

from odfdo.scripts import to_markdown

SCRIPT = Path(to_markdown.__file__)


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
    out, _err, exitcode = run_params(params)
    assert exitcode == 1
    assert "usage:" in out


def test_version():
    params = ["--version"]
    out, _err, exitcode = run_params(params)
    assert exitcode == 0
    assert "odfdo-markdown v3" in out


def test_no_file():
    params = ["none_file"]
    out, _err, exitcode = run_params(params)
    assert exitcode == 1
    assert "Export text document in markdown format to stdout" in out


def test_md_osq_bad(samples):
    source = samples("simple_table.ods")
    params = [source]
    out, err, exitcode = run_params(params)
    assert exitcode == 1
    assert "usage:" in out
    assert "Type of document 'spreadsheet' not supported" in err


def test_md_1(samples):
    source = samples("example.odt")
    params = [source]
    print(source)
    out, err, exitcode = run_params(params)
    print(out)
    print(err)
    assert exitcode == 0
    assert "odfdo Test Case Document" in out
    assert "First paragraph" in out
