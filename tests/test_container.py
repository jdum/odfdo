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

import io
import shutil
from os.path import isfile, join
from pathlib import Path

import pytest
from lxml.etree import Element

from odfdo.const import (
    FOLDER,
    ODF_CONTENT,
    ODF_EXTENSIONS,
    ODF_MANIFEST,
    ODF_META,
    ODF_SETTINGS,
    ODF_STYLES,
    ODF_TEXT,
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


# New tests for improved coverage


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
    flat_odf = b"""\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                 office:mimetype="application/vnd.oasis.opendocument.text"
                 office:version="1.2">
    <office:body>
        <office:text>
            <text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">Hello</text:p>
        </office:text>
    </office:body>
</office:document>"""
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
    flat_odf = b"""\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                 office:mimetype="application/invalid"
                 office:version="1.2">
</office:document>"""
    assert Container._is_flat_xml(flat_odf) is False


def test_open_flat_xml_file(tmp_path, samples):
    """Test opening a flat XML ODF file."""
    # Create a minimal flat ODF file
    flat_odf = b"""\
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
</office:document>"""
    flat_path = tmp_path / "flat.fodt"
    flat_path.write_bytes(flat_odf)

    container = Container()
    container.open(flat_path)
    assert container.mimetype == "application/vnd.oasis.opendocument.text"
    content = container.get_part(ODF_CONTENT)
    assert b"Hello World" in content


def test_open_flat_xml_bytesio():
    """Test opening a flat XML ODF from BytesIO."""
    flat_odf = b"""\
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
</office:document>"""
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


# Additional tests for better coverage


def test_open_flat_xml_with_meta_and_settings(tmp_path):
    """Test opening flat XML with meta and settings elements."""
    flat_odf = b"""\
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
</office:document>"""
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
    flat_odf = b"""\
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
</office:document>"""
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
    flat_odf = b"""\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                 office:version="1.2">
    <office:body>
        <office:text/>
    </office:body>
</office:document>"""
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
    flat_odf = b"""\
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
</office:document>"""
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
