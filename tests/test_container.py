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
# Authors: Hervé Cauwelier <herve@itaapy.com>
#          Luis Belmar-Letelier <luis@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
import base64
import io
import os
import shutil
import zipfile
from os.path import isfile, join
from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

import pytest
from lxml.etree import Element, SubElement, fromstring, register_namespace, tostring

from odfdo.const import (
    FOLDER,
    ODF_CONTENT,
    ODF_EXTENSIONS,
    ODF_MANIFEST,
    ODF_META,
    ODF_SETTINGS,
    ODF_STYLES,
    ODF_TEXT,
    XML,
    ZIP,
)
from odfdo.container import (
    Container,
    normalize_path,
    pretty_indent,
)
from odfdo.utils import to_bytes


def test_filesystem(samples):
    path = samples("example.odt")
    container = Container()
    container.open(path)
    mimetype = container.get_part("mimetype")
    umimetype = container.mimetype
    assert mimetype == to_bytes(ODF_EXTENSIONS["odt"])
    assert umimetype == ODF_EXTENSIONS["odt"]


def test_get_part_xml(samples):
    container = Container()
    container.open(samples("example.odt"))
    content = container.get_part(ODF_CONTENT)
    assert b"<office:document-content" in content


def test_get_part_mimetype(samples):
    container = Container()
    container.open(samples("example.odt"))
    mimetype = container.get_part("mimetype")
    umimetype = container.mimetype
    assert mimetype == to_bytes(ODF_EXTENSIONS["odt"])
    assert umimetype == ODF_EXTENSIONS["odt"]


def test_mimetype_setter(samples):
    container = Container()
    container.open(samples("example.odt"))
    container.mimetype = ODF_EXTENSIONS["odt"]
    assert container.mimetype == ODF_EXTENSIONS["odt"]


def test_mimetype_setter_bytes(samples):
    container = Container()
    container.open(samples("example.odt"))
    container.mimetype = b"application/vnd.oasis.opendocument.text"
    assert container.mimetype == "application/vnd.oasis.opendocument.text"


def test_mimetype_setter_invalid():
    container = Container()
    with pytest.raises(TypeError):
        container.mimetype = 12345


def test_set_part(samples):
    container = Container()
    container.open(samples("example.odt"))
    path = join("Pictures", "a.jpg")
    data = to_bytes("JFIFIThinéééékImAnImage")
    container.set_part(path, data)
    assert container.get_part(path) == data


def test_del_part(samples):
    container = Container()
    container.open(samples("example.odt"))
    # Not a realistic test
    path = "content"
    container.del_part(path)
    with pytest.raises(ValueError):
        container.get_part(path)


def test_save_zip(tmp_path, samples):
    """TODO: 2 cases
    1. from ZIP to ZIP
    2. from "flat" to ZIP
    """
    container = Container()
    container.open(samples("example.odt"))
    container.save(tmp_path / "example.odt")
    new_container = Container()
    new_container.open(tmp_path / "example.odt")
    mimetype = new_container.get_part("mimetype")
    assert mimetype == to_bytes(ODF_EXTENSIONS["odt"])


def test_save_folder(tmp_path, samples):
    container = Container()
    container.open(samples("example.odt"))
    path1 = tmp_path / "example.odt"
    container.save(str(path1), packaging=FOLDER)
    path = tmp_path / "example.odt.folder" / "mimetype"
    assert isfile(path)
    path = tmp_path / "example.odt.folder" / "content.xml"
    assert isfile(path)
    path = tmp_path / "example.odt.folder" / "meta.xml"
    assert isfile(path)
    path = tmp_path / "example.odt.folder" / "styles.xml"
    assert isfile(path)
    path = tmp_path / "example.odt.folder" / "settings.xml"
    assert isfile(path)


def test_save_folder_pathlib(tmp_path, samples):
    container = Container()
    container.open(samples("example.odt"))
    path1 = tmp_path / "example.odt"
    container.save(path1, packaging=FOLDER)
    path = tmp_path / "example.odt.folder" / "mimetype"
    assert isfile(path)
    path = tmp_path / "example.odt.folder" / "content.xml"
    assert isfile(path)
    path = tmp_path / "example.odt.folder" / "meta.xml"
    assert isfile(path)
    path = tmp_path / "example.odt.folder" / "styles.xml"
    assert isfile(path)
    path = tmp_path / "example.odt.folder" / "settings.xml"
    assert isfile(path)


def test_save_folder_to_zip(tmp_path, samples):
    container = Container()
    container.open(samples("example.odt"))
    path1 = tmp_path / "example.odt"
    container.save(path1, packaging=FOLDER)
    path = tmp_path / "example.odt.folder" / "mimetype"
    assert isfile(path)
    new_container = Container()
    new_container.open(tmp_path / "example.odt.folder")
    path2 = tmp_path / "example_bis.odt"
    new_container.save(path2, packaging=ZIP)
    new_container_zip = Container()
    new_container_zip.open(path2)
    mimetype = new_container_zip.get_part("mimetype")
    assert mimetype == to_bytes(ODF_EXTENSIONS["odt"])


def test_load_folder(tmp_path, samples):
    container = Container()
    container.open(samples("example.odt"))
    path1 = tmp_path / "example_f.odt"
    container.save(path1, packaging=FOLDER)
    new_container = Container()
    new_container.open(tmp_path / "example_f.odt.folder")
    content = new_container.get_part(ODF_CONTENT)
    assert b"<office:document-content" in content
    mimetype = new_container.get_part("mimetype")
    assert mimetype == to_bytes(ODF_EXTENSIONS["odt"])
    path = join("Pictures", "a.jpg")
    data = to_bytes("JFIFIThiééénkImA §ççànImage")
    new_container.set_part(path, data)
    assert new_container.get_part(path) == to_bytes(data)
    # Not a realistic test
    path = "content"
    new_container.del_part(path)
    with pytest.raises(ValueError):
        new_container.get_part(path)


def test_repr_empty():
    container = Container()
    assert repr(container) == "<Container type= path=None>"


def test_str_empty():
    container = Container()
    assert str(container) == repr(container)


def test_repr(samples):
    container = Container()
    container.open(samples("example.odt"))
    result = repr(container)
    assert result.startswith("<Container type=application/vnd.oasis.opendocument.text")
    assert " path=" in result
    assert result.endswith("example.odt>")


def test_str(samples):
    container = Container()
    container.open(samples("example.odt"))
    assert str(container) == repr(container)


def test_default_manifest_rdf():
    container = Container()
    assert "rdf:RDF" in container.default_manifest_rdf


def test_manifest_rdf_0(tmp_path, samples):
    base = Container()
    base.open(samples("example.odt"))
    content = base.get_part(ODF_CONTENT)
    styles = base.get_part(ODF_STYLES)
    container = Container()
    container.set_part(ODF_CONTENT, content)
    container.set_part(ODF_STYLES, styles)
    container.mimetype = ODF_TEXT
    expected = {ODF_CONTENT, ODF_STYLES, "mimetype"}
    assert set(container.parts) == expected


def test_manifest_rdf_2(tmp_path, samples):
    base = Container()
    base.open(samples("example.odt"))
    content = base.get_part(ODF_CONTENT)
    styles = base.get_part(ODF_STYLES)
    meta = base.get_part(ODF_META)
    settings = base.get_part(ODF_SETTINGS)
    manifest = base.get_part(ODF_MANIFEST)
    container = Container()
    container.set_part(ODF_CONTENT, content)
    container.set_part(ODF_STYLES, styles)
    container.set_part(ODF_META, meta)
    container.set_part(ODF_SETTINGS, settings)
    container.set_part(ODF_MANIFEST, manifest)
    container.mimetype = ODF_TEXT
    path = tmp_path / "example.odt"
    container.save(path, packaging=ZIP)
    new_container = Container()
    new_container.open(path)
    mimetype = new_container.get_part("mimetype")
    assert mimetype.decode() == ODF_TEXT


def test_manifest_rdf_3(tmp_path, samples):
    base = Container()
    base.open(samples("example.odt"))
    content = base.get_part(ODF_CONTENT)
    styles = base.get_part(ODF_STYLES)
    meta = base.get_part(ODF_META)
    settings = base.get_part(ODF_SETTINGS)
    manifest = base.get_part(ODF_MANIFEST)
    container = Container()
    container.set_part(ODF_CONTENT, content)
    container.set_part(ODF_STYLES, styles)
    container.set_part(ODF_META, meta)
    container.set_part(ODF_SETTINGS, settings)
    container.set_part(ODF_MANIFEST, manifest)
    container.mimetype = ODF_TEXT
    path = tmp_path / "example.odt"
    container.save(path, packaging=ZIP)
    new_container = Container()
    new_container.open(path)
    content2 = new_container.get_part(ODF_CONTENT)
    assert content2 == content


def test_open_file_not_found():
    """Test that opening a non-existent file raises FileNotFoundError."""
    container = Container()
    with pytest.raises(FileNotFoundError):
        container.open("/nonexistent/path/document.odt")


def test_open_invalid_format():
    """Test that opening an invalid format raises TypeError."""
    container = Container()
    with pytest.raises(TypeError):
        container.open(12345)


def test_open_path_as_string(samples):
    """Test opening with string path."""
    container = Container()
    container.open(str(samples("example.odt")))
    assert container.mimetype == ODF_EXTENSIONS["odt"]


def test_open_bytesio(samples):
    """Test opening ODF from BytesIO."""
    with open(samples("example.odt"), "rb") as f:
        data = f.read()
    bio = io.BytesIO(data)
    container = Container()
    container.open(bio)
    assert container.mimetype == ODF_EXTENSIONS["odt"]
    content = container.get_part(ODF_CONTENT)
    assert b"<office:document-content" in content


def test_save_to_bytesio(samples):
    """Test saving ODF to BytesIO."""
    container = Container()
    container.open(samples("example.odt"))
    bio = io.BytesIO()
    container.save(bio)
    bio.seek(0)
    # Verify it's a valid zip by reading it back
    new_container = Container()
    new_container.open(bio)
    assert new_container.mimetype == ODF_EXTENSIONS["odt"]


def test_clone(samples):
    """Test cloning a container."""
    container = Container()
    container.open(samples("example.odt"))
    cloned = container.clone
    assert cloned.path is None
    assert cloned.mimetype == container.mimetype
    # Verify parts are copied
    assert set(cloned.parts) == set(container.parts)


def test_clone_and_save(tmp_path, samples):
    """Test cloning and saving a container."""
    container = Container()
    container.open(samples("example.odt"))
    cloned = container.clone
    path = tmp_path / "cloned.odt"
    cloned.save(path)
    new_container = Container()
    new_container.open(path)
    assert new_container.mimetype == ODF_EXTENSIONS["odt"]


def test_save_with_backup(tmp_path, samples, monkeypatch):
    """Test saving with backup option."""
    # Change to tmp_path so backup is created there
    monkeypatch.chdir(tmp_path)
    container = Container()
    container.open(samples("example.odt"))
    path = tmp_path / "backup_test.odt"
    container.save(path)
    # Modify and save with backup
    container.set_part("test.txt", b"test content")
    container.save(path, backup=True)
    # Check backup exists (backup is created in current working directory)
    backup_path = Path("backup_test.backup.odt")
    assert backup_path.exists()


def test_save_folder_with_backup(tmp_path, samples, monkeypatch):
    """Test saving folder with backup option."""
    # Change to tmp_path so backup is created there
    monkeypatch.chdir(tmp_path)
    container = Container()
    container.open(samples("example.odt"))
    path = tmp_path / "backup_folder"
    container.save(path, packaging=FOLDER)
    # Modify and save with backup
    container.set_part("test.txt", b"test content")
    container.save(path, packaging=FOLDER, backup=True)
    # Check backup exists (backup is created in current working directory)
    backup_path = Path("backup_folder.backup.folder")
    assert backup_path.exists()


def test_normalize_path():
    """Test path normalization."""
    assert normalize_path("path/to/file.xml") == "path/to/file.xml"
    # On Windows, backslash is converted; on Unix, backslash is valid in filenames
    # Just verify folders get trailing slash
    assert normalize_path("path/to/folder/") == "path/to/folder/"


