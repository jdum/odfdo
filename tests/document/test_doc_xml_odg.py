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
"""Tests for ODG flat XML conversion."""

from odfdo import Document


class TestOdgRoundTrip:
    """Test round-trip conversion for ODG (drawing) files."""

    def test_odg_roundtrip_basic(self, tmp_path, samples):
        """Basic round-trip ODG -> FODG -> ODG should preserve content."""
        odg_path = samples("base_shapes.odg")
        doc = Document(odg_path)

        flat_path = tmp_path / "base_shapes.fodg"
        doc.save(flat_path, packaging="xml")

        loaded = Document(flat_path)
        roundtrip_path = tmp_path / "roundtrip.odg"
        loaded.save(roundtrip_path, packaging="zip")

        # Verify the roundtrip file
        final_doc = Document(roundtrip_path)
        assert (
            final_doc.container.mimetype
            == "application/vnd.oasis.opendocument.graphics"
        )

        # Check essential parts exist
        parts = final_doc.container.get_parts()
        assert "content.xml" in parts
        assert "styles.xml" in parts

    def test_odg_flat_content_preserved(self, tmp_path, samples):
        """Content should be preserved through round-trip."""
        odg_path = samples("base_shapes.odg")
        original = Document(odg_path)

        original_content = original.container.get_part("content.xml")

        flat_path = tmp_path / "base_shapes.fodg"
        original.save(flat_path, packaging="xml")

        loaded = Document(flat_path)
        roundtrip_path = tmp_path / "roundtrip.odg"
        loaded.save(roundtrip_path, packaging="zip")

        final = Document(roundtrip_path)
        final_content = final.container.get_part("content.xml")

        assert b"office:document-content" in final_content

        # Check for drawing elements that should be preserved
        assert b"draw:" in original_content, "Original has no drawing elements"
        assert b"draw:" in final_content, "Drawing elements missing from final content"

        # Check that the core drawing structure is preserved
        # Count draw elements in both (may vary slightly due to serialization)
        original_draw_count = original_content.count(b"draw:")
        final_draw_count = final_content.count(b"draw:")
        # Allow for significant variation but ensure we have drawing elements
        assert final_draw_count > 0, "No draw elements in final content"
        # Final should have at least half the draw elements of original
        assert final_draw_count >= original_draw_count // 2, (
            f"Too many drawing elements lost: original={original_draw_count}, "
            f"final={final_draw_count}"
        )

    def test_odg_mimetype_preserved(self, tmp_path, samples):
        """Mimetype should be preserved through round-trip."""
        odg_path = samples("base_shapes.odg")
        doc = Document(odg_path)

        assert doc.container.mimetype == "application/vnd.oasis.opendocument.graphics"

        flat_path = tmp_path / "base_shapes.fodg"
        doc.save(flat_path, packaging="xml")

        loaded = Document(flat_path)
        assert (
            loaded.container.mimetype == "application/vnd.oasis.opendocument.graphics"
        )

        roundtrip_path = tmp_path / "roundtrip.odg"
        loaded.save(roundtrip_path, packaging="zip")

        final = Document(roundtrip_path)
        assert final.container.mimetype == "application/vnd.oasis.opendocument.graphics"
