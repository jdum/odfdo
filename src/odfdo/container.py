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
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
"""Container class, ODF file management."""

from __future__ import annotations

import base64
import contextlib
import io
import os
import shutil
import sys
import textwrap
import time
from copy import deepcopy
from functools import cache
from pathlib import Path, PurePath
from zipfile import ZIP_DEFLATED, ZIP_STORED, BadZipfile, ZipFile, is_zipfile

from lxml.etree import (
    Element,
    XMLSyntaxError,
    _Element,
    _ElementTree,
    fromstring,
    tostring,
)

from .const import (
    FOLDER,
    ODF_CONTENT,
    ODF_EXTENSIONS,
    ODF_FLAT_EXTENSIONS,
    ODF_MANIFEST,
    ODF_META,
    ODF_MIMETYPE_TO_FLAT_EXTENSION,
    ODF_MIMETYPES,
    ODF_SETTINGS,
    ODF_STYLES,
    OFFICE_PREFIX,
    OFFICE_VERSION,
    PACKAGING,
    XML,
    ZIP,
)
from .element import NAMESPACES_XML, xpath_compile
from .utils import bytes_to_str, str_to_bytes

TAB = "  "
TEXT_CONTENT = {
    "config:config-item",
    "db:data-source-setting-value",
    "db:table-filter-pattern",
    "db:table-type",
    "dc:creator",
    "dc:date",
    "dc:description",
    "dc:language",
    "dc:subject",
    "dc:title",
    "form:item",
    "form:option",
    "math:math",
    "meta:creation-date",
    "meta:date-string",
    "meta:editing-cycles",
    "meta:editing-duration",
    "meta:generator",
    "meta:initial-creator",
    "meta:keyword",
    "meta:print-date",
    "meta:printed-by",
    "meta:user-defined",
    "number:currency-symbol",
    "number:embedded-text",
    "number:text",
    "office:script",
    "presentation:date-time-decl",
    "presentation:footer-decl",
    "presentation:header-decl",
    "svg:desc",
    "svg:title",
    "table:desc",
    "table:title",
    "text:a",
    "text:author-initials",
    "text:author-name",
    "text:bibliography-mark",
    "text:bookmark-ref",
    "text:chapter",
    "text:character-count",
    "text:conditional-text",
    "text:creation-date",
    "text:creation-time",
    "text:creator",
    "text:database-display",
    "text:database-name",
    "text:database-row-number",
    "text:date",
    "text:dde-connection",
    "text:description",
    "text:editing-cycles",
    "text:editing-duration",
    "text:execute-macro",
    "text:expression",
    "text:file-name",
    "text:h",
    "text:hidden-paragraph",
    "text:hidden-text",
    "text:image-count",
    "text:index-entry-span",
    "text:index-title-template",
    "text:initial-creator",
    "text:keywords",
    "text:line-break",
    "text:linenumbering-separator",
    "text:measure",
    "text:meta",
    "text:meta-field",
    "text:modification-date",
    "text:modification-time",
    "text:note-citation",
    "text:note-continuation-notice-backward",
    "text:note-continuation-notice-forward",
    "text:note-ref",
    "text:number",
    "text:object-count",
    "text:p",
    "text:page-continuation",
    "text:page-count",
    "text:page-number",
    "text:page-variable-get",
    "text:page-variable-set",
    "text:paragraph-count",
    "text:placeholder",
    "text:print-date",
    "text:print-time",
    "text:printed-by",
    "text:reference-ref",
    "text:ruby-base",
    "text:ruby-text",
    "text:s",
    "text:script",
    "text:sender-city",
    "text:sender-company",
    "text:sender-country",
    "text:sender-email",
    "text:sender-fax",
    "text:sender-firstname",
    "text:sender-initials",
    "text:sender-lastname",
    "text:sender-phone-private",
    "text:sender-phone-work",
    "text:sender-position",
    "text:sender-postal-code",
    "text:sender-state-or-province",
    "text:sender-street",
    "text:sender-title",
    "text:sequence",
    "text:sequence-ref",
    "text:sheet-name",
    "text:soft-page-break",
    "text:span",
    "text:subject",
    "text:tab",
    "text:table-count",
    "text:table-formula",
    "text:template-name",
    "text:text-input",
    "text:time",
    "text:title",
    "text:user-defined",
    "text:user-field-get",
    "text:user-field-input",
    "text:variable-get",
    "text:variable-input",
    "text:variable-set",
    "text:word-count",
}

XML_TAG = b'<?xml version="1.0" encoding="UTF-8"?>\n'
NS_OFFICE = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"


def printwarn(message: str) -> None:
    """Print a message on stderr.

    Args:
        message: the text to print.
    """
    print(f"Warning: {message}", file=sys.stderr)


@cache
def _ns_tag(tag: str) -> str:
    """Return the tag prefixed by NS_OFFICE."""
    return f"{{{NS_OFFICE}}}{tag}"


def pretty_indent(
    elem: _ElementTree | _Element,
    level: int = 0,
    ending_level: int = 0,
    textual_parent: bool = False,
) -> _ElementTree | _Element:
    """Return an indented _ElementTree.

    Args:
        elem: the source Element.
        level: current indentation level.
        ending_level: previous indentation level.
        textual_parent: True if the parent element contains text.

    """
    nb_child = len(elem)
    follow_level = level + 1
    tag = f"{elem.prefix}:{elem.tag.rpartition('}')[2]}"
    if tag in TEXT_CONTENT:
        is_textual = True
        if not textual_parent:
            elem.tail = "\n" + ending_level * TAB
    elif tag == "office:binary-data":
        is_textual = True
        elem.text = (
            textwrap.fill(
                elem.text,
                initial_indent=(ending_level + 11) * TAB,
                subsequent_indent=(follow_level * TAB)[:-1],
                width=79,
            ).lstrip()
            + "\n"
            + (follow_level - 1) * TAB
        )
        if not elem.tail:
            elem.tail = "\n" + ending_level * TAB
    else:
        is_textual = False
        if not textual_parent:
            elem.tail = "\n" + ending_level * TAB
            if nb_child > 0:
                elem.text = "\n" + follow_level * TAB
        else:
            if nb_child > 0:
                elem.text = (elem.text or "") + "\n" + follow_level * TAB
            if not elem.tail:
                elem.tail = "\n" + ending_level * TAB
    if nb_child > 0:
        for sub_elem in elem[:-1]:
            pretty_indent(sub_elem, follow_level, follow_level, is_textual)
        pretty_indent(elem[-1], follow_level, level, is_textual)
    return elem


