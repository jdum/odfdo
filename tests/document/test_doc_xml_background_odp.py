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
"""Tests for background image handling in ODP flat XML conversion.

This tests the fix background images in ODP files.
"""

from odfdo import Document


class TestOdpBackgroundImagesFlat:
    """Test that background images in ODP are preserved in flat XML format."""

    def test_odp_to_flat_includes_background_images(self, tmp_path, samples):
        """Converting ODP with backgrounds to flat XML should embed all images."""
        odp_path = samples("background.odp")
        doc = Document(odp_path)

        flat_path = tmp_path / "background.fodp"
        doc.save(flat_path, packaging="xml")

        flat_content = flat_path.read_text()

        # Count binary data sections - should have 2 (1 fill-image + 1 regular image)
        # The original ODP has 2 images; LibreOffice may duplicate them but we preserve unique ones
        binary_data_count = flat_content.count("<office:binary-data>")
        assert binary_data_count == 2, (
            f"Expected 2 binary data sections, found {binary_data_count}"
        )

    def test_odp_to_flat_preserves_fill_images(self, tmp_path, samples):
        """draw:fill-image elements should be converted to binary data."""
        odp_path = samples("background.odp")
        doc = Document(odp_path)

        flat_path = tmp_path / "background.fodp"
        doc.save(flat_path, packaging="xml")

        flat_content = flat_path.read_text()

        # Check that fill-image elements with binary data exist
        assert "<draw:fill-image" in flat_content
        # After conversion, xlink:href should be replaced with binary-data
        assert "<office:binary-data>" in flat_content

    def test_odp_flat_roundtrip_preserves_images(self, tmp_path, samples):
        """Round-trip ODP -> FODP -> ODP should preserve all images."""
        odp_path = samples("background.odp")
        doc = Document(odp_path)

        flat_path = tmp_path / "background.fodp"
        doc.save(flat_path, packaging="xml")

        loaded = Document(flat_path)
        roundtrip_path = tmp_path / "roundtrip.odp"
        loaded.save(roundtrip_path, packaging="zip")

        final_doc = Document(roundtrip_path)
        parts = final_doc.container.get_parts()

        # Should have Pictures directory with 2 images
        image_parts = [p for p in parts if p.startswith("Pictures/")]
        assert len(image_parts) >= 2, (
            f"Expected at least 2 images, found {len(image_parts)}"
        )

        # Verify image content is not empty
        for img_part in image_parts:
            content = final_doc.container.get_part(img_part)
            assert content is not None
            assert len(content) > 0

    def test_odp_flat_image_content_integrity(self, tmp_path, samples):
        """Image binary content should be preserved through conversion."""
        odp_path = samples("background.odp")
        original = Document(odp_path)

        original_parts = original.container.get_parts()
        original_images = {
            p: original.container.get_part(p)
            for p in original_parts
            if p.startswith("Pictures/")
        }

        flat_path = tmp_path / "background.fodp"
        original.save(flat_path, packaging="xml")

        loaded = Document(flat_path)
        roundtrip_path = tmp_path / "roundtrip.odp"
        loaded.save(roundtrip_path, packaging="zip")

        # Check roundtrip images
        final = Document(roundtrip_path)
        final_parts = final.container.get_parts()
        final_images = {
            p: final.container.get_part(p)
            for p in final_parts
            if p.startswith("Pictures/")
        }

        # Should have same number of images
        assert len(final_images) == len(original_images)

        # Image sizes should match (content preserved)
        for img_name in original_images:
            orig_size = len(original_images[img_name])
            found_match = False
            for final_name in final_images:
                if len(final_images[final_name]) == orig_size:
                    found_match = True
                    break
            assert found_match, f"Could not find matching image for {img_name}"

    def test_styles_xml_images_converted(self, tmp_path, samples):
        """Images in styles.xml (backgrounds) should be converted to binary data."""
        odp_path = samples("background.odp")
        doc = Document(odp_path)

        flat_path = tmp_path / "background.fodp"
        doc.save(flat_path, packaging="xml")

        flat_content = flat_path.read_text()

        # The flat file should have draw:image elements with binary-data children
        # in the styles section (not just content section)
        assert "<draw:image" in flat_content

        # Count image occurrences in styles section
        # The styles section should have converted images
        styles_start = flat_content.find("<office:styles>")
        styles_end = flat_content.find("</office:styles>")
        if styles_start != -1 and styles_end != -1:
            styles_section = flat_content[styles_start:styles_end]
            # After conversion, images in styles should have binary data
            assert "<office:binary-data>" in styles_section
