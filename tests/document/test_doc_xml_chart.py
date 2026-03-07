# Copyright 2018-2026 Jérôme Dumonteil
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Authors (odfdo project): jerome.dumonteil@gmail.com
# The odfdo project is a derivative work of the lpod-python project:
# https://github.com/lpod/lpod-python
"""Tests for chart embedding in flat XML conversion.

This tests that embedded charts (in draw:object elements) are properly
embedded when converting ODF files to flat XML format.
"""

from odfdo import Document


class TestChartFlatConversion:
    """Test that embedded charts are preserved in flat XML format."""

    def test_chart_odt_to_flat_preserves_object(self, tmp_path, samples):
        """Converting ODT with chart to flat XML should embed the object."""
        odt_path = samples("chart.odt")
        doc = Document(odt_path)

        flat_path = tmp_path / "chart.fodt"
        doc.save(flat_path, packaging="xml")

        flat_content = flat_path.read_text()

        # Check that draw:object is present with embedded content
        assert "<draw:object>" in flat_content
        assert "<office:document" in flat_content
        # The embedded document should have the chart mimetype
        assert (
            'office:mimetype="application/vnd.oasis.opendocument.chart"' in flat_content
        )

    def test_chart_flat_has_all_namespaces(self, tmp_path, samples):
        """Embedded object should have all necessary namespace declarations."""
        odt_path = samples("chart.odt")
        doc = Document(odt_path)

        flat_path = tmp_path / "chart.fodt"
        doc.save(flat_path, packaging="xml")

        flat_content = flat_path.read_text()

        # Check that the embedded office:document has chart namespaces
        # These are essential for LibreOffice to render the chart
        assert "xmlns:chart=" in flat_content
        assert "xmlns:chartooo=" in flat_content
        assert "xmlns:table=" in flat_content

    def test_chart_flat_roundtrip_preserves_object(self, tmp_path, samples):
        """Round-trip ODT -> FODT -> ODT should preserve the embedded chart."""
        odt_path = samples("chart.odt")
        doc = Document(odt_path)

        flat_path = tmp_path / "chart.fodt"
        doc.save(flat_path, packaging="xml")

        loaded = Document(flat_path)
        roundtrip_path = tmp_path / "roundtrip.odt"
        loaded.save(roundtrip_path, packaging="zip")

        # Check that the roundtrip ODT has the Object 1 parts
        final_doc = Document(roundtrip_path)
        parts = final_doc.container.get_parts()

        # Should have Object 1 directory with chart content
        assert "Object 1/content.xml" in parts
        assert "Object 1/meta.xml" in parts

    def test_chart_flat_has_proper_document_structure(self, tmp_path, samples):
        """Embedded object should have proper office:document structure."""
        odt_path = samples("chart.odt")
        doc = Document(odt_path)

        flat_path = tmp_path / "chart.fodt"
        doc.save(flat_path, packaging="xml")

        flat_content = flat_path.read_text()

        # Check for proper office:document structure
        assert "<office:meta>" in flat_content
        assert "<office:body>" in flat_content
        assert "<office:chart>" in flat_content
        assert "<chart:chart" in flat_content

    def test_chart_object_replacement_image_embedded(self, tmp_path, samples):
        """Object replacement image should be embedded as binary data."""
        odt_path = samples("chart.odt")
        doc = Document(odt_path)

        flat_path = tmp_path / "chart.fodt"
        doc.save(flat_path, packaging="xml")

        flat_content = flat_path.read_text()

        # Check that there's a draw:image after draw:object with binary data
        # This is the preview image for the chart
        assert "<draw:image>" in flat_content
        assert "<office:binary-data>" in flat_content