def normalize_path(path: str) -> str:
    """Normalize a string path to Posix format.

    Args:
        path: The path to normalize.

    Returns:
        str: Posix representation of the path."""
    if path.endswith("/"):  # folder
        return PurePath(path[:-1]).as_posix() + "/"
    return PurePath(path).as_posix()


class Container:
    """Storage of the ODF document, as zip or other format."""

    def __init__(self, path: Path | str | io.BytesIO | None = None) -> None:
        """Storage of the ODF document, as zip or other format.

        Args:
            path: The path to the ODF file, a file-like object, or None.
        """
        self.__parts: dict[str, bytes | None] = {}
        self.__parts_ts: dict[str, int] = {}
        self.__path_like: Path | str | io.BytesIO | None = None
        self.__packaging: str = ZIP
        self.path: Path | None = None  # or Path
        if path:
            self.open(path)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} type={self.mimetype} path={self.path}>"

    def open(self, path_or_file: Path | str | io.BytesIO) -> None:
        """Load the content of an ODF file.

        Args:
            path_or_file: Path to the document, or an opened file.
        """
        self.__path_like = path_or_file
        if isinstance(path_or_file, (str, Path)):
            self.path = Path(path_or_file).expanduser()
            if not self.path.exists():
                raise FileNotFoundError(str(self.path))
            self.__path_like = self.path
        if (self.path or isinstance(self.__path_like, io.BytesIO)) and is_zipfile(
            self.__path_like
        ):
            self.__packaging = ZIP
            return self._read_zip()
        if self.path:
            is_folder = False
            with contextlib.suppress(OSError):
                is_folder = self.path.is_dir()
            if is_folder:
                self.__packaging = FOLDER
                return self._read_folder()
            # Check if it's a flat XML file
            with contextlib.suppress(OSError, ValueError):
                content = self.path.read_bytes()
                if self._is_flat_xml(content):
                    self.__packaging = XML
                    return self._read_xml(content)
        # Check if it's a BytesIO with flat XML
        if isinstance(self.__path_like, io.BytesIO):
            content = self.__path_like.getvalue()
            if self._is_flat_xml(content):
                self.__packaging = XML
                return self._read_xml(content)
        msg = f"Document format not managed by odfdo: {type(path_or_file)}."
        raise TypeError(msg)

    @staticmethod
    def _is_flat_xml(content: bytes) -> bool:
        """Check if content is a Flat ODF XML file.

        Args:
            content: The file content to check.

        Returns:
            True if the content appears to be a Flat ODF XML file.
        """
        # Must start with XML declaration or be parseable XML
        if not content.strip():
            return False
        if not content.lstrip().startswith(b"<?xml"):
            return False
        # Quick check for office:document element
        if b"office:document" not in content:
            return False
        try:
            root = fromstring(content)
        except (
            XMLSyntaxError,
            ValueError,
            TypeError,
        ):
            return False
        if root.tag != _ns_tag("document"):
            return False
        # Check for office:mimetype attribute
        mimetype = root.get(_ns_tag("mimetype"))
        if mimetype in ODF_MIMETYPES:
            return True
        # And accept if it has office:body child
        return root.find(_ns_tag("body")) is not None

    def _read_zip(self) -> None:
        if isinstance(self.__path_like, io.BytesIO):
            self.__path_like.seek(0)
        with ZipFile(self.__path_like) as zf:  # type: ignore
            mimetype = bytes_to_str(zf.read("mimetype"))
            if mimetype not in ODF_MIMETYPES:
                raise ValueError(f"Document of unknown type {mimetype}")
            self.__parts["mimetype"] = str_to_bytes(mimetype)
        if self.path is None:
            if isinstance(self.__path_like, io.BytesIO):
                self.__path_like.seek(0)
            # read the full file at once and forget file
            with ZipFile(self.__path_like) as zf:  # type: ignore
                for name in zf.namelist():
                    upath = normalize_path(name)
                    self.__parts[upath] = zf.read(name)
            self.__path_like = None

    def _read_folder(self) -> None:
        try:
            mimetype, timestamp = self._get_folder_part("mimetype")
        except OSError:
            msg = "Corrupted or not an OpenDocument folder (missing mimetype)"
            printwarn(msg)
            mimetype = b""
            timestamp = int(time.time())
        if bytes_to_str(mimetype) not in ODF_MIMETYPES:
            # Try to detect from content.xml if available
            detected = self._detect_mimetype_from_folder()
            if detected:
                msg = f"Document of unknown type {mimetype!r}, detected as {detected}."
                printwarn(msg)
                mimetype = str_to_bytes(detected)
            else:
                msg = f"Document of unknown type {mimetype!r}, try with ODF Text."
                printwarn(msg)
                mimetype = str_to_bytes(ODF_EXTENSIONS["odt"])
            self.__parts["mimetype"] = mimetype
            self.__parts_ts["mimetype"] = timestamp

    @staticmethod
    def _detect_image_mime_type(data: bytes) -> str:
        """Detect image mime type from file content."""
        if data.startswith(b"\xff\xd8\xff"):
            return "image/jpeg"
        if data.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"
        if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
            return "image/gif"
        if data.startswith(b"<?xml") or b"<svg" in data[:100]:
            return "image/svg+xml"
        if data.startswith(b"BM"):
            return "image/bmp"
        if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
            return "image/webp"
        return "application/octet-stream"

    @staticmethod
    def _image_mime_type_to_ext(mime_type: str) -> str:
        """Convert mime type to file extension."""
        mapping = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/gif": "gif",
            "image/svg+xml": "svg",
            "image/bmp": "bmp",
            "image/webp": "webp",
            "image/tiff": "tiff",
        }
        return mapping.get(mime_type, "bin")

    @staticmethod
    def _suffix_to_mime_type(
        suffix: str,
        default: str = "application/octet-stream",
    ) -> str:
        """Convert file extension to mime type."""
        mapping = {
            ".xml": "text/xml",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
        }
        return mapping.get(suffix.lower(), default)

    def _read_xml(self, content: bytes) -> None:
        """Read a Flat ODF XML file and extract parts.

        Args:
            content: The XML content as bytes.
        """
        root = fromstring(content)
        mimetype, original_nsmap = self._extract_mimetype_and_namespaces(root)
        self.__parts["mimetype"] = str_to_bytes(mimetype)

        content_root, styles_root = self._create_document_roots(original_nsmap)
        master_style_refs = self._collect_master_style_refs(root)
        image_parts = self._distribute_elements(
            root, content_root, styles_root, master_style_refs
        )

        # Process embedded content
        xlink_ns = "{http://www.w3.org/1999/xlink}"
        image_counter = self._process_embedded_images(
            content_root, styles_root, image_parts, xlink_ns
        )
        image_counter = self._process_fill_images(
            content_root, styles_root, image_parts, image_counter, xlink_ns
        )
        self._process_embedded_objects(content_root, xlink_ns)
        self._process_form_images(content_root, image_parts)

        # Store image parts
        for path, data in image_parts.items():
            if path not in self.__parts:
                self.__parts[path] = data

        self._serialize_documents(content_root, styles_root)
        self._create_manifest()

    def _detect_mimetype_from_content(self, root: _Element) -> str:
        """Detect mimetype from body content when attribute is missing.

        Args:
            root: The root element of the parsed XML.

        Returns:
            The detected mimetype string.
        """
        body = root.find(_ns_tag("body"))
        if body is not None:
            if body.find(_ns_tag("spreadsheet")) is not None:
                return ODF_EXTENSIONS["ods"]
            if body.find(_ns_tag("presentation")) is not None:
                return ODF_EXTENSIONS["odp"]
            if body.find(_ns_tag("drawing")) is not None:
                return ODF_EXTENSIONS["odg"]
            if body.find(_ns_tag("chart")) is not None:
                return ODF_EXTENSIONS["odc"]
            if body.find(_ns_tag("image")) is not None:
                return ODF_EXTENSIONS["odi"]
            if body.find(_ns_tag("formula")) is not None:
                return ODF_EXTENSIONS["odf"]
        return ODF_EXTENSIONS["odt"]

    def _detect_mimetype_from_folder(self) -> str | None:
        """Detect mimetype by examining content.xml in folder.

        Returns:
            The detected mimetype string or None if detection fails.
        """
        try:
            if self.path is None:
                return None
            content_path = self.path / "content.xml"
            if not content_path.exists():
                return None
            root = fromstring(content_path.read_bytes())
            return self._detect_mimetype_from_content(root)
        except Exception:
            return None

    def _extract_mimetype_and_namespaces(
        self, root: _Element
    ) -> tuple[str, dict[str, str]]:
        """Extract mimetype and namespaces from the root element.

        Args:
            root: The root element of the parsed XML.

        Returns:
            Tuple of (mimetype, original_nsmap).
        """
        mimetype = root.get(_ns_tag("mimetype"))
        if mimetype is None:
            mimetype = self._detect_mimetype_from_content(root)
        # Filter out None keys (default namespace) and manifest namespace
        original_nsmap = {
            prefix: uri
            for prefix, uri in root.nsmap.items()
            if prefix is not None
            and uri != "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"
        }
        return mimetype, original_nsmap

    def _create_document_roots(
        self, original_nsmap: dict[str, str]
    ) -> tuple[Element, Element]:
        """Create content and styles document roots.

        Args:
            original_nsmap: The original namespace map.

        Returns:
            Tuple of (content_root, styles_root).
        """
        content_root = Element(_ns_tag("document-content"), nsmap=original_nsmap)
        content_root.set(_ns_tag("version"), OFFICE_VERSION)

        styles_root = Element(_ns_tag("document-styles"), nsmap=original_nsmap)
        styles_root.set(_ns_tag("version"), OFFICE_VERSION)

        return content_root, styles_root

    def _collect_master_style_refs(self, root: _Element) -> set[str]:
        """Collect style names referenced from master-styles.

        These styles (like header/footer paragraph styles) need to stay in styles.xml.

        Args:
            root: The root element of the parsed XML.

        Returns:
            Set of style names referenced from master-styles.
        """
        ns_style = "{urn:oasis:names:tc:opendocument:xmlns:style:1.0}"
        ns_text = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"
        ns_draw = "{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}"
        ns_presentation = "{urn:oasis:names:tc:opendocument:xmlns:presentation:1.0}"
        master_style_refs: set[str] = set()

        for child in root:
            if child.tag == _ns_tag("master-styles"):
                for elem in child.iter():
                    style_ref = elem.get(f"{ns_text}style-name")
                    if style_ref:
                        master_style_refs.add(style_ref)
                    style_name = elem.get(f"{ns_style}name")
                    if style_name:
                        master_style_refs.add(style_name)
                    draw_style = elem.get(f"{ns_draw}style-name")
                    if draw_style:
                        master_style_refs.add(draw_style)
                    pres_style = elem.get(f"{ns_presentation}style-name")
                    if pres_style:
                        master_style_refs.add(pres_style)

        return master_style_refs

    def _distribute_elements(
        self,
        root: _Element,
        content_root: Element,
        styles_root: Element,
        master_style_refs: set[str],
    ) -> dict[str, bytes]:
        """Distribute child elements to content or styles roots.

        Args:
            root: The root element of the parsed XML.
            content_root: The content document root.
            styles_root: The styles document root.
            master_style_refs: Set of style names referenced from master-styles.

        Returns:
            Dictionary of image parts.
        """
        ns_style = "{urn:oasis:names:tc:opendocument:xmlns:style:1.0}"
        image_parts: dict[str, bytes] = {}

        for child in root:
            tag = child.tag
            if tag == _ns_tag("meta"):
                self._process_meta_element(child)
            elif tag == _ns_tag("document-meta"):
                self._process_document_meta_element(child)
            elif tag == _ns_tag("settings"):
                self._process_settings_element(child)
            elif tag == _ns_tag("automatic-styles"):
                self._process_automatic_styles(
                    child, content_root, styles_root, master_style_refs, ns_style
                )
            elif tag in {
                _ns_tag("styles"),
                _ns_tag("master-styles"),
                _ns_tag("font-face-decls"),
            }:
                self._merge_or_append_to_styles(child, styles_root)
            else:
                content_root.append(child)

        return image_parts

    def _process_meta_element(self, meta: _Element) -> None:
        """Process meta element and store as meta.xml."""
        meta_root = Element(
            _ns_tag("document-meta"),
            nsmap={
                "office": NS_OFFICE,
                "meta": "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
                "dc": "http://purl.org/dc/elements/1.1/",
            },
        )
        meta_root.set(_ns_tag("version"), OFFICE_VERSION)
        meta_root.append(meta)
        meta_xml = XML_TAG + tostring(
            meta_root, encoding="UTF-8", xml_declaration=False
        )
        self.__parts[ODF_META] = meta_xml

    def _process_document_meta_element(self, doc_meta: _Element) -> None:
        """Process document-meta element (already wrapped) and store as meta.xml."""
        meta_xml = XML_TAG + tostring(doc_meta, encoding="UTF-8", xml_declaration=False)
        self.__parts[ODF_META] = meta_xml

    def _process_settings_element(self, settings: _Element) -> None:
        """Process settings element and store as settings.xml."""
        settings_xml = XML_TAG + (
            b"<office:document-settings xmlns:office="
            b'"urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            b'xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0">'
        )
        for settings_child in settings:
            settings_xml += tostring(
                settings_child, encoding="UTF-8", xml_declaration=False
            )
        settings_xml += b"</office:document-settings>"
        self.__parts[ODF_SETTINGS] = settings_xml

    def _process_automatic_styles(
        self,
        auto_styles: _Element,
        content_root: Element,
        styles_root: Element,
        master_style_refs: set[str],
        ns_style: str,
    ) -> None:
        """Distribute automatic-styles to content or styles roots.

        - Styles referenced from master-styles go to styles.xml
        - Page layouts go to styles.xml
        - Everything else goes to content.xml
        """
        content_auto = content_root.find(_ns_tag("automatic-styles"))
        if content_auto is None:
            content_auto = Element(_ns_tag("automatic-styles"))
            content_root.insert(0, content_auto)

        styles_auto = styles_root.find(_ns_tag("automatic-styles"))
        if styles_auto is None:
            styles_auto = Element(_ns_tag("automatic-styles"))
            styles_root.append(styles_auto)

        for grandchild in auto_styles:
            tag_name = grandchild.tag.split("}")[-1]
            style_name = grandchild.get(f"{ns_style}name")
            is_page_layout = tag_name == "page-layout"
            is_master_style = style_name is not None and style_name in master_style_refs

            if is_page_layout or is_master_style:
                styles_auto.append(grandchild)
            else:
                content_auto.append(grandchild)

    def _merge_or_append_to_styles(self, child: _Element, styles_root: Element) -> None:
        """Merge child into styles root or append if not exists."""
        tag = child.tag
        existing = styles_root.find(tag)
        if existing is not None:
            for grandchild in child:
                existing.append(grandchild)
        else:
            styles_root.append(child)

    def _process_embedded_images(
        self,
        content_root: Element,
        styles_root: Element,
        image_parts: dict[str, bytes],
        xlink_ns: str,
    ) -> int:
        """Process draw:image elements with office:binary-data.

        Returns:
            The updated image counter.
        """
        ns_draw = "{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}"
        xpath_expr = xpath_compile("descendant::draw:image[office:binary-data]")
        image_counter = 0

        for root_elem in (content_root, styles_root):
            for img_elem in xpath_expr(root_elem):
                binary_data_elem = img_elem.find(_ns_tag("binary-data"))
                if binary_data_elem is not None and binary_data_elem.text:
                    try:
                        image_data = base64.standard_b64decode(
                            binary_data_elem.text.strip()
                        )
                        mime_type = img_elem.get(f"{ns_draw}mime-type")
                        if mime_type is None or mime_type == "None":
                            mime_type = self._detect_image_mime_type(image_data)
                        ext = self._image_mime_type_to_ext(mime_type)

                        image_counter += 1
                        image_path = f"Pictures/image{image_counter}.{ext}"
                        image_parts[image_path] = image_data

                        img_elem.remove(binary_data_elem)
                        img_elem.set(f"{xlink_ns}href", image_path)
                        img_elem.set(f"{xlink_ns}type", "simple")
                        img_elem.set(f"{xlink_ns}show", "embed")
                        img_elem.set(f"{xlink_ns}actuate", "onLoad")
                    except Exception as e:
                        printwarn(f"Failed to decode embedded image: {e}")

        return image_counter

    def _process_fill_images(
        self,
        content_root: Element,
        styles_root: Element,
        image_parts: dict[str, bytes],
        image_counter: int,
        xlink_ns: str,
    ) -> int:
        """Process draw:fill-image elements with office:binary-data.

        Returns:
            The updated image counter.
        """
        xpath_fill_expr = xpath_compile(
            "descendant::draw:fill-image[office:binary-data]"
        )

        for root_elem in (content_root, styles_root):
            for fill_img_elem in xpath_fill_expr(root_elem):
                binary_data_elem = fill_img_elem.find(_ns_tag("binary-data"))
                if binary_data_elem is None or not binary_data_elem.text:
                    continue
                try:
                    image_data = base64.standard_b64decode(
                        binary_data_elem.text.strip()
                    )
                    mime_type = self._detect_image_mime_type(image_data)
                    ext = self._image_mime_type_to_ext(mime_type)

                    image_counter += 1
                    image_path = f"Pictures/image{image_counter}.{ext}"
                    image_parts[image_path] = image_data

                    fill_img_elem.remove(binary_data_elem)
                    fill_img_elem.set(f"{xlink_ns}href", image_path)
                    fill_img_elem.set(f"{xlink_ns}type", "simple")
                except Exception as e:
                    printwarn(f"Failed to decode embedded fill image: {e}")

        return image_counter

    def _process_embedded_objects(self, content_root: Element, xlink_ns: str) -> None:
        """Process draw:object elements with embedded content."""
        object_counter = 0
        xpath_obj_expr = xpath_compile("descendant::draw:object[office:document]")

        for obj_elem in xpath_obj_expr(content_root):
            try:
                object_counter += 1
                obj_path = f"Object {object_counter}"

                doc_wrapper = obj_elem.find(_ns_tag("document"))
                # Can not happen: XPath already filters for objects with document
                if doc_wrapper is None:  # pragma: no cover
                    continue

                # Create object content.xml from body
                body_elem = doc_wrapper.find(_ns_tag("body"))
                if body_elem is not None:
                    content_root_elem = Element(
                        _ns_tag("document-content"),
                        nsmap={"office": NS_OFFICE},
                    )
                    content_root_elem.set(_ns_tag("version"), OFFICE_VERSION)
                    for child in list(body_elem):
                        content_root_elem.append(child)

                    obj_content_xml = XML_TAG + tostring(
                        content_root_elem, encoding="UTF-8", xml_declaration=False
                    )
                    self.__parts[f"{obj_path}/content.xml"] = obj_content_xml

                # Extract styles
                auto_styles = doc_wrapper.find(_ns_tag("automatic-styles"))
                if auto_styles is not None:
                    styles_root_elem = Element(
                        _ns_tag("document-styles"),
                        nsmap={
                            "office": NS_OFFICE,
                            "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
                        },
                    )
                    styles_root_elem.set(_ns_tag("version"), OFFICE_VERSION)
                    styles_root_elem.append(auto_styles)

                    obj_styles_xml = XML_TAG + tostring(
                        styles_root_elem, encoding="UTF-8", xml_declaration=False
                    )
                    self.__parts[f"{obj_path}/styles.xml"] = obj_styles_xml

                # Extract meta
                meta_elem = doc_wrapper.find(_ns_tag("meta"))
                if meta_elem is not None:
                    meta_root_elem = Element(
                        _ns_tag("document-meta"),
                        nsmap={
                            "office": NS_OFFICE,
                            "meta": "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
                        },
                    )
                    meta_root_elem.set(_ns_tag("version"), OFFICE_VERSION)
                    for child in list(meta_elem):
                        meta_root_elem.append(child)

                    obj_meta_xml = XML_TAG + tostring(
                        meta_root_elem, encoding="UTF-8", xml_declaration=False
                    )
                    self.__parts[f"{obj_path}/meta.xml"] = obj_meta_xml

                # Replace the embedded object with a reference
                for child in list(obj_elem):
                    obj_elem.remove(child)
                obj_elem.set(f"{xlink_ns}href", f"./{obj_path}")
                obj_elem.set(f"{xlink_ns}type", "simple")
                obj_elem.set(f"{xlink_ns}show", "embed")
                obj_elem.set(f"{xlink_ns}actuate", "onLoad")

            except Exception as e:
                printwarn(f"Failed to extract embedded object: {e}")

    def _process_form_images(
        self, content_root: Element, image_parts: dict[str, bytes]
    ) -> None:
        """Process form elements with embedded image data."""
        ns_form = "{urn:oasis:names:tc:opendocument:xmlns:form:1.0}"
        xpath_form_img = xpath_compile("descendant::form:*[office:binary-data]")
        image_counter = 0

        for form_elem in xpath_form_img(content_root):
            binary_data_elem = form_elem.find(_ns_tag("binary-data"))
            if binary_data_elem is None or not binary_data_elem.text:
                continue
            try:
                image_data = base64.standard_b64decode(binary_data_elem.text.strip())
                mime_type = self._detect_image_mime_type(image_data)
                ext = self._image_mime_type_to_ext(mime_type)

                image_counter += 1
                image_path = f"Pictures/image{image_counter}.{ext}"
                image_parts[image_path] = image_data

                form_elem.remove(binary_data_elem)
                form_elem.set(f"{ns_form}image-data", image_path)
            except Exception as e:
                printwarn(f"Failed to decode embedded form image: {e}")

    def _serialize_documents(self, content_root: Element, styles_root: Element) -> None:
        """Serialize content.xml and styles.xml."""
        if len(content_root) > 0:
            content_xml = XML_TAG + tostring(
                content_root, encoding="UTF-8", xml_declaration=False
            )
            self.__parts[ODF_CONTENT] = content_xml

        if len(styles_root) > 0:
            styles_xml = XML_TAG + tostring(
                styles_root, encoding="UTF-8", xml_declaration=False
            )
            self.__parts[ODF_STYLES] = styles_xml

    def _create_manifest(self) -> None:
        """Create the META-INF/manifest.xml from current parts."""
        manifest_parts = [
            XML_TAG,
            b'<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">\n',
        ]

        # Add mimetype entry
        mimetype = (
            self.__parts.get("mimetype") or b"application/vnd.oasis.opendocument.text"
        )

        manifest_parts.append(
            f'<manifest:file-entry manifest:media-type="{mimetype.decode()}" manifest:full-path="/"/>\n'.encode()
        )

        # Add entries for each part
        for path, data in self.__parts.items():
            if data is None or path == "mimetype":
                continue
            # Determine media type based on path
            media_type = self._suffix_to_mime_type(Path(path).suffix)
            manifest_parts.append(
                f'<manifest:file-entry manifest:media-type="{media_type}" manifest:full-path="{path}"/>\n'.encode()
            )

        manifest_parts.append(b"</manifest:manifest>")
        self.__parts[ODF_MANIFEST] = b"".join(manifest_parts)

    def _parse_folder(self, folder: str) -> list[str]:
        parts = []
        if self.path is None:
            raise ValueError("Document path is not defined")
        root = self.path / folder
        for path in root.iterdir():
            if path.name.startswith("."):  # no hidden files
                continue
            relative_path = path.relative_to(self.path)
            if path.is_file():
                parts.append(relative_path.as_posix())
            if path.is_dir():
                sub_parts = self._parse_folder(str(relative_path))
                if sub_parts:
                    parts.extend(sub_parts)
                else:
                    # store leaf directories
                    parts.append(relative_path.as_posix() + "/")
        return parts

    def _get_folder_parts(self) -> list[str]:
        """Get the list of members in the ODF folder."""
        return self._parse_folder("")

    def _get_folder_part(self, name: str) -> tuple[bytes, int]:
        """Get bytes of a part from the ODF folder, with timestamp."""
        if self.path is None:
            raise ValueError("Document path is not defined")
        path = self.path / name
        timestamp = int(path.stat().st_mtime)
        if path.is_dir():
            return (b"", timestamp)
        return (path.read_bytes(), timestamp)

    def _get_folder_part_timestamp(self, name: str) -> int:
        if self.path is None:
            raise ValueError("Document path is not defined")
        path = self.path / name
        try:
            timestamp = int(path.stat().st_mtime)
        except OSError:
            timestamp = -1
        return timestamp

    def _get_zip_part(self, name: str) -> bytes | None:
        """Get bytes of a part from the Zip ODF file.

        No cache.
        """
        if self.path is None:
            raise ValueError("Document path is not defined")
        try:
            with ZipFile(self.path) as zf:
                upath = normalize_path(name)
                self.__parts[upath] = zf.read(name)
                return self.__parts[upath]
        except BadZipfile:
            return None

    def _get_all_zip_part(self) -> None:
        """Read all parts.

        No cache.
        """
        if self.path is None:
            raise ValueError("Document path is not defined")
        try:
            with ZipFile(self.path) as zf:
                for name in zf.namelist():
                    upath = normalize_path(name)
                    self.__parts[upath] = zf.read(name)
        except BadZipfile:
            pass

    def _save_zip(self, target: str | Path | io.BytesIO) -> None:
        """Save a Zip ODF from the available parts."""
        parts = self.__parts
        with ZipFile(target, "w", compression=ZIP_DEFLATED) as filezip:
            # Parts to save, except manifest at the end
            part_names = list(parts.keys())
            try:
                part_names.remove(ODF_MANIFEST)
            except ValueError:
                printwarn(f"Missing '{ODF_MANIFEST}'")
            # "Pretty-save" parts in some order
            # mimetype requires to be first and uncompressed
            mimetype = parts.get("mimetype")
            if mimetype is None:
                raise ValueError("Mimetype is not defined")
            try:
                filezip.writestr("mimetype", mimetype, ZIP_STORED)
                part_names.remove("mimetype")
            except (
                ValueError,
                KeyError,
            ):
                printwarn("Missing 'mimetype'")
            # XML parts
            for path in ODF_CONTENT, ODF_META, ODF_SETTINGS, ODF_STYLES:
                if path not in parts:
                    printwarn(f"Missing '{path}'")
                    continue
                part = parts[path]
                if part is None:
                    continue
                filezip.writestr(path, part)
                part_names.remove(path)
            # Everything else
            for path in part_names:
                data = parts[path]
                if data is None:
                    # Deleted
                    continue
                filezip.writestr(path, data)
            with contextlib.suppress(KeyError):
                part = parts[ODF_MANIFEST]
                if part is not None:
                    filezip.writestr(ODF_MANIFEST, part)

    def _save_folder(self, folder: Path | str) -> None:
        """Save a folder ODF from the available parts."""

        def dump(part_path: str, content: bytes) -> None:
            if part_path.endswith("/"):  # folder
                is_folder = True
                pure_path = PurePath(folder, part_path[:-1])
            else:
                is_folder = False
                pure_path = PurePath(folder, part_path)
            path = Path(pure_path)
            if is_folder:
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
                path.chmod(0o666)

        for part_path, data in self.__parts.items():
            if data is None:
                # Deleted
                continue
            dump(part_path, data)

    def _encoded_image(self, elem: _Element) -> _Element | None:
        mime_type = elem.get(
            "{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}mime-type"
        )
        path = elem.get("{http://www.w3.org/1999/xlink}href")
        if not path:
            return None
        path = path.lstrip("./")
        content = self.__parts[path]
        if not content:
            return None
        text = base64.standard_b64encode(content).decode()
        # Only include mime-type attribute if it's a valid value
        if mime_type and mime_type != "None":
            ebytes = (
                f'<draw:image draw:mime-type="{mime_type}">'
                f"<office:binary-data>{text}\n</office:binary-data></draw:image>"
            ).encode()
        else:
            ebytes = (
                f"<draw:image>"
                f"<office:binary-data>{text}\n</office:binary-data></draw:image>"
            ).encode()
        root = fromstring(NAMESPACES_XML % ebytes)
        return root[0]

    def _embed_form_image_data(self, elem: _Element, image_path: str) -> None:
        """Embed image data for form elements with form:image-data attribute.

        Form elements (like image buttons) reference images via form:image-data
        attribute. We need to embed the image as base64 and replace the
        attribute reference with the embedded data.
        """
        # Strip leading "./" from path
        path = image_path.lstrip("./")
        content = self.__parts.get(path)
        if not content:
            return

        # Encode the image as base64
        text = base64.standard_b64encode(content).decode()

        # Create the office:binary-data element
        binary_data_elem = Element(_ns_tag("binary-data"))
        binary_data_elem.text = text + "\n"

        # Append the binary-data element to the form element
        elem.append(binary_data_elem)

    def _encoded_fill_image(self, elem: _Element) -> _Element | None:
        """Encode a draw:fill-image element with binary data.

        draw:fill-image elements reference images via xlink:href and are used
        for background images in presentations.
        """
        path = elem.get("{http://www.w3.org/1999/xlink}href")
        if not path:
            return None
        # Strip leading "./" from path (e.g., "./Pictures/image.jpg")
        path = path.lstrip("./")
        content = self.__parts[path]
        if not content:
            return None
        # mime_type = self._suffix_to_mime_type(Path(path).suffix, "image/jpeg")
        name = elem.get("{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}name")
        display_name = elem.get(
            "{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}display-name"
        )
        text = base64.standard_b64encode(content).decode()
        # Build the element with preserved attributes
        attrs = []
        if name:
            attrs.append(f'draw:name="{name}"')
        if display_name:
            attrs.append(f'draw:display-name="{display_name}"')
        attr_str = " ".join(attrs)
        if attr_str:
            attr_str = " " + attr_str
        ebytes = (
            f"<draw:fill-image{attr_str}>"
            f"<office:binary-data>{text}\n</office:binary-data></draw:fill-image>"
        ).encode()
        root = fromstring(NAMESPACES_XML % ebytes)
        return root[0]

    def _encoded_object(self, elem: _Element) -> _Element | None:
        """Encode a draw:object element by embedding the object content.

        draw:object elements reference embedded ODF objects (like charts)
        via xlink:href. In flat format, we need to embed the object content
        directly as an office:document structure.
        """
        path = elem.get("{http://www.w3.org/1999/xlink}href")
        if not path:
            return None
        # Strip leading "./" from path (e.g., "./Object 1")
        path = path.lstrip("./")

        # Check if we have parts for this object (Object 1/content.xml, etc.)
        content_path = f"{path}/content.xml"
        styles_path = f"{path}/styles.xml"
        meta_path = f"{path}/meta.xml"

        # If we don't have the object parts, return None to keep original reference
        if content_path not in self.__parts:
            return None

        # Parse the content.xml
        try:
            content_doc = fromstring(self.__parts[content_path])
        except Exception:
            return None

        # Create a new office:document element with the same namespace map
        # This preserves all namespace declarations from the original
        obj_doc = Element(_ns_tag("document"), nsmap=content_doc.nsmap)

        # Add required office:document attributes
        obj_doc.set(_ns_tag("mimetype"), "application/vnd.oasis.opendocument.chart")
        obj_doc.set(_ns_tag("version"), OFFICE_VERSION)

        # Force all namespace declarations by adding dummy attributes
        # lxml optimizes away namespace declarations if they're already in scope
        # We add them with a unique suffix to prevent optimization
        for prefix, uri in content_doc.nsmap.items():
            if prefix and prefix != "office":
                # Use a special attribute that won't conflict with real ones
                dummy_attr = f"{{{uri}}}__{prefix}__decl"
                obj_doc.set(dummy_attr, "")

        # Add meta if available
        if self.__parts.get(meta_path):
            try:
                meta_root = fromstring(self.__parts[meta_path])
                for child in meta_root:
                    obj_doc.append(child)
            except Exception as e:
                printwarn(f"Error in meta {e}")

        # Add empty styles (objects often don't have separate styles)
        styles_elem = Element(_ns_tag("styles"))
        obj_doc.append(styles_elem)

        # Add automatic-styles from styles.xml if available
        if self.__parts.get(styles_path):
            try:
                styles_root = fromstring(self.__parts[styles_path])
                auto_styles = styles_root.find(_ns_tag("automatic-styles"))
                if auto_styles is not None:
                    obj_doc.append(auto_styles)
            except Exception as e:
                printwarn(f"Error in styles path {e}")

        # Extract automatic-styles from content and add to obj_doc
        content_auto_styles = content_doc.find(_ns_tag("automatic-styles"))
        if content_auto_styles is not None:
            obj_doc.append(content_auto_styles)

        # Add body with content from content.xml
        body_elem = Element(_ns_tag("body"))
        content_body = content_doc.find(_ns_tag("body"))
        if content_body is not None:
            for child in content_body:
                body_elem.append(child)
        else:
            # If no office:body, add all children except automatic-styles
            for child in content_doc:
                if child.tag != _ns_tag("automatic-styles"):
                    body_elem.append(child)
        obj_doc.append(body_elem)

        # Create the draw:object element with the embedded content
        # To preserve namespace declarations, we need to serialize and re-parse
        # because lxml optimizes them away when appending to parent
        new_obj = Element("{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}object")

        # Serialize the embedded document to a string
        obj_doc_str = tostring(obj_doc, encoding="unicode", pretty_print=False)

        # Parse it back and append to new_obj
        # This preserves the namespace declarations from the original serialization
        obj_doc_parsed = fromstring(obj_doc_str.encode("utf-8"))
        new_obj.append(obj_doc_parsed)

        return new_obj

    def _xml_content(self, pretty: bool = True) -> bytes:
        mimetype_b = self.__parts["mimetype"]
        if mimetype_b is None:
            # use some default
            mimetype = "application/vnd.oasis.opendocument.text"
        else:
            mimetype = mimetype_b.decode("utf8")
        doc_xml = (
            OFFICE_PREFIX.decode("utf8")
            + f'office:version="{OFFICE_VERSION}"\n'
            + f'office:mimetype="{mimetype}">'
            + "</office:document>"
        )
        root = fromstring(doc_xml.encode("utf8"))
        for path in ODF_META, ODF_SETTINGS, ODF_STYLES, ODF_CONTENT:
            if path not in self.__parts:
                printwarn(f"Missing '{path}'")
                continue
            part = self.__parts[path]
            if part is None:
                continue
            if isinstance(part, bytes):
                xpart = fromstring(part)
            else:
                xpart = part
            if path in {ODF_CONTENT, ODF_STYLES}:
                # Process draw:image elements (both content and styles)
                xpath = xpath_compile("descendant::draw:image")
                images = xpath(xpart)
                if images:
                    for elem in images:
                        encoded = self._encoded_image(elem)
                        if encoded is not None:
                            elem.getparent().replace(elem, encoded)
                # Process draw:fill-image elements (used for background images in presentations)
                xpath_fill = xpath_compile("descendant::draw:fill-image")
                fill_images = xpath_fill(xpart)
                if fill_images:
                    for elem in fill_images:
                        encoded = self._encoded_fill_image(elem)
                        if encoded is not None:
                            elem.getparent().replace(elem, encoded)
                # Process draw:object elements (embedded objects like charts)
                if path == ODF_CONTENT:
                    xpath_obj = xpath_compile("descendant::draw:object")
                    objects = xpath_obj(xpart)
                    if objects:
                        for elem in objects:
                            encoded = self._encoded_object(elem)
                            if encoded is not None:
                                elem.getparent().replace(elem, encoded)
                    # Process form elements with form:image-data attribute
                    # (used for form control images like buttons with images)
                    ns_form = "{urn:oasis:names:tc:opendocument:xmlns:form:1.0}"
                    xpath_form = xpath_compile("descendant::form:*[@form:image-data]")
                    form_elems = xpath_form(xpart)
                    if form_elems:
                        for elem in form_elems:
                            image_path = elem.get(f"{ns_form}image-data")
                            if image_path:
                                self._embed_form_image_data(elem, image_path)
            for child in xpart:
                root.append(child)
        if pretty:
            bytes_tree: bytes = tostring(
                pretty_indent(root),
                encoding="unicode",
            ).encode("utf8")
            return XML_TAG + bytes_tree
        else:
            return tostring(  # type: ignore[no-any-return]
                root,
                encoding="UTF-8",
                xml_declaration=True,
            )

    def _save_xml(
        self,
        target: Path | str | io.BytesIO,
        pretty: bool = True,
    ) -> None:
        """Save a XML flat ODF format from the available parts."""
        if isinstance(target, (Path, str)):
            target_path = Path(target)
            # Preserve Flat ODF extension is exists, default to .xml
            if target_path.suffix.lower() not in ODF_FLAT_EXTENSIONS:
                target_path = target_path.with_suffix(".xml")
            target_path.write_bytes(self._xml_content(pretty))
        else:
            target.write(self._xml_content(pretty))

    # Public API

    def get_parts(self) -> list[str]:
        """Get the list of the parts in the Container.

        Returns:
            The list of path of the parts in the Container.
        """
        if not self.path:
            # maybe a file like zip archive or xml
            return list(self.__parts.keys())
        if self.__packaging == ZIP:
            parts = []
            with ZipFile(self.path) as zf:
                for name in zf.namelist():
                    upath = normalize_path(name)
                    parts.append(upath)
            return parts
        elif self.__packaging == FOLDER:
            return self._get_folder_parts()
        elif self.__packaging == XML:
            # For flat XML, parts are stored in memory
            return list(self.__parts.keys())
        else:
            raise ValueError("Unable to provide parts of the document")

    @property
    def parts(self) -> list[str]:
        """Get the list of the parts in the Container.

        Returns:
            The list of path of the parts in the Container.
        """
        return self.get_parts()

    def get_part(self, path: str) -> str | bytes | None:
        """Get the actual content of a part of the ODF Container.

        Args:
            path: path of the required part.

        Returns:
            The actual content of the part.
        """
        path = str(path)
        if path in self.__parts:
            part = self.__parts[path]
            if part is None:
                raise ValueError(f'Part "{path}" is deleted')
            if self.__packaging == FOLDER:
                cache_ts = self.__parts_ts.get(path, -1)
                current_ts = self._get_folder_part_timestamp(path)
                if current_ts != cache_ts:
                    part, timestamp = self._get_folder_part(path)
                    self.__parts[path] = part
                    self.__parts_ts[path] = timestamp
            return part
        if self.__packaging == ZIP:
            return self._get_zip_part(path)
        if self.__packaging == FOLDER:
            part, timestamp = self._get_folder_part(path)
            self.__parts[path] = part
            self.__parts_ts[path] = timestamp
            return part
        return None

    @property
    def default_manifest_rdf(self) -> str:
        return (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<rdf:RDF xmlns:rdf="http://www.w3.org/'
            '1999/02/22-rdf-syntax-ns#">\n'
            '  <rdf:Description rdf:about="styles.xml">\n'
            '    <rdf:type rdf:resource="http://docs.oasis-open.org/'
            f'ns/office/{OFFICE_VERSION}/meta/odf#StylesFile"/>\n'
            "  </rdf:Description>\n"
            '  <rdf:Description rdf:about="">\n'
            '    <ns0:hasPart xmlns:ns0="http://docs.oasis-open.org/ns/'
            f'office/{OFFICE_VERSION}/meta/pkg#" rdf:resource="styles.xml"/>\n'
            "  </rdf:Description>\n"
            '  <rdf:Description rdf:about="content.xml">\n'
            '    <rdf:type rdf:resource="http://docs.oasis-open.org/'
            f'ns/office/{OFFICE_VERSION}/meta/odf#ContentFile"/>\n'
            "  </rdf:Description>\n"
            '  <rdf:Description rdf:about="">\n'
            '    <ns0:hasPart xmlns:ns0="http://docs.oasis-open.org/ns/office'
            f'/{OFFICE_VERSION}/meta/pkg#" rdf:resource="content.xml"/>\n'
            "  </rdf:Description>\n"
            '  <rdf:Description rdf:about="">\n'
            '    <rdf:type rdf:resource="http://docs.oasis-open.org/ns/office'
            f'/{OFFICE_VERSION}/meta/pkg#Document"/>\n'
            "  </rdf:Description>\n"
            "</rdf:RDF>\n"
        )

    @property
    def mimetype(self) -> str:
        """Return str value of mimetype of the document."""
        with contextlib.suppress(Exception):
            b_mimetype = self.get_part("mimetype")
            if isinstance(b_mimetype, bytes):
                return bytes_to_str(b_mimetype)
        return ""

    @mimetype.setter
    def mimetype(self, mimetype: str | bytes) -> None:
        """Set mimetype value of the document."""
        if isinstance(mimetype, str):
            self.__parts["mimetype"] = str_to_bytes(mimetype)
        elif isinstance(mimetype, bytes):
            self.__parts["mimetype"] = mimetype
        else:
            raise TypeError(f'Wrong mimetype "{mimetype!r}"')

    def set_part(self, path: str, data: bytes) -> None:
        """Replace or add a new part.

        Args:
            path: The relative path in the Container.
            data: Content of the part.
        """
        self.__parts[path] = data

    def del_part(self, path: str) -> None:
        """Mark a part for deletion.

        Args:
            path: The relative path in the Container.
        """
        self.__parts[path] = None

    @property
    def clone(self) -> Container:
        """Make a copy of this container with no path."""
        if self.path and self.__packaging == ZIP:
            self._get_all_zip_part()
        clone = deepcopy(self)
        clone.path = None
        return clone

    def _backup_or_unlink(self, backup: bool, target: str | Path) -> None:
        if backup:
            self._do_backup(target)
        else:
            self._do_unlink(target)

    @staticmethod
    def _do_backup(target: str | Path) -> None:
        path = Path(target)
        if not path.exists():
            return
        back_file = path.parent / (path.stem + ".backup" + path.suffix)
        if back_file.is_dir():
            try:
                shutil.rmtree(back_file)
            except OSError as e:
                printwarn(str(e))
        try:
            shutil.move(target, back_file)
        except OSError as e:
            printwarn(str(e))

    @staticmethod
    def _do_unlink(target: str | Path) -> None:
        path = Path(target)
        if path.exists():
            try:
                shutil.rmtree(path)
            except OSError as e:
                printwarn(str(e))

    def _clean_save_packaging(self, packaging: str | None) -> str:
        if not packaging:
            packaging = self.__packaging if self.__packaging else ZIP
        packaging = packaging.strip().lower()
        if packaging not in PACKAGING:
            msg = f'Packaging of type "{packaging}" is not supported'
            raise ValueError(msg)
        return packaging

    def _clean_save_target(
        self,
        target: str | Path | io.BytesIO | None,
    ) -> str | io.BytesIO:
        if target is None:
            target = self.path
        if isinstance(target, Path):
            target = str(target)
        if isinstance(target, str):
            while target.endswith(os.sep):
                target = target[:-1]
            while target.endswith(".folder"):
                target = target.split(".folder", 1)[0]
        return target  # type: ignore

    def _save_as_zip(
        self,
        target: str | Path | io.BytesIO,
        backup: bool,
    ) -> None:
        if isinstance(target, (str, Path)) and backup:
            self._do_backup(target)
        self._save_zip(target)

    def _save_as_folder(self, target: str | Path, backup: bool) -> None:
        if not isinstance(target, (str, Path)):
            raise TypeError(
                f"Saving in folder format requires a folder name, not '{target!r}'"
            )
        if not str(target).endswith(".folder"):
            target = str(target) + ".folder"
        self._backup_or_unlink(backup, target)
        self._save_folder(target)

    def _save_as_xml(
        self,
        target: str | Path | io.BytesIO,
        backup: bool,
        pretty: bool = True,
    ) -> None:
        if not isinstance(target, (str, Path, io.BytesIO)):
            raise TypeError(
                f"Saving in XML format requires a path name, not '{target!r}'"
            )
        if isinstance(target, (str, Path)):
            target_path = Path(target)
            suffix = target_path.suffix.lower()
            if suffix not in ODF_FLAT_EXTENSIONS and suffix != ".xml":
                flat_ext = ODF_MIMETYPE_TO_FLAT_EXTENSION.get(self.mimetype, ".xml")
                target_path = target_path.with_suffix(flat_ext)
            if backup:
                self._do_backup(target_path)
            self._save_xml(target_path, pretty)
        else:
            self._save_xml(target, pretty)

    def save(
        self,
        target: str | Path | io.BytesIO | None,
        packaging: str | None = None,
        backup: bool = False,
        pretty: bool = False,
    ) -> None:
        """Save the container to the given target, a path or a file-like
        object.

        Package the output document in the same format than current document,
        unless "packaging" is different.

        Args:
            target: The path, file-like object, or Path object where the
                document will be saved.
            packaging: The packaging format to use. Can be 'zip', 'xml', or
                'folder'. If None, the current packaging is used.
            backup: If True, a backup of the original file is created.
            pretty: If True, the XML output will be pretty-printed.
        """
        parts = self.__parts
        packaging = self._clean_save_packaging(packaging)
        # Load parts else they will be considered deleted
        for path in self.parts:
            if path not in parts:
                self.get_part(path)
        target = self._clean_save_target(target)
        if packaging == FOLDER:
            if isinstance(target, io.BytesIO):
                msg = "Impossible to save on io.BytesIO with 'folder' packaging"
                raise TypeError(msg)
            self._save_as_folder(target, backup)
        elif packaging == XML:
            self._save_as_xml(target, backup, pretty)
        else:
            # default:
            self._save_as_zip(target, backup)
