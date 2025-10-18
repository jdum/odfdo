# Copyright 2018-2025 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com

import subprocess
import sys
from pathlib import Path

from odfdo.scripts import meta_print

SCRIPT = Path(meta_print.__file__)
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


def test_meta_print_no_param():
    params = []
    out, _err, exitcode = run_params(params)
    assert exitcode == 1
    assert b"usage:" in out
    assert b"Error: OSError" in out


def test_meta_print_no_file():
    params = ["-i", "none_file1", "-o", "none_file2"]
    out, _err, exitcode = run_params(params)
    assert exitcode == 1
    assert b"usage:" in out
    assert b"FileNotFoundError" in out


def test_meta_print_language(samples):
    source = str(samples(SOURCE))
    params = ["-l", "-i", source]
    out, _err, _exitcode = run_params(params)
    assert b"Default style language: fr-FR" in out
    assert b"Statistic:" in out


def test_meta_print_odf_version(samples):
    source = str(samples(SOURCE))
    params = ["-v", "-i", source]
    out, _err, _exitcode = run_params(params)
    assert b"OpenDocument format version: 1.3" in out
    assert b"Statistic:" in out


def test_meta_print_text(samples):
    source = str(samples(SOURCE))
    params = ["-i", source]
    out, _err, _exitcode = run_params(params)
    assert b"Creation date:" in out
    assert b"Statistic:" in out
    assert b"Object count:" in out


def test_meta_print_json(samples):
    source = str(samples(SOURCE))
    params = ["-j", "-i", source]
    out, _err, _exitcode = run_params(params)
    assert b"meta:creation-date" in out
    assert b"dc:date" in out
    assert b"meta:table-count" in out
    assert b"meta:generator" in out
    assert b"meta:initial-creator" in out