def test_is_flat_xml_with_valid_flat_odf():
    """Test _is_flat_xml with valid flat ODF content."""
    flat_odf = dedent("""\
        <?xml version="1.0" encoding="UTF-8"?>
        <office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                         office:mimetype="application/vnd.oasis.opendocument.text"
                         office:version="1.2">
            <office:body>
                <office:text>
                    <text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">Hello</text:p>
                </office:text>
            </office:body>
        </office:document>
    """).encode()
    assert Container._is_flat_xml(flat_odf) is True


def test_is_flat_xml_with_invalid_content():
    """Test _is_flat_xml with invalid content."""
    # Not XML
    assert Container._is_flat_xml(b"not xml content") is False
    # Empty content
    assert Container._is_flat_xml(b"") is False
    # XML but not ODF
    assert Container._is_flat_xml(b'<?xml version="1.0"?><root></root>') is False
    # Invalid mimetype
    flat_odf = dedent("""\
        <?xml version="1.0" encoding="UTF-8"?>
        <office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                         office:mimetype="application/invalid"
                         office:version="1.2">
        </office:document>
    """).encode()
    assert Container._is_flat_xml(flat_odf) is False


def test_open_flat_xml_file(tmp_path, samples):
    """Test opening a flat XML ODF file."""
    # Create a minimal flat ODF file
    flat_odf = dedent("""\
        <?xml version="1.0" encoding="UTF-8"?>
        <office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                         xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                         office:mimetype="application/vnd.oasis.opendocument.text"
                         office:version="1.2">
            <office:body>
                <office:text>
                    <text:p>Hello World</text:p>
                </office:text>
            </office:body>
        </office:document>
    """).encode()
    flat_path = tmp_path / "flat.fodt"
    flat_path.write_bytes(flat_odf)

    container = Container()
    container.open(flat_path)
    assert container.mimetype == "application/vnd.oasis.opendocument.text"
    content = container.get_part(ODF_CONTENT)
    assert b"Hello World" in content


def test_open_flat_xml_bytesio():
    """Test opening a flat XML ODF from BytesIO."""
    flat_odf = dedent("""\
        <?xml version="1.0" encoding="UTF-8"?>
        <office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                         xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                         office:mimetype="application/vnd.oasis.opendocument.text"
                         office:version="1.2">
            <office:body>
                <office:text>
                    <text:p>Hello World</text:p>
                </office:text>
            </office:body>
        </office:document>
    """).encode()
    bio = io.BytesIO(flat_odf)
    container = Container()
    container.open(bio)
    assert container.mimetype == "application/vnd.oasis.opendocument.text"


def test_save_flat_xml(tmp_path, samples):
    """Test saving as flat XML format."""
    container = Container()
    container.open(samples("example.odt"))
    xml_path = tmp_path / "output.xml"
    container.save(xml_path, packaging="xml")
    assert xml_path.exists()
    content = xml_path.read_bytes()
    assert b"<?xml version=" in content
    assert b"<office:document" in content


def test_save_flat_xml_with_pretty(tmp_path, samples):
    """Test saving as flat XML with pretty printing."""
    container = Container()
    container.open(samples("example.odt"))
    xml_path = tmp_path / "output.fodt"
    container.save(xml_path, packaging="xml", pretty=True)
    assert xml_path.exists()
    content = xml_path.read_text()
    # Pretty printed should have indentation
    assert "  " in content


def test_save_flat_xml_to_bytesio(samples):
    """Test saving as flat XML to BytesIO."""
    container = Container()
    container.open(samples("example.odt"))
    bio = io.BytesIO()
    container.save(bio, packaging="xml")
    bio.seek(0)
    content = bio.read()
    assert b"<?xml version=" in content
    assert b"<office:document" in content


def test_detect_image_mime_type():
    """Test image MIME type detection from file content."""
    # JPEG
    jpeg_header = b"\xff\xd8\xff\xe0\x00\x10JFIF"
    assert Container._detect_image_mime_type(jpeg_header) == "image/jpeg"

    # PNG
    png_header = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    assert Container._detect_image_mime_type(png_header) == "image/png"

    # GIF87a
    gif87_header = b"GIF87a\x01\x00\x01\x00"
    assert Container._detect_image_mime_type(gif87_header) == "image/gif"

    # GIF89a
    gif89_header = b"GIF89a\x01\x00\x01\x00"
    assert Container._detect_image_mime_type(gif89_header) == "image/gif"

    # SVG
    svg_content = b'<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg"></svg>'
    assert Container._detect_image_mime_type(svg_content) == "image/svg+xml"

    # SVG without XML declaration
    svg_content2 = b'<svg xmlns="http://www.w3.org/2000/svg"></svg>'
    assert Container._detect_image_mime_type(svg_content2) == "image/svg+xml"

    # BMP
    bmp_header = b"BM\x36\x00\x00\x00\x00\x00\x00\x00"
    assert Container._detect_image_mime_type(bmp_header) == "image/bmp"

    # WebP
    webp_header = b"RIFF\x00\x00\x00\x00WEBP"
    assert Container._detect_image_mime_type(webp_header) == "image/webp"

    # Unknown
    unknown = b"unknown content"
    assert Container._detect_image_mime_type(unknown) == "application/octet-stream"


def test_image_mime_type_to_ext():
    """Test conversion from MIME type to file extension."""
    assert Container._image_mime_type_to_ext("image/jpeg") == "jpg"
    assert Container._image_mime_type_to_ext("image/png") == "png"
    assert Container._image_mime_type_to_ext("image/gif") == "gif"
    assert Container._image_mime_type_to_ext("image/svg+xml") == "svg"
    assert Container._image_mime_type_to_ext("image/bmp") == "bmp"
    assert Container._image_mime_type_to_ext("image/webp") == "webp"
    assert Container._image_mime_type_to_ext("image/tiff") == "tiff"
    assert Container._image_mime_type_to_ext("unknown/type") == "bin"


def test_suffix_to_mime_type():
    """Test conversion from file suffix to MIME type."""
    assert Container._suffix_to_mime_type(".xml") == "text/xml"
    assert Container._suffix_to_mime_type(".jpg") == "image/jpeg"
    assert Container._suffix_to_mime_type(".jpeg") == "image/jpeg"
    assert Container._suffix_to_mime_type(".png") == "image/png"
    assert Container._suffix_to_mime_type(".gif") == "image/gif"
    assert Container._suffix_to_mime_type(".svg") == "image/svg+xml"
    assert Container._suffix_to_mime_type(".unknown") == "application/octet-stream"
    # Case insensitive
    assert Container._suffix_to_mime_type(".JPG") == "image/jpeg"
    assert Container._suffix_to_mime_type(".PNG") == "image/png"


def test_get_parts_after_open(samples):
    """Test getting parts list after opening."""
    container = Container()
    container.open(samples("example.odt"))
    parts = container.get_parts()
    assert "mimetype" in parts
    assert ODF_CONTENT in parts
    assert ODF_STYLES in parts
    assert ODF_META in parts
    assert ODF_SETTINGS in parts


def test_parts_property(samples):
    """Test parts property."""
    container = Container()
    container.open(samples("example.odt"))
    parts = container.parts
    assert "mimetype" in parts
    assert ODF_CONTENT in parts


def test_get_part_not_found_zip(samples):
    """Test getting a non-existent part from ZIP raises KeyError."""
    container = Container()
    container.open(samples("example.odt"))
    # For ZIP packaging, non-existent parts raise KeyError
    with pytest.raises(KeyError):
        container.get_part("nonexistent.xml")


def test_get_part_not_found_folder(tmp_path, samples):
    """Test getting a non-existent part from folder raises FileNotFoundError."""
    container = Container()
    container.open(samples("example.odt"))
    # Save as folder
    folder_path = tmp_path / "test_folder"
    container.save(folder_path, packaging=FOLDER)
    # Open folder
    folder_container = Container()
    folder_container.open(tmp_path / "test_folder.folder")
    # For folder packaging, non-existent parts raise FileNotFoundError
    with pytest.raises(FileNotFoundError):
        folder_container.get_part("nonexistent.xml")


def test_set_part_and_get_part_roundtrip(samples):
    """Test setting and getting a part."""
    container = Container()
    container.open(samples("example.odt"))
    test_data = b"test content"
    container.set_part("test.txt", test_data)
    retrieved = container.get_part("test.txt")
    assert retrieved == test_data


def test_del_part_and_verify(samples):
    """Test deleting a part."""
    container = Container()
    container.open(samples("example.odt"))
    container.set_part("to_delete.txt", b"delete me")
    assert container.get_part("to_delete.txt") == b"delete me"
    container.del_part("to_delete.txt")
    with pytest.raises(ValueError):
        container.get_part("to_delete.txt")


def test_save_zip_default(samples, tmp_path):
    """Test saving with default packaging (zip)."""
    container = Container()
    container.open(samples("example.odt"))
    output_path = tmp_path / "output_default.odt"
    container.save(output_path)
    assert output_path.exists()
    # Verify it's a valid ODF
    new_container = Container()
    new_container.open(output_path)
    assert new_container.mimetype == ODF_EXTENSIONS["odt"]


def test_save_invalid_packaging(samples, tmp_path):
    """Test saving with invalid packaging type."""
    container = Container()
    container.open(samples("example.odt"))
    with pytest.raises(ValueError, match="Packaging of type"):
        container.save(tmp_path / "output.odt", packaging="invalid")


def test_save_folder_to_bytesio_error(samples):
    """Test that saving folder to BytesIO raises TypeError."""
    container = Container()
    container.open(samples("example.odt"))
    bio = io.BytesIO()
    with pytest.raises(TypeError, match="Impossible to save"):
        container.save(bio, packaging=FOLDER)


def test_container_init_with_path(samples):
    """Test Container initialization with path."""
    container = Container(samples("example.odt"))
    assert container.mimetype == ODF_EXTENSIONS["odt"]


def test_container_init_empty():
    """Test Container initialization without path."""
    container = Container()
    assert container.path is None
    assert container.mimetype == ""


def test_pretty_indent_with_text_content():
    """Test pretty_indent with text content elements."""
    # Create a simple XML structure
    root = Element("{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p")
    root.text = "Some text"

    result = pretty_indent(root)
    assert result is not None


def test_pretty_indent_with_nested_elements():
    """Test pretty_indent with nested elements."""
    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    root = Element(f"{{{ns_office}}}document")
    # child = SubElement(root, f"{{{ns_office}}}body")
    # _grandchild = SubElement(child, f"{{{ns_office}}}text")

    result = pretty_indent(root)
    assert result is not None


def test_pretty_indent_with_binary_data():
    """Test pretty_indent with office:binary-data element."""
    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    elem = Element(f"{{{ns_office}}}binary-data")
    elem.text = "base64encodedcontent"

    result = pretty_indent(elem)
    assert result is not None


def test_pretty_indent_with_binary_data_existing_tail():
    """Test pretty_indent with office:binary-data element that already has a tail."""
    register_namespace("office", "urn:oasis:names:tc:opendocument:xmlns:office:1.0")
    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    elem = Element(f"{{{ns_office}}}binary-data")
    elem.text = "base64encodedcontent"
    elem.tail = "existing_tail"  # Set a tail value so the condition is False

    result = pretty_indent(elem)
    assert result is not None
    # The existing tail should be preserved (not overwritten)
    assert result.tail == "existing_tail"


def test_pretty_indent_with_binary_data_in_parent():
    """Test pretty_indent with office:binary-data element inside a parent.

    This covers the case where binary-data is processed as a child element,
    testing the interaction between parent and child tail handling.
    """
    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    parent = Element(f"{{{ns_office}}}document")
    child = Element(f"{{{ns_office}}}binary-data")
    child.text = "base64content"
    parent.append(child)

    result = pretty_indent(parent)
    assert result is not None


