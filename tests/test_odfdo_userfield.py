# Copyright 2018-2025 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com

import io
import subprocess
import sys
from pathlib import Path

from odfdo import Document

SCRIPT = Path(__file__).parent.parent / "src" / "odfdo" / "scripts" / "userfield.py"
SAMPLES = Path(__file__).parent / "samples"
SOURCE = SAMPLES / "user_fields.odt"


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
    assert b"usage:" in out
    assert b"Error: ValueError, missing arguments" in out


def test_no_file():
    params = ["-i", "none_file1", "-o", "none_file2", "-anr"]
    out, _err, exitcode = run_params(params)
    assert exitcode == 1
    assert b"usage:" in out
    assert b"FileNotFoundError" in out


def test_field():
    params = ["-i", f"{SOURCE}", "-f", "city"]
    out, _err, _exitcode = run_params(params)
    assert b"Paris" in out


def test_field2():
    params = ["-i", f"{SOURCE}", "-f", "city", "-f", "phone"]
    out, _err, _exitcode = run_params(params)
    assert b"Paris" in out
    assert b"77 77 77 77 77" in out


def test_field3():
    params = ["-i", f"{SOURCE}", "-f", "city", "-f", "phone", "-f", "counter"]
    out, _err, _exitcode = run_params(params)
    assert b"Paris" in out
    assert b"77 77 77 77 77" in out
    assert b"42" in out


def test_all():
    params = ["-i", f"{SOURCE}", "-a"]
    out, _err, _exitcode = run_params(params)
    assert b"Paris" in out
    assert b"77 77 77 77 77" in out
    assert b"42" in out
    assert b"city" not in out
    assert b"string" not in out


def test_all_name():
    params = ["-i", f"{SOURCE}", "-an"]
    out, _err, _exitcode = run_params(params)
    assert b"Paris" in out
    assert b"77 77 77 77 77" in out
    assert b"42" in out
    assert b"city" in out
    assert b"string" not in out


def test_all_name_type():
    params = ["-i", f"{SOURCE}", "-ant"]
    out, _err, _exitcode = run_params(params)
    assert b"Paris" in out
    assert b"77 77 77 77 77" in out
    assert b"42" in out
    assert b"city" in out
    assert b"string" in out


def test_all_name_type_repr():
    params = ["-i", f"{SOURCE}", "-antr"]
    out, _err, _exitcode = run_params(params)
    assert b"Paris" in out
    assert b"77 77 77 77 77" in out
    assert b"42" in out
    assert b"city" in out
    assert b"string" in out


def test_set_err():
    params = ["-i", f"{SOURCE}", "-s", "city"]
    _out, err, _exitcode = run_params(params)
    assert b"expected 2 arguments" in err


def test_set():
    params = ["-i", f"{SOURCE}", "-s", "city", "Lyon"]
    out, _err, _exitcode = run_params(params)
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.body.get_user_field_value("city") == "Lyon"


def test_set2():
    params = ["-i", f"{SOURCE}", "-s", "city", "Lyon", "-s", "counter", "99"]
    out, _err, _exitcode = run_params(params)
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.body.get_user_field_value("city") == "Lyon"
    assert document.body.get_user_field_value("counter") == "99"
