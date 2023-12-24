# Copyright 2018-2023 Jérôme Dumonteil
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
"""Container class, ODF file management.
"""
from __future__ import annotations

import contextlib
import io
import os
import shutil
from copy import deepcopy
from importlib import resources as rso
from pathlib import Path, PurePath
from zipfile import ZIP_DEFLATED, ZIP_STORED, BadZipfile, ZipFile, is_zipfile

from .const import (
    ODF_CONTENT,
    ODF_EXTENSIONS,
    ODF_MANIFEST,
    ODF_META,
    ODF_MIMETYPES,
    ODF_SETTINGS,
    ODF_STYLES,
    ODF_TEMPLATES,
)
from .manifest import Manifest
from .scriptutils import printwarn
from .utils import to_bytes, to_str


class Container:
    """Representation of the ODF file."""

    def __init__(self, path: Path | str | io.BytesIO | None = None):
        self.__parts = {}
        self.__parts_ts = {}
        self.__packaging = None
        self.__path_like = None
        self.__packaging = "zip"
        self.path = None  # or Path
        if path:
            self.open(path)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} type={self.mimetype} path={self.path}>"

    def open(self, path_or_file: Path | str | io.BytesIO) -> None:
        """Load the content of an ODF file."""
        self.__path_like = path_or_file
        if isinstance(path_or_file, (str, Path)):
            self.path = Path(path_or_file)
            if not self.path.exists():
                raise FileNotFoundError(str(self.path))
        if (self.path or isinstance(path_or_file, io.BytesIO)) and is_zipfile(
            path_or_file
        ):
            self.__packaging = "zip"
            return self._read_zip()
        if self.path:
            is_folder = False
            with contextlib.suppress(OSError):
                is_folder = self.path.is_dir()
            if is_folder:
                self.__packaging = "folder"
                return self._read_folder()
        raise TypeError(f"Document format not managed by odfdo: {type(path_or_file)}.")

    @classmethod
    def from_template(cls, template: str | Path) -> Container:
        """Return a Container instance based on template argument."""
        template_container = cls()
        if template in ODF_TEMPLATES:
            template_container = cls()
            template_name = ODF_TEMPLATES[template]
            with rso.as_file(
                rso.files("odfdo.templates").joinpath(template_name)
            ) as template_path:
                template_container.open(template_path)
        else:
            # custome template
            template_container.open(template)
        # Return a copy of the template container
        clone = template_container.clone
        # Change type from template to regular
        mimetype = clone.mimetype.replace("-template", "")
        clone.mimetype = mimetype
        # Update the manifest
        manifest = Manifest(ODF_MANIFEST, clone)
        manifest.set_media_type("/", mimetype)
        clone.set_part(ODF_MANIFEST, manifest.serialize())
        return clone

    def _read_zip(self) -> None:
        with ZipFile(self.__path_like) as zf:
            mimetype = zf.read("mimetype").decode("utf8", "ignore")
            if mimetype not in ODF_MIMETYPES:
                raise ValueError(f"Document of unknown type {mimetype}")
            self.__parts["mimetype"] = to_bytes(mimetype)
        if self.path is None:
            # read the full file at once and forget file
            with ZipFile(self.__path_like) as zf:
                for name in zf.namelist():
                    upath = PurePath(name).as_posix()
                    self.__parts[upath] = zf.read(name)
            self.__path_like = None

    def _read_folder(self) -> None:
        try:
            mimetype, timestamp = self._get_folder_part("mimetype")
        except OSError:
            printwarn("Corrupted or not an OpenDocument folder (missing mimetype)")
            mimetype = b""
            timestamp = None
        if to_str(mimetype) not in ODF_MIMETYPES:
            message = f"Document of unknown type {mimetype}, try with ODF Text."
            printwarn(message)
            mimetype = to_bytes(ODF_EXTENSIONS["odt"])
            self.__parts["mimetype"] = mimetype
            self.__parts_ts["mimetype"] = timestamp

    def _parse_folder(self, folder: str) -> list[str]:
        parts = []
        root = self.path / folder
        for path in root.iterdir():
            if path.name.startswith("."):  # no hidden files
                continue
            relative_path = path.relative_to(self.path)
            if path.is_file():
                parts.append(relative_path.as_posix())
            if path.is_dir():
                sub_parts = self._parse_folder(relative_path)
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
        path = self.path / name
        timestamp = path.stat().st_mtime
        if path.is_dir():
            return (b"", timestamp)
        return (path.read_bytes(), timestamp)

    def _get_folder_part_timestamp(self, name: str) -> int:
        path = self.path / name
        try:
            timestamp = path.stat().st_mtime
        except OSError:
            timestamp = -1
        return timestamp

    def _get_zip_part(self, name: str) -> bytes | None:
        """Get bytes of a part from the Zip ODF file. No cache."""
        try:
            with ZipFile(self.path) as zf:
                if name.endswith("/"):  # folder
                    upath = PurePath(name[:-1]).as_posix() + "/"
                else:
                    upath = PurePath(name).as_posix()
                self.__parts[upath] = zf.read(name)
                return self.__parts[upath]
        except BadZipfile:
            return None

    def _get_all_zip_part(self) -> None:
        """Read all parts. No cache."""
        try:
            with ZipFile(self.path) as zf:
                for name in zf.namelist():
                    if name.endswith("/"):  # folder
                        upath = PurePath(name[:-1]).as_posix() + "/"
                    else:
                        upath = PurePath(name).as_posix()
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
            try:
                filezip.writestr("mimetype", parts["mimetype"], ZIP_STORED)
                part_names.remove("mimetype")
            except (ValueError, KeyError):
                printwarn("Missing 'mimetype'")
            # XML parts
            for path in ODF_CONTENT, ODF_META, ODF_SETTINGS, ODF_STYLES:
                if path not in parts:
                    printwarn(f"Missing '{path}'")
                    continue
                filezip.writestr(path, parts[path])
                part_names.remove(path)
            # Everything else
            for path in part_names:
                data = parts[path]
                if data is None:
                    # Deleted
                    continue
                filezip.writestr(path, data)
            # Manifest
            with contextlib.suppress(KeyError):
                filezip.writestr(ODF_MANIFEST, parts[ODF_MANIFEST])

    def _save_folder(self, folder: str) -> None:
        """Save a folder ODF from the available parts."""

        def dump(part_path: str, content: bytes):
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

    # Public API

    def get_parts(self) -> list[str]:
        """Get the list of members."""
        if not self.path:
            # maybe a file like zip archive
            return list(self.__parts.keys())
        if self.__packaging == "zip":
            parts = []
            with ZipFile(self.path) as zf:
                for name in zf.namelist():
                    if name.endswith("/"):
                        parts.append(PurePath(name[:-1]).as_posix() + "/")
                    else:
                        parts.append(PurePath(name).as_posix())
            return parts
        elif self.__packaging == "folder":
            return self._get_folder_parts()
        else:
            raise ValueError("Unable to provide parts of the document.")

    def get_part(self, path: str) -> str | bytes | None:
        """Get the bytes of a part of the ODF."""
        path = str(path)
        if path in self.__parts:
            part = self.__parts[path]
            if part is None:
                raise ValueError(f'Part "{path}" is deleted')
            if self.__packaging == "folder":
                cache_ts = self.__parts_ts.get(path, -1)
                current_ts = self._get_folder_part_timestamp(path)
                if current_ts != cache_ts:
                    part, timestamp = self._get_folder_part(path)
                    self.__parts[path] = part
                    self.__parts_ts[path] = timestamp
            return part
        if self.__packaging == "zip":
            return self._get_zip_part(path)
        if self.__packaging == "folder":
            part, timestamp = self._get_folder_part(path)
            self.__parts[path] = part
            self.__parts_ts[path] = timestamp
            return part
        return None

    @property
    def mimetype(self) -> str:
        """Return unicode value of mimetype of the document."""
        try:
            return self.get_part("mimetype").decode("utf8", "ignore")
        except Exception:
            return ""

    @mimetype.setter
    def mimetype(self, mimetype: str | bytes) -> None:
        """Set mimetype value of the document."""
        self.__parts["mimetype"] = to_bytes(mimetype)

    def set_part(self, path: str, data: str | bytes) -> None:
        """Replace or add a new part."""
        self.__parts[path] = data

    def del_part(self, path: str) -> None:
        """Mark a part for deletion."""
        self.__parts[path] = None

    @property
    def clone(self) -> Container:
        """Make a copy of this container with no path."""
        if self.path and self.__packaging == "zip":
            self._get_all_zip_part()
        clone = deepcopy(self)
        clone.path = None
        return clone

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

    def _save_packaging(self, packaging: str | None) -> str:
        if not packaging:
            packaging = self.__packaging if self.__packaging else "zip"
        packaging = packaging.strip().lower()
        # if packaging not in ('zip', 'flat', 'folder'):
        if packaging not in ("zip", "folder"):
            raise ValueError(f'Packaging of type "{packaging}" is not supported')
        return packaging

    def _save_target(self, target: str | Path | io.BytesIO | None) -> str | io.BytesIO:
        if target is None:
            target = self.path
        if isinstance(target, Path):
            target = str(target)
        if isinstance(target, str):
            while target.endswith(os.sep):
                target = target[:-1]
            while target.endswith(".folder"):
                target = target.split(".folder", 1)[0]
        return target

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
        if backup:
            self._do_backup(target)
        else:
            path = Path(target)
            if path.exists():
                try:
                    shutil.rmtree(path)
                except OSError as e:
                    printwarn(str(e))
        self._save_folder(target)

    def save(
        self,
        target: str | Path | io.BytesIO | None,
        packaging: str | None = None,
        backup: bool = False,
    ) -> None:
        """Save the container to the given target, a path or a file-like
        object.

        Package the output document in the same format than current document,
        unless "packaging" is different.

        Arguments:

            target -- str or file-like or Path

            packaging -- 'zip', or for debugging purpose 'folder'

            backup -- boolean
        """
        parts = self.__parts
        packaging = self._save_packaging(packaging)
        # Load parts else they will be considered deleted
        for path in self.get_parts():
            if path not in parts:
                self.get_part(path)
        target = self._save_target(target)
        if packaging == "folder":
            if isinstance(target, io.BytesIO):
                raise TypeError(
                    "Impossible to save on io.BytesIO with 'folder' packaging"
                )
            self._save_as_folder(target, backup)
        else:
            # default:
            self._save_as_zip(target, backup)