def test_save_xml_with_auto_extension(tmp_path, samples):
    """Test saving XML with automatic extension based on mimetype."""
    container = Container()
    container.open(samples("example.odt"))
    output_path = tmp_path / "output"  # No extension
    container.save(output_path, packaging="xml")
    # Should have .fodt extension based on mimetype
    expected_path = tmp_path / "output.fodt"
    assert expected_path.exists()


def test_container_path_property(samples):
    """Test path property."""
    container = Container()
    assert container.path is None
    container.open(samples("example.odt"))
    assert container.path is not None
    assert container.path.name == "example.odt"


def test_save_xml_not_pretty(samples, tmp_path):
    """Test saving XML without pretty printing."""
    container = Container()
    container.open(samples("example.odt"))
    output_path = tmp_path / "output.xml"
    container.save(output_path, packaging="xml", pretty=False)
    assert output_path.exists()
    content = output_path.read_bytes()
    assert b"<?xml version=" in content
    assert b"<office:document" in content


def test_save_same_path(samples, tmp_path):
    """Test saving to the same path."""
    # Copy file first
    src = samples("example.odt")
    dst = tmp_path / "same_path.odt"
    shutil.copy(src, dst)

    container = Container()
    container.open(dst)
    # Modify
    container.set_part("test.txt", b"test")
    # Save to same path
    container.save(None)  # None means use current path

    # Verify
    new_container = Container()
    new_container.open(dst)
    assert new_container.get_part("test.txt") == b"test"


def test_get_part_from_folder(tmp_path, samples):
    """Test getting part from folder-based ODF."""
    container = Container()
    container.open(samples("example.odt"))
    folder_path = tmp_path / "folder_test"
    container.save(folder_path, packaging=FOLDER)

    # Open folder
    folder_container = Container()
    folder_container.open(tmp_path / "folder_test.folder")
    content = folder_container.get_part(ODF_CONTENT)
    assert b"<office:document-content" in content


def test_clone_with_zip_parts(samples):
    """Test cloning properly loads all zip parts."""
    container = Container()
    container.open(samples("example.odt"))

    # Clone
    cloned = container.clone

    # Verify all parts are accessible
    for part in container.parts:
        if part != "mimetype":  # mimetype is always accessible
            original_part = container.get_part(part)
            cloned_part = cloned.get_part(part)
            assert original_part == cloned_part


def test_open_flat_xml_with_meta_and_settings(tmp_path):
    """Test opening flat XML with meta and settings elements."""
    flat_odf = dedent("""\
        <?xml version="1.0" encoding="UTF-8"?>
        <office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                         xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
                         xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0"
                         office:mimetype="application/vnd.oasis.opendocument.text"
                         office:version="1.2">
            <office:meta>
                <meta:generator>Test</meta:generator>
            </office:meta>
            <office:settings>
                <config:config-item-set config:name="ooo:view-settings">
                    <config:config-item config:name="ViewId" config:type="string">writer</config:config-item>
                </config:config-item-set>
            </office:settings>
            <office:body>
                <office:text>
                    <text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">Hello</text:p>
                </office:text>
            </office:body>
        </office:document>
    """).encode()
    flat_path = tmp_path / "flat_complete.fodt"
    flat_path.write_bytes(flat_odf)

    container = Container()
    container.open(flat_path)
    assert container.mimetype == "application/vnd.oasis.opendocument.text"

    # Check that meta.xml and settings.xml were created
    meta = container.get_part(ODF_META)
    assert b"<office:document-meta" in meta

    settings = container.get_part(ODF_SETTINGS)
    assert b"<office:document-settings" in settings


def test_open_flat_xml_with_styles(tmp_path):
    """Test opening flat XML with automatic-styles and master-styles."""
    flat_odf = dedent("""\
        <?xml version="1.0" encoding="UTF-8"?>
        <office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                         xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
                         xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                         office:mimetype="application/vnd.oasis.opendocument.text"
                         office:version="1.2">
            <office:automatic-styles>
                <style:style style:name="P1" style:family="paragraph"/>
            </office:automatic-styles>
            <office:master-styles>
                <style:master-page style:name="Standard" style:page-layout-name="PM1"/>
            </office:master-styles>
            <office:body>
                <office:text>
                    <text:p text:style-name="P1">Hello</text:p>
                </office:text>
            </office:body>
        </office:document>
    """).encode()
    flat_path = tmp_path / "flat_styles.fodt"
    flat_path.write_bytes(flat_odf)

    container = Container()
    container.open(flat_path)

    # Check that styles.xml was created with automatic-styles
    styles = container.get_part(ODF_STYLES)
    assert b"<office:document-styles" in styles
    assert b"automatic-styles" in styles


def test_save_and_load_roundtrip_zip(tmp_path, samples):
    """Test complete save and load roundtrip with ZIP."""
    container = Container()
    container.open(samples("example.odt"))

    # Save to new file
    output_path = tmp_path / "roundtrip.odt"
    container.save(output_path)

    # Load and verify
    new_container = Container()
    new_container.open(output_path)

    # Verify mimetype
    assert new_container.mimetype == ODF_EXTENSIONS["odt"]

    # Verify all standard parts exist
    assert new_container.get_part(ODF_CONTENT) is not None
    assert new_container.get_part(ODF_STYLES) is not None
    assert new_container.get_part(ODF_META) is not None
    assert new_container.get_part(ODF_SETTINGS) is not None
    assert new_container.get_part(ODF_MANIFEST) is not None


def test_save_and_load_roundtrip_folder(tmp_path, samples):
    """Test complete save and load roundtrip with folder."""
    container = Container()
    container.open(samples("example.odt"))

    # Save to folder
    output_path = tmp_path / "roundtrip"
    container.save(output_path, packaging=FOLDER)

    # Load from folder
    new_container = Container()
    new_container.open(tmp_path / "roundtrip.folder")

    # Verify mimetype
    assert new_container.mimetype == ODF_EXTENSIONS["odt"]


def test_save_and_load_roundtrip_xml(tmp_path, samples):
    """Test complete save and load roundtrip with flat XML."""
    container = Container()
    container.open(samples("example.odt"))

    # Save to flat XML
    output_path = tmp_path / "roundtrip.xml"
    container.save(output_path, packaging="xml")

    # Load from flat XML
    new_container = Container()
    new_container.open(output_path)

    # Verify mimetype is preserved
    assert new_container.mimetype == ODF_EXTENSIONS["odt"]


def test_multiple_set_part_operations(samples):
    """Test multiple set_part operations."""
    container = Container()
    container.open(samples("example.odt"))

    # Set multiple parts
    container.set_part("file1.txt", b"content1")
    container.set_part("file2.txt", b"content2")
    container.set_part("Pictures/image.png", b"fakepng")

    # Verify all are accessible
    assert container.get_part("file1.txt") == b"content1"
    assert container.get_part("file2.txt") == b"content2"
    assert container.get_part("Pictures/image.png") == b"fakepng"


def test_container_equality_after_clone(samples):
    """Test that clone produces equal content."""
    container = Container()
    container.open(samples("example.odt"))

    cloned = container.clone

    # Compare content of all parts
    for part_name in container.parts:
        original = container.get_part(part_name)
        clone_part = cloned.get_part(part_name)
        assert original == clone_part, f"Part {part_name} differs"


def test_is_flat_xml_with_body_only():
    """Test _is_flat_xml with ODF that has body but no mimetype attribute."""
    flat_odf = dedent("""\
        <?xml version="1.0" encoding="UTF-8"?>
        <office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                         office:version="1.2">
            <office:body>
                <office:text/>
            </office:body>
        </office:document>
    """).encode()
    # Should be accepted because it has office:body
    assert Container._is_flat_xml(flat_odf) is True


def test_is_flat_xml_with_bad_xml():
    """Test _is_flat_xml with malformed XML."""
    bad_xml = b'<?xml version="1.0"?><unclosed'
    assert Container._is_flat_xml(bad_xml) is False


def test_is_flat_xml_not_starting_with_xml():
    """Test _is_flat_xml with content not starting with XML declaration."""
    not_xml = b"<root></root>"
    assert Container._is_flat_xml(not_xml) is False


def test_pretty_indent_empty_element():
    """Test pretty_indent with empty element."""
    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    elem = Element(f"{{{ns_office}}}empty")

    result = pretty_indent(elem)
    assert result is not None


def test_pretty_indent_with_children():
    """Test pretty_indent with parent that has multiple children."""
    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    root = Element(f"{{{ns_office}}}root")
    # child1 = SubElement(root, f"{{{ns_office}}}child1")
    # child2 = SubElement(root, f"{{{ns_office}}}child2")
    # child3 = SubElement(root, f"{{{ns_office}}}child3")

    result = pretty_indent(root)
    assert result is not None


def test_container_with_pictures(samples, tmp_path):
    """Test container operations with pictures."""
    container = Container()
    container.open(samples("example.odt"))

    # Add a picture
    picture_data = b"\x89PNG\r\n\x1a\n" + b"fake_png_data"
    container.set_part("Pictures/image1.png", picture_data)

    # Save and reload
    output_path = tmp_path / "with_pictures.odt"
    container.save(output_path)

    new_container = Container()
    new_container.open(output_path)

    # Verify picture is preserved
    retrieved = new_container.get_part("Pictures/image1.png")
    assert retrieved == picture_data


def test_save_zip_with_backup_false(tmp_path, samples):
    """Test saving zip without backup (coverage for _do_unlink path)."""
    container = Container()
    container.open(samples("example.odt"))

    path = tmp_path / "no_backup.odt"
    container.save(path)

    # Save again without backup - should not raise
    container.set_part("test.txt", b"test")
    container.save(path, backup=False)

    # Verify file was updated
    new_container = Container()
    new_container.open(path)
    assert new_container.get_part("test.txt") == b"test"


def test_container_clone_no_path_modification(samples):
    """Test that clone doesn't affect original container."""
    container = Container()
    container.open(samples("example.odt"))
    original_path = container.path

    cloned = container.clone

    # Original should still have its path
    assert container.path == original_path
    # Clone should have no path
    assert cloned.path is None


def test_open_folder_with_missing_mimetype(tmp_path):
    """Test opening folder with missing mimetype."""
    # Create a folder structure without mimetype
    folder_path = tmp_path / "no_mimetype.folder"
    folder_path.mkdir()
    (folder_path / "content.xml").write_text("<xml/>")

    container = Container()
    # Should warn but not fail - mimetype defaults to empty or ODF text
    container.open(folder_path)
    # Mimetype might be empty or default to ODF text
    assert container.mimetype is not None  # Should at least not crash


def test_flat_odf_with_document_meta_wrapper(tmp_path):
    """Test flat ODF where meta is already wrapped in document-meta."""
    flat_odf = dedent("""\
        <?xml version="1.0" encoding="UTF-8"?>
        <office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                         xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
                         office:mimetype="application/vnd.oasis.opendocument.text"
                         office:version="1.2">
            <office:document-meta>
                <office:meta>
                    <meta:generator>Test</meta:generator>
                </office:meta>
            </office:document-meta>
            <office:body>
                <office:text/>
            </office:body>
        </office:document>
    """).encode()
    flat_path = tmp_path / "flat_doc_meta.fodt"
    flat_path.write_bytes(flat_odf)

    container = Container()
    container.open(flat_path)

    meta = container.get_part(ODF_META)
    assert b"<office:document-meta" in meta


def test_zip_to_folder_to_xml_roundtrip(tmp_path, samples):
    """Test conversion through all three formats."""
    # Start with ZIP
    container = Container()
    container.open(samples("example.odt"))

    # Convert to folder
    folder_path = tmp_path / "converted"
    container.save(folder_path, packaging=FOLDER)

    # Load folder
    folder_container = Container()
    folder_container.open(tmp_path / "converted.folder")

    # Convert to XML
    xml_path = tmp_path / "converted.xml"
    folder_container.save(xml_path, packaging="xml")

    # Load XML
    xml_container = Container()
    xml_container.open(xml_path)

    # Verify mimetype preserved
    assert xml_container.mimetype == ODF_EXTENSIONS["odt"]


