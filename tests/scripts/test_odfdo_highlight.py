# Copyright 2018-2026 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com
from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

import pytest

from odfdo.document import Document
from odfdo.scripts import highlight
from odfdo.scripts.highlight import main as main_script
from odfdo.scripts.highlight import main_highlight, parse_cli_args

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


def test_highlight_no_param():
    params = []
    out, err, exitcode = run_params(params)
    print(out, err, exitcode)
    assert exitcode == 2
    assert b"usage:" in err
    assert b"required" in err
    assert b"pattern" in err


# direct access to internal function


def test_highlight_2_no_param_on_main_function(monkeypatch, capsys):
    with pytest.raises(SystemExit) as result:
        monkeypatch.setattr(sys, "argv", [])
        main_script()
        assert result.value.code >= 1
    captured = capsys.readouterr()

    assert "usage:" in captured.err
    assert "required" in captured.err
    assert "pattern" in captured.err


def test_highlight_2_no_param(monkeypatch):
    with pytest.raises(SystemExit) as result:
        params = parse_cli_args([])
        main_script(params)
        assert result.value.code >= 1


def test_highlight_2_some_param_on_main_function(monkeypatch, capsysbinary, samples):
    source = str(samples("base_text.odt"))

    monkeypatch.setattr(sys, "argv", ["odfdo-highlight", "-i", source, "-b", "odfdo"])
    main_script()
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    display_name = " ".join(["odfdo", "highlight", "bold"])
    name = display_name.replace(" ", "_20_")
    assert len(document.body.get_spans(style=name)) == 1


def test_highlight_2_version(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--version"])
        assert result.value.code == 0
    captured = capsys.readouterr()

    assert "odfdo-highlight v3" in captured.out


def test_highlight_2_help(capsys):
    with pytest.raises(SystemExit) as result:
        parse_cli_args(["--help"])
        assert result.value.code == 0
    captured = capsys.readouterr()

    assert "Search for a regular expression" in captured.out


def test_highlight_2_no_style():
    params = parse_cli_args(["pattern"])

    with pytest.raises(SystemExit) as result:
        main_highlight(params)
        assert result.value.code >= 1


def test_highlight_2_no_file():
    params = parse_cli_args(["-i", "none_file1", "-o", "none_file2", "-b", "pattern"])

    with pytest.raises(FileNotFoundError) as result:
        main_highlight(params)
        assert result.value.code >= 1


def test_highlight_2_replace1(capsysbinary, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args(["-i", source, "-b", "odfdo"])

    main_highlight(params)
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    display_name = " ".join(["odfdo", "highlight", "bold"])
    name = display_name.replace(" ", "_20_")
    assert len(document.body.get_spans(style=name)) == 1


def test_highlight_2_replace2(capsysbinary, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args(["-i", source, "-a", "-b", "This"])

    main_highlight(params)
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    display_name = " ".join(["odfdo", "highlight", "italic", "bold"])
    name = display_name.replace(" ", "_20_")
    assert len(document.body.get_spans(style=name)) == 6


def test_highlight_2_replace3(capsysbinary, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args(["-i", source, "-c", "red", "paragraph"])

    main_highlight(params)
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    display_name = " ".join(["odfdo", "highlight", "red"])
    name = display_name.replace(" ", "_20_")
    assert len(document.body.get_spans(style=name)) == 7


def test_highlight_2_replace4(capsysbinary, samples):
    source = str(samples("base_text.odt"))
    params = parse_cli_args(["-i", source, "-c", "red", "-g", "yellow", "paragraph"])

    main_highlight(params)
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    display_name = " ".join(["odfdo", "highlight", "red", "yellow"])
    name = display_name.replace(" ", "_20_")
    assert len(document.body.get_spans(style=name)) == 7


def test_highlight_2_replace4_duplicate(capsysbinary, tmp_path, samples):
    source = str(samples("base_text.odt"))
    dest = tmp_path / "replaced.odt"
    params = parse_cli_args(
        [
            "-i",
            source,
            "-c",
            "red",
            "-g",
            "yellow",
            "-o",
            str(dest),
            "paragraph",
        ]
    )

    main_highlight(params)

    params2 = parse_cli_args(
        [
            "-i",
            str(dest),
            "-c",
            "red",
            "-g",
            "yellow",
            "paragraph",
        ]
    )

    main_highlight(params2)
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    display_name = " ".join(["odfdo", "highlight", "red", "yellow"])
    name = display_name.replace(" ", "_20_")
    assert len(document.body.get_spans(style=name)) == 14


def test_highlight_2_toc_replaced(capsysbinary, samples):
    source = str(samples("toc_done.odt"))
    params = parse_cli_args(["-i", source, "-c", "red", "-g", "yellow", "title"])

    main_highlight(params)
    captured = capsysbinary.readouterr()

    content = io.BytesIO(captured.out)
    document = Document(content)
    content.close()
    display_name = " ".join(["odfdo", "highlight", "red", "yellow"])
    name = display_name.replace(" ", "_20_")
    assert len(document.body.get_spans(style=name)) == 12
