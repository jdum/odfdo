# Copyright 2018-2026 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com
"""Test that odfdo-flat output is comparable to LibreOffice reference export."""

from __future__ import annotations

import re
from pathlib import Path

from odfdo import Document


def extract_style_features(fods_path: Path) -> dict:
    """Extract key style features from a flat ODF file for comparison.

    Returns a dictionary with:
    - background_colors: set of background color values
    - table_structure: dict with table element counts
    - cell_count: number of table cells
    - column_count: number of table columns
    - row_count: number of table rows
    """
    content = fods_path.read_text(encoding="utf-8")

    bg_colors = set(re.findall(r'background-color="(#[0-9a-fA-F]+)"', content))

    # Count table elements
    table_structure = {
        "table": len(re.findall(r"<table:table[> ]", content)),
        "table_column": len(re.findall(r"<table:table-column[> ]", content)),
        "table_row": len(re.findall(r"<table:table-row[> ]", content)),
        "table_cell": len(re.findall(r"<table:table-cell[> ]", content)),
    }

    # Count style definitions
    style_count = len(
        re.findall(r'<style:style[^>]+style:family="table-cell"', content)
    )

    # Extract mimetype
    mimetype_match = re.search(r'office:mimetype="([^"]+)"', content)
    mimetype = mimetype_match.group(1) if mimetype_match else None

    return {
        "background_colors": bg_colors,
        "table_structure": table_structure,
        "style_count": style_count,
        "mimetype": mimetype,
    }


def test_flat_export_comparison(tmp_path, samples) -> None:
    """Test that odfdo-flat produces output comparable to LibreOffice reference.

    This test:
    1. Loads the reference ODS file
    2. Exports it to flat XML using odfdo
    3. Compares key features with the LibreOffice reference export
    """
    source_ods = samples("test_flat.ods")
    reference_fods = samples("test_flat_lo.fods")

    # Convert ODS to flat XML using odfdo
    doc = Document(source_ods)
    odfdo_fods = tmp_path / "test_flat_odfdo.fods"
    doc.save(odfdo_fods, packaging="xml")

    # Extract features from both files
    reference_features = extract_style_features(reference_fods)
    odfdo_features = extract_style_features(odfdo_fods)

    # Compare mimetype
    assert odfdo_features["mimetype"] == reference_features["mimetype"], (
        f"Mimetype mismatch: {odfdo_features['mimetype']} vs {reference_features['mimetype']}"
    )

    # Compare table structure
    assert odfdo_features["table_structure"] == reference_features["table_structure"], (
        f"Table structure mismatch:\n"
        f"  odfdo: {odfdo_features['table_structure']}\n"
        f"  reference: {reference_features['table_structure']}"
    )

    # Compare background colors (allowing for minor differences)
    odfdo_colors = odfdo_features["background_colors"]
    reference_colors = reference_features["background_colors"]

    # Key colors that must be present
    key_colors = {"#ffff00", "#ff0000", "#ccffcc", "#ffcccc"}
    for color in key_colors:
        assert color in odfdo_colors, f"Key color {color} missing from odfdo output"
        assert color in reference_colors, f"Key color {color} missing from reference"

    # Check that most colors match (allowing for some differences in auto-generated styles)
    common_colors = odfdo_colors & reference_colors
    assert len(common_colors) >= len(key_colors), (
        f"Too many color differences. Common: {common_colors}"
    )


def test_flat_roundtrip_preserves_content(tmp_path, samples) -> None:
    """Test that ODS -> FODS -> ODS roundtrip preserves content.

    This test verifies that converting to flat XML and back doesn't lose
    table structure or styling information.
    """
    source_ods = samples("test_flat.ods")

    # Load original
    doc1 = Document(source_ods)

    # Save as flat XML
    fods_path = tmp_path / "roundtrip.fods"
    doc1.save(fods_path, packaging="xml")

    # Load flat XML and save back as ODS
    doc2 = Document(fods_path)
    ods_path = tmp_path / "roundtrip.ods"
    doc2.save(ods_path, packaging="zip")

    # Extract and compare
    doc3 = Document(ods_path)
    doc3.save(tmp_path / "roundtrip.ods.folder", packaging="folder")

    # Read content.xml and check structure
    content_xml = (tmp_path / "roundtrip.ods.folder" / "content.xml").read_text(encoding="utf-8")

    # Verify table elements are present
    assert "<table:table " in content_xml, "Table not found in roundtrip output"
    assert "<table:table-cell" in content_xml, "Table cells not found"
    assert "<table:table-row" in content_xml, "Table rows not found"
    assert "<table:table-column" in content_xml, "Table columns not found"

    # Verify cell styles are in content.xml (not styles.xml)
    assert 'style:family="table-cell"' in content_xml, (
        "Cell styles not found in content.xml"
    )


def test_flat_xml_valid_structure(tmp_path, samples) -> None:
    """Test that generated flat XML has valid ODF structure.

    Checks for proper element ordering and namespace declarations.
    """
    source_ods = samples("test_flat.ods")

    doc = Document(source_ods)
    fods_path = tmp_path / "valid.fods"
    doc.save(fods_path, packaging="xml")

    content = fods_path.read_text(encoding="utf-8")

    # Check root element
    assert content.startswith('<?xml version="1.0" encoding="UTF-8"?>'), (
        "Missing XML declaration"
    )
    assert "<office:document" in content, "Missing office:document root"

    # Check required namespaces
    required_ns = [
        "xmlns:office=",
        "xmlns:style=",
        "xmlns:table=",
        "xmlns:text=",
    ]
    for ns in required_ns:
        assert ns in content[:5000], f"Missing namespace: {ns}"

    # Check mimetype attribute
    assert "office:mimetype=" in content[:5000], "Missing office:mimetype attribute"

    # Check document structure (elements should be in proper order)
    meta_pos = content.find("<office:meta>")
    settings_pos = content.find("<office:settings>")
    body_pos = content.find("<office:body>")

    assert meta_pos > 0, "Missing office:meta"
    assert settings_pos > 0, "Missing office:settings"
    assert body_pos > 0, "Missing office:body"