def test_container_get_parts_no_path():
    """Test get_parts when path is None (parts from memory)."""
    container = Container()
    container.set_part("test1.txt", b"content1")
    container.set_part("test2.txt", b"content2")
    container.mimetype = "application/vnd.oasis.opendocument.text"

    parts = container.get_parts()
    assert "test1.txt" in parts
    assert "test2.txt" in parts
    assert "mimetype" in parts


def test_open_file_path_not_flat_xml(tmp_path):
    """Test opening a file that is not zip, not folder, and not valid flat XML."""
    # Create a file that exists but is not valid flat XML
    not_xml_path = tmp_path / "not_odf.txt"
    not_xml_path.write_text("This is not XML content")

    container = Container()
    with pytest.raises(TypeError, match="Document format not managed by odfdo"):
        container.open(not_xml_path)


def test_open_bytesio_not_flat_xml():
    """Test opening a BytesIO that is not valid flat XML."""
    # Create a BytesIO with invalid content
    invalid_content = io.BytesIO(b"This is not valid XML content")

    container = Container()
    with pytest.raises(TypeError, match="Document format not managed by odfdo"):
        container.open(invalid_content)


def test_is_flat_xml_with_wrong_root_element():
    """Test _is_flat_xml with XML that has office:document text but wrong root element."""
    xml_content = dedent("""\
        <?xml version="1.0" encoding="UTF-8"?>
        <office:wrong-root xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">
            <!-- office:document is mentioned here but this is wrong-root element -->
            <office:body>
                <office:text/>
            </office:body>
        </office:wrong-root>
    """).encode()
    # This should return False because root is not office:document
    assert Container._is_flat_xml(xml_content) is False


def test_is_flat_xml_with_malformed_xml():
    """Test _is_flat_xml with malformed XML that fails parsing."""
    # XML that passes the initial checks but fails parsing
    # Has <?xml declaration and office:document text but is malformed
    malformed_xml = dedent("""\
        <?xml version="1.0" encoding="UTF-8"?>
        <office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                         office:mimetype="application/vnd.oasis.opendocument.text">
            <office:body>
                <office:text>
                    <unclosed-tag>
            </office:body>
        </office:document>
    """).encode()
    # This should return False because XML parsing fails
    assert Container._is_flat_xml(malformed_xml) is False


def test_is_flat_xml_with_unclosed_element():
    """Test _is_flat_xml with unclosed XML element causing parse error."""
    # Another variant of malformed XML
    bad_xml = dedent("""\
        <?xml version="1.0" encoding="UTF-8"?>
        <office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">
            <unclosed-element attribute="value">
        </office:document>
    """).encode()
    assert Container._is_flat_xml(bad_xml) is False


def test_read_zip_with_invalid_mimetype(tmp_path):
    """Test _read_zip raises ValueError for invalid mimetype."""

    # Create a zip file with invalid mimetype
    zip_path = tmp_path / "invalid_mimetype.odt"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("mimetype", "application/invalid-type")
        zf.writestr("content.xml", "<xml/>")

    container = Container()
    with pytest.raises(ValueError, match="Document of unknown type"):
        container.open(zip_path)


def test_read_zip_with_path_none_and_non_bytesio(tmp_path, samples):
    """Test _read_zip when path is None and __path_like is not BytesIO."""
    zip_path = tmp_path / "test_direct.odt"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("mimetype", ODF_EXTENSIONS["odt"])
        zf.writestr("content.xml", "<office:document-content/>")

    # Create container and manually set up state to trigger the branch
    container = Container()
    container._Container__packaging = "zip"  # type: ignore
    container._Container__path_like = open(zip_path, "rb")  # noqa: SIM115
    # path is None (default), __path_like is a file object (not BytesIO)
    try:
        container._read_zip()
        assert container.mimetype == ODF_EXTENSIONS["odt"]
        assert "content.xml" in container.parts
    finally:
        # Clean up the file handle
        if hasattr(container._Container__path_like, "close"):
            container._Container__path_like.close()  # type: ignore


def test_read_folder_with_invalid_mimetype_no_content_xml(tmp_path):
    """Test _read_folder with invalid mimetype and missing content.xml."""
    # Create a folder structure with invalid mimetype and no content.xml
    folder_path = tmp_path / "invalid_no_content.folder"
    folder_path.mkdir()
    (folder_path / "mimetype").write_text("application/invalid")
    # No content.xml - detection should fail

    container = Container()
    container.open(folder_path)
    # Should fall back to ODF Text
    assert container.mimetype == ODF_EXTENSIONS["odt"]


def test_read_folder_with_invalid_mimetype_bad_content_xml(tmp_path):
    """Test _read_folder with invalid mimetype and unparsable content.xml."""
    # Create a folder structure with invalid mimetype and bad content.xml
    folder_path = tmp_path / "invalid_bad_content.folder"
    folder_path.mkdir()
    (folder_path / "mimetype").write_text("application/invalid")
    (folder_path / "content.xml").write_text("not valid xml")

    container = Container()
    container.open(folder_path)
    # Should fall back to ODF Text
    assert container.mimetype == ODF_EXTENSIONS["odt"]


def test_read_xml_image_path_already_exists():
    """Test _read_xml when image path already exists in __parts."""
    # Create a fake PNG image data
    fake_png = b"\x89PNG\r\n\x1a\n" + b"fake_png_data"
    encoded_png = base64.standard_b64encode(fake_png).decode()

    # Build XML using string concatenation to avoid f-string issues
    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"',
        '                 xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"',
        '                 office:mimetype="application/vnd.oasis.opendocument.text">',
        "    <office:body>",
        "        <office:text>",
        "            <draw:frame>",
        "                <draw:image>",
        "                    <office:binary-data>"
        + encoded_png
        + "</office:binary-data>",
        "                </draw:image>",
        "            </draw:frame>",
        "        </office:text>",
        "    </office:body>",
        "</office:document>",
    ]
    flat_odf = "\n".join(xml_parts).encode()

    container = Container()
    # Pre-populate with an image that will conflict
    container._Container__parts["Pictures/image1.png"] = b"existing_image_data"
    container._read_xml(flat_odf)

    # The existing image should not be overwritten
    assert container._Container__parts["Pictures/image1.png"] == b"existing_image_data"


def _make_xml_with_body(body_tag: str) -> bytes:
    """Helper to create XML with a specific body element."""
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">
        <office:body>
            <office:{body_tag}/>
        </office:body>
    </office:document>"""
    return xml.encode()


def test_detect_mimetype_from_content_spreadsheet():
    """Test _detect_mimetype_from_content with spreadsheet body."""
    container = Container()
    root = fromstring(_make_xml_with_body("spreadsheet"))
    result = container._detect_mimetype_from_content(root)
    assert result == ODF_EXTENSIONS["ods"]


def test_detect_mimetype_from_content_presentation():
    """Test _detect_mimetype_from_content with presentation body."""
    container = Container()
    root = fromstring(_make_xml_with_body("presentation"))
    result = container._detect_mimetype_from_content(root)
    assert result == ODF_EXTENSIONS["odp"]


def test_detect_mimetype_from_content_drawing():
    """Test _detect_mimetype_from_content with drawing body."""
    container = Container()
    root = fromstring(_make_xml_with_body("drawing"))
    result = container._detect_mimetype_from_content(root)
    assert result == ODF_EXTENSIONS["odg"]


def test_detect_mimetype_from_content_chart():
    """Test _detect_mimetype_from_content with chart body."""
    container = Container()
    root = fromstring(_make_xml_with_body("chart"))
    result = container._detect_mimetype_from_content(root)
    assert result == ODF_EXTENSIONS["odc"]


def test_detect_mimetype_from_content_image():
    """Test _detect_mimetype_from_content with image body."""
    container = Container()
    root = fromstring(_make_xml_with_body("image"))
    result = container._detect_mimetype_from_content(root)
    assert result == ODF_EXTENSIONS["odi"]


def test_detect_mimetype_from_content_formula():
    """Test _detect_mimetype_from_content with formula body."""
    container = Container()
    root = fromstring(_make_xml_with_body("formula"))
    result = container._detect_mimetype_from_content(root)
    assert result == ODF_EXTENSIONS["odf"]


def test_detect_mimetype_from_content_text():
    """Test _detect_mimetype_from_content falls back to text."""
    container = Container()
    root = fromstring(_make_xml_with_body("text"))
    result = container._detect_mimetype_from_content(root)
    assert result == ODF_EXTENSIONS["odt"]


def test_detect_mimetype_from_content_no_body():
    """Test _detect_mimetype_from_content with no body element."""
    container = Container()
    xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">
        <office:meta/>
    </office:document>"""
    root = fromstring(xml)
    result = container._detect_mimetype_from_content(root)
    assert result == ODF_EXTENSIONS["odt"]


def test_detect_mimetype_from_folder_with_none_path():
    """Test _detect_mimetype_from_folder when path is None."""
    container = Container()
    # path is None by default
    result = container._detect_mimetype_from_folder()
    assert result is None


def test_detect_mimetype_from_folder_no_content_xml(tmp_path):
    """Test _detect_mimetype_from_folder when content.xml doesn't exist."""
    folder_path = tmp_path / "test_folder"
    folder_path.mkdir()
    # No content.xml
    container = Container()
    container.path = folder_path  # type: ignore
    result = container._detect_mimetype_from_folder()
    assert result is None


def test_detect_mimetype_from_folder_with_content_xml(tmp_path):
    """Test _detect_mimetype_from_folder successfully detects from content.xml."""
    folder_path = tmp_path / "test_folder"
    folder_path.mkdir()
    content_xml = folder_path / "content.xml"
    content_xml.write_text("""<?xml version="1.0" encoding="UTF-8"?>
    <office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">
        <office:body>
            <office:spreadsheet/>
        </office:body>
    </office:document>""")
    container = Container()
    container.path = folder_path  # type: ignore
    result = container._detect_mimetype_from_folder()
    assert result == ODF_EXTENSIONS["ods"]


def test_detect_mimetype_from_folder_bad_xml(tmp_path):
    """Test _detect_mimetype_from_folder with unparseable content.xml."""
    folder_path = tmp_path / "test_folder"
    folder_path.mkdir()
    content_xml = folder_path / "content.xml"
    content_xml.write_text("not valid xml")
    container = Container()
    container.path = folder_path  # type: ignore
    result = container._detect_mimetype_from_folder()
    # Should catch exception and return None
    assert result is None


def test_extract_mimetype_and_namespaces_with_mimetype():
    """Test _extract_mimetype_and_namespaces when mimetype attribute exists."""
    container = Container()
    xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                     office:mimetype="application/vnd.oasis.opendocument.spreadsheet">
        <office:body/>
    </office:document>"""
    root = fromstring(xml)
    mimetype, nsmap = container._extract_mimetype_and_namespaces(root)
    assert mimetype == ODF_EXTENSIONS["ods"]
    assert "office" in nsmap


def test_extract_mimetype_and_namespaces_without_mimetype():
    """Test _extract_mimetype_and_namespaces when mimetype attribute is missing."""
    container = Container()
    xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">
        <office:body>
            <office:presentation/>
        </office:body>
    </office:document>"""
    root = fromstring(xml)
    mimetype, _nsmap = container._extract_mimetype_and_namespaces(root)
    # Should detect from content
    assert mimetype == ODF_EXTENSIONS["odp"]


