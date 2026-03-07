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
"""Tests for flat XML conversion with missing parts.

This tests that flat ODF files with missing parts (like settings.xml,
styles.xml) can be converted to standard ODF format.
"""

from odfdo import Document


class TestFlatXmlWithMissingParts:
    """Test flat XML conversion when some parts are missing."""

    def test_flat_xml_with_document_meta_wrapper(self, tmp_path, samples):
        """Flat XML with office:document-meta wrapper should be handled."""
        xml_path = samples("example.xml")
        doc = Document(xml_path)

        # Should have meta.xml extracted
        parts = doc.container.get_parts()
        assert "meta.xml" in parts

    def test_flat_xml_to_odt_with_missing_parts(self, tmp_path, samples):
        """Converting flat XML with missing parts to ODT should work."""
        xml_path = samples("example.xml")
        doc = Document(xml_path)

        odt_path = tmp_path / "example.odt"
        doc.save(odt_path, packaging="zip")

        loaded = Document(odt_path)
        assert loaded.container.mimetype == "application/vnd.oasis.opendocument.text"

    def test_flat_xml_missing_settings_styles(self, tmp_path, samples):
        """Flat XML without settings.xml and styles.xml should convert."""
        xml_path = samples("example.xml")
        doc = Document(xml_path)

        # Check that settings and styles are not in parts
        parts = doc.container.get_parts()
        assert "settings.xml" not in parts
        assert "styles.xml" not in parts

        # Should still be able to save
        odt_path = tmp_path / "example.odt"
        doc.save(odt_path, packaging="zip")

        # Verify the saved ODT
        loaded = Document(odt_path)
        saved_parts = loaded.container.get_parts()
        assert "content.xml" in saved_parts
        assert "meta.xml" in saved_parts
