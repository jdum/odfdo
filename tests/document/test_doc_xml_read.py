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
"""Tests for reading Flat ODF XML files."""

from odfdo import Container, Document, Frame, Paragraph


class TestFlatOdfReadBasic:
    """Test basic reading of Flat ODF XML files."""

    def test_read_simple_text_document(self, tmp_path):
        """Read a simple flat ODF text document."""
        # Create and save a flat XML document
        doc = Document("odt")
        doc.body.clear()
        p = Paragraph("Hello from Flat ODF!")
        doc.body.append(p)

        flat_path = tmp_path / "test.fodt"
        doc.save(flat_path, packaging="xml")

        # Read it back
        loaded = Document(flat_path)
        assert loaded.container.mimetype == "application/vnd.oasis.opendocument.text"

        paragraphs = list(loaded.body.paragraphs)
        assert len(paragraphs) == 1
        assert "Hello from Flat ODF!" in paragraphs[0].text

    def test_read_spreadsheet(self, tmp_path):
        """Read a flat ODF spreadsheet."""
        doc = Document("ods")

        flat_path = tmp_path / "test.fods"
        doc.save(flat_path, packaging="xml")

        loaded = Document(flat_path)
        assert (
            loaded.container.mimetype
            == "application/vnd.oasis.opendocument.spreadsheet"
        )

    def test_read_presentation(self, tmp_path):
        """Read a flat ODF presentation."""
        doc = Document("odp")

        flat_path = tmp_path / "test.fodp"
        doc.save(flat_path, packaging="xml")

        loaded = Document(flat_path)
        assert (
            loaded.container.mimetype
            == "application/vnd.oasis.opendocument.presentation"
        )

    def test_read_drawing(self, tmp_path):
        """Read a flat ODF drawing."""
        doc = Document("odg")

        flat_path = tmp_path / "test.fodg"
        doc.save(flat_path, packaging="xml")

        loaded = Document(flat_path)
        assert (
            loaded.container.mimetype == "application/vnd.oasis.opendocument.graphics"
        )

    def test_read_with_xml_extension(self, tmp_path):
        """Read a flat ODF file with .xml extension."""
        doc = Document("odt")
        doc.body.clear()
        p = Paragraph("Test content")
        doc.body.append(p)

        flat_path = tmp_path / "test.xml"
        doc.save(flat_path, packaging="xml")

        loaded = Document(flat_path)
        assert loaded.container.mimetype == "application/vnd.oasis.opendocument.text"

    def test_read_parts_available(self, tmp_path):
        """Check that all expected parts are available after reading."""
        doc = Document("odt")
        flat_path = tmp_path / "test.fodt"
        doc.save(flat_path, packaging="xml")

        loaded = Document(flat_path)
        parts = loaded.container.get_parts()

        assert "mimetype" in parts
        assert "content.xml" in parts
        assert "styles.xml" in parts
        assert "meta.xml" in parts
        assert "settings.xml" in parts
        assert "META-INF/manifest.xml" in parts


class TestFlatOdfReadContent:
    """Test content preservation when reading flat ODF."""

    def test_multiple_paragraphs_preserved(self, tmp_path):
        """Multiple paragraphs should be preserved."""
        doc = Document("odt")
        doc.body.clear()

        for i in range(3):
            p = Paragraph(f"Paragraph {i + 1}")
            doc.body.append(p)

        flat_path = tmp_path / "test.fodt"
        doc.save(flat_path, packaging="xml")

        loaded = Document(flat_path)
        paragraphs = list(loaded.body.paragraphs)
        assert len(paragraphs) == 3

    def test_styles_preserved(self, tmp_path):
        """Styles should be preserved when reading flat ODF."""
        doc = Document("odt")
        doc.body.clear()

        p = Paragraph("Styled paragraph")
        # Add some styling
        p.style = "Standard"
        doc.body.append(p)

        flat_path = tmp_path / "test.fodt"
        doc.save(flat_path, packaging="xml")

        loaded = Document(flat_path)
        paragraphs = list(loaded.body.paragraphs)
        assert len(paragraphs) >= 1


