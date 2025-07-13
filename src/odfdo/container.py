# Copyright 2018-2025 Jérôme Dumonteil
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
from pathlib import Path, PurePath
from zipfile import ZIP_DEFLATED, ZIP_STORED, BadZipfile, ZipFile, is_zipfile

from lxml.etree import _Element, _ElementTree, fromstring, tostring

from .const import (
    FOLDER,
    ODF_CONTENT,
    ODF_EXTENSIONS,
    ODF_MANIFEST,
    ODF_META,
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
    "text:span",
    "text:subject",
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

# "office:binary-data" removed,


def printwarn(message: str) -> None:
    print(f"Warning: {message}", file=sys.stderr)


def pretty_indent(
    elem: _ElementTree | _Element,
    level: int = 0,
    ending_level: int = 0,
    textual_parent: bool = False,
) -> _ElementTree | _Element:
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
    if path.endswith("/"):  # folder
        return PurePath(path[:-1]).as_posix() + "/"
    return PurePath(path).as_posix()


class Container:
    """Storage of the ODF document, as zip or other format."""

    def __init__(self, path: Path | str | io.BytesIO | None = None) -> None:
        """Storage of the ODF document, as zip or other format.

        Arguments:

        path -- path like, io.BytesIO or None
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
        """Load the content of an ODF file."""
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
        raise TypeError(f"Document format not managed by odfdo: {type(path_or_file)}.")

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
            printwarn("Corrupted or not an OpenDocument folder (missing mimetype)")
            mimetype = b""
            timestamp = int(time.time())
        if bytes_to_str(mimetype) not in ODF_MIMETYPES:
            message = f"Document of unknown type {mimetype!r}, try with ODF Text."
            printwarn(message)
            self.__parts["mimetype"] = str_to_bytes(ODF_EXTENSIONS["odt"])
            self.__parts_ts["mimetype"] = timestamp

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
        """Get bytes of a part from the Zip ODF file. No cache."""
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
        """Read all parts. No cache."""
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
            except (ValueError, KeyError):
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
        content = self.__parts[path]
        if not content:
            return None
        text = base64.standard_b64encode(content).decode()
        ebytes = (
            f'<draw:image draw:mime-type="{mime_type}">'
            f"<office:binary-data>{text}\n</office:binary-data></draw:image>"
        ).encode()
        root = fromstring(NAMESPACES_XML % ebytes)
        return root[0]

    def _xml_content(self, pretty: bool = True) -> bytes:
        mimetype = self.__parts["mimetype"].decode("utf8")
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
            if path == ODF_CONTENT:
                xpath = xpath_compile("descendant::draw:image")
                images = xpath(xpart)
                if images:
                    for elem in images:
                        encoded = self._encoded_image(elem)
                        elem.getparent().replace(elem, encoded)
            for child in xpart:
                root.append(child)
        if pretty:
            xml_header = b'<?xml version="1.0" encoding="UTF-8"?>\n'
            bytes_tree = tostring(
                pretty_indent(root),
                encoding="unicode",
            ).encode("utf8")
            return xml_header + bytes_tree
        else:
            return tostring(root, encoding="UTF-8", xml_declaration=True)

    def _save_xml(self, target: Path | str | io.BytesIO, pretty: bool = True) -> None:
        """Save a XML flat ODF format from the available parts."""
        if isinstance(target, (Path, str)):
            target = Path(target).with_suffix(".xml")
            target.write_bytes(self._xml_content(pretty))
        else:
            target.write(self._xml_content(pretty))

    # Public API

    def get_parts(self) -> list[str]:
        """Get the list of members."""
        if not self.path:
            # maybe a file like zip archive
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
        else:
            raise ValueError("Unable to provide parts of the document")

    @property
    def parts(self) -> list[str]:
        """Get the list of members."""
        return self.get_parts()

    def get_part(self, path: str) -> str | bytes | None:
        """Get the bytes of a part of the ODF."""
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
            '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n'
            '  <rdf:Description rdf:about="styles.xml">\n'
            f'    <rdf:type rdf:resource="http://docs.oasis-open.org/ns/office/{OFFICE_VERSION}/meta/odf#StylesFile"/>\n'
            "  </rdf:Description>\n"
            '  <rdf:Description rdf:about="">\n'
            f'    <ns0:hasPart xmlns:ns0="http://docs.oasis-open.org/ns/office/{OFFICE_VERSION}/meta/pkg#" rdf:resource="styles.xml"/>\n'
            "  </rdf:Description>\n"
            '  <rdf:Description rdf:about="content.xml">\n'
            f'    <rdf:type rdf:resource="http://docs.oasis-open.org/ns/office/{OFFICE_VERSION}/meta/odf#ContentFile"/>\n'
            "  </rdf:Description>\n"
            '  <rdf:Description rdf:about="">\n'
            f'    <ns0:hasPart xmlns:ns0="http://docs.oasis-open.org/ns/office/{OFFICE_VERSION}/meta/pkg#" rdf:resource="content.xml"/>\n'
            "  </rdf:Description>\n"
            '  <rdf:Description rdf:about="">\n'
            f'    <rdf:type rdf:resource="http://docs.oasis-open.org/ns/office/{OFFICE_VERSION}/meta/pkg#Document"/>\n'
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
        """Replace or add a new part."""
        self.__parts[path] = data

    def del_part(self, path: str) -> None:
        """Mark a part for deletion."""
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
        back_file = Path(path.stem + ".backup" + path.suffix)
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
            raise ValueError(f'Packaging of type "{packaging}" is not supported')
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

    def _save_as_zip(self, target: str | Path | io.BytesIO, backup: bool) -> None:
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
            if not str(target).endswith(".xml"):
                target = str(target) + ".xml"
            if backup:
                self._do_backup(target)
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

        Arguments:

            target -- str or file-like or Path

            packaging -- 'zip', or for debugging purpose 'xml' or 'folder'

            backup -- boolean
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
                raise TypeError(
                    "Impossible to save on io.BytesIO with 'folder' packaging"
                )
            self._save_as_folder(target, backup)
        elif packaging == XML:
            self._save_as_xml(target, backup, pretty)
        else:
            # default:
            self._save_as_zip(target, backup)
