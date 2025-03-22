# Copyright 2018-2025 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com

import subprocess
import sys
from pathlib import Path
from textwrap import dedent

from odfdo.scripts import headers

SCRIPT = Path(headers.__file__)


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
    out, err, exitcode = run_params(params)
    print(out, err, exitcode)
    assert exitcode > 0


def test_no_file():
    params = ["none_file"]
    out, err, exitcode = run_params(params)
    assert exitcode == 1
    assert "sage:" in out
    assert "FileNotFoundError" in err


def test_no_headers(samples):
    source0 = str(samples("list.odt"))
    params = [source0]
    out, _err, exitcode = run_params(params)
    print(out)
    expected = ""
    assert exitcode == 0
    assert out == expected


def test_base1(samples):
    source1 = str(samples("base_text.odt"))
    params = [source1]
    out, _err, exitcode = run_params(params)
    print(out)
    expected = (
        "1. odfdo Test Case Document\n"
        "1.1. Level 2 Title\n"
        "2. First Title of the Second Section\n"
    )
    assert exitcode == 0
    assert out == expected


def test_base_depth0(samples):
    source1 = str(samples("base_text.odt"))
    params = ["--depth", "0", source1]
    out, _err, exitcode = run_params(params)
    print(out)
    expected = ""
    assert exitcode == 0
    assert out == expected


def test_base_depth1(samples):
    source1 = str(samples("base_text.odt"))
    params = ["--depth", "1", source1]
    out, _err, exitcode = run_params(params)
    print(out)
    expected = "1. odfdo Test Case Document\n2. First Title of the Second Section\n"
    assert exitcode == 0
    assert out == expected


def test_toc_depth0(samples):
    source2 = str(samples("toc.odt"))
    params = ["-d", "0", source2]
    out, _err, exitcode = run_params(params)
    print(out)
    expected = ""
    assert exitcode == 0
    assert out == expected


def test_toc_depth1(samples):
    source2 = str(samples("toc.odt"))
    params = ["-d1", source2]
    out, _err, exitcode = run_params(params)
    print(out)
    expected = "1. Level 1 title 1\n2. Level 1 title 2\n3. Level 1 title 3\n"
    assert exitcode == 0
    assert out == expected


def test_toc_depth2(samples):
    source2 = str(samples("toc.odt"))
    params = ["--depth", "2", source2]
    out, _err, exitcode = run_params(params)
    print(out)
    expected = (
        "1. Level 1 title 1\n1.1. Level 2 title 1\n2. Level 1 title 2\n2.1. Level 2 "
        "title 2\n3. Level 1 title 3\n3.1. Level 2 title 1\n3.2. Level 2 title 2\n"
    )
    assert exitcode == 0
    assert out == expected


def test_toc_depth3(samples):
    source2 = str(samples("toc.odt"))
    params = ["--depth", "3", source2]
    out, _err, exitcode = run_params(params)
    print(out)
    expected = dedent(
        """\
        1. Level 1 title 1
        1.1. Level 2 title 1
        2. Level 1 title 2
        2.1.1. Level 3 title 1
        2.2. Level 2 title 2
        3. Level 1 title 3
        3.1. Level 2 title 1
        3.1.1. Level 3 title 1
        3.1.2. Level 3 title 2
        3.2. Level 2 title 2
        3.2.1. Level 3 title 1
        3.2.2. Level 3 title 2
        """
    ).strip()
    assert exitcode == 0
    assert out.strip() == expected


def test_toc_all(samples):
    source2 = str(samples("toc.odt"))
    params = [source2]
    out, _err, exitcode = run_params(params)
    print(out)
    expected = dedent(
        """\
        1. Level 1 title 1
        1.1. Level 2 title 1
        2. Level 1 title 2
        2.1.1. Level 3 title 1
        2.2. Level 2 title 2
        3. Level 1 title 3
        3.1. Level 2 title 1
        3.1.1. Level 3 title 1
        3.1.2. Level 3 title 2
        3.2. Level 2 title 2
        3.2.1. Level 3 title 1
        3.2.2. Level 3 title 2
        """
    ).strip()

    assert exitcode == 0
    assert out.strip() == expected


def test_toc_depth4(samples):
    source2 = str(samples("toc.odt"))
    params = ["--depth", "9999", source2]
    out, _err, exitcode = run_params(params)
    print(out)
    expected = dedent(
        """\
        1. Level 1 title 1
        1.1. Level 2 title 1
        2. Level 1 title 2
        2.1.1. Level 3 title 1
        2.2. Level 2 title 2
        3. Level 1 title 3
        3.1. Level 2 title 1
        3.1.1. Level 3 title 1
        3.1.2. Level 3 title 2
        3.2. Level 2 title 2
        3.2.1. Level 3 title 1
        3.2.2. Level 3 title 2
        """
    ).strip()
    assert exitcode == 0
    assert out.strip() == expected


def test_toc_depth9999(samples):
    source2 = str(samples("toc.odt"))
    params = ["--depth", "9999", source2]
    out, _err, exitcode = run_params(params)
    print(out)
    expected = dedent(
        """\
        1. Level 1 title 1
        1.1. Level 2 title 1
        2. Level 1 title 2
        2.1.1. Level 3 title 1
        2.2. Level 2 title 2
        3. Level 1 title 3
        3.1. Level 2 title 1
        3.1.1. Level 3 title 1
        3.1.2. Level 3 title 2
        3.2. Level 2 title 2
        3.2.1. Level 3 title 1
        3.2.2. Level 3 title 2
        """
    ).strip()
    assert exitcode == 0
    assert out.strip() == expected


def test_help():
    params = ["--help"]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    assert "Print the headers" in out


def test_version():
    params = ["--version"]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    assert "odfdo-headers v3" in out
