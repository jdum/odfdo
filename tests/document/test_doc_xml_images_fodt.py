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
"""Tests for images.fodt sample file conversions."""

import xml.etree.ElementTree as ElementTree
import zipfile
from io import BytesIO
from pathlib import Path

import pytest

from odfdo import Document


@pytest.fixture
def images_fodt(samples) -> Path:
    """Provide the path to images.fodt sample file."""
    return samples("images.fodt")


class TestImagesFodtLoad:
    """Test loading the images.fodt sample file."""

    def test_load_images_fodt(self, images_fodt):
        """images.fodt should load successfully."""
        doc = Document(images_fodt)
        assert doc.container.mimetype == "application/vnd.oasis.opendocument.text"

    def test_images_fodt_has_images(self, images_fodt):
        """images.fodt should contain image parts."""
        doc = Document(images_fodt)
        parts = doc.container.get_parts()
        image_parts = [p for p in parts if p.startswith("Pictures/")]
        assert len(image_parts) >= 2
        assert "Pictures/image1.png" in image_parts
        assert "Pictures/image2.png" in image_parts

    def test_images_fodt_image_content(self, images_fodt):
        """Image parts should have actual content."""
        doc = Document(images_fodt)
        image1 = doc.container.get_part("Pictures/image1.png")
        image2 = doc.container.get_part("Pictures/image2.png")
        assert image1 is not None
        assert image2 is not None
        assert len(image1) > 0
        assert len(image2) > 0
        # Check PNG magic bytes
        assert image1[:8] == b"\x89PNG\r\n\x1a\n"
        assert image2[:8] == b"\x89PNG\r\n\x1a\n"

    def test_images_fodt_content_preserved(self, images_fodt):
        """Text content should be preserved."""
        doc = Document(images_fodt)
        paragraphs = list(doc.body.paragraphs)
        assert len(paragraphs) >= 30
        # Check first paragraph
        assert paragraphs[0].text == "aaa"


class TestImagesFodtToOdt:
    """Test converting images.fodt to .odt format."""

    def test_convert_to_odt(self, images_fodt, tmp_path):
        """Convert images.fodt to regular ODF (.odt)."""
        doc = Document(images_fodt)
        odt_path = tmp_path / "converted.odt"
        doc.save(odt_path)
        assert odt_path.exists()

    def test_odt_has_all_parts(self, images_fodt, tmp_path):
        """Converted ODT should have all required parts."""
        doc = Document(images_fodt)
        odt_path = tmp_path / "converted.odt"
        doc.save(odt_path)

        with zipfile.ZipFile(odt_path, "r") as zf:
            names = zf.namelist()
            assert "mimetype" in names
            assert "content.xml" in names
            assert "styles.xml" in names
            assert "meta.xml" in names
            assert "settings.xml" in names
            assert "META-INF/manifest.xml" in names

    def test_odt_has_images(self, images_fodt, tmp_path):
        """Converted ODT should preserve images."""
        doc = Document(images_fodt)
        odt_path = tmp_path / "converted.odt"
        doc.save(odt_path)

        with zipfile.ZipFile(odt_path, "r") as zf:
            names = zf.namelist()
            image_names = [n for n in names if n.startswith("Pictures/")]
            assert len(image_names) >= 2

    def test_odt_image_content_preserved(self, images_fodt, tmp_path):
        """Image content should be preserved in ODT."""
        doc = Document(images_fodt)
        original_image1 = doc.container.get_part("Pictures/image1.png")

        odt_path = tmp_path / "converted.odt"
        doc.save(odt_path)

        with zipfile.ZipFile(odt_path, "r") as zf:
            odt_image1 = zf.read("Pictures/image1.png")

        assert original_image1 == odt_image1

    def test_odt_valid_xml(self, images_fodt, tmp_path):
        """XML parts in converted ODT should be valid."""

        doc = Document(images_fodt)
        odt_path = tmp_path / "converted.odt"
        doc.save(odt_path)

        with zipfile.ZipFile(odt_path, "r") as zf:
            for xml_file in ["content.xml", "styles.xml", "meta.xml", "settings.xml"]:
                content = zf.read(xml_file)
                try:
                    ElementTree.fromstring(content)  # noqa: S314
                except ElementTree.ParseError as e:
                    pytest.fail(f"{xml_file} is invalid XML: {e}")

    def test_odt_content_preserved(self, images_fodt, tmp_path):
        """Text content should be preserved after ODT conversion."""
        doc = Document(images_fodt)
        original_texts = [p.text for p in doc.body.paragraphs if p.text]

        odt_path = tmp_path / "converted.odt"
        doc.save(odt_path)

        reloaded = Document(odt_path)
        reloaded_texts = [p.text for p in reloaded.body.paragraphs if p.text]

        # Check some key texts are preserved
        assert "aaa" in reloaded_texts
        assert (
            len(reloaded_texts) >= len(original_texts) * 0.9
        )  # Allow for minor differences


