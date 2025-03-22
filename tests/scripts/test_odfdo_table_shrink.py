# Copyright 2018-2025 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com

import io
import subprocess
import sys
from pathlib import Path

from odfdo import Document
from odfdo.scripts import table_shrink

SCRIPT = Path(table_shrink.__file__)


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
    out, _err, exitcode = run_params(params)
    assert exitcode == 1
    assert b"usage: odfdo-table-shrink" in out


def test_no_file():
    params = ["-i", "none_file1", "-o", "none_file2"]
    out, _err, exitcode = run_params(params)
    assert exitcode == 1
    assert b"usage:" in out
    assert b"FileNotFoundError" in out


def test_trim_1(samples):
    source = str(samples("test_col_cell_blue.ods"))
    params = ["-i", source]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    table = document.body.get_table(0)
    assert table.size == (3, 3)


def test_trim_2(samples):
    source = str(samples("test_col_cell.ods"))
    params = ["-i", source]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    table = document.body.get_table(0)
    assert table.size == (7, 16)


def test_trim_3(samples):
    source = str(samples("simple_table_named_range.ods"))
    params = ["-i", source]
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


def test_trim_4(samples):
    source = str(samples("simple_table.ods"))
    params = ["-i", source]
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


def test_trim_5(samples):
    source = str(samples("styled_table.ods"))
    params = ["-i", source]
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


def test_color_1_1(samples):
    source = str(samples("test_col_cell_blue.ods"))
    params = ["-i", source]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.get_cell_background_color(0, "a1") == "#2a6099"
    assert document.get_cell_background_color(0, "b1") == "#2a6099"
    assert document.get_cell_background_color(0, "c1") == "#2a6099"
    assert document.get_cell_background_color(0, "d1") == "#ffffff"
    assert document.get_cell_background_color(0, (1000, 0)) == "#ffffff"


def test_color_1_2(samples):
    source = str(samples("test_col_cell_blue.ods"))
    params = ["-i", source]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.get_cell_background_color(0, "a2") == "#2a6099"
    assert document.get_cell_background_color(0, "b2") == "#ffff00"
    assert document.get_cell_background_color(0, "c2") == "#2a6099"
    assert document.get_cell_background_color(0, "d2") == "#ffffff"
    assert document.get_cell_background_color(0, (1000, 1)) == "#ffffff"


def test_color_1_3(samples):
    source = str(samples("test_col_cell_blue.ods"))
    params = ["-i", source]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.get_cell_background_color(0, "a3") == "#2a6099"
    assert document.get_cell_background_color(0, "b3") == "#2a6099"
    assert document.get_cell_background_color(0, "c3") == "#2a6099"
    assert document.get_cell_background_color(0, "d3") == "#ffffff"
    assert document.get_cell_background_color(0, (1000, 2)) == "#ffffff"


def test_color_2_1(samples):
    source = str(samples("test_col_cell.ods"))
    params = ["-i", source]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.get_cell_background_color(0, "a1") == "#ffffff"
    assert document.get_cell_background_color(0, "c1") == "#ffff00"
    assert document.get_cell_background_color(0, "d1") == "#ffffff"
    assert document.get_cell_background_color(0, "f1") == "#e6e905"
    assert document.get_cell_background_color(0, "g1") == "#ffffff"
    assert document.get_cell_background_color(0, (1000, 0)) == "#ffffff"


def test_color_2_2(samples):
    source = str(samples("test_col_cell.ods"))
    params = ["-i", source]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.get_cell_background_color(0, "a2") == "#ffffff"
    assert document.get_cell_background_color(0, "c2") == "#ff3838"
    assert document.get_cell_background_color(0, "f2") == "#e6e905"
    assert document.get_cell_background_color(0, "g2") == "#ffffff"
    assert document.get_cell_background_color(0, (1000, 1)) == "#ffffff"


def test_color_2_5(samples):
    source = str(samples("test_col_cell.ods"))
    params = ["-i", source]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.get_cell_background_color(0, "f5") == "#e6e905"


def test_color_2_6(samples):
    source = str(samples("test_col_cell.ods"))
    params = ["-i", source]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.get_cell_background_color(0, "a6") == "#3465a4"
    assert document.get_cell_background_color(0, "c6") == "#3465a4"
    assert document.get_cell_background_color(0, "f6") == "#e6e905"
    assert document.get_cell_background_color(0, "g6") == "#3465a4"
    assert document.get_cell_background_color(0, "h6") == "#ffffff"
    assert document.get_cell_background_color(0, (1000, 5)) == "#ffffff"