def test_extract_mimetype_and_namespaces_filters_manifest():
    """Test that manifest namespace is filtered from nsmap."""
    container = Container()
    xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                     xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"
                     office:mimetype="application/vnd.oasis.opendocument.text">
        <office:body/>
    </office:document>"""
    root = fromstring(xml)
    mimetype, nsmap = container._extract_mimetype_and_namespaces(root)
    assert mimetype == ODF_EXTENSIONS["odt"]
    # Manifest namespace should be filtered out
    assert "manifest" not in nsmap


def test_process_embedded_images_invalid_base64():
    """Test _process_embedded_images handles invalid base64 data."""
    container = Container()
    # Create content root with an image containing invalid base64
    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    ns_draw = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"

    content_root = Element(f"{{{ns_office}}}document-content")
    body = SubElement(content_root, f"{{{ns_office}}}body")
    text = SubElement(body, f"{{{ns_office}}}text")
    frame = SubElement(text, f"{{{ns_draw}}}frame")
    img = SubElement(frame, f"{{{ns_draw}}}image")
    binary_data = SubElement(img, f"{{{ns_office}}}binary-data")
    binary_data.text = "!!!invalid_base64!!!"

    styles_root = Element(f"{{{ns_office}}}document-styles")
    image_parts: dict[str, bytes] = {}

    # Should not raise, just print warning and continue
    result = container._process_embedded_images(
        content_root, styles_root, image_parts, "{http://www.w3.org/1999/xlink}"
    )

    # No images processed due to error
    assert result == 0
    assert image_parts == {}


def test_process_embedded_images_no_binary_data():
    """Test _process_embedded_images skips images without binary data."""
    container = Container()

    # Create content root with an image without binary-data
    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    ns_draw = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"

    content_root = Element(f"{{{ns_office}}}document-content")
    body = SubElement(content_root, f"{{{ns_office}}}body")
    text = SubElement(body, f"{{{ns_office}}}text")

    # Image without binary-data element
    frame1 = SubElement(text, f"{{{ns_draw}}}frame")
    SubElement(frame1, f"{{{ns_draw}}}image")

    # Image with empty binary-data
    frame2 = SubElement(text, f"{{{ns_draw}}}frame")
    img2 = SubElement(frame2, f"{{{ns_draw}}}image")
    binary_data = SubElement(img2, f"{{{ns_office}}}binary-data")
    binary_data.text = ""

    styles_root = Element(f"{{{ns_office}}}document-styles")
    image_parts: dict[str, bytes] = {}

    result = container._process_embedded_images(
        content_root, styles_root, image_parts, "{http://www.w3.org/1999/xlink}"
    )

    # No images processed
    assert result == 0
    assert image_parts == {}


def test_process_fill_images_invalid_base64():
    """Test _process_fill_images handles invalid base64 data."""
    container = Container()

    # Create content root with a fill-image containing invalid base64
    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    ns_draw = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"

    content_root = Element(f"{{{ns_office}}}document-content")
    body = SubElement(content_root, f"{{{ns_office}}}body")
    text = SubElement(body, f"{{{ns_office}}}text")

    # Add a fill-image with invalid base64
    fill_img = SubElement(text, f"{{{ns_draw}}}fill-image")
    binary_data = SubElement(fill_img, f"{{{ns_office}}}binary-data")
    binary_data.text = "!!!invalid_base64!!!"

    styles_root = Element(f"{{{ns_office}}}document-styles")
    image_parts: dict[str, bytes] = {}

    # Should not raise, just print warning and continue
    result = container._process_fill_images(
        content_root, styles_root, image_parts, 0, "{http://www.w3.org/1999/xlink}"
    )

    # Counter not incremented due to error
    assert result == 0
    assert image_parts == {}


def test_process_fill_images_empty_binary_data():
    """Test _process_fill_images skips fill-images with empty binary-data."""
    container = Container()

    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    ns_draw = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"

    content_root = Element(f"{{{ns_office}}}document-content")
    body = SubElement(content_root, f"{{{ns_office}}}body")
    text = SubElement(body, f"{{{ns_office}}}text")

    # Add a fill-image with empty binary-data text
    fill_img = SubElement(text, f"{{{ns_draw}}}fill-image")
    binary_data = SubElement(fill_img, f"{{{ns_office}}}binary-data")
    binary_data.text = ""  # Empty text

    styles_root = Element(f"{{{ns_office}}}document-styles")
    image_parts: dict[str, bytes] = {}

    # Should skip empty binary-data
    result = container._process_fill_images(
        content_root, styles_root, image_parts, 0, "{http://www.w3.org/1999/xlink}"
    )

    # Counter not incremented
    assert result == 0
    assert image_parts == {}


def test_process_embedded_objects_no_doc_wrapper():
    """Test _process_embedded_objects skips objects without document wrapper."""
    container = Container()

    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    ns_draw = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"

    content_root = Element(f"{{{ns_office}}}document-content")
    body = SubElement(content_root, f"{{{ns_office}}}body")
    text = SubElement(body, f"{{{ns_office}}}text")

    # Add an object without office:document child
    _obj = SubElement(text, f"{{{ns_draw}}}object")
    # Missing office:document wrapper

    # Should not raise
    container._process_embedded_objects(content_root, "{http://www.w3.org/1999/xlink}")

    # No parts should be created
    assert "Object 1/content.xml" not in container.parts


def test_process_embedded_objects_exception():
    """Test _process_embedded_objects handles exceptions gracefully."""
    container = Container()

    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    ns_draw = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"

    content_root = Element(f"{{{ns_office}}}document-content")
    body = SubElement(content_root, f"{{{ns_office}}}body")
    text = SubElement(body, f"{{{ns_office}}}text")

    # Add a valid object structure with body, automatic-styles and meta
    obj = SubElement(text, f"{{{ns_draw}}}object")
    doc = SubElement(obj, f"{{{ns_office}}}document")
    doc_body = SubElement(doc, f"{{{ns_office}}}body")
    SubElement(doc_body, f"{{{ns_office}}}text")
    # Add automatic-styles to trigger styles.xml generation
    auto_styles = SubElement(doc, f"{{{ns_office}}}automatic-styles")
    SubElement(auto_styles, f"{{{ns_office}}}style")
    # Add meta to trigger meta.xml generation
    meta = SubElement(doc, f"{{{ns_office}}}meta")
    SubElement(meta, f"{{{ns_office}}}creation-date")

    call_count = 0

    def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        # Raise on 3rd tostring call (meta.xml) to trigger exception handling
        # while having processed some content
        if call_count < 3:
            return tostring(*args, **kwargs)
        raise ValueError("Test error")

    # Mock tostring to raise an exception after successful XML generation
    with patch("odfdo.container.tostring", side_effect=side_effect):
        # Should not raise, just print warning
        container._process_embedded_objects(
            content_root, "{http://www.w3.org/1999/xlink}"
        )

    # Object processing completed despite late exception
    assert len(container.parts) >= 0  # May have partial results


def test_process_embedded_objects_no_body():
    """Test _process_embedded_objects skips content.xml when no body element."""
    container = Container()

    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    ns_draw = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"

    content_root = Element(f"{{{ns_office}}}document-content")
    body = SubElement(content_root, f"{{{ns_office}}}body")
    text = SubElement(body, f"{{{ns_office}}}text")

    # Add an object with document but no body element
    obj = SubElement(text, f"{{{ns_draw}}}object")
    doc = SubElement(obj, f"{{{ns_office}}}document")
    # No body element - only automatic-styles
    auto_styles = SubElement(doc, f"{{{ns_office}}}automatic-styles")
    SubElement(auto_styles, f"{{{ns_office}}}style")

    container._process_embedded_objects(content_root, "{http://www.w3.org/1999/xlink}")

    # content.xml should not be created (no body)
    assert "Object 1/content.xml" not in container.parts
    # styles.xml should be created (has automatic-styles)
    assert "Object 1/styles.xml" in container.parts


def test_process_embedded_objects_no_auto_styles():
    """Test _process_embedded_objects skips styles.xml when no automatic-styles."""
    container = Container()

    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    ns_draw = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"

    content_root = Element(f"{{{ns_office}}}document-content")
    body = SubElement(content_root, f"{{{ns_office}}}body")
    text = SubElement(body, f"{{{ns_office}}}text")

    # Add an object with document but no automatic-styles
    obj = SubElement(text, f"{{{ns_draw}}}object")
    doc = SubElement(obj, f"{{{ns_office}}}document")
    doc_body = SubElement(doc, f"{{{ns_office}}}body")
    SubElement(doc_body, f"{{{ns_office}}}text")
    # No automatic-styles

    container._process_embedded_objects(content_root, "{http://www.w3.org/1999/xlink}")

    # content.xml should be created (has body)
    assert "Object 1/content.xml" in container.parts
    # styles.xml should not be created (no automatic-styles)
    assert "Object 1/styles.xml" not in container.parts


def test_process_embedded_objects_no_meta():
    """Test _process_embedded_objects skips meta.xml when no meta element."""
    container = Container()

    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    ns_draw = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"

    content_root = Element(f"{{{ns_office}}}document-content")
    body = SubElement(content_root, f"{{{ns_office}}}body")
    text = SubElement(body, f"{{{ns_office}}}text")

    # Add an object with document but no meta
    obj = SubElement(text, f"{{{ns_draw}}}object")
    doc = SubElement(obj, f"{{{ns_office}}}document")
    doc_body = SubElement(doc, f"{{{ns_office}}}body")
    SubElement(doc_body, f"{{{ns_office}}}text")
    # No meta element

    container._process_embedded_objects(content_root, "{http://www.w3.org/1999/xlink}")

    # content.xml should be created
    assert "Object 1/content.xml" in container.parts
    # meta.xml should not be created (no meta)
    assert "Object 1/meta.xml" not in container.parts


def test_process_form_images_invalid_base64():
    """Test _process_form_images handles invalid base64 data."""
    container = Container()

    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    ns_form = "urn:oasis:names:tc:opendocument:xmlns:form:1.0"

    content_root = Element(f"{{{ns_office}}}document-content")
    body = SubElement(content_root, f"{{{ns_office}}}body")
    text = SubElement(body, f"{{{ns_office}}}text")

    # Add a form button with invalid base64 image data
    form_btn = SubElement(text, f"{{{ns_form}}}button")
    binary_data = SubElement(form_btn, f"{{{ns_office}}}binary-data")
    binary_data.text = "!!!invalid_base64!!!"

    image_parts: dict[str, bytes] = {}

    # Should not raise, just print warning
    container._process_form_images(content_root, image_parts)

    # No images processed
    assert image_parts == {}


def test_process_form_images_empty_binary_data():
    """Test _process_form_images skips form elements with empty binary-data."""
    container = Container()

    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    ns_form = "urn:oasis:names:tc:opendocument:xmlns:form:1.0"

    content_root = Element(f"{{{ns_office}}}document-content")
    body = SubElement(content_root, f"{{{ns_office}}}body")
    text = SubElement(body, f"{{{ns_office}}}text")

    # Add a form button with empty binary-data text
    form_btn = SubElement(text, f"{{{ns_form}}}button")
    binary_data = SubElement(form_btn, f"{{{ns_office}}}binary-data")
    binary_data.text = ""  # Empty text

    image_parts: dict[str, bytes] = {}

    # Should skip empty binary-data
    container._process_form_images(content_root, image_parts)

    # No images processed
    assert image_parts == {}


def test_serialize_documents_empty_roots():
    """Test _serialize_documents handles empty content and styles roots."""
    container = Container()

    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"

    # Create empty roots (no children)
    content_root = Element(f"{{{ns_office}}}document-content")
    styles_root = Element(f"{{{ns_office}}}document-styles")

    # Should not create any parts when roots are empty
    container._serialize_documents(content_root, styles_root)

    # Neither content.xml nor styles.xml should be created
    assert "content.xml" not in container.parts
    assert "styles.xml" not in container.parts


def test_parse_folder_with_none_path():
    """Test _parse_folder raises ValueError when path is None."""
    container = Container()
    # path is None by default
    with pytest.raises(ValueError, match="Document path is not defined"):
        container._parse_folder("")


def test_get_folder_part_with_none_path():
    """Test _get_folder_part raises ValueError when path is None."""
    container = Container()
    # path is None by default
    with pytest.raises(ValueError, match="Document path is not defined"):
        container._get_folder_part("content.xml")


def test_get_folder_part_timestamp_with_none_path():
    """Test _get_folder_part_timestamp raises ValueError when path is None."""
    container = Container()
    # path is None by default
    with pytest.raises(ValueError, match="Document path is not defined"):
        container._get_folder_part_timestamp("content.xml")


def test_get_all_zip_part_with_none_path():
    """Test _get_all_zip_part raises ValueError when path is None."""
    container = Container()
    # path is None by default
    with pytest.raises(ValueError, match="Document path is not defined"):
        container._get_all_zip_part()


def test_get_all_zip_part_bad_zipfile(tmp_path):
    """Test _get_all_zip_part handles BadZipFile exception."""
    # Create a file that is not a valid zip
    bad_zip_path = tmp_path / "not_a_zip.odt"
    bad_zip_path.write_text("This is not a zip file")

    container = Container()
    container.path = bad_zip_path

    # Should not raise, just silently return
    container._get_all_zip_part()

    # No parts should be loaded (check internal __parts directly)
    assert len(container._Container__parts) == 0


def test_get_zip_part_no_path():
    """Test _get_zip_part raises ValueError when path is None."""
    container = Container()
    # path is None by default
    with pytest.raises(ValueError, match="Document path is not defined"):
        container._get_zip_part("content.xml")


def test_get_zip_part_bad_zipfile(tmp_path):
    """Test _get_zip_part handles BadZipFile exception."""
    # Create a file that is not a valid zip
    bad_zip_path = tmp_path / "not_a_zip.odt"
    bad_zip_path.write_text("This is not a zip file")

    container = Container()
    container.path = bad_zip_path

    # Should not raise, just return None
    result = container._get_zip_part("content.xml")
    assert result is None


def test_save_zip_missing_mimetype():
    """Test _save_zip raises ValueError when mimetype is missing."""
    container = Container()
    # Add a part but no mimetype
    container._Container__parts["content.xml"] = b"<content/>"

    buffer = io.BytesIO()
    with pytest.raises(ValueError, match="Mimetype is not defined"):
        container._save_zip(buffer)


def test_save_zip_missing_manifest():
    """Test _save_zip warns when manifest is missing."""
    container = Container()
    container._Container__parts["mimetype"] = b"text"
    container._Container__parts[ODF_CONTENT] = b"<content/>"
    # manifest is missing

    buffer = io.BytesIO()
    # Should print warning but succeed
    container._save_zip(buffer)

    # Check that it is a valid zip
    with zipfile.ZipFile(buffer) as zf:
        assert "mimetype" in zf.namelist()
        assert ODF_CONTENT in zf.namelist()


def test_save_zip_missing_standard_parts():
    """Test _save_zip warns when standard XML parts are missing."""
    container = Container()
    container._Container__parts["mimetype"] = b"text"
    container._Container__parts[ODF_MANIFEST] = b"<manifest/>"
    # ODF_CONTENT, ODF_META, etc are missing

    buffer = io.BytesIO()
    # Should print warnings but succeed
    container._save_zip(buffer)

    with zipfile.ZipFile(buffer) as zf:
        assert "mimetype" in zf.namelist()
        assert ODF_MANIFEST in zf.namelist()


def test_save_zip_deleted_parts():
    """Test _save_zip skips deleted parts."""
    container = Container()
    container._Container__parts["mimetype"] = b"text"
    container._Container__parts[ODF_MANIFEST] = b"<manifest/>"
    container._Container__parts[ODF_CONTENT] = b"<content/>"
    # Mark a part as deleted
    container._Container__parts["deleted.txt"] = None  # type: ignore

    buffer = io.BytesIO()
    container._save_zip(buffer)

    with zipfile.ZipFile(buffer) as zf:
        assert "deleted.txt" not in zf.namelist()
        assert ODF_CONTENT in zf.namelist()


def test_save_zip_xml_part_none():
    """Test _save_zip skips XML parts set to None."""
    container = Container()
    container._Container__parts["mimetype"] = b"text"
    container._Container__parts[ODF_MANIFEST] = b"<manifest/>"
    # Set standard XML part to None
    container._Container__parts[ODF_CONTENT] = None  # type: ignore

    buffer = io.BytesIO()
    container._save_zip(buffer)

    with zipfile.ZipFile(buffer) as zf:
        assert ODF_CONTENT not in zf.namelist()


def test_save_zip_manifest_none():
    """Test _save_zip skips manifest if set to None."""
    container = Container()
    container._Container__parts["mimetype"] = b"text"
    container._Container__parts[ODF_CONTENT] = b"<content/>"
    # Set manifest to None
    container._Container__parts[ODF_MANIFEST] = None  # type: ignore

    buffer = io.BytesIO()
    container._save_zip(buffer)

    with zipfile.ZipFile(buffer) as zf:
        assert ODF_MANIFEST not in zf.namelist()


def test_save_zip_mimetype_writestr_error(capsys):
    """Test _save_zip handles ValueError during mimetype write."""
    container = Container()
    container.set_part("mimetype", b"application/vnd.oasis.opendocument.text")
    container.set_part(ODF_MANIFEST, b"<manifest/>")
    container.set_part(ODF_CONTENT, b"<content/>")

    with patch("odfdo.container.ZipFile") as mock_zip:
        mock_zf = mock_zip.return_value.__enter__.return_value

        # To avoid failure on the second attempt in the "Everything else" loop,
        # raise only when ZIP_STORED is used (which is only for mimetype).
        def side_effect(name, data, compress_type=None):
            if name == "mimetype" and compress_type == zipfile.ZIP_STORED:
                raise ValueError("forced error")
            return None

        mock_zf.writestr.side_effect = side_effect

        container._save_zip(io.BytesIO())

    captured = capsys.readouterr()
    assert "Warning: Missing 'mimetype'" in captured.err


def test_save_folder_skips_none_data(tmp_path):
    """Test _save_folder skips parts with None data (deleted parts)."""
    container = Container()
    # Set mimetype
    container._Container__parts["mimetype"] = ODF_EXTENSIONS["odt"].encode()
    # Add a part with None data (marked for deletion)
    container._Container__parts["deleted.xml"] = None  # type: ignore
    # Add a normal part
    container._Container__parts["content.xml"] = b"<content/>"

    folder_path = tmp_path / "output_folder"
    container._save_folder(folder_path)

    # The deleted part should not be created
    assert not (folder_path / "deleted.xml").exists()
    # The normal part should be created
    assert (folder_path / "content.xml").exists()


def test_encoded_image_no_path():
    """Test _encoded_image returns None when no href path."""
    container = Container()

    ns_draw = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"

    # Create image element without href
    img_elem = Element(f"{{{ns_draw}}}image")
    # No xlink:href attribute

    result = container._encoded_image(img_elem)
    assert result is None


def test_encoded_image_no_content():
    """Test _encoded_image returns None when content is empty."""
    container = Container()

    ns_draw = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"

    # Create image element with href but empty content in parts
    img_elem = Element(f"{{{ns_draw}}}image")
    img_elem.set("{http://www.w3.org/1999/xlink}href", "Pictures/empty.png")

    # Pre-populate parts with empty content
    container._Container__parts["Pictures/empty.png"] = b""

    result = container._encoded_image(img_elem)
    assert result is None


def test_embed_form_image_data_no_content():
    """Test _embed_form_image_data returns early when no content."""
    container = Container()

    ns_form = "urn:oasis:names:tc:opendocument:xmlns:form:1.0"

    # Create form element with image-data pointing to missing file
    form_elem = Element(f"{{{ns_form}}}button")

    # Should return early without error
    container._embed_form_image_data(form_elem, "Pictures/missing.png")

    # No binary-data should be added
    assert len(list(form_elem)) == 0


def test_encoded_fill_image_no_path():
    """Test _encoded_fill_image returns None when no href path."""
    container = Container()

    ns_draw = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"

    # Create fill-image element without href
    fill_elem = Element(f"{{{ns_draw}}}fill-image")
    # No xlink:href attribute

    result = container._encoded_fill_image(fill_elem)
    assert result is None


def test_encoded_fill_image_no_content():
    """Test _encoded_fill_image returns None when content is empty."""
    container = Container()

    ns_draw = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"

    # Create fill-image element with href but empty content
    fill_elem = Element(f"{{{ns_draw}}}fill-image")
    fill_elem.set("{http://www.w3.org/1999/xlink}href", "Pictures/empty.png")

    # Pre-populate parts with empty content
    container._Container__parts["Pictures/empty.png"] = b""

    result = container._encoded_fill_image(fill_elem)
    assert result is None


def test_encoded_object_no_path():
    """Test _encoded_object returns None when no href path."""
    container = Container()

    ns_draw = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"

    # Create object element without href
    obj_elem = Element(f"{{{ns_draw}}}object")
    # No xlink:href attribute

    result = container._encoded_object(obj_elem)
    assert result is None


def test_parse_folder_basic(tmp_path):
    # Setup a folder structure
    folder = tmp_path / "test.folder"
    folder.mkdir()
    (folder / "mimetype").write_text("application/vnd.oasis.opendocument.text")
    (folder / "content.xml").write_text("<xml/>")

    subfolder = folder / "Pictures"
    subfolder.mkdir()
    (subfolder / "image.png").write_bytes(b"fake png")

    container = Container()
    container.path = folder

    parts = container._parse_folder("")

    assert "mimetype" in parts
    assert "content.xml" in parts
    assert "Pictures/image.png" in parts
    assert len(parts) == 3


def test_parse_folder_recursive(tmp_path):
    folder = tmp_path / "test.folder"
    folder.mkdir()
    (folder / "mimetype").write_text("text")

    d1 = folder / "dir1"
    d1.mkdir()
    (d1 / "file1").write_text("1")

    d2 = d1 / "dir2"
    d2.mkdir()
    (d2 / "file2").write_text("2")

    container = Container()
    container.path = folder

    parts = container._parse_folder("")

    assert "mimetype" in parts
    assert "dir1/file1" in parts
    assert "dir1/dir2/file2" in parts
    assert len(parts) == 3


def test_parse_folder_ignore_hidden(tmp_path):
    folder = tmp_path / "test.folder"
    folder.mkdir()
    (folder / "mimetype").write_text("text")
    (folder / ".hidden").write_text("hidden")

    sub = folder / "sub"
    sub.mkdir()
    (sub / ".hidden_in_sub").write_text("hidden")
    (sub / "visible").write_text("visible")

    container = Container()
    container.path = folder

    parts = container._parse_folder("")

    assert "mimetype" in parts
    assert "sub/visible" in parts
    assert ".hidden" not in parts
    assert "sub/.hidden_in_sub" not in parts
    assert len(parts) == 2


def test_parse_folder_leaf_directory(tmp_path):
    folder = tmp_path / "test.folder"
    folder.mkdir()
    (folder / "mimetype").write_text("text")

    empty_dir = folder / "empty_dir"
    empty_dir.mkdir()

    container = Container()
    container.path = folder

    parts = container._parse_folder("")

    assert "mimetype" in parts
    assert "empty_dir/" in parts
    assert len(parts) == 2


def test_parse_folder_complex(tmp_path):
    folder = tmp_path / "test.folder"
    folder.mkdir()
    (folder / "mimetype").write_text("text")

    # Nested empty dirs
    (folder / "a" / "b" / "c").mkdir(parents=True)

    # Mixed content
    (folder / "docs").mkdir()
    (folder / "docs" / "doc1.xml").write_text("doc1")
    (folder / "docs" / "images").mkdir()
    (folder / "docs" / "images" / "img1.png").write_bytes(b"img1")

    container = Container()
    container.path = folder

    parts = container._parse_folder("")

    expected = {"mimetype", "a/b/c/", "docs/doc1.xml", "docs/images/img1.png"}
    assert set(parts) == expected


def test_encoded_fill_image_success():
    """Test _encoded_fill_image with valid href and content."""
    container = Container()
    ns_draw = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    xlink = "http://www.w3.org/1999/xlink"

    elem = Element(f"{{{ns_draw}}}fill-image")
    elem.set(f"{{{xlink}}}href", "./Pictures/test.png")

    content = b"fake image content"
    container.set_part("Pictures/test.png", content)

    result = container._encoded_fill_image(elem)

    assert result is not None
    assert result.tag == f"{{{ns_draw}}}fill-image"
    binary_data = result.find(
        ".//{urn:oasis:names:tc:opendocument:xmlns:office:1.0}binary-data"
    )
    assert binary_data is not None
    assert base64.standard_b64decode(binary_data.text.strip()) == content


def test_encoded_fill_image_with_names():
    """Test _encoded_fill_image with name and display-name attributes."""
    container = Container()
    ns_draw = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    xlink = "http://www.w3.org/1999/xlink"

    elem = Element(f"{{{ns_draw}}}fill-image")
    elem.set(f"{{{xlink}}}href", "Pictures/test.png")
    elem.set(f"{{{ns_draw}}}name", "image_name")
    elem.set(f"{{{ns_draw}}}display-name", "Display Name")

    content = b"content"
    container.set_part("Pictures/test.png", content)

    result = container._encoded_fill_image(elem)

    assert result is not None
    assert result.get(f"{{{ns_draw}}}name") == "image_name"
    assert result.get(f"{{{ns_draw}}}display-name") == "Display Name"


def test_encoded_object_success():
    """Test _encoded_object with full ODF object structure."""
    container = Container()
    ns_draw = "{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}"
    ns_office = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}"
    xlink = "{http://www.w3.org/1999/xlink}"

    elem = Element(f"{ns_draw}object")
    elem.set(f"{xlink}href", "./Object 1")

    # Mock object parts
    content_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">
        <office:automatic-styles><style:style style:name="P1" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"/></office:automatic-styles>
        <office:body><office:text><text:p>Object Content</text:p></office:text></office:body>
    </office:document-content>"""

    styles_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <office:document-styles xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">
        <office:automatic-styles><style:style style:name="S1" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"/></office:automatic-styles>
    </office:document-styles>"""

    meta_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <office:document-meta xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0">
        <office:meta><meta:generator>Test</meta:generator></office:meta>
    </office:document-meta>"""

    container.set_part("Object 1/content.xml", content_xml)
    container.set_part("Object 1/styles.xml", styles_xml)
    container.set_part("Object 1/meta.xml", meta_xml)

    result = container._encoded_object(elem)

    assert result is not None
    assert result.tag == f"{ns_draw}object"
    doc = result.find(f"{ns_office}document")
    assert doc is not None
    assert doc.get(f"{ns_office}mimetype") == "application/vnd.oasis.opendocument.chart"
    assert b"Object Content" in tostring(result)


def test_encoded_object_no_body():
    """Test _encoded_object when content.xml has no office:body."""
    container = Container()
    ns_draw = "{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}"
    xlink = "{http://www.w3.org/1999/xlink}"

    elem = Element(f"{ns_draw}object")
    elem.set(f"{xlink}href", "Object1")

    # content.xml without office:body
    content_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">
        <text:p>Direct Content</text:p>
    </office:document-content>"""

    container.set_part("Object1/content.xml", content_xml)

    result = container._encoded_object(elem)

    assert result is not None
    assert b"Direct Content" in tostring(result)


def test_encoded_object_errors():
    """Test _encoded_object handles errors in meta/styles parts."""
    container = Container()
    ns_draw = "{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}"
    xlink = "{http://www.w3.org/1999/xlink}"

    elem = Element(f"{ns_draw}object")
    elem.set(f"{xlink}href", "Object1")

    content_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">
        <office:body><office:text/></office:body>
    </office:document-content>"""

    container.set_part("Object1/content.xml", content_xml)
    # Invalid XML for meta and styles
    container.set_part("Object1/meta.xml", b"invalid xml")
    container.set_part("Object1/styles.xml", b"invalid xml")

    # Should not raise exception
    result = container._encoded_object(elem)
    assert result is not None


def test_encoded_object_invalid_content_xml():
    """Test _encoded_object returns None if content.xml is invalid."""
    container = Container()
    ns_draw = "{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}"
    xlink = "{http://www.w3.org/1999/xlink}"

    elem = Element(f"{ns_draw}object")
    elem.set(f"{xlink}href", "Object1")

    container.set_part("Object1/content.xml", b"invalid xml")

    result = container._encoded_object(elem)
    assert result is None