class TestImagesFodtToFolder:
    """Test converting images.fodt to folder format."""

    def test_convert_to_folder(self, images_fodt, tmp_path):
        """Convert images.fodt to folder format."""
        doc = Document(images_fodt)
        folder_path = tmp_path / "converted.folder"
        doc.save(folder_path, packaging="folder")
        assert folder_path.exists()
        assert folder_path.is_dir()

    def test_folder_has_all_parts(self, images_fodt, tmp_path):
        """Converted folder should have all required parts."""
        doc = Document(images_fodt)
        folder_path = tmp_path / "converted.folder"
        doc.save(folder_path, packaging="folder")

        assert (folder_path / "mimetype").exists()
        assert (folder_path / "content.xml").exists()
        assert (folder_path / "styles.xml").exists()
        assert (folder_path / "meta.xml").exists()
        assert (folder_path / "settings.xml").exists()
        assert (folder_path / "META-INF" / "manifest.xml").exists()

    def test_folder_has_images(self, images_fodt, tmp_path):
        """Converted folder should preserve images."""
        doc = Document(images_fodt)
        folder_path = tmp_path / "converted.folder"
        doc.save(folder_path, packaging="folder")

        pictures_dir = folder_path / "Pictures"
        assert pictures_dir.exists()
        image_files = list(pictures_dir.glob("image*.png"))
        assert len(image_files) >= 2

    def test_folder_image_content_preserved(self, images_fodt, tmp_path):
        """Image content should be preserved in folder format."""
        doc = Document(images_fodt)
        original_image1 = doc.container.get_part("Pictures/image1.png")

        folder_path = tmp_path / "converted.folder"
        doc.save(folder_path, packaging="folder")

        folder_image1 = (folder_path / "Pictures" / "image1.png").read_bytes()
        assert original_image1 == folder_image1


class TestImagesFodtRoundTrip:
    """Test round-trip conversions starting from images.fodt."""

    def test_fodt_to_odt_to_fodt(self, images_fodt, tmp_path):
        """Round-trip: fodt -> odt -> fodt."""
        # fodt -> odt
        doc1 = Document(images_fodt)
        odt_path = tmp_path / "intermediate.odt"
        doc1.save(odt_path)

        # odt -> fodt
        doc2 = Document(odt_path)
        final_fodt = tmp_path / "final.fodt"
        doc2.save(final_fodt, packaging="xml")

        assert final_fodt.exists()

        # Verify final fodt
        final_doc = Document(final_fodt)
        assert final_doc.container.mimetype == "application/vnd.oasis.opendocument.text"
        image_parts = [
            p for p in final_doc.container.get_parts() if p.startswith("Pictures/")
        ]
        assert len(image_parts) >= 2

    def test_fodt_to_folder_to_odt(self, images_fodt, tmp_path):
        """Round-trip: fodt -> folder -> odt."""
        # fodt -> folder
        doc1 = Document(images_fodt)
        folder_path = tmp_path / "intermediate.folder"
        doc1.save(folder_path, packaging="folder")

        # folder -> odt
        doc2 = Document(folder_path)
        final_odt = tmp_path / "final.odt"
        doc2.save(final_odt)

        assert final_odt.exists()

        # Verify final odt
        final_doc = Document(final_odt)
        assert final_doc.container.mimetype == "application/vnd.oasis.opendocument.text"

        with zipfile.ZipFile(final_odt, "r") as zf:
            names = zf.namelist()
            image_names = [n for n in names if n.startswith("Pictures/")]
            assert len(image_names) >= 2

    def test_content_preserved_after_round_trip(self, images_fodt, tmp_path):
        """Content should be preserved after round-trip conversion."""
        original_doc = Document(images_fodt)
        original_texts = [p.text for p in original_doc.body.paragraphs if p.text]

        # fodt -> odt -> fodt -> odt
        odt1 = tmp_path / "step1.odt"
        original_doc.save(odt1)

        doc2 = Document(odt1)
        fodt = tmp_path / "step2.fodt"
        doc2.save(fodt, packaging="xml")

        doc3 = Document(fodt)
        final_odt = tmp_path / "final.odt"
        doc3.save(final_odt)

        final_doc = Document(final_odt)
        final_texts = [p.text for p in final_doc.body.paragraphs if p.text]

        # Check key content is preserved
        assert "aaa" in final_texts
        assert len(final_texts) >= len(original_texts) * 0.9

    def test_images_preserved_after_round_trip(self, images_fodt, tmp_path):
        """Images should be preserved after round-trip conversion."""
        original_doc = Document(images_fodt)
        original_image1 = original_doc.container.get_part("Pictures/image1.png")

        # fodt -> odt -> fodt -> odt
        odt1 = tmp_path / "step1.odt"
        original_doc.save(odt1)

        doc2 = Document(odt1)
        fodt = tmp_path / "step2.fodt"
        doc2.save(fodt, packaging="xml")

        doc3 = Document(fodt)
        final_odt = tmp_path / "final.odt"
        doc3.save(final_odt)

        final_doc = Document(final_odt)
        final_image1 = final_doc.container.get_part("Pictures/image1.png")

        assert original_image1 == final_image1


class TestImagesFodtToVariousFormats:
    """Test converting images.fodt to various formats."""

    def test_save_to_different_flat_extensions(self, images_fodt, tmp_path):
        """Save to different flat ODF extensions."""
        doc = Document(images_fodt)

        # Save with .xml extension
        xml_path = tmp_path / "test.xml"
        doc.save(xml_path, packaging="xml")
        assert xml_path.exists()

        # Reload and verify
        reloaded = Document(xml_path)
        assert reloaded.container.mimetype == "application/vnd.oasis.opendocument.text"
        image_parts = [
            p for p in reloaded.container.get_parts() if p.startswith("Pictures/")
        ]
        assert len(image_parts) >= 2

    def test_save_bytesio(self, images_fodt):
        """Save to BytesIO and reload."""

        doc = Document(images_fodt)
        buffer = BytesIO()
        doc.save(buffer, packaging="xml")

        # Verify content was written
        assert buffer.tell() > 0

        # Reload from BytesIO
        buffer.seek(0)
        reloaded = Document(buffer)
        assert reloaded.container.mimetype == "application/vnd.oasis.opendocument.text"
