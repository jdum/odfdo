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
"""Tests for Flat ODF automatic extension detection."""

import xml.etree.ElementTree as ElementTree
from io import BytesIO

import pytest

from odfdo import Document, Paragraph


class TestFlatOdfAutoExtension:
    """Test automatic Flat ODF extension detection."""

    def test_text_no_extension(self, tmp_path):
        """Text document without extension should get .fodt"""
        doc = Document("odt")
        target = tmp_path / "testfile"
        doc.save(target, packaging="xml")
        assert (tmp_path / "testfile.fodt").exists()

    def test_spreadsheet_no_extension(self, tmp_path):
        """Spreadsheet document without extension should get .fods"""
        doc = Document("ods")
        target = tmp_path / "testfile"
        doc.save(target, packaging="xml")
        assert (tmp_path / "testfile.fods").exists()

    def test_presentation_no_extension(self, tmp_path):
        """Presentation document without extension should get .fodp"""
        doc = Document("odp")
        target = tmp_path / "testfile"
        doc.save(target, packaging="xml")
        assert (tmp_path / "testfile.fodp").exists()

    def test_drawing_no_extension(self, tmp_path):
        """Drawing document without extension should get .fodg"""
        doc = Document("odg")
        target = tmp_path / "testfile"
        doc.save(target, packaging="xml")
        assert (tmp_path / "testfile.fodg").exists()

    def test_explicit_fodt_preserved(self, tmp_path):
        """Explicit .fodt extension should be preserved"""
        doc = Document("odt")
        target = tmp_path / "testfile.fodt"
        doc.save(target, packaging="xml")
        assert (tmp_path / "testfile.fodt").exists()
        assert not (tmp_path / "testfile.fodt.xml").exists()

    def test_explicit_fods_preserved(self, tmp_path):
        """Explicit .fods extension should be preserved"""
        doc = Document("ods")
        target = tmp_path / "testfile.fods"
        doc.save(target, packaging="xml")
        assert (tmp_path / "testfile.fods").exists()

    def test_explicit_xml_preserved(self, tmp_path):
        """Explicit .xml extension should be preserved"""
        doc = Document("odt")
        target = tmp_path / "testfile.xml"
        doc.save(target, packaging="xml")
        assert (tmp_path / "testfile.xml").exists()

    def test_wrong_extension_replaced(self, tmp_path):
        """Wrong extension should be replaced with correct flat extension"""
        doc = Document("odt")
        target = tmp_path / "testfile.txt"
        doc.save(target, packaging="xml")
        assert (tmp_path / "testfile.fodt").exists()
        assert not (tmp_path / "testfile.txt").exists()

    def test_doc_extension_replaced(self, tmp_path):
        """.doc extension should be replaced with correct flat extension"""
        doc = Document("odt")
        target = tmp_path / "testfile.doc"
        doc.save(target, packaging="xml")
        assert (tmp_path / "testfile.fodt").exists()
        assert not (tmp_path / "testfile.doc").exists()

    def test_uppercase_extension_preserved(self, tmp_path):
        """Uppercase flat extension should be preserved"""
        doc = Document("odt")
        target = tmp_path / "testfile.FODT"
        doc.save(target, packaging="xml")
        assert (tmp_path / "testfile.FODT").exists()

    def test_mixed_case_extension_preserved(self, tmp_path):
        """Mixed case flat extension should be preserved"""
        doc = Document("ods")
        target = tmp_path / "testfile.FoDs"
        doc.save(target, packaging="xml")
        assert (tmp_path / "testfile.FoDs").exists()

    def test_bytesio_still_works(self):
        """BytesIO should work without extension handling"""
        doc = Document("odt")
        buffer = BytesIO()
        doc.save(buffer, packaging="xml")
        assert buffer.tell() > 0
        content = buffer.getvalue().decode("utf-8")
        assert "office:document" in content

    def test_unknown_mimetype_fallback_to_xml(self, tmp_path):
        """Unknown mimetype should fall back to .xml"""
        doc = Document("odt")
        doc.container.mimetype = "application/x-unknown-type"
        target = tmp_path / "testfile"
        doc.save(target, packaging="xml")
        assert (tmp_path / "testfile.xml").exists()

    def test_string_path_no_extension(self, tmp_path):
        """String path without extension should work"""
        doc = Document("odt")
        target = str(tmp_path / "stringtest")
        doc.save(target, packaging="xml")
        assert (tmp_path / "stringtest.fodt").exists()

    def test_pathlib_path_no_extension(self, tmp_path):
        """Pathlib Path without extension should work"""
        doc = Document("odt")
        target = tmp_path / "pathlibtest"
        doc.save(target, packaging="xml")
        assert (tmp_path / "pathlibtest.fodt").exists()


class TestFlatOdfContentValidation:
    """Test that saved flat ODF files are valid."""

    def test_flat_odf_is_valid_xml(self, tmp_path):
        """Saved flat ODF should be valid XML"""
        doc = Document("odt")
        target = tmp_path / "validtest.fodt"
        doc.save(target, packaging="xml")

        tree = ElementTree.parse(target)  # noqa: S314
        root = tree.getroot()

        assert "document" in root.tag
        ns_office = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}"
        assert root.tag == f"{ns_office}document"

        assert (
            root.get(f"{ns_office}mimetype")
            == "application/vnd.oasis.opendocument.text"
        )
        assert root.get(f"{ns_office}version") is not None

    def test_flat_odf_has_body(self, tmp_path):
        """Saved flat ODF should have office:body element"""
        doc = Document("odt")
        doc.body.clear()
        doc.body.append(Paragraph("Test content"))

        target = tmp_path / "bodytest.fodt"
        doc.save(target, packaging="xml")

        content = target.read_text(encoding="utf-8")
        assert "<office:body>" in content
        assert "<office:text>" in content


class TestFlatOdfMimetypeMapping:
    """Test mimetype to flat extension mapping."""

    @pytest.mark.parametrize(
        "template,expected_ext,mimetype",
        [
            ("odt", ".fodt", "application/vnd.oasis.opendocument.text"),
            ("ods", ".fods", "application/vnd.oasis.opendocument.spreadsheet"),
            ("odp", ".fodp", "application/vnd.oasis.opendocument.presentation"),
            ("odg", ".fodg", "application/vnd.oasis.opendocument.graphics"),
        ],
    )
    def test_mimetype_mapping(self, tmp_path, template, expected_ext, mimetype):
        """Test that each document type gets correct extension"""
        doc = Document(template)
        assert doc.container.mimetype == mimetype

        target = tmp_path / "typetest"
        doc.save(target, packaging="xml")
        assert (tmp_path / f"typetest{expected_ext}").exists()
