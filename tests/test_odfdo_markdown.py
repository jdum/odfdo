# Copyright 2018-2024 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "odfdo" / "scripts" / "to_markdown.py"
ODT_FILE = Path(__file__).parent / "samples" / "example.odt"
ODS_FILE = Path(__file__).parent / "samples" / "simple_table.ods"


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


def test_md_osq_bad():
    params = [str(ODS_FILE)]
    out, err, exitcode = run_params(params)
    assert exitcode == 1
    assert "usage:" in out
    assert "Type of document 'spreadsheet' not supported" in err


def test_md_1():
    params = [str(ODT_FILE)]
    print(str(ODT_FILE))
    out, err, exitcode = run_params(params)
    print(out)
    print(err)
    assert exitcode == 0
    assert "odfdo Test Case Document" in out
    assert "First paragraph" in out