def test_color_2_7(samples):
    source = str(samples("test_col_cell.ods"))
    params = ["-i", source]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.get_cell_background_color(0, "f7") == "#e6e905"


def test_color_2_8(samples):
    source = str(samples("test_col_cell.ods"))
    params = ["-i", source]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.get_cell_background_color(0, "a8") == "#b4c7dc"
    assert document.get_cell_background_color(0, "b8") == "#b4c7dc"
    assert document.get_cell_background_color(0, "c8") == "#ffff6d"
    assert document.get_cell_background_color(0, "d8") == "#ff3838"
    assert document.get_cell_background_color(0, "e8") == "#b4c7dc"
    assert document.get_cell_background_color(0, "f8") == "#e6e905"
    assert document.get_cell_background_color(0, "g8") == "#b4c7dc"
    assert document.get_cell_background_color(0, "h8") == "#ffffff"
    assert document.get_cell_background_color(0, (1000, 5)) == "#ffffff"


def test_color_2_9(samples):
    source = str(samples("test_col_cell.ods"))
    params = ["-i", source]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.get_cell_background_color(0, "f9") == "#e6e905"


def test_color_2_10(samples):
    source = str(samples("test_col_cell.ods"))
    params = ["-i", source]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.get_cell_background_color(0, "a10") == "#ed4c05"
    assert document.get_cell_background_color(0, "b10") == "#ed4c05"
    assert document.get_cell_background_color(0, "c10") == "#ed4c05"
    assert document.get_cell_background_color(0, "d10") == "#ed4c05"
    assert document.get_cell_background_color(0, "e10") == "#ed4c05"
    assert document.get_cell_background_color(0, "f10") == "#e6e905"
    assert document.get_cell_background_color(0, "g10") == "#ed4c05"
    assert document.get_cell_background_color(0, "h10") == "#ffffff"
    assert document.get_cell_background_color(0, (1000, 9)) == "#ffffff"


def test_color_2_11(samples):
    source = str(samples("test_col_cell.ods"))
    params = ["-i", source]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.get_cell_background_color(0, "f11") == "#e6e905"


def test_color_2_12(samples):
    source = str(samples("test_col_cell.ods"))
    params = ["-i", source]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.get_cell_background_color(0, "a12") == "#168253"
    assert document.get_cell_background_color(0, "b12") == "#168253"
    assert document.get_cell_background_color(0, "c12") == "#168253"
    assert document.get_cell_background_color(0, "d12") == "#168253"
    assert document.get_cell_background_color(0, "e12") == "#168253"
    assert document.get_cell_background_color(0, "f12") == "#e6e905"
    assert document.get_cell_background_color(0, "g12") == "#168253"
    assert document.get_cell_background_color(0, "h12") == "#ffffff"
    assert document.get_cell_background_color(0, (1000, 11)) == "#ffffff"


def test_color_2_13(samples):
    source = str(samples("test_col_cell.ods"))
    params = ["-i", source]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.get_cell_background_color(0, "f13") == "#e6e905"


def test_color_2_14(samples):
    source = str(samples("test_col_cell.ods"))
    params = ["-i", source]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.get_cell_background_color(0, "f14") == "#fff5ce"


def test_color_2_15(samples):
    source = str(samples("test_col_cell.ods"))
    params = ["-i", source]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.get_cell_background_color(0, "a15") == "#55215b"
    assert document.get_cell_background_color(0, "b15") == "#55215b"
    assert document.get_cell_background_color(0, "c15") == "#55215b"
    assert document.get_cell_background_color(0, "d15") == "#55215b"
    assert document.get_cell_background_color(0, "e15") == "#55215b"
    assert document.get_cell_background_color(0, "f15") == "#55215b"
    assert document.get_cell_background_color(0, "g15") == "#55215b"
    assert document.get_cell_background_color(0, "h15") == "#ffffff"
    assert document.get_cell_background_color(0, (1000, 14)) == "#ffffff"


def test_color_2_16(samples):
    source = str(samples("test_col_cell.ods"))
    params = ["-i", source]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.get_cell_background_color(0, "f16") == "#e6e905"


def test_color_2_17(samples):
    source = str(samples("test_col_cell.ods"))
    params = ["-i", source]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.get_cell_background_color(0, "f17") == "#ffffff"
