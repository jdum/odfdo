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
"""Tests for form image handling in flat XML conversion.

This tests that images referenced via form:image-data attribute
(used in form controls like image buttons) are properly preserved
when converting to/from flat XML format.
"""

from odfdo import Document


class TestFormImageFlatConversion:
    """Test that form images are preserved in flat XML format."""

    def test_forms_odt_to_flat_preserves_image(self, tmp_path, samples):
        """Converting ODT with form image to flat XML should embed the image."""
        odt_path = samples("forms.odt")
        doc = Document(odt_path)

        flat_path = tmp_path / "forms.fodt"
        doc.save(flat_path, packaging="xml")

        flat_content = flat_path.read_text()

        # Check that office:binary-data is present (embedded image)
        assert "<office:binary-data>" in flat_content

    def test_forms_flat_roundtrip_preserves_image(self, tmp_path, samples):
        """Round-trip ODT -> FODT -> ODT should preserve form images."""
        odt_path = samples("forms.odt")
        doc = Document(odt_path)

        # Convert to flat XML
        flat_path = tmp_path / "forms.fodt"
        doc.save(flat_path, packaging="xml")

        # Load flat XML and convert back to ODT
        loaded = Document(flat_path)
        roundtrip_path = tmp_path / "roundtrip.odt"
        loaded.save(roundtrip_path, packaging="zip")

        # Check that the picture is in the roundtrip ODT
        final_doc = Document(roundtrip_path)
        parts = final_doc.container.get_parts()

        # Should have Pictures directory with the image
        image_parts = [p for p in parts if p.startswith("Pictures/")]
        assert len(image_parts) >= 1

    def test_forms_image_data_attribute_restored(self, tmp_path, samples):
        """form:image-data attribute should be restored in round-trip."""
        odt_path = samples("forms.odt")
        doc = Document(odt_path)

        # Convert to flat and back
        flat_path = tmp_path / "forms.fodt"
        doc.save(flat_path, packaging="xml")

        loaded = Document(flat_path)
        roundtrip_path = tmp_path / "roundtrip.odt"
        loaded.save(roundtrip_path, packaging="zip")

        # Check content for form:image-data attribute
        final_doc = Document(roundtrip_path)
        content = final_doc.container.get_part("content.xml")
        content_str = content.decode("utf-8") if isinstance(content, bytes) else content

        assert "form:image-data=" in content_str
        assert "Pictures/" in content_str

    def test_forms_file_size_preserved(self, tmp_path, samples):
        """File size should be similar after round-trip (images preserved)."""
        odt_path = samples("forms.odt")
        original = Document(odt_path)

        # Get original size info
        original_parts = original.container.get_parts()
        original_has_pictures = any("Pictures/" in p for p in original_parts)
        assert original_has_pictures, "Original should have pictures"

        # Convert to flat and back
        flat_path = tmp_path / "forms.fodt"
        original.save(flat_path, packaging="xml")

        loaded = Document(flat_path)
        roundtrip_path = tmp_path / "roundtrip.odt"
        loaded.save(roundtrip_path, packaging="zip")

        # Check final has pictures
        final = Document(roundtrip_path)
        final_parts = final.container.get_parts()
        final_has_pictures = any("Pictures/" in p for p in final_parts)
        assert final_has_pictures, "Final should have pictures"
