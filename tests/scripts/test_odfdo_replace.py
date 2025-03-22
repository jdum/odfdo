# Copyright 2018-2025 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com

import io
import subprocess
import sys
from pathlib import Path

from odfdo import Document
from odfdo.scripts import replace

SCRIPT = Path(replace.__file__)


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
    assert exitcode == 2
    assert b"usage:" in err
    assert b"odfdo-replace: error: the following arguments are required" in err


def test_no_file():
    params = ["-i", "none_file1", "-o", "none_file2", "pattern", "replacement"]
    out, _err, exitcode = run_params(params)
    assert exitcode == 1
    assert b"usage:" in out
    assert b"FileNotFoundError" in out


def test_replace1(samples):
    source = str(samples("base_text.odt"))
    params = ["-i", source, "odfdo", "FOO"]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.body.search("FOO") is not None


def test_replace2(samples):
    source = str(samples("base_text.odt"))
    params = ["-i", source, "not here", "FOO"]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.body.search("FOO") is None


def test_replace3(samples):
    source = str(samples("base_text.odt"))
    params = ["-i", source, "paragraph", "FOO"]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.body.search("odfdo") is not None
    assert document.body.search("FOO") is not None
    assert document.body.search("paragraph") is None


def test_replace_formatted_1(samples):
    source = str(samples("base_text.odt"))
    params = ["-f", "-i", source, "paragraph", "FOO"]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert document.body.search("odfdo") is not None
    assert document.body.search("FOO") is not None
    assert document.body.search("paragraph") is None


def test_replace_formatted_2(samples):
    source = str(samples("base_text.odt"))
    params = ["-i", source, "paragraph", "FOO\nBAR"]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert len(document.body.get_elements("//text:line-break")) == 0
    assert document.body.search("odfdo") is not None
    assert document.body.search("FOO") is not None
    assert document.body.search("BAR") is not None
    assert document.body.search("paragraph") is None


def test_replace_formatted_3(samples):
    source = str(samples("base_text.odt"))
    params = ["-f", "-i", source, "paragraph", "FOO\n\nBAR"]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    assert len(document.body.get_elements("//text:line-break")) == 14
    assert document.body.search("odfdo") is not None
    assert document.body.search("FOO") is not None
    assert document.body.search("BAR") is not None
    assert document.body.search("paragraph") is None
