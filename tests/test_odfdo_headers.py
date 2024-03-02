# Copyright 2018-2024 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com

import shlex
import subprocess
from pathlib import Path
from textwrap import dedent

SCRIPT = Path(__file__).parent.parent / "odfdo" / "scripts" / "headers.py"
SAMPLES = Path(__file__).parent / "samples"
SOURCE0 = SAMPLES / "list.odt"
SOURCE1 = SAMPLES / "base_text.odt"
SOURCE2 = SAMPLES / "toc.odt"


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
    print(out, err, exitcode)
    assert exitcode > 0


def test_no_file():
    params = "none_file"
    out, err, exitcode = run_params(params)
    assert exitcode == 1
    assert b"sage:" in out
    assert b"FileNotFoundError" in err


def test_no_headers():
    params = f"{SOURCE0}"
    out, err, exitcode = run_params(params)
    print(out)
    expected = b""
    assert exitcode == 0
    assert out == expected


def test_base1():
    params = f"{SOURCE1}"
    out, err, exitcode = run_params(params)
    print(out)
    expected = (
        b"1. odfdo Test Case Document\n"
        b"1.1. Level 2 Title\n"
        b"2. First Title of the Second Section\n"
    )
    assert exitcode == 0
    assert out == expected


def test_base_depth0():
    params = f"--depth 0 {SOURCE1}"
    out, err, exitcode = run_params(params)
    print(out)
    expected = b""
    assert exitcode == 0
    assert out == expected


def test_base_depth1():
    params = f"--depth 1 {SOURCE1}"
    out, err, exitcode = run_params(params)
    print(out)
    expected = b"1. odfdo Test Case Document\n2. First Title of the Second Section\n"
    assert exitcode == 0
    assert out == expected


def test_toc_depth0():
    params = f"-d 0 {SOURCE2}"
    out, err, exitcode = run_params(params)
    print(out)
    expected = b""
    assert exitcode == 0
    assert out == expected


def test_toc_depth1():
    params = f"-d1 {SOURCE2}"
    out, err, exitcode = run_params(params)
    print(out)
    expected = b"1. Level 1 title 1\n2. Level 1 title 2\n3. Level 1 title 3\n"
    assert exitcode == 0
    assert out == expected


def test_toc_depth2():
    params = f"--depth 2 {SOURCE2}"
    out, err, exitcode = run_params(params)
    print(out)
    expected = (
        b"1. Level 1 title 1\n1.1. Level 2 title 1\n2. Level 1 title 2\n2.1. Level 2 "
        b"title 2\n3. Level 1 title 3\n3.1. Level 2 title 1\n3.2. Level 2 title 2\n"
    )
    assert exitcode == 0
    assert out == expected


def test_toc_depth3():
    params = f"--depth 3 {SOURCE2}"
    out, err, exitcode = run_params(params)
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
    ).encode()
    assert exitcode == 0
    assert out == expected


def test_toc_all():
    params = f"{SOURCE2}"
    out, err, exitcode = run_params(params)
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
    ).encode()

    assert exitcode == 0
    assert out == expected


def test_toc_depth4():
    params = f"--depth 9999 {SOURCE2}"
    out, err, exitcode = run_params(params)
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
    ).encode()
    assert exitcode == 0
    assert out == expected


def test_toc_depth9999():
    params = f"--depth 9999 {SOURCE2}"
    out, err, exitcode = run_params(params)
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
    ).encode()
    assert exitcode == 0
    assert out == expected


def test_help():
    params = "--help"
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    assert b"Print the headers" in out


def test_version():
    params = "--version"
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    assert b"odfdo-headers v3" in out
