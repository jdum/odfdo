# Copyright 2018-2023 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com

import shlex
import subprocess
from pathlib import Path

from odfdo import Document

SCRIPT = Path(__file__).parent.parent / "odfdo" / "scripts" / "folder.py"
SAMPLES = Path(__file__).parent / "samples"


def run_params(params):
    command = shlex.split(f"python {SCRIPT} {params}")
    proc = subprocess.Popen(
        command,
        text=True,
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
    assert "Convert standard ODF file to folder" in out


def test_no_file():
    params = "none_file"
    out, err, exitcode = run_params(params)
    assert exitcode == 1
    assert "Convert standard ODF file to folder" in out


def test_folder_1(tmp_path):
    source = SAMPLES / "test_diff1.odt"
    document_src = Document(source)
    tmp_source = tmp_path / "test.odt"
    document_src.save(tmp_source)
    assert tmp_source.exists()
    params = str(tmp_source)
    out, err, exitcode = run_params(params)
    print(out)
    print(err)
    assert exitcode == 0
    path = tmp_path / "test.odt.folder"
    assert path.is_dir()


def test_folder_2(tmp_path):
    source = SAMPLES / "test_diff1.odt"
    document_src = Document(source)
    tmp_source = tmp_path / "test.odt"
    document_src.save(tmp_source)
    params1 = str(tmp_source)
    out, err, exitcode = run_params(params1)
    assert exitcode == 0
    tmp_source.unlink()
    assert not tmp_source.exists()
    params2 = str(tmp_path / "test.odt.folder")
    out, err, exitcode = run_params(params2)
    assert exitcode == 0
    assert tmp_source.exists()