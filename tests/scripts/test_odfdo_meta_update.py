# Copyright 2018-2025 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com

import io
import json
import subprocess
import sys
from pathlib import Path

from odfdo import Document
from odfdo.scripts import meta_update

SCRIPT = Path(meta_update.__file__)
SOURCE = "meta.odt"
JSON_CONTENT = {
    "meta:editing-cycles": 42,
    "meta:generator": "my generator",
    "dc:subject": None,
    "meta:user-defined": [
        {
            "meta:name": "size",
            "meta:value-type": "string",
            "value": "big",
        },
    ],
}


def run_params(params: list):
    command = [sys.executable, SCRIPT] + params
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_meta_update_no_param():
    params = []
    out, _err, exitcode = run_params(params)
    assert exitcode == 1
    assert b"usage:" in out
    assert b"Error:" in out


def test_meta_update_no_file():
    params = ["-i", "none_file1", "-o", "none_file2"]
    out, _err, exitcode = run_params(params)
    assert exitcode == 1
    assert b"usage:" in out
    assert b"Error" in out


def test_meta_update_no_json_file():
    params = ["-j"]
    _out, _err, exitcode = run_params(params)
    assert exitcode >= 1


def test_meta_update_strip(samples):
    source = str(samples(SOURCE))
    params = ["-s", "-i", source]
    out, _err, exitcode = run_params(params)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    metadata = document.meta.as_dict(full=True)
    assert metadata["meta:editing-cycles"] == 1
    assert metadata["dc:title"] is None
    assert metadata["dc:description"] is None
    assert metadata["dc:creator"] is None
    assert metadata["meta:keyword"] is None
    assert metadata["dc:subject"] is None
    assert metadata["dc:language"] is None
    assert metadata["meta:user-defined"] == []


def test_meta_update_json_changed(tmp_path, samples):
    source = str(samples(SOURCE))
    json_string = json.dumps(JSON_CONTENT)
    jpath = tmp_path / "json_data.json"
    jpath.write_text(json_string, encoding="utf8")
    params = ["-i", source, "-j", str(jpath)]
    out, _err, exitcode = run_params(params)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    metadata = document.meta.as_dict(full=True)
    assert metadata["meta:editing-cycles"] == 42
    assert metadata["meta:generator"] == "my generator"


def test_meta_update_json_removed(tmp_path, samples):
    source = str(samples(SOURCE))
    json_string = json.dumps(JSON_CONTENT)
    jpath = tmp_path / "json_data.json"
    jpath.write_text(json_string, encoding="utf8")
    params = ["-i", source, "-j", str(jpath)]
    out, _err, exitcode = run_params(params)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    metadata = document.meta.as_dict(full=True)
    assert metadata["dc:subject"] is None


def test_meta_update_json_kept(tmp_path, samples):
    source = str(samples(SOURCE))
    json_string = json.dumps(JSON_CONTENT)
    jpath = tmp_path / "json_data.json"
    jpath.write_text(json_string, encoding="utf8")
    params = ["-i", source, "-j", str(jpath)]
    out, _err, exitcode = run_params(params)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    metadata = document.meta.as_dict(full=True)
    assert metadata["dc:title"] == "Intitulé"


def test_meta_update_json_user(tmp_path, samples):
    source = str(samples(SOURCE))
    json_string = json.dumps(JSON_CONTENT)
    jpath = tmp_path / "json_data.json"
    jpath.write_text(json_string, encoding="utf8")
    params = ["-i", source, "-j", str(jpath)]
    out, _err, exitcode = run_params(params)
    assert exitcode == 0
    content = io.BytesIO(out)
    document = Document(content)
    content.close()
    metadata_user = document.meta.as_dict(full=True)["meta:user-defined"]
    assert len(metadata_user) == 5
    assert len([item for item in metadata_user if item["meta:name"] == "size"]) == 1
