# Copyright 2018-2025 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com

import io
import subprocess
import sys
from pathlib import Path

from odfdo import Document
from odfdo.scripts import highlight

SCRIPT = Path(highlight.__file__)


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
    out, err, exitcode = run_params(params)
    print(out, err, exitcode)
    assert exitcode == 2
    assert b"usage:" in err
    assert b"required" in err
    assert b"pattern" in err


def test_no_style():
    params = ["pattern"]
    out, err, exitcode = run_params(params)
    print(out, err, exitcode)
    assert exitcode == 1
    assert b"required" in err
    assert b"style" in err


def test_no_file():
    params = ["-i", "none_file1", "-o", "none_file2", "-b", "pattern"]
    out, err, exitcode = run_params(params)
    assert exitcode == 1
    assert b"sage:" in out
    assert b"FileNotFoundError" in err


def test_replace1(samples):
    source = str(samples("base_text.odt"))
    params = ["-i", source, "-b", "odfdo"]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    display_name = " ".join(["odfdo", "highlight", "bold"])
    name = display_name.replace(" ", "_20_")
    print(document.body.serialize())
    assert len(document.body.get_spans(style=name)) == 1


def test_replace2(samples):
    source = str(samples("base_text.odt"))
    params = ["-i", source, "-a", "-b", "This"]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    display_name = " ".join(["odfdo", "highlight", "italic", "bold"])
    name = display_name.replace(" ", "_20_")
    assert len(document.body.get_spans(style=name)) == 6


def test_replace3(samples):
    source = str(samples("base_text.odt"))
    params = ["-i", source, "-c", "red", "paragraph"]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    display_name = " ".join(["odfdo", "highlight", "red"])
    name = display_name.replace(" ", "_20_")
    assert len(document.body.get_spans(style=name)) == 7


def test_replace4(samples):
    source = str(samples("base_text.odt"))
    params = ["-i", source, "-c", "red", "-g", "yellow", "paragraph"]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    display_name = " ".join(["odfdo", "highlight", "red", "yellow"])
    name = display_name.replace(" ", "_20_")
    assert len(document.body.get_spans(style=name)) == 7


def test_help():
    params = ["--help"]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    assert b"Search and highlight" in out


def test_version():
    params = ["--version"]
    out, err, exitcode = run_params(params)
    print(err)
    assert exitcode == 0
    assert b"odfdo-highlight v3" in out