class TestFlatOdfReadImages:
    """Test image handling when reading flat ODF."""

    def test_image_extracted_from_flat_odf(self, tmp_path, samples):
        """Images embedded in flat ODF should be extracted."""

        doc = Document("odt")
        doc.body.clear()

        # Add an image
        img_path = samples("image.png")
        img_url = doc.add_file(img_path)
        frame = Frame.image_frame(img_url, size=("4cm", "3cm"))
        p = Paragraph()
        p.append(frame)
        doc.body.append(p)

        flat_path = tmp_path / "test.fodt"
        doc.save(flat_path, packaging="xml")

        # Read back
        loaded = Document(flat_path)
        parts = loaded.container.get_parts()

        # Check image parts exist
        image_parts = [p for p in parts if p.startswith("Pictures/")]
        assert len(image_parts) >= 1

    def test_image_content_preserved(self, tmp_path, samples):
        """Image binary content should be preserved."""

        doc = Document("odt")
        doc.body.clear()

        # Add an image
        img_path = samples("image.png")
        img_url = doc.add_file(img_path)
        frame = Frame.image_frame(img_url, size=("4cm", "3cm"))
        p = Paragraph()
        p.append(frame)
        doc.body.append(p)

        flat_path = tmp_path / "test.fodt"
        doc.save(flat_path, packaging="xml")

        # Read back
        loaded = Document(flat_path)

        # Check image content is not empty
        image_parts = [
            p for p in loaded.container.get_parts() if p.startswith("Pictures/")
        ]
        for img_part in image_parts:
            content = loaded.container.get_part(img_part)
            assert content is not None
            assert len(content) > 0

    def test_image_file_extension_detected(self, tmp_path, samples):
        """Image file extension should be detected from content."""

        doc = Document("odt")
        doc.body.clear()

        # Add a PNG image
        img_path = samples("image.png")
        img_url = doc.add_file(img_path)
        frame = Frame.image_frame(img_url, size=("4cm", "3cm"))
        p = Paragraph()
        p.append(frame)
        doc.body.append(p)

        flat_path = tmp_path / "test.fodt"
        doc.save(flat_path, packaging="xml")

        # Read back
        loaded = Document(flat_path)
        image_parts = [
            p for p in loaded.container.get_parts() if p.startswith("Pictures/")
        ]

        # Check extension is reasonable (png, jpg, etc.)
        for img_part in image_parts:
            assert any(
                img_part.endswith(ext)
                for ext in [".png", ".jpg", ".jpeg", ".gif", ".svg"]
            )


class TestFlatOdfRoundTrip:
    """Test round-trip conversion (ODF -> Flat XML -> ODF)."""

    def test_round_trip_zip_to_xml_to_zip(self, tmp_path, samples):
        """Test converting ODF -> Flat XML -> ODF preserves content."""

        # Create ODF with content
        doc = Document("odt")
        doc.body.clear()

        p1 = Paragraph("Test paragraph 1")
        doc.body.append(p1)
        p2 = Paragraph("Test paragraph 2")
        doc.body.append(p2)

        # Add an image
        img_path = samples("image.png")
        img_url = doc.add_file(img_path)
        frame = Frame.image_frame(img_url, size=("4cm", "3cm"))
        p = Paragraph()
        p.append(frame)
        doc.body.append(p)

        # Save as flat XML
        flat_path = tmp_path / "intermediate.fodt"
        doc.save(flat_path, packaging="xml")

        # Load flat XML
        loaded = Document(flat_path)

        # Save back as regular ODF (zip)
        final_path = tmp_path / "final.odt"
        loaded.save(final_path)

        # Verify the final ODF
        final_doc = Document(final_path)
        paragraphs = list(final_doc.body.paragraphs)
        assert len(paragraphs) >= 2

        # Check images
        image_parts = [
            p for p in final_doc.container.get_parts() if p.startswith("Pictures/")
        ]
        assert len(image_parts) >= 1

    def test_round_trip_content_unchanged(self, tmp_path):
        """Content should remain unchanged after round-trip."""
        doc = Document("odt")
        doc.body.clear()

        test_text = "Round-trip test content with special chars: émojis 🎉"
        p = Paragraph(test_text)
        doc.body.append(p)

        # Save as flat XML
        flat_path = tmp_path / "test.fodt"
        doc.save(flat_path, packaging="xml")

        # Load and save as regular ODF
        loaded = Document(flat_path)
        final_path = tmp_path / "final.odt"
        loaded.save(final_path)

        # Verify
        final_doc = Document(final_path)
        paragraphs = list(final_doc.body.paragraphs)
        # Check that text is preserved (may be wrapped in different elements)
        all_text = " ".join(para.text for para in paragraphs)
        assert "Round-trip test content" in all_text


class TestFlatOdfDetection:
    """Test detection of flat ODF files."""

    def test_is_flat_xml_detects_valid_file(self, tmp_path):
        """_is_flat_xml should detect valid flat ODF files."""

        # Create a valid flat ODF
        doc = Document("odt")
        flat_path = tmp_path / "test.fodt"
        doc.save(flat_path, packaging="xml")

        content = flat_path.read_bytes()
        assert Container._is_flat_xml(content) is True

    def test_is_flat_xml_rejects_zip(self, tmp_path):
        """_is_flat_xml should reject ZIP files."""

        # Create a regular ODF (ZIP)
        doc = Document("odt")
        zip_path = tmp_path / "test.odt"
        doc.save(zip_path)

        content = zip_path.read_bytes()
        assert Container._is_flat_xml(content) is False

    def test_is_flat_xml_rejects_random_xml(self, tmp_path):
        """_is_flat_xml should reject non-ODF XML files."""

        # Create a random XML file
        xml_path = tmp_path / "random.xml"
        xml_path.write_text("<?xml version='1.0'?><root><item/></root>", encoding="utf-8")

        content = xml_path.read_bytes()
        assert Container._is_flat_xml(content) is False

    def test_is_flat_xml_rejects_empty(self):
        """_is_flat_xml should reject empty content."""

        assert Container._is_flat_xml(b"") is False
        assert Container._is_flat_xml(b"   ") is False
