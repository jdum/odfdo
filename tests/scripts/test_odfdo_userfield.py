# Copyright 2018-2025 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com
from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

import pytest

from odfdo.document import Document
from odfdo.scripts import userfield
from odfdo.scripts.userfield import main as main_script
from odfdo.scripts.userfield import main_userfields, parse_cli_args

SCRIPT = Path(userfield.__file__)
SOURCE = "user_fields.odt"


def run_params(params: list):
    command = [sys.executable, SCRIPT] + params
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_userfields_no_param():
    params = []
    out, _err, exitcode = run_params(params)
    assert exitcode == 1
    assert b"usage:" in out
    assert b"Error: ValueError, missing arguments" in out


# direct access to internal function


def test_userfields_2_no_param_on_main_function(monkeypatch):
    with pytest.raises(SystemExit) as result:
        monkeypatch.setattr(sys, "argv", [])
        main_script()
        assert result.value.code >= 1


def test_userfields_2_no_param():
    with pytest.raises(SystemExit) as result:
        params = parse_cli_args([])
        main_userfields(params)
        assert result.value.code >= 1


def test_userfields_2_version(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--version"])
        assert result.value.code == 0
    captured = capsys.readouterr()

    assert "odfdo-userfield v3" in captured.out


def test_userfields_2_help(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--help"])
        assert result.value.code == 0
    captured = capsys.readouterr()

    assert "usage: odfdo-userfield" in captured.out


def test_userfields_2_no_file():
    params = parse_cli_args(["-i", "none_file1", "-o", "none_file2", "-anr"])

    with pytest.raises(SystemExit) as result:
        main_userfields(params)
        assert result.value.code >= 1


def test_userfields_2_field(capsys, samples):
    source = str(samples(SOURCE))
    params = parse_cli_args(["-i", source, "-f", "city"])

    main_userfields(params)
    captured = capsys.readouterr()

    assert "Paris" in captured.out


def test_userfields_2_field2(capsys, samples):
    source = str(samples(SOURCE))
    params = parse_cli_args(["-i", source, "-f", "city", "-f", "phone"])

    main_userfields(params)
    captured = capsys.readouterr()

    assert "Paris" in captured.out
    assert "77 77 77 77 77" in captured.out


def test_userfields_2_field3(capsys, samples):
    source = str(samples(SOURCE))
    params = parse_cli_args(
        ["-i", source, "-f", "city", "-f", "phone", "-f", "counter"]
    )

    main_userfields(params)
    captured = capsys.readouterr()

    assert "Paris" in captured.out
    assert "77 77 77 77 77" in captured.out
    assert "42" in captured.out


def test_userfields_2_all(capsys, samples):
    source = str(samples(SOURCE))
    params = parse_cli_args(["-i", source, "-a"])

    main_userfields(params)
    captured = capsys.readouterr()

    assert "Paris" in captured.out
    assert "77 77 77 77 77" in captured.out
    assert "42" in captured.out
    assert "city" not in captured.out
    assert "string" not in captured.out


def test_userfields_2_all_name(capsys, samples):
    source = str(samples(SOURCE))
    params = parse_cli_args(["-i", source, "-an"])

    main_userfields(params)
    captured = capsys.readouterr()

    assert "Paris" in captured.out
    assert "77 77 77 77 77" in captured.out
    assert "42" in captured.out
    assert "city" in captured.out
    assert "string" not in captured.out


def test_userfields_2_all_name_type(capsys, samples):
    source = str(samples(SOURCE))
    params = parse_cli_args(["-i", source, "-ant"])

    main_userfields(params)
    captured = capsys.readouterr()

    assert "Paris" in captured.out
    assert "77 77 77 77 77" in captured.out
    assert "42" in captured.out
    assert "city" in captured.out
    assert "string" in captured.out


def test_userfields_2_all_name_type_repr(capsys, samples):
    source = str(samples(SOURCE))
    params = parse_cli_args(["-i", source, "-antr"])

    main_userfields(params)
    captured = capsys.readouterr()

    assert "Paris" in captured.out
    assert "77 77 77 77 77" in captured.out
    assert "42" in captured.out
    assert "city" in captured.out
    assert "string" in captured.out


def test_userfields_2_set_err(capsys, samples):
    source = str(samples(SOURCE))

    with pytest.raises(SystemExit) as result:
        parse_cli_args(["-i", source, "-s", "city"])
        assert result.value.code >= 1
    captured = capsys.readouterr()

    assert "expected 2 arguments" in captured.err


def test_userfields_2_set(capsysbinary, samples):
    source = str(samples(SOURCE))
    params = parse_cli_args(["-i", source, "-s", "city", "Lyon"])

    main_userfields(params)
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    assert document.body.get_user_field_value("city") == "Lyon"


def test_userfields_2_set2(capsysbinary, samples):
    source = str(samples(SOURCE))
    params = parse_cli_args(["-i", source, "-s", "city", "Lyon", "-s", "counter", "99"])

    main_userfields(params)
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    assert document.body.get_user_field_value("city") == "Lyon"
    assert document.body.get_user_field_value("counter") == "99"


def test_userfields_2_set3_unknown(capsysbinary, samples):
    source = str(samples(SOURCE))
    params = parse_cli_args(
        [
            "-i",
            source,
            "-s",
            "city",
            "Lyon",
            "-s",
            "counter",
            "99",
            "-s",
            "unknown_field",
            "nothing",
        ]
    )

    main_userfields(params)
    captured = capsysbinary.readouterr()

    assert b"unknown user-field" in captured.err

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    assert document.body.get_user_field_value("city") == "Lyon"
    assert document.body.get_user_field_value("counter") == "99"
