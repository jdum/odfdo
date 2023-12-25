# Copyright 2018-2023 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com

import io
import shlex
import subprocess
from pathlib import Path

from odfdo import Document

SCRIPT = Path(__file__).parent.parent / "odfdo" / "scripts" / "replace.py"
SAMPLES = Path(__file__).parent / "samples"
SOURCE = SAMPLES / "base_text.odt"


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
    assert exitcode == 1
    assert b"Usage:" in out
    assert b"Two arguments are required" in out


def test_no_file():
    params = "-i none_file1 -o none_file2 pattern replacement"
    out, err, exitcode = run_params(params)
    assert exitcode == 1
    assert b"Usage:" in out
    assert b"FileNotFoundError" in err


def test_replace1():
    params = f"-i {SOURCE} odfdo FOO"
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.body.search("FOO") is not None


def test_replace2():
    params = f"-i {SOURCE} 'not here' FOO"
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.body.search("FOO") is None


def test_replace3():
    params = f"-i {SOURCE} paragraph FOO"
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.body.search("odfdo") is not None
    assert document.body.search("FOO") is not None
    assert document.body.search("paragraph") is None
