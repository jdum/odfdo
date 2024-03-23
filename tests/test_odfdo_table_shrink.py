# Copyright 2018-2024 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com

import io
import shlex
import subprocess
from pathlib import Path

from odfdo import Document

SCRIPT = Path(__file__).parent.parent / "odfdo" / "scripts" / "table_shrink.py"
SAMPLES = Path(__file__).parent / "samples"
SOURCE1 = SAMPLES / "test_col_cell_blue.ods"
SOURCE2 = SAMPLES / "test_col_cell.ods"
SOURCE3 = SAMPLES / "simple_table_named_range.ods"
SOURCE4 = SAMPLES / "simple_table.ods"
SOURCE5 = SAMPLES / "styled_table.ods"


def run_params(params):
    command = shlex.split(f"python {SCRIPT} {params}")
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_no_param():
    params = ""
    out, err, exitcode = run_params(params)
    assert exitcode == 1
    assert b"usage: odfdo-table-shrink" in out


def test_no_file():
    params = "-i none_file1 -o none_file2"
    out, err, exitcode = run_params(params)
    assert exitcode == 1
    assert b"usage:" in out
    assert b"FileNotFoundError" in out


def test_trim_1():
    params = f"-i {SOURCE1}"
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    table = document.body.get_table(0)
    assert table.size == (3, 3)


def test_trim_2():
    params = f"-i {SOURCE2}"
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    table = document.body.get_table(0)
    assert table.size == (7, 16)


def test_trim_3():
    params = f"-i {SOURCE3}"
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    table = document.body.get_table(0)
    assert table.size == (7, 4)
    table = document.body.get_table(1)
    assert table.size == (1, 1)
    table = document.body.get_table(2)
    assert table.size == (2, 2)


def test_trim_4():
    params = f"-i {SOURCE4}"
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    table = document.body.get_table(0)
    assert table.size == (7, 4)
    table = document.body.get_table(1)
    assert table.size == (1, 1)
    table = document.body.get_table(2)
    assert table.size == (2, 2)


def test_trim_5():
    params = f"-i {SOURCE5}"
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    table = document.body.get_table(0)
    assert table.size == (5, 10)
    table = document.body.get_table(1)
    assert table.size == (1, 1)
    table = document.body.get_table(2)
    assert table.size == (1, 1)
