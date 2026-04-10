# Copyright 2018-2026 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com
from __future__ import annotations

import os
import platform
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

from odfdo import Document
from odfdo.scripts import flat
from odfdo.scripts.flat import main as main_script
from odfdo.scripts.flat import main_convert_flat, parse_cli_args
from odfdo.scripts.folder import main_convert_folder
from odfdo.scripts.folder import parse_cli_args as folder_parse_cli_args

SCRIPT = Path(flat.__file__)


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


def test_flat_no_param():
    params = []
    out, err, exitcode = run_params(params)
    print(out, err, exitcode)
    assert exitcode == 2
    if platform.system() != "Windows":
        assert "odfdo-flat: error: the following arguments are required" in err
        assert "usage" in err


# direct access to internal function


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Fails on Windows due to stdin/output capture conflict.",
)
def test_flat_2_no_param_on_main_function(monkeypatch):
    with pytest.raises(SystemExit) as result:
        monkeypatch.setattr(sys, "argv", [])
        main_script()
        assert result.value.code >= 1


@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="Fails on Windows due to stdin/output capture conflict.",
)
def test_flat_2_no_param():
    with pytest.raises(SystemExit) as result:
        params = parse_cli_args([])
        main_convert_flat(params)
        assert result.value.code >= 1


def test_flat_2_version(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--version"])
        assert result.value.code == 0
    captured = capsys.readouterr()

    assert "odfdo-flat v3" in captured.out


def test_flat_2_help(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--help"])
        assert result.value.code == 0
    captured = capsys.readouterr()

    assert "Convert a standard ODF file" in captured.out


def test_flat_2_no_file_on_main(monkeypatch):
    with pytest.raises(SystemExit) as result:
        monkeypatch.setattr(sys, "argv", ["xxx", "none_file"])
        main_script()
        assert result.value.code >= 1


def test_flat_2_no_file():
    params = parse_cli_args(["none_file"])
    with pytest.raises(SystemExit) as result:
        main_convert_flat(params)
        assert result.value.code >= 1


def test_flat_2_odt_to_fodt(capsys, tmp_path, samples):
    source = samples("test_diff1.odt")
    document_src = Document(source)
    tmp_source = tmp_path / "test.odt"
    document_src.save(tmp_source)
    assert tmp_source.exists()
    params = parse_cli_args([str(tmp_source)])
    main_convert_flat(params)
    captured = capsys.readouterr()
    print(captured.out)
    print(captured.err)
    path = tmp_path / "test.fodt"
    assert path.is_file()


def test_flat_2_fodt_to_odt(tmp_path, samples):
    source = samples("test_diff1.odt")
    document_src = Document(source)
    tmp_source = tmp_path / "test.odt"
    document_src.save(tmp_source)
    # First convert to flat
    params1 = parse_cli_args([str(tmp_source)])
    main_convert_flat(params1)
    tmp_source.unlink()
    assert not tmp_source.exists()
    # Then convert back to ODF
    params2 = parse_cli_args([str(tmp_path / "test.fodt")])
    main_convert_flat(params2)
    assert tmp_source.exists()


def test_flat_2_ods_to_fods(capsys, tmp_path, samples):
    source = samples("simple_table.ods")
    document_src = Document(source)
    tmp_source = tmp_path / "test.ods"
    document_src.save(tmp_source)
    assert tmp_source.exists()
    params = parse_cli_args([str(tmp_source)])
    main_convert_flat(params)
    captured = capsys.readouterr()
    print(captured.out)
    print(captured.err)
    path = tmp_path / "test.fods"
    assert path.is_file()


def test_flat_2_fods_to_ods(tmp_path, samples):
    source = samples("simple_table.ods")
    document_src = Document(source)
    tmp_source = tmp_path / "test.ods"
    document_src.save(tmp_source)
    # First convert to flat
    params1 = parse_cli_args([str(tmp_source)])
    main_convert_flat(params1)
    tmp_source.unlink()
    assert not tmp_source.exists()
    # Then convert back to ODF
    params2 = parse_cli_args([str(tmp_path / "test.fods")])
    main_convert_flat(params2)
    assert tmp_source.exists()


def test_flat_2_folder_to_fodt(capsys, tmp_path, samples):
    # First create a folder structure
    source = samples("test_diff1.odt")
    document_src = Document(source)
    tmp_source = tmp_path / "test.odt"
    document_src.save(tmp_source)
    # Convert to folder

    params1 = folder_parse_cli_args([str(tmp_source)])
    main_convert_folder(params1)
    tmp_source.unlink()
    assert not tmp_source.exists()
    # Convert folder to flat
    params2 = parse_cli_args([str(tmp_path / "test.odt.folder")])
    main_convert_flat(params2)
    captured = capsys.readouterr()
    print(captured.out)
    print(captured.err)
    path = tmp_path / "test.fodt"
    assert path.is_file()


def test_is_flat_xml_file_1(tmp_path):
    # Test with recognized suffix
    p1 = tmp_path / "test.fodt"
    p1.write_text("dummy")
    assert flat.is_flat_xml_file(p1) is True


def test_is_flat_xml_file_2(tmp_path):
    # Test with .xml suffix and correct content
    p2 = tmp_path / "test.xml"
    p2.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<office:document xmlns:office="
        '"urn:oasis:names:tc:opendocument:xmlns:office:1.0"/>'
    )
    assert flat.is_flat_xml_file(p2) is True


def test_is_flat_xml_file_3(tmp_path):
    # Test with no suffix and correct content
    p3 = tmp_path / "test_no_suffix"
    p3.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<office:document xmlns:office="
        '"urn:oasis:names:tc:opendocument:xmlns:office:1.0"/>'
    )
    assert flat.is_flat_xml_file(p3) is True


def test_is_flat_xml_file_4(tmp_path):
    # Test with .xml suffix but wrong content
    p4 = tmp_path / "wrong.xml"
    p4.write_text('<?xml version="1.0"?><root/>')
    assert flat.is_flat_xml_file(p4) is False


def test_is_flat_xml_file_5(tmp_path):
    # Test with no suffix and wrong content
    p5 = tmp_path / "wrong_no_suffix"
    p5.write_text("not xml at all")
    assert flat.is_flat_xml_file(p5) is False


def test_is_flat_xml_file_6(tmp_path):
    # Test with other suffix
    p6 = tmp_path / "test.txt"
    p6.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<office:document xmlns:office="
        '"urn:oasis:names:tc:opendocument:xmlns:office:1.0"/>'
    )
    assert flat.is_flat_xml_file(p6) is False


def test_is_flat_xml_file_oserror(tmp_path):
    # Trigger OSError by passing a directory where a file is expected
    p = tmp_path / "test_dir.xml"
    p.mkdir()
    assert flat.is_flat_xml_file(p) is False


def test_convert_flat_not_file_or_folder(tmp_path):
    fifo = tmp_path / "test_fifo"
    try:
        os.mkfifo(fifo)
    except (AttributeError, OSError):
        pytest.skip("FIFOs not supported on this platform")

    with pytest.raises(ValueError, match="Not a file or folder"):
        flat.convert_flat(str(fifo))


def test_flat_runpy(tmp_path, samples, monkeypatch):
    source = samples("test_diff1.odt")
    tmp_source = tmp_path / "test_runpy.odt"
    tmp_source.write_bytes(source.read_bytes())
    monkeypatch.setattr(sys, "argv", ["odfdo-flat", str(tmp_source)])
    runpy.run_path(str(SCRIPT), run_name="__main__")
    assert (tmp_path / "test_runpy.fodt").exists()