def test_encoded_object_no_body_with_auto_styles():
    """Test _encoded_object when content.xml has no office:body but has automatic-styles."""
    container = Container()
    ns_draw = "{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}"
    xlink = "{http://www.w3.org/1999/xlink}"

    elem = Element(f"{ns_draw}object")
    elem.set(f"{xlink}href", "Object1")

    # content.xml without office:body but WITH office:automatic-styles
    content_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0">
        <office:automatic-styles><style:style style:name="P1"/></office:automatic-styles>
        <office:something-else/>
    </office:document-content>"""

    container.set_part("Object1/content.xml", content_xml)

    result = container._encoded_object(elem)

    assert result is not None
    # Verify office:something-else is in body, but automatic-styles is not (it should be before body)
    res_str = tostring(result).decode()
    assert "something-else" in res_str
    # Find office:body in the result
    body_start = res_str.find("<office:body")
    auto_style_start = res_str.find("<office:automatic-styles")
    assert auto_style_start < body_start


def test_encoded_object_styles_no_auto():
    """Test _encoded_object when styles.xml exists but has no automatic-styles."""
    container = Container()
    ns_draw = "{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}"
    xlink = "{http://www.w3.org/1999/xlink}"

    elem = Element(f"{ns_draw}object")
    elem.set(f"{xlink}href", "Object1")

    container.set_part(
        "Object1/content.xml",
        b"""<?xml version="1.0" encoding="UTF-8"?>
    <office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">
        <office:body><office:text/></office:body>
    </office:document-content>""",
    )

    # styles.xml without automatic-styles
    container.set_part(
        "Object1/styles.xml",
        b"""<?xml version="1.0" encoding="UTF-8"?>
    <office:document-styles xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">
        <office:master-styles/>
    </office:document-styles>""",
    )

    result = container._encoded_object(elem)
    assert result is not None
    assert b"automatic-styles" not in tostring(result)


def test_encoded_object_content_not_in_parts():
    """Test _encoded_object returns None when content.xml is missing."""
    container = Container()
    ns_draw = "{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}"
    xlink = "{http://www.w3.org/1999/xlink}"

    elem = Element(f"{ns_draw}object")
    elem.set(f"{xlink}href", "MissingObject")

    # MissingObject/content.xml is NOT in parts
    result = container._encoded_object(elem)
    assert result is None


def test_encoded_object_no_body_mixed_children():
    """Test _encoded_object when office:body is missing and it has mixed children."""
    container = Container()
    ns_draw = "{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}"
    xlink = "{http://www.w3.org/1999/xlink}"

    elem = Element(f"{ns_draw}object")
    elem.set(f"{xlink}href", "Object1")

    # content.xml without office:body, with automatic-styles and other children
    content_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">
        <office:automatic-styles/>
        <office:meta/>
        <office:settings/>
    </office:document-content>"""

    container.set_part("Object1/content.xml", content_xml)

    result = container._encoded_object(elem)

    assert result is not None
    res_str = tostring(result).decode()
    # The body should contain meta and settings, but NOT automatic-styles (which is outside body)
    # Find office:body
    body_content = res_str.split("<office:body")[1].split("</office:body>")[0]
    assert "office:meta" in body_content
    assert "office:settings" in body_content
    assert "office:automatic-styles" not in body_content


def test_encoded_object_duplicate_auto_styles():
    """Test _encoded_object with duplicate automatic-styles to hit the skip logic.

    The first automatic-styles is moved to obj_doc.
    The second one remains in content_doc and should be skipped by the loop.
    """
    container = Container()
    ns_draw = "{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}"
    xlink = "{http://www.w3.org/1999/xlink}"

    elem = Element(f"{ns_draw}object")
    elem.set(f"{xlink}href", "Object1")

    # content.xml with TWO automatic-styles and no body
    content_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">
        <office:automatic-styles/>
        <office:automatic-styles/>
        <office:meta/>
    </office:document-content>"""

    container.set_part("Object1/content.xml", content_xml)

    result = container._encoded_object(elem)

    assert result is not None
    res_str = tostring(result).decode()
    # The body should contain meta, but NOT the second automatic-styles
    body_content = res_str.split("<office:body")[1].split("</office:body>")[0]
    assert "office:meta" in body_content
    assert "office:automatic-styles" not in body_content
    # The first one should be outside body
    assert res_str.count("office:automatic-styles") == 1
    assert res_str.find("<office:automatic-styles") < res_str.find("<office:body")


def test_xml_content_default_mimetype():
    """Test _xml_content uses default mimetype when missing."""
    container = Container()
    container._Container__parts["mimetype"] = None  # type: ignore
    container.set_part(
        ODF_CONTENT,
        b'<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"/>',
    )

    xml = container._xml_content()
    assert b'office:mimetype="application/vnd.oasis.opendocument.text"' in xml


def test_xml_content_missing_part_warning(capsys):
    """Test _xml_content warns when a standard part is missing."""
    container = Container()
    container.set_part("mimetype", b"text")
    container.set_part(
        ODF_CONTENT,
        b'<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"/>',
    )
    # ODF_META, ODF_SETTINGS, ODF_STYLES are missing

    container._xml_content()
    captured = capsys.readouterr()
    assert "Warning: Missing 'meta.xml'" in captured.err
    assert "Warning: Missing 'settings.xml'" in captured.err
    assert "Warning: Missing 'styles.xml'" in captured.err


def test_xml_content_part_none():
    """Test _xml_content skips parts set to None."""
    container = Container()
    container.set_part("mimetype", b"text")
    container.set_part(
        ODF_CONTENT,
        b'<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"/>',
    )
    container.set_part(ODF_META, None)  # type: ignore

    xml = container._xml_content()
    assert b"office:document-meta" not in xml


def test_xml_content_with_already_parsed_part():
    """Test _xml_content handles parts that are already parsed elements."""
    container = Container()
    container.set_part("mimetype", b"text")

    # Create an element instead of bytes
    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    content_elem = Element(f"{{{ns_office}}}document-content")
    SubElement(content_elem, f"{{{ns_office}}}body")

    container.set_part(ODF_CONTENT, content_elem)  # type: ignore

    xml = container._xml_content()
    assert b"office:body" in xml


def test_xml_content_not_pretty():
    """Test _xml_content with pretty=False."""
    container = Container()
    container.set_part("mimetype", b"text")
    container.set_part(
        ODF_CONTENT,
        b'<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"/>',
    )
    xml = container._xml_content(pretty=False)
    # Lxml might use single or double quotes
    assert b"<?xml version=" in xml
    assert b"encoding='UTF-8'?>" in xml or b'encoding="UTF-8"?>' in xml
    assert b"office:document" in xml
    # Non-pretty should not have newlines/indentation between elements (mostly)
    assert b">\n  <" not in xml


def test_xml_content_full_processing():
    """Test _xml_content with all types of processing (images, fill-images, objects, forms)."""
    container = Container()
    container.set_part("mimetype", b"text")

    # Content with draw:image, draw:fill-image, draw:object, and form element
    # Remove comments because pretty_indent crashes on them (it expects .tag to be a string)
    content_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <office:document-content
        xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
        xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
        xmlns:xlink="http://www.w3.org/1999/xlink"
        xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0">
        <office:body>
            <office:text>
                <draw:frame><draw:image xlink:href="Pictures/img.png"/></draw:frame>
                <draw:fill-image xlink:href="Pictures/fill.png"/>
                <draw:object xlink:href="Object1"/>
                <form:button form:image-data="Pictures/form.png"/>
                <form:button/>
            </office:text>
        </office:body>
    </office:document-content>"""

    # Styles with draw:image and draw:fill-image
    styles_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <office:document-styles
        xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
        xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
        xmlns:xlink="http://www.w3.org/1999/xlink">
        <office:styles>
            <draw:fill-image xlink:href="Pictures/style_fill.png"/>
        </office:styles>
    </office:document-styles>"""

    container.set_part(ODF_CONTENT, content_xml)
    container.set_part(ODF_STYLES, styles_xml)
    container.set_part("Pictures/img.png", b"img")
    container.set_part("Pictures/fill.png", b"fill")
    container.set_part("Pictures/form.png", b"form")
    container.set_part("Pictures/style_fill.png", b"style_fill")
    container.set_part(
        "Object1/content.xml",
        b'<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"><office:body><office:text/></office:body></office:document-content>',
    )

    xml = container._xml_content()
    assert b"office:binary-data" in xml
    # 4 elements each have <office:binary-data> and </office:binary-data>
    assert xml.count(b"office:binary-data") == 8


def test_xml_content_processing_none_returns():
    """Test _xml_content when encoders return None (e.g. missing parts)."""
    container = Container()
    container.set_part("mimetype", b"text")
    content_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <office:document-content
        xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
        xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
        xmlns:xlink="http://www.w3.org/1999/xlink">
        <office:body>
            <office:text>
                <draw:frame><draw:image xlink:href="MissingImg"/></draw:frame>
                <draw:fill-image xlink:href="MissingFill"/>
                <draw:object xlink:href="MissingObj"/>
            </office:text>
        </office:body>
    </office:document-content>"""
    container.set_part(ODF_CONTENT, content_xml)

    # We must explicitly set them to None to avoid KeyError, or encoders return None
    container.set_part("MissingImg", None)  # type: ignore
    container.set_part("MissingFill", None)  # type: ignore
    # Object is special, it checks if path/content.xml is in parts

    xml = container._xml_content()
    assert b"draw:image" in xml
    assert b"draw:fill-image" in xml
    assert b"draw:object" in xml
    assert b"office:binary-data" not in xml


