# Copyright 2018-2025 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from textwrap import dedent

import pytest

from odfdo.scripts import headers
from odfdo.scripts.headers import main as main_script
from odfdo.scripts.headers import main_headers, parse_cli_args

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


def test_headers_no_param():
    params = []
    out, err, exitcode = run_params(params)
    print(out, err, exitcode)
    assert exitcode > 0


# direct access to internal function


def test_headers_2_no_param_on_main_function(monkeypatch):
    with pytest.raises(Exception) as result:
        monkeypatch.setattr(sys, "argv", [])
        main_script()
        assert result.value.code >= 1


def test_headers_2_no_param(monkeypatch):
    with pytest.raises(Exception) as result:
        params = parse_cli_args([])
        main_headers(params)
        assert result.value.code >= 1


def test_headers_2_version(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--version"])
        assert result.value.code == 0
    captured = capsys.readouterr()

    assert "odfdo-headers v3" in captured.out


def test_headers_2_help(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--help"])
        assert result.value.code == 0
    captured = capsys.readouterr()

    assert "Display the hierarchical headers" in captured.out


def test_headers_2_no_file():
    params = parse_cli_args(["none_file"])

    with pytest.raises(FileNotFoundError) as result:
        main_headers(params)
        assert result.value.code >= 1


def test_headers_2_no_headers(capsys, samples):
    source0 = samples("list.odt")
    params = parse_cli_args([str(source0)])

    main_headers(params)
    captured = capsys.readouterr()

    expected = ""
    assert captured.out == expected


def test_headers_2_base1(capsys, samples):
    source1 = samples("base_text.odt")
    params = parse_cli_args([str(source1)])

    main_headers(params)
    captured = capsys.readouterr()

    expected = (
        "1. odfdo Test Case Document\n"
        "1.1. Level 2 Title\n"
        "2. First Title of the Second Section\n"
    )
    assert captured.out == expected


def test_headers_2_base_depth0(capsys, samples):
    source1 = samples("base_text.odt")
    params = parse_cli_args(["--depth", "0", str(source1)])

    main_headers(params)
    captured = capsys.readouterr()

    expected = ""
    assert captured.out == expected


def test_headers_2_base_depth1(capsys, samples):
    source1 = samples("base_text.odt")
    params = parse_cli_args(["--depth", "1", str(source1)])

    main_headers(params)
    captured = capsys.readouterr()

    expected = "1. odfdo Test Case Document\n2. First Title of the Second Section\n"
    assert captured.out == expected


def test_headers_2_toc_depth0(capsys, samples):
    source2 = samples("toc.odt")
    params = parse_cli_args(["-d", "0", str(source2)])

    main_headers(params)
    captured = capsys.readouterr()

    expected = ""
    assert captured.out == expected


def test_headers_2_toc_depth1(capsys, samples):
    source2 = samples("toc.odt")
    params = parse_cli_args(["-d1", str(source2)])

    main_headers(params)
    captured = capsys.readouterr()

    expected = "1. Level 1 title 1\n2. Level 1 title 2\n3. Level 1 title 3\n"
    assert captured.out == expected


def test_headers_2_toc_depth2(capsys, samples):
    source2 = samples("toc.odt")
    params = parse_cli_args(["--depth", "2", str(source2)])

    main_headers(params)
    captured = capsys.readouterr()

    expected = (
        "1. Level 1 title 1\n1.1. Level 2 title 1\n2. Level 1 title 2\n2.1. Level 2 "
        "title 2\n3. Level 1 title 3\n3.1. Level 2 title 1\n3.2. Level 2 title 2\n"
    )
    assert captured.out == expected


def test_headers_2_toc_depth3(capsys, samples):
    source2 = samples("toc.odt")
    params = parse_cli_args(["--depth", "3", str(source2)])

    main_headers(params)
    captured = capsys.readouterr()

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
    assert captured.out.strip() == expected


def test_headers_2_toc_all(capsys, samples):
    source2 = samples("toc.odt")
    params = parse_cli_args([str(source2)])

    main_headers(params)
    captured = capsys.readouterr()

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
    assert captured.out.strip() == expected


def test_headers_2_toc_depth4(capsys, samples):
    source2 = samples("toc.odt")
    params = parse_cli_args(["--depth", "4", str(source2)])

    main_headers(params)
    captured = capsys.readouterr()

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
    assert captured.out.strip() == expected


def test_headers_2_toc_depth9999(capsys, samples):
    source2 = samples("toc.odt")
    params = parse_cli_args(["--depth", "9999", str(source2)])

    main_headers(params)
    captured = capsys.readouterr()

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
    assert captured.out.strip() == expected
