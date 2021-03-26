# Copyright 2018-2020 Jérôme Dumonteil
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
"""Container class, ODF file management
"""
import os
from os.path import join, dirname, exists
from pathlib import PurePath, Path
import shutil
from copy import deepcopy

# from io import BytesIO
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, BadZipfile, is_zipfile

from .const import (
    ODF_MIMETYPES,
    ODF_MANIFEST,
    ODF_TEMPLATES,
    ODF_TEMPLATES_DIR,
    ODF_CONTENT,
    ODF_META,
    ODF_SETTINGS,
    ODF_STYLES,
    ODF_EXTENSIONS,
)
from .manifest import Manifest
from .scriptutils import printwarn

from .utils import to_bytes, to_str


class Container:
    """Representation of the ODF file."""

    def __init__(self, path=None):
        self.__parts = {}
        self.__parts_ts = {}
        self.__packaging = None
        self.__path_like = None
        self.__packaging = "zip"
        self.path = None
        if path:
            self.open(path)

    def open(self, path_or_file):
        """Load the content of an ODF file"""
        self.__path_like = path_or_file
        if isinstance(path_or_file, (str, bytes, Path)):
            self.path = path_or_file
            if not exists(self.path):
                raise OSError(f"File not found: {self.path}")
        else:
            self.path = None
        if is_zipfile(path_or_file):
            self.__packaging = "zip"
            return self.__read_zip()
        # to guess other packaging types
        if self.path:
            try:
                is_folder = os.path.isdir(self.path)
            except OSError:
                is_folder = False
            if is_folder:
                self.__packaging = "folder"
                return self.__read_folder()
        # last try, flat xml either by path or file
        # self._read_flat() # FIXME: not implemented
        raise ValueError("Document format not managed by this tool.")

    @classmethod
    def new(cls, path_or_file):
        """Return a Container instance based on template argument."""
        test_file = to_str(path_or_file)
        if test_file in ODF_TEMPLATES:
            path_or_file = join(
                dirname(__file__), ODF_TEMPLATES_DIR, ODF_TEMPLATES[test_file]
            )
        template_container = cls()
        template_container.open(path_or_file)
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

    def __read_zip(self):
        with ZipFile(self.__path_like) as zf:
            mimetype = zf.read("mimetype").decode("utf-8", "ignore")
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

    def __read_folder(self):
        try:
            mimetype, timestamp = self.__get_folder_part("mimetype")
        except OSError:
            printwarn("corrupted or not an OpenDocument folder " "(missing mimetype)")
            mimetype = b""
            timestamp = None
        if to_str(mimetype) not in ODF_MIMETYPES:
            message = f"Document of unknown type {mimetype}, " "try with ODF Text."
            printwarn(message)
            mimetype = to_bytes(ODF_EXTENSIONS["odt"])
            self.__parts["mimetype"] = mimetype
            self.__parts_ts["mimetype"] = timestamp

    def __get_folder_parts(self):
        """Get the list of members in the ODF folder."""

        def parse_folder(folder):
            parts = []
            file_names = os.listdir(join(self.path, folder))
            for f in file_names:
                if f.startswith("."):  # no hidden files
                    continue
                if os.path.isfile(join(self.path, folder, f)):
                    part_name = PurePath(folder, f).as_posix()
                    parts.append(part_name)
                if os.path.isdir(join(self.path, folder, f)):
                    sub_folder = join(folder, f)
                    sub_parts = parse_folder(sub_folder)
                    if sub_parts:
                        parts.extend(sub_parts)
                    else:
                        # store leaf directories
                        parts.append(PurePath(sub_folder).as_posix() + "/")
            return parts

        return parse_folder("")

    def __get_folder_part(self, name):
        """Get bytes of a part from the ODF folder, with timestamp."""
        path = join(self.path, name)
        timestamp = os.stat(path).st_mtime
        if os.path.isdir(path):
            return ("", timestamp)
        with open(path, "rb") as f:
            part = f.read()
        return (part, timestamp)

    def __get_folder_part_timestamp(self, name):
        path = join(self.path, name)
        try:
            timestamp = os.stat(path).st_mtime
        except OSError:
            timestamp = -1
        return timestamp

    def __get_zip_part(self, name):
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

    def __get_all_zip_part(self):
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

    def __save_zip(self, target):
        """Save a Zip ODF from the available parts."""
        parts = self.__parts

        with ZipFile(target, "w", compression=ZIP_DEFLATED) as filezip:
            # Parts to save, except manifest at the end
            part_names = list(parts.keys())
            try:
                part_names.remove(ODF_MANIFEST)
            except ValueError:
                printwarn("missing '%s'" % ODF_MANIFEST)
            # "Pretty-save" parts in some order
            # mimetype requires to be first and uncompressed
            try:
                filezip.writestr("mimetype", parts["mimetype"], ZIP_STORED)
                part_names.remove("mimetype")
            except (ValueError, KeyError):
                printwarn("missing 'mimetype'")
            # XML parts
            for path in ODF_CONTENT, ODF_META, ODF_SETTINGS, ODF_STYLES:
                if path not in parts:
                    printwarn("missing '%s'" % path)
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
            try:
                filezip.writestr(ODF_MANIFEST, parts[ODF_MANIFEST])
            except KeyError:
                pass

    def __save_folder(self, folder):
        """Save a folder ODF from the available parts."""

        def dump(path, content):
            if path.endswith("/"):  # folder
                is_folder = True
                file_name = PurePath(folder, path[:-1])
            else:
                is_folder = False
                file_name = PurePath(folder, path)
            dir_name = dirname(file_name)
            if not exists(dir_name):
                os.makedirs(dir_name, 0o755)
            if is_folder:
                if not os.path.isdir(file_name):
                    os.makedirs(file_name, 0o777)
            else:
                with open(file_name, "wb", 0o666) as f:
                    f.write(content)

        for path, data in self.__parts.items():
            if data is None:
                # Deleted
                continue
            dump(path, data)

    # Public API

    def get_parts(self):
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
            return self.__get_folder_parts()
        else:
            raise ValueError("Unable to provide parts of the document.")

    def get_part(self, path):
        """Get the bytes of a part of the ODF."""
        if path in self.__parts:
            part = self.__parts[path]
            if part is None:
                raise ValueError(f'part "{path}" is deleted')
            if self.__packaging == "folder":
                cache_ts = self.__parts_ts.get(path, -1)
                current_ts = self.__get_folder_part_timestamp(path)
                if current_ts != cache_ts:
                    part, timestamp = self.__get_folder_part(path)
                    self.__parts[path] = part
                    self.__parts_ts[path] = timestamp
            return part
        if self.__packaging == "zip":
            return self.__get_zip_part(path)
        if self.__packaging == "folder":
            part, timestamp = self.__get_folder_part(path)
            self.__parts[path] = part
            self.__parts_ts[path] = timestamp
            return part
        return None

    @property
    def mimetype(self):
        """Return unicode value of mimetype of the document."""
        return self.get_part("mimetype").decode("utf-8", "ignore")

    @mimetype.setter
    def mimetype(self, m):
        """Set mimetype value of the document."""
        self.__parts["mimetype"] = to_bytes(m)

    def set_part(self, path, data):
        """Replace or add a new part."""
        self.__parts[path] = data

    def del_part(self, path):
        """Mark a part for deletion."""
        self.__parts[path] = None

    @property
    def clone(self):
        """Make a copy of this container with no path."""
        if self.path and self.__packaging == "zip":
            self.__get_all_zip_part()
        clone = deepcopy(self)
        setattr(clone, "path", None)
        return clone

    @staticmethod
    def __do_backup(target):
        prefix, ext = os.path.splitext(target)
        if len(ext) <= 1:
            ext = ""
        back_file = prefix + ".backup" + ext
        if exists(target):
            if os.path.isdir(back_file):
                try:
                    shutil.rmtree(back_file)
                except OSError as e:
                    printwarn(str(e))
            try:
                shutil.move(target, back_file)
            except OSError as e:
                printwarn(str(e))

    def save(self, target=None, packaging=None, backup=False):
        """Save the container to the given target, a path or a file-like
        object.

        Package the output document in the same format than current document,
        unless "packaging" is different.

        Arguments:

            target -- str or file-like

            packaging -- 'zip', or for debugging purpose 'folder'

            backup -- boolean
        """
        parts = self.__parts
        # Packaging
        if packaging is None:
            if self.__packaging:
                packaging = self.__packaging
            else:
                packaging = "zip"  # default
        packaging = packaging.strip().lower()
        # if packaging not in ('zip', 'flat', 'folder'):
        if packaging not in ("zip", "folder"):
            raise ValueError('packaging type "%s" not supported' % packaging)
        # Load parts else they will be considered deleted
        for path in self.get_parts():
            if path not in parts:
                self.get_part(path)
        # Open output file
        # close_after = False
        if target is None:
            target = self.path
        if isinstance(target, str):
            while target.endswith(os.sep):
                target = target[:-1]
            while target.endswith(".folder"):
                target = target.split(".folder", 1)[0]
        if packaging == "zip":
            if isinstance(target, str) and backup:
                self.__do_backup(target)
            self.__save_zip(target)
        if packaging == "folder":
            if not isinstance(target, str):
                raise ValueError(
                    "Saving in folder format requires a folder "
                    "name, not %s." % target
                )
            if not target.endswith(".folder"):
                target = target + ".folder"
            if backup:
                self.__do_backup(target)
            else:
                if exists(target):
                    try:
                        shutil.rmtree(target)
                    except OSError as e:
                        printwarn(str(e))
            self.__save_folder(target)
