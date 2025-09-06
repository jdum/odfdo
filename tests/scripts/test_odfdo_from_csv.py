# Copyright 2018-2025 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com

import io
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

from odfdo import Document
from odfdo.scripts import from_csv

SCRIPT = Path(from_csv.__file__)


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


def test_version():
    params = ["--version"]
    out, _err, exitcode = run_params(params)
    assert exitcode == 0
    assert b"odfdo-from-csv v3" in out


def test_no_file():
    params = ["-i", "none_file"]
    _out, err, exitcode = run_params(params)
    assert exitcode == 1
    assert b"FileNotFoundError" in err


def test_csv_1(samples):
    source = samples("text1.csv")
    params = ["-i", source]
    out, err, exitcode = run_params(params)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    table = document.body.tables[0]
    assert table.name == "table"
    assert table.get_row_values(0) == ["foo1", "foo2"]
    assert table.get_row_values(1) == [1, 2]


def test_csv_2(samples):
    source = samples("text2.csv")
    params = ["-i", source, "-t", "sheet"]
    out, _err, exitcode = run_params(params)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    table = document.body.tables[0]
    assert table.name == "sheet"
    assert table.get_row_values(0) == ["foo1", "foo2", "txt content", "décimal"]
    assert table.get_row_values(1) == [1, 2, "some text with, comma", Decimal("-3.14")]
    assert table.get_row_values(2) == [3, 4, "text with space", Decimal("0.01")]