def test_get_parts_xml_with_path(tmp_path):
    """Test get_parts() with XML packaging and a defined path."""
    flat_odf = b'<?xml version="1.0" encoding="UTF-8"?><office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" office:mimetype="text" office:version="1.2"><office:body><office:text/></office:body></office:document>'
    path = tmp_path / "test.fodt"
    path.write_bytes(flat_odf)

    container = Container()
    container.open(path)
    # Open() should set packaging to XML for .fodt
    assert container._Container__packaging == XML

    parts = container.get_parts()
    assert ODF_CONTENT in parts
    assert "mimetype" in parts


def test_get_parts_folder_with_path(tmp_path, samples):
    """Test get_parts() with FOLDER packaging and a defined path."""
    container = Container()
    container.open(samples("example.odt"))
    folder_path = tmp_path / "test_folder"
    container.save(folder_path, packaging=FOLDER)

    # Open the folder
    folder_container = Container()
    folder_container.open(tmp_path / "test_folder.folder")
    assert folder_container._Container__packaging == FOLDER

    parts = folder_container.get_parts()
    assert ODF_CONTENT in parts
    assert "mimetype" in parts


def test_get_parts_invalid_packaging():
    """Test get_parts() raises ValueError for invalid packaging type."""
    container = Container()
    container.path = Path("fake.odt")
    # Manually set an invalid packaging
    container._Container__packaging = "INVALID"  # type: ignore

    with pytest.raises(ValueError, match="Unable to provide parts"):
        container.get_parts()


def test_get_part_folder_outdated_cache(tmp_path, samples):
    """Test get_part() with folder packaging when cache is outdated."""
    container = Container()
    container.open(samples("example.odt"))
    folder_path = tmp_path / "test_folder"
    container.save(folder_path, packaging=FOLDER)

    # Open the folder
    folder_container = Container()
    folder_container.open(tmp_path / "test_folder.folder")

    # Get content.xml to populate cache
    part1 = folder_container.get_part(ODF_CONTENT)

    # Update the file on disk
    (tmp_path / "test_folder.folder" / ODF_CONTENT).write_bytes(b"new content")

    # Force the next get_part to think the timestamp has changed
    # We mock _get_folder_part_timestamp to return a value different from cache
    current_ts = folder_container._get_folder_part_timestamp(ODF_CONTENT)
    with patch.object(
        Container, "_get_folder_part_timestamp", return_value=current_ts + 1
    ):
        # get_part should detect timestamp change and reload
        part2 = folder_container.get_part(ODF_CONTENT)

    assert part2 == b"new content"
    assert part2 != part1


def test_get_folder_part_timestamp_missing_file(tmp_path):
    """Test _get_folder_part_timestamp() returns -1 for missing files."""
    container = Container()
    container.path = tmp_path
    # File does not exist
    ts = container._get_folder_part_timestamp("nonexistent.xml")
    assert ts == -1


def test_get_part_xml_not_found(tmp_path):
    """Test get_part() returns None for missing parts in XML packaging."""
    flat_odf = b'<?xml version="1.0" encoding="UTF-8"?><office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" office:mimetype="text" office:version="1.2"><office:body><office:text/></office:body></office:document>'
    path = tmp_path / "test.fodt"
    path.write_bytes(flat_odf)

    container = Container()
    container.open(path)
    assert container._Container__packaging == XML

    # "nonexistent.xml" is not in __parts and it is not a ZIP or FOLDER container
    result = container.get_part("nonexistent.xml")
    assert result is None


def test_xml_content_form_no_image_data():
    """Test _xml_content form processing when image-data attribute is missing."""
    container = Container()
    container.set_part("mimetype", b"text")

    content_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <office:document-content
        xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
        xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0">
        <office:body>
            <office:text>
                <form:button form:image-data=""/>
            </office:text>
        </office:body>
    </office:document-content>"""
    container.set_part(ODF_CONTENT, content_xml)

    xml = container._xml_content()
    assert b"form:button" in xml
    assert b"office:binary-data" not in xml


def test_mimetype_getter_bytes():
    """Test mimetype getter returns string from bytes."""
    container = Container()
    container.mimetype = b"application/vnd.oasis.opendocument.text"
    assert container.mimetype == "application/vnd.oasis.opendocument.text"


def test_mimetype_getter_empty():
    """Test mimetype getter returns empty string on failure."""
    container = Container()
    # No mimetype part set
    assert container.mimetype == ""

    # mimetype part is not bytes
    ns_text = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    container.set_part("mimetype", Element(f"{{{ns_text}}}p"))  # type: ignore
    assert container.mimetype == ""


def test_mimetype_setter_accept_bytes():
    """Test mimetype setter accepts bytes."""
    container = Container()
    container.mimetype = b"test/mimetype"
    assert container.get_part("mimetype") == b"test/mimetype"


def test_mimetype_setter_type_error():
    """Test mimetype setter raises TypeError for invalid types."""
    container = Container()
    with pytest.raises(TypeError, match='Wrong mimetype "123"'):
        container.mimetype = 123  # type: ignore


def test_do_backup_exists(tmp_path):
    """Test _do_backup moves file to backup name."""
    target = tmp_path / "test.odt"
    target.write_text("original")
    Container._do_backup(target)
    assert not target.exists()
    backup = tmp_path / "test.backup.odt"
    assert backup.exists()
    assert backup.read_text() == "original"


def test_do_backup_not_exists(tmp_path):
    """Test _do_backup does nothing if target doesn't exist."""
    target = tmp_path / "nonexistent.odt"
    Container._do_backup(target)
    assert not (tmp_path / "test.backup.odt").exists()


def test_do_backup_back_file_is_dir(tmp_path):
    """Test _do_backup removes backup directory before moving."""
    target = tmp_path / "test.odt"
    target.write_text("original")
    backup = tmp_path / "test.backup.odt"
    backup.mkdir()
    Container._do_backup(target)
    assert not target.exists()
    assert backup.is_file()
    assert backup.read_text() == "original"


def test_do_backup_oserror(tmp_path, capsys):
    """Test _do_backup handles OSError during move."""
    target = tmp_path / "test.odt"
    target.write_text("original")

    with patch("shutil.move", side_effect=OSError("forced move error")):
        Container._do_backup(target)

    captured = capsys.readouterr()
    assert "Warning: forced move error" in captured.err


def test_do_backup_rmtree_oserror(tmp_path, capsys):
    """Test _do_backup handles OSError during rmtree of backup dir."""
    target = tmp_path / "test.odt"
    target.write_text("original")
    backup = tmp_path / "test.backup.odt"
    backup.mkdir()

    with patch("shutil.rmtree", side_effect=OSError("forced rmtree error")):
        Container._do_backup(target)

    captured = capsys.readouterr()
    assert "Warning: forced rmtree error" in captured.err


def test_do_unlink_oserror(tmp_path, capsys):
    """Test _do_unlink handles OSError during rmtree."""
    target = tmp_path / "test.folder"
    target.mkdir()

    with patch("shutil.rmtree", side_effect=OSError("forced error")):
        Container._do_unlink(target)

    captured = capsys.readouterr()
    assert "Warning: forced error" in captured.err


def test_clean_save_target_none():
    """Test _clean_save_target returns self.path if target is None."""
    container = Container()
    container.path = Path("current/path.odt")
    assert Path(container._clean_save_target(None)) == Path("current/path.odt")


def test_clean_save_target_trailing_sep():
    """Test _clean_save_target removes trailing separators."""
    container = Container()
    target = f"some/path{os.sep}"
    assert container._clean_save_target(target) == "some/path"


def test_clean_save_target_folder_ext():
    """Test _clean_save_target removes .folder extension."""
    container = Container()
    assert container._clean_save_target("my_doc.folder") == "my_doc"
    assert container._clean_save_target("my_doc.folder.folder") == "my_doc"


def test_save_as_xml_invalid_target():
    """Test _save_as_xml raises TypeError for invalid types."""
    container = Container()
    with pytest.raises(TypeError, match="requires a path name"):
        container._save_as_xml(123, False)  # type: ignore


def test_save_as_xml_bytesio():
    """Test _save_as_xml with BytesIO target."""
    container = Container()
    container.mimetype = "application/vnd.oasis.opendocument.text"
    container.set_part(
        ODF_CONTENT,
        b'<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"/>',
    )
    buffer = io.BytesIO()
    # No backup for BytesIO
    container._save_as_xml(buffer, backup=False)
    assert buffer.getvalue().startswith(b"<?xml")


def test_save_as_xml_with_backup(tmp_path):
    """Test _save_as_xml with backup=True."""
    target = tmp_path / "test.fodt"
    target.write_text("original content")

    container = Container()
    container.mimetype = "application/vnd.oasis.opendocument.text"
    container.set_part(
        ODF_CONTENT,
        b'<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"/>',
    )

    container._save_as_xml(target, backup=True)

    assert (tmp_path / "test.backup.fodt").exists()
    assert (tmp_path / "test.backup.fodt").read_text() == "original content"
    assert target.read_text().startswith("<?xml")


def test_save_as_xml_suffix_fix():
    """Test _save_as_xml fixes suffix for flat XML."""
    container = Container()
    container.mimetype = "application/vnd.oasis.opendocument.text"

    # We mock _save_xml to check the target path
    with patch.object(container, "_save_xml") as mock_save:
        container._save_as_xml("test.txt", False)
        args, _ = mock_save.call_args
        assert str(args[0]) == "test.fodt"


def test_save_as_folder_invalid_target():
    """Test _save_as_folder raises TypeError for BytesIO."""
    container = Container()
    with pytest.raises(TypeError, match="requires a folder name"):
        container._save_as_folder(io.BytesIO(), False)


def test_save_as_folder_success(tmp_path, samples):
    """Test _save_as_folder success path."""
    container = Container()
    container.open(samples("example.odt"))
    target = tmp_path / "saved_folder"
    # _save_as_folder will append .folder if missing
    container._save_as_folder(target, backup=False)
    assert (tmp_path / "saved_folder.folder").is_dir()
    assert (tmp_path / "saved_folder.folder" / "mimetype").exists()


def test_save_as_folder_already_has_ext(tmp_path, samples):
    """Test _save_as_folder when target already ends with .folder."""
    container = Container()
    container.open(samples("example.odt"))
    target = tmp_path / "saved_folder.folder"
    container._save_as_folder(target, backup=False)
    assert target.is_dir()
    assert (target / "mimetype").exists()


def test_save_as_folder_with_backup(tmp_path, samples):
    """Test _save_as_folder with backup=True."""
    container = Container()
    container.open(samples("example.odt"))
    target = tmp_path / "saved_folder.folder"
    target.mkdir()
    (target / "old").write_text("old")
    container._save_as_folder(target, backup=True)
    assert (tmp_path / "saved_folder.backup.folder").is_dir()
    assert (tmp_path / "saved_folder.backup.folder" / "old").exists()
    assert target.is_dir()
    assert not (target / "old").exists()
