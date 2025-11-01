# Copyright 2018-2025 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com
from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

from odfdo import Document
from odfdo.scripts import meta_update
from odfdo.scripts.meta_update import main as main_script
from odfdo.scripts.meta_update import main_meta_update, parse_cli_args

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


# direct access to internal function


def test_meta_update_2_no_param_on_main_function(monkeypatch, capsys):
    with pytest.raises(SystemExit) as result:
        monkeypatch.setattr(sys, "argv", [])
        main_script()
        assert result.type is SystemExit
        assert result.value.code >= 1
    captured = capsys.readouterr()

    assert "usage" in captured.out


def test_meta_update_2_no_param(capsys):
    params = parse_cli_args([])

    with pytest.raises(SystemExit) as result:
        main_meta_update(params)
        assert result.type is SystemExit
        assert result.value.code == 1
    captured = capsys.readouterr()

    assert "usage" in captured.out


def test_meta_update_2_no_file(capsys):
    params = parse_cli_args(["-i", "none_file1", "-o", "none_file2"])

    with pytest.raises(SystemExit) as result:
        main_meta_update(params)
        assert result.type is SystemExit
        assert result.value.code == 1
    captured = capsys.readouterr()

    assert "usage" in captured.out
    assert "FileNotFoundError" in captured.out


def test_meta_update_2_no_json_file(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["-j"])
        assert result.value.code >= 1


def test_meta_update_2_strip(capsysbinary, samples):
    source = str(samples(SOURCE))
    params = parse_cli_args(["-s", "-i", source])

    main_meta_update(params)
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
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


def test_meta_update_2_json_changed(capsysbinary, tmp_path, samples):
    source = str(samples(SOURCE))
    json_string = json.dumps(JSON_CONTENT)
    jpath = tmp_path / "json_data.json"
    jpath.write_text(json_string, encoding="utf8")
    params = parse_cli_args(["-i", source, "-j", str(jpath)])

    main_meta_update(params)
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    metadata = document.meta.as_dict(full=True)
    assert metadata["meta:editing-cycles"] == 42
    assert metadata["meta:generator"] == "my generator"


def test_meta_update_2_json_removed(capsysbinary, tmp_path, samples):
    source = str(samples(SOURCE))
    json_string = json.dumps(JSON_CONTENT)
    jpath = tmp_path / "json_data.json"
    jpath.write_text(json_string, encoding="utf8")
    params = parse_cli_args(["-i", source, "-j", str(jpath)])

    main_meta_update(params)
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    metadata = document.meta.as_dict(full=True)
    assert metadata["dc:subject"] is None


def test_meta_update_2_json_kept(capsysbinary, tmp_path, samples):
    source = str(samples(SOURCE))
    json_string = json.dumps(JSON_CONTENT)
    jpath = tmp_path / "json_data.json"
    jpath.write_text(json_string, encoding="utf8")
    params = parse_cli_args(["-i", source, "-j", str(jpath)])

    main_meta_update(params)
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    metadata = document.meta.as_dict(full=True)
    assert metadata["dc:title"] == "Intitulé"


def test_meta_update_2_json_user(capsysbinary, tmp_path, samples):
    source = str(samples(SOURCE))
    json_string = json.dumps(JSON_CONTENT)
    jpath = tmp_path / "json_data.json"
    jpath.write_text(json_string, encoding="utf8")
    params = parse_cli_args(["-i", source, "-j", str(jpath)])

    main_meta_update(params)
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    metadata_user = document.meta.as_dict(full=True)["meta:user-defined"]
    assert len(metadata_user) == 5
    assert len([item for item in metadata_user if item["meta:name"] == "size"]) == 1


def test_meta_update_2_json_user_out_put_path(tmp_path, samples):
    source = str(samples(SOURCE))
    json_string = json.dumps(JSON_CONTENT)
    jpath = tmp_path / "json_data.json"
    jpath.write_text(json_string, encoding="utf8")
    dest_path = tmp_path / "output.odt"
    params = parse_cli_args(["-i", source, "-j", str(jpath), "-o", str(dest_path)])

    main_meta_update(params)

    document = Document(dest_path)
    metadata_user = document.meta.as_dict(full=True)["meta:user-defined"]
    assert len(metadata_user) == 5
    assert len([item for item in metadata_user if item["meta:name"] == "size"]) == 1


def test_meta_update_2_no_json_or_strip(capsys, samples):
    source = str(samples(SOURCE))
    params = parse_cli_args(["-i", source])

    with pytest.raises(SystemExit) as result:
        main_meta_update(params)
        assert result.type is SystemExit
        assert result.value.code == 1
    captured = capsys.readouterr()

    assert "required" in captured.out
