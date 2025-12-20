# Copyright 2018-2025 Jérôme Dumonteil
# Copyright (c) 2009-2013 Ars Aperta, Itaapy, Pierlis, Talend.
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
#          Romain Gauthier <romain@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
"""Document class, root of the ODF document."""

from __future__ import annotations

import contextlib
import io
import posixpath
from contextlib import suppress
from copy import deepcopy
from importlib import resources as rso
from operator import itemgetter
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO, cast

from .const import (
    ODF_CONTENT,
    ODF_MANIFEST,
    ODF_MANIFEST_NAME,
    ODF_MANIFEST_RDF,
    ODF_META,
    ODF_SETTINGS,
    ODF_STYLES,
    ODF_TEMPLATES,
    PACKAGING,
    XML,
    ZIP,
)
from .container import Container
from .content import Content
from .datatype import Boolean
from .element import Element
from .image import DrawFillImage, DrawImage
from .manifest import Manifest
from .meta import Meta
from .mixin_md import MDDocument
from .styles import Styles
from .table import Table
from .utils import FAMILY_MAPPING, Blob, bytes_to_str, is_RFC3066
from .xmlpart import XmlPart

if TYPE_CHECKING:
    from .body import Body
    from .style_base import StyleBase

AUTOMATIC_PREFIX = "odfdo_auto_"

UNDERLINE_LVL = ["=", "-", ":", "`", "'", '"', "~", "^", "_", "*", "+"]


def _underline_string(level: int, name: str) -> str:
    """Generate an underline string for a given name and level.

    Uses a predefined set of characters for underlining, based on the `level`.
    If the level is out of bounds, returns a newline.

    Args:
        level: The nesting level, which determines the underline character.
        name: The string to be underlined. The length of this string
            determines the length of the underline.

    Returns:
        str: The underline string, or a newline if the level is too high.
    """
    if level >= len(UNDERLINE_LVL):
        return "\n"
    return UNDERLINE_LVL[level] * len(name)


def _show_styles(element: Element, level: int = 0) -> str | None:
    """Recursively generate a formatted string representation of a style element.

    This function is used for creating a human-readable tree of styles,
    including their attributes and children.

    Args:
        element: The style element to represent.
        level: The current nesting level for indentation and underlining.

    Returns:
        str | None: A formatted string representing the style element, or
            `None` if the element is empty (no attributes or children).
    """
    output: list[str] = []
    attributes = element.attributes
    children = element.children
    # Don't show the empty elements
    if not attributes and not children:
        return None
    tag_name = element.tag
    output.append(tag_name)
    # Underline the name
    output.append(_underline_string(level, tag_name))
    # Add a separation between name and attributes
    output[-1] += "\n"

    # Attributes
    attrs: list[str] = []
    for key, value in attributes.items():
        attrs.append(f"{key}: {value}")
    if attrs:
        attrs.sort()
        # Add a separation between attributes and children
        attrs[-1] += "\n"
        output.extend(attrs)

    # Children
    # Sort children according to their names
    children2 = [(child.tag, child) for child in children]
    children2.sort()
    children = [child for name, child in children2]
    for child in children:
        child_output = _show_styles(child, level + 1)
        if child_output:
            output.append(child_output)
    return "\n".join(output)


def _get_part_path(path: str) -> str:
    """Map a short name to the full path of a core ODF XML part.

    For example, "content" is mapped to "content.xml". If the path is not
    a recognized short name, it is returned unchanged.

    Args:
        path: The short name or full path of the part.

    Returns:
        str: The full path of the XML part.
    """
    return {
        "content": ODF_CONTENT,
        "meta": ODF_META,
        "settings": ODF_SETTINGS,
        "styles": ODF_STYLES,
        "manifest": ODF_MANIFEST,
    }.get(path, path)


def _get_part_class(
    path: str,
) -> type[XmlPart] | None:
    """Get the specialized class for a core ODF XML part.

    Args:
        path: The full path of the XML part (e.g., "content.xml").

    Returns:
        type[XmlPart] | None: The class corresponding to the part
            (e.g., `Content` for "content.xml"), or `None` if the part
            is not a recognized core XML part with a specialized class.
    """
    name = Path(path).name
    return {
        ODF_CONTENT: Content,
        ODF_META: Meta,
        ODF_SETTINGS: XmlPart,
        ODF_STYLES: Styles,
        ODF_MANIFEST_NAME: Manifest,
    }.get(name)


def _container_from_template(template: str | Path | io.BytesIO) -> Container:
    """Return a Container instance based on the provided template.

    Args:
        template: The template to use. Can be a string representing a
            predefined template name (e.g., "text"), a file path (str or Path)
            to a custom template, or a file-like object (`io.BytesIO`).

    Returns:
        A new `Container` instance initialized from the template.
    """
    template_container = Container()
    if isinstance(template, str) and template in ODF_TEMPLATES:
        template = ODF_TEMPLATES[template]
        with rso.as_file(
            rso.files("odfdo.templates").joinpath(template)
        ) as template_path:
            template_container.open(template_path)
    else:
        # custom template
        template_container.open(template)
    # Return a copy of the template container
    container = template_container.clone
    # Change type from template to regular
    mimetype = container.mimetype.replace("-template", "")
    container.mimetype = mimetype
    # Update the manifest
    manifest = Manifest(ODF_MANIFEST, container)
    manifest.set_media_type("/", mimetype)
    container.set_part(ODF_MANIFEST, manifest.serialize())
    return container


class Document(MDDocument):
    """Abstraction of the ODF document."""

    def __init__(
        self,
        target: str | bytes | Path | Container | io.BytesIO | None = "text",
    ) -> None:
        """Initialize a Document.

        This can either create a new document from a template or load an
        existing one from a path, file-like object, or Container.

        Args:
            target:
                The source to create or load the document from.
                - If a string like "text", "spreadsheet", "presentation",
                  "drawing", or their file extensions ("odt", "ods", "odp",
                  "odg"), a new document is created from a default template.
                  Note: These templates are not truly empty and may require
                  clearing (e.g., `document.body.clear()`).
                - If a path (str or Path) to an existing ODF file, the file
                  is loaded.
                - If a `Container` object, it is used directly.
                - If a file-like object (`io.BytesIO`), the document is loaded
                  from it.
                - If `None`, an empty container is created.
                - If `bytes`, the content is loaded as a string.

        To create a document from a custom template, use the `Document.new()`
        classmethod instead.

        When creating an “empty” document: the document is a copy of the
        default templates document provided with this library, which, as
        templates, are not really empty. It may be useful to clear the newly
        created document: `document.body.clear()`, or adjust meta information
        like description or language: `document.language = 'fr-FR'`.
        """
        # Cache of XML parts
        self.__xmlparts: dict[str, XmlPart] = {}
        # Cache of the body
        self.__body: Element | None = None
        self.container: Container | None = None
        if isinstance(target, bytes):
            # eager conversion
            target = bytes_to_str(target)
        if target is None:
            # empty document, you probably don't want this.
            self.container = Container()
            return
        if isinstance(target, Path):
            # let's assume we open a container on existing file
            self.container = Container(target)
            return
        if isinstance(target, Container):
            # special internal case, use an existing container
            self.container = target
            return
        if isinstance(target, str):
            if target in ODF_TEMPLATES:
                # assuming a new document from templates
                self.container = _container_from_template(target)
                return
            # let's assume we open a container on existing file
            self.container = Container(target)
            return
        if isinstance(target, io.BytesIO):
            self.container = Container(target)
            return
        raise TypeError(f"Unknown Document source type: '{target!r}'")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} type={self.get_type()} path={self.path}>"

    def __str__(self) -> str:
        try:
            return str(self.get_formatted_text())
        except NotImplementedError:
            return str(self.body)

    @classmethod
    def new(cls, template: str | Path | io.BytesIO = "text") -> Document:
        """Create a new Document from a template.

        Args:
            template: The template to use.
                - If a string like "text", "spreadsheet", etc., a default
                  template is used.
                - If a path to a custom template file, that template is used.
                - If a file-like object, the template is read from it.

        Returns:
            Document: A new Document instance based on the template.
        """
        container = _container_from_template(template)
        return cls(container)

    # Public API

    @property
    def path(self) -> Path | None:
        """Get or set the path of the document's container.

        When getting, it returns the `Path` object of the container, or `None`
        if the container is not set.

        When setting, it accepts a string or `Path` object to update the
        container's path.

        Returns:
            The `Path` object of the container, or `None` if the container is not set.
        """
        if not self.container:
            return None
        return self.container.path

    @path.setter
    def path(self, path_or_str: str | Path) -> None:
        if not self.container:
            return
        self.container.path = Path(path_or_str)

    def get_parts(self) -> list[str]:
        """Get the names of all available parts within the document's archive.

        This is a helper method for the `parts` property.

        Returns:
            A list of strings, where each string is the path of a part.

        Raises:
            ValueError: If the document's container is empty.
        """
        if not self.container:
            raise ValueError("Empty Container")
        return self.container.parts

    @property
    def parts(self) -> list[str]:
        """Get the names of all available parts within the document's archive.

        The paths are relative to the archive root, e.g.,
        'content.xml', 'Pictures/100000000000032000000258912EB1C3.jpg'.

        This is a convenience property that calls `get_parts()`.

        Returns:
            A list of strings, where each string is the path of a part.
        """
        return self.get_parts()

    def get_part(self, path: str) -> XmlPart | str | bytes | None:
        """Return the bytes of the given part. The path is relative to the
        archive, e.g. "Pictures/1003200258912EB1C3.jpg".

        'content', 'meta', 'settings', 'styles' and 'manifest' are shortcuts to
        the real path, e.g. content.xml, and return a dedicated object with its
        own API.

        path formatted as URI, so always use '/' separator
        """
        if not self.container:
            raise ValueError("Empty Container")
        # "./ObjectReplacements/Object 1"
        path = path.lstrip("./")
        path = _get_part_path(path)
        cls = _get_part_class(path)
        # Raw bytes
        if cls is None:
            return self.container.get_part(path)
        # XML part
        part = self.__xmlparts.get(path)
        if part is None:
            self.__xmlparts[path] = part = cls(path, self.container)
        return part

    def set_part(self, path: str, data: bytes) -> None:
        """Set the bytes of a given part within the document's archive.

        This method updates the content of an existing part or adds a new part
        to the document.

        Args:
            path: The path of the part relative to the archive, e.g.,
                "Pictures/image.jpg". Shortcuts like "content", "meta",
                "settings", "styles", and "manifest" are also supported.
                The path should use '/' as a separator.
            data: The `bytes` object containing the content to set for the part.

        Raises:
            ValueError: If the document's container is empty.
        """
        if not self.container:
            raise ValueError("Empty Container")
        # "./ObjectReplacements/Object 1"
        path = path.lstrip("./")
        path = _get_part_path(path)
        cls = _get_part_class(path)
        # XML part overwritten
        if cls is not None:
            with suppress(KeyError):
                self.__xmlparts[path]
        self.container.set_part(path, data)

    def del_part(self, path: str) -> None:
        """Mark a part for deletion from the document's archive.

        This method marks a specified part for deletion from the ODF document.
        The actual deletion occurs when the document is saved.

        Args:
            path: The path of the part relative to the archive, e.g.,
                "Pictures/1003200258912EB1C3.jpg". Shortcuts like "content"
                are also supported.

        Raises:
            ValueError: If the document's container is empty, or if an attempt
                is made to delete a mandatory part (e.g., "manifest.xml").
        """
        if not self.container:
            raise ValueError("Empty Container")
        path = _get_part_path(path)
        cls = _get_part_class(path)
        if path == ODF_MANIFEST or cls is not None:
            raise ValueError(f"part '{path}' is mandatory")
        self.container.del_part(path)

    @property
    def mimetype(self) -> str:
        """Get or set the MIME type of the document.

        When getting, it returns the MIME type as a string (e.g.,
        "application/vnd.oasis.opendocument.text").

        When setting, it accepts a new MIME type as a string.

        Returns:
            The MIME type as a string.

        Raises:
            ValueError: If the document's container is empty.
        """
        if not self.container:
            raise ValueError("Empty Container")
        return self.container.mimetype

    @mimetype.setter
    def mimetype(self, mimetype: str) -> None:
        if not self.container:
            raise ValueError("Empty Container")
        self.container.mimetype = mimetype

    def get_type(self) -> str:
        """Get the ODF type (also called class) of this document.

        Returns: 'chart', 'database', 'formula', 'graphics',
            'graphics-template', 'image', 'presentation',
            'presentation-template', 'spreadsheet', 'spreadsheet-template',
            'text', 'text-master', 'text-template' or 'text-web'
        """
        # The mimetype must be with the form:
        # application/vnd.oasis.opendocument.text

        # Isolate and return the last part
        return self.mimetype.rsplit(".", 1)[-1]

    @property
    def body(self) -> Body:
        """Get the body element of the content part.

        The body element is where the actual content of the ODF document
        (e.g., paragraphs, tables, images) is stored.

        Returns:
            The `Body` element of the document's content part.

        Raises:
            ValueError: If the content part is missing or the body element cannot be retrieved.
        """
        if self.__body is None:
            self.__body = self.content.body
        return self.__body  # type: ignore[return-value]

    @property
    def meta(self) -> Meta:
        """Get the meta part (meta.xml) of the document.

        The meta part stores metadata about the document, such as author,
        creation date, and modification date.

        Returns:
            The `Meta` object representing the document's metadata.

        Raises:
            ValueError: If the metadata part is empty or cannot be retrieved as a `Meta` object.
        """
        metadata = self.get_part(ODF_META)
        if metadata is None or not isinstance(metadata, Meta):
            raise ValueError("Empty Meta")
        return metadata

    @property
    def manifest(self) -> Manifest:
        """Get the manifest part (manifest.xml) of the document.

        The manifest lists all files within the ODF package and their MIME types.

        Returns:
            The `Manifest` object representing the document's manifest.

        Raises:
            ValueError: If the manifest part is empty or cannot be retrieved as a `Manifest` object.
        """
        manifest = self.get_part(ODF_MANIFEST)
        if manifest is None or not isinstance(manifest, Manifest):
            raise ValueError("Empty Manifest")
        return manifest

    def _get_formatted_text_footnotes(
        self,
        result: list[str],
        context: dict,
        rst_mode: bool,
    ) -> None:
        # Separate text from notes
        if rst_mode:
            result.append("\n")
        else:
            result.append("----\n")
        for citation, body in context["footnotes"]:
            if rst_mode:
                result.append(f".. [#] {body}\n")
            else:
                result.append(f"[{citation}] {body}\n")
        # Append a \n after the notes
        result.append("\n")
        # Reset for the next paragraph
        context["footnotes"] = []

    def _get_formatted_text_annotations(
        self,
        result: list[str],
        context: dict,
        rst_mode: bool,
    ) -> None:
        # Insert the annotations
        # With a separation
        if rst_mode:
            result.append("\n")
        else:
            result.append("----\n")
        for annotation in context["annotations"]:
            if rst_mode:
                result.append(f".. [#] {annotation}\n")
            else:
                result.append(f"[*] {annotation}\n")
        context["annotations"] = []

    def _get_formatted_text_images(
        self,
        result: list[str],
        context: dict,
        rst_mode: bool,
    ) -> None:
        # Insert the images ref, only in rst mode
        result.append("\n")
        for ref, filename, (width, height) in context["images"]:
            result.append(f".. {ref} image:: {filename}\n")
            if width is not None:
                result.append(f"   :width: {width}\n")
            if height is not None:
                result.append(f"   :height: {height}\n")
        context["images"] = []

    def _get_formatted_text_endnotes(
        self,
        result: list[str],
        context: dict,
        rst_mode: bool,
    ) -> None:
        # Append the end notes
        if rst_mode:
            result.append("\n\n")
        else:
            result.append("\n========\n")
        for citation, body in context["endnotes"]:
            if rst_mode:
                result.append(f".. [*] {body}\n")
            else:
                result.append(f"({citation}) {body}\n")

    def get_formatted_text(self, rst_mode: bool = False) -> str:
        """Return a formatted string representation of the document's content.

        For text-based documents, this includes handling of footnotes, annotations,
        and image references. For spreadsheets, it returns a CSV representation.

        Args:
            rst_mode: If True, formats the output in reStructuredText (RST)
                syntax, especially for footnotes and annotations.

        Returns:
            str: The formatted text content of the document.

        Raises:
            NotImplementedError: If the document type is not supported for
                formatted text extraction.
        """
        # For the moment, only "type='text'"
        doc_type = self.get_type()
        if doc_type == "spreadsheet":
            return self._tables_csv()
        if doc_type in {
            "text",
            "text-template",
            "presentation",
            "presentation-template",
        }:
            return self._formatted_text(rst_mode)
        raise NotImplementedError(f"Type of document '{doc_type}' not supported yet")

    def _tables_csv(self) -> str:
        return "\n\n".join(str(table) for table in self.body.tables)

    def _formatted_text(self, rst_mode: bool) -> str:
        # Initialize an empty context
        context = {
            "document": self,
            "footnotes": [],
            "endnotes": [],
            "annotations": [],
            "rst_mode": rst_mode,
            "img_counter": 0,
            "images": [],
            "no_img_level": 0,
        }
        body = self.body
        # Get the text
        result = []
        for child in body.children:
            # self._get_formatted_text_child(result, element, context, rst_mode)
            # if child.tag == "table:table":
            #     result.append(child.get_formatted_text(context))
            #     return
            result.append(child.get_formatted_text(context))
            if context["footnotes"]:
                self._get_formatted_text_footnotes(result, context, rst_mode)
            if context["annotations"]:
                self._get_formatted_text_annotations(result, context, rst_mode)
            # Insert the images ref, only in rst mode
            if context["images"]:
                self._get_formatted_text_images(result, context, rst_mode)
        if context["endnotes"]:
            self._get_formatted_text_endnotes(result, context, rst_mode)
        return "".join(result)

    def get_formated_meta(self) -> str:
        """Return meta information as text, with some formatting.

        (Redirection to new implementation for compatibility.)

        Returns:
            A formatted string containing the document's metadata.
        """
        return self.meta.as_text()

    def to_markdown(self) -> str:
        """Export the document content to Markdown format.

        Currently, only text documents are supported.

        Returns:
            str: The Markdown representation of the document.

        Raises:
            NotImplementedError: If the document type is not 'text'.
        """
        doc_type = self.get_type()
        if doc_type not in {
            "text",
        }:
            raise NotImplementedError(
                f"Type of document '{doc_type}' not supported yet"
            )
        return self._markdown_export()

    def _add_binary_part(self, blob: Blob) -> str:
        if not self.container:
            raise ValueError("Empty Container")
        manifest = self.manifest
        if manifest.get_media_type("Pictures/") is None:
            manifest.add_full_path("Pictures/")
        path = posixpath.join("Pictures", blob.name)
        self.container.set_part(path, blob.content)
        manifest.add_full_path(path, blob.mime_type)
        return path

    def add_file(self, path_or_file: str | Path | BinaryIO) -> str:
        """Insert a file from a path or a file-like object into the document's container.

        The internal name of the file in the "Pictures/" folder is generated
        by a hash function. The method returns the full path (URI) that can be
        used to reference the added file within the document's content.

        Args:
            path_or_file: The path to the file (str or Path) or a file-like
                object (`BinaryIO`) containing the file's content.

        Returns:
            The full path (URI) to reference the added file in the content.

        Raises:
            ValueError: If the document's container is empty.
        """
        if not self.container:
            raise ValueError("Empty Container")
        if isinstance(path_or_file, (str, Path)):
            blob = Blob.from_path(path_or_file)
        else:
            blob = Blob.from_io(path_or_file)
        return self._add_binary_part(blob)

    @property
    def clone(self) -> Document:
        """Return an exact, deep copy of the document.

        All internal structures, including the container and its parts,
        are duplicated.

        Returns:
            A new `Document` instance that is a deep copy of the original.

        Raises:
            ValueError: If the original document's container is empty.
        """
        clone = object.__new__(self.__class__)
        for name in self.__dict__:
            if name == "_Document__body":
                setattr(clone, name, None)
            elif name == "_Document__xmlparts":
                setattr(clone, name, {})
            elif name == "container":
                if not self.container:
                    raise ValueError("Empty Container")
                setattr(clone, name, self.container.clone)
            else:
                value = deepcopy(getattr(self, name))
                setattr(clone, name, value)
        return clone

    def _check_manifest_rdf(self) -> None:
        manifest = self.manifest
        if not self.container:
            return
        parts = self.container.parts
        if manifest.get_media_type(ODF_MANIFEST_RDF):
            if ODF_MANIFEST_RDF not in parts:
                self.container.set_part(
                    ODF_MANIFEST_RDF, self.container.default_manifest_rdf.encode("utf8")
                )
        else:
            if ODF_MANIFEST_RDF in parts:
                self.container.del_part(ODF_MANIFEST_RDF)

    def save(
        self,
        target: str | Path | io.BytesIO | None = None,
        packaging: str = ZIP,
        pretty: bool | None = None,
        backup: bool = False,
    ) -> None:
        """Save the document to a target path or file-like object.

        The document can be saved at its original location, or to a new path
        or file-like object. It can be saved as a Zip file (default),
        flat XML format, or as files in a folder (for debugging purposes).
        XML parts can be pretty printed.

        Note: 'xml' packaging is an experimental work in progress.

        Args:
            target: The destination to save the document to. Can be a string
                path, a `Path` object, or a file-like object (`io.BytesIO`).
                If `None`, the document is saved to its original path.
            packaging: The packaging format: 'zip' (default), 'folder', or 'xml'.
            pretty: If `True`, XML parts will be pretty-printed. If `None` (default),
                it defaults to `True` for 'folder' and 'xml' packaging.
            backup: If `True`, a backup of the existing file will be created
                before saving.

        Raises:
            ValueError: If the document's container is empty or an unsupported
                packaging type is specified.
            RuntimeError: In unexpected scenarios during XML part handling.
        """
        if not self.container:
            raise ValueError("Empty Container")
        if packaging not in PACKAGING:
            raise ValueError(f'Packaging of type "{packaging}" is not supported')
        # Some advertising
        self.meta.set_generator_default()
        # Synchronize data with container
        container = self.container
        if pretty is None:
            pretty = packaging in {"folder", "xml"}
        pretty = bool(pretty)
        backup = bool(backup)
        self._check_manifest_rdf()
        if pretty and packaging != XML:
            for path, part in self.__xmlparts.items():
                if part is not None:
                    container.set_part(path, part.pretty_serialize())
            for path in (ODF_CONTENT, ODF_META, ODF_SETTINGS, ODF_STYLES):
                if path in self.__xmlparts:
                    continue
                cls = _get_part_class(path)
                if cls is None:
                    raise RuntimeError("Should never happen")
                # XML part
                self.__xmlparts[path] = part = cls(path, container)
                container.set_part(path, part.pretty_serialize())
        else:
            for path, part in self.__xmlparts.items():
                if part is not None:
                    container.set_part(path, part.serialize())
        container.save(target, packaging=packaging, backup=backup, pretty=pretty)

    @property
    def content(self) -> Content:
        """Get the content part (content.xml) of the document.

        Returns:
            The `Content` object representing the document's content.

        Raises:
            ValueError: If the content part is empty or cannot be retrieved.
        """
        content: Content | None = self.get_part(ODF_CONTENT)  # type:ignore
        if content is None:
            raise ValueError("Empty Content")
        return content

    @property
    def styles(self) -> Styles:
        """Get the styles part (styles.xml) of the document.

        Returns:
            The `Styles` object representing the document's styles.

        Raises:
            ValueError: If the styles part is empty or cannot be retrieved.
        """
        styles: Styles | None = self.get_part(ODF_STYLES)  # type:ignore
        if styles is None:
            raise ValueError("Empty Styles")
        return styles

    # Styles over several parts

    def get_styles(
        self,
        family: str | bytes = "",
        automatic: bool = False,
    ) -> list[StyleBase]:
        """Retrieve a list of styles from both content.xml and styles.xml.

        This method allows filtering styles by family and can include automatic
        styles in the search.

        Args:
            family: The style family to filter by (e.g., 'paragraph', 'text').
                Can be a string or bytes.
            automatic: If `True`, includes automatic styles from styles.xml.

        Returns:
            A list of `StyleBase` objects matching the criteria.
        """
        # compatibility with old versions:
        if isinstance(family, bytes):
            family = bytes_to_str(family)
        return self.content.get_styles(family=family) + self.styles.get_styles(
            family=family, automatic=automatic
        )

    def get_style(
        self,
        family: str,
        name_or_element: str | StyleBase | None = None,
        display_name: str | None = None,
    ) -> StyleBase | None:
        """Return the style uniquely identified by its name and family.

        If `name_or_element` is already a `StyleBase` object, it is returned directly.
        If `name_or_element` is `None`, the default style for the given `family` is fetched.
        If `display_name` is provided, it is used to search for styles by their
        user-facing name (as seen in desktop applications), rather than their
        internal `name`.

        Args:
            family: The style family (e.g., 'paragraph', 'text', 'graphic',
                'table', 'list', 'number', 'page-layout', 'master-page').
            name_or_element: The internal name of the style (str), a `StyleBase`
                object itself, or `None` to fetch the default style.
            display_name: The user-facing display name of the style.

        Returns:
            The matching `StyleBase` object, or `None` if no matching style is found.
        """
        # 1. content.xml
        element = self.content.get_style(
            family, name_or_element=name_or_element, display_name=display_name
        )
        if element is not None:
            return element
        # 2. styles.xml
        return self.styles.get_style(
            family,
            name_or_element=name_or_element,
            display_name=display_name,
        )

    def get_parent_style(self, style: StyleBase) -> StyleBase | None:
        """Get the parent style of a given style.

        Args:
            style: The `StyleBase` object for which to find the parent.

        Returns:
            The parent `StyleBase` object, or `None` if the style
            has no parent or the parent style cannot be found.
        """
        family = style.family
        if family is None:
            return None
        parent_style_name = style.parent_style  # type: ignore [attr-defined]
        if not parent_style_name:
            return None
        return self.get_style(family, parent_style_name)

    def get_list_style(self, style: StyleBase) -> StyleBase | None:
        """Get the list style associated with a given style.

        Args:
            style: The `StyleBase` object from which to get the list style name.

        Returns:
            The list `StyleBase` object, or `None` if the style
            has no associated list style or it cannot be found.
        """
        list_style_name = style.list_style_name  # type: ignore[attr-defined]
        if not list_style_name:
            return None
        return self.get_style("list", list_style_name)

    @staticmethod
    def _pseudo_style_attribute(
        style_element: StyleBase | Element, attribute: str
    ) -> Any:
        if hasattr(style_element, attribute):
            return getattr(style_element, attribute)
        return ""

    def _set_automatic_name(self, style: StyleBase, family: str) -> None:
        """Generate a name for the new automatic style."""
        if not hasattr(style, "name"):
            # do nothing
            return
        styles = self.get_styles(family=family, automatic=True)
        max_index = 0
        for existing_style in styles:
            if not hasattr(existing_style, "name"):
                continue
            if not existing_style.name.startswith(AUTOMATIC_PREFIX):
                continue
            try:
                index = int(existing_style.name[len(AUTOMATIC_PREFIX) :])
            except ValueError:
                continue
            max_index = max(max_index, index)

        style.name = f"{AUTOMATIC_PREFIX}{max_index + 1}"

    def _insert_style_get_common_styles(
        self,
        family: str,
        name: str,
    ) -> tuple[Any, Any]:
        style_container = self.styles.get_element("office:styles")
        existing = self.styles.get_style(family, name)
        return existing, style_container

    def _insert_style_get_automatic_styles(
        self,
        style: StyleBase,
        family: str,
        name: str,
    ) -> tuple[Any, Any]:
        style_container = self.content.get_element("office:automatic-styles")
        # A name ?
        if name:
            if hasattr(style, "name"):
                style.name = name
            existing = self.content.get_style(family, name)
        else:
            self._set_automatic_name(style, family)
            existing = None
        return existing, style_container

    def _insert_style_get_default_styles(
        self,
        style: StyleBase,
        family: str,
        name: str,
    ) -> tuple[Any, Any]:
        style_container = self.styles.get_element("office:styles")
        style.tag = "style:default-style"
        if name:
            with contextlib.suppress(KeyError):
                style.del_attribute("style:name")
        existing = self.styles.get_style(family)
        return existing, style_container

    def _insert_style_get_master_page(
        self,
        family: str,
        name: str,
    ) -> tuple[Any, Any]:
        style_container = self.styles.get_element("office:master-styles")
        existing = self.styles.get_style(family, name)
        return existing, style_container

    def _insert_style_get_font_face_default(
        self,
        family: str,
        name: str,
    ) -> tuple[Any, Any]:
        style_container = self.styles.get_element("office:font-face-decls")
        existing = self.styles.get_style(family, name)
        return existing, style_container

    def _insert_style_get_font_face(
        self,
        family: str,
        name: str,
    ) -> tuple[Any, Any]:
        style_container = self.content.get_element("office:font-face-decls")
        existing = self.content.get_style(family, name)
        return existing, style_container

    def _insert_style_get_page_layout(
        self,
        family: str,
        name: str,
    ) -> tuple[Any, Any]:
        # force to automatic
        style_container = self.styles.get_element("office:automatic-styles")
        existing = self.styles.get_style(family, name)
        return existing, style_container

    def _insert_style_get_draw_fill_image(
        self,
        name: str,
    ) -> tuple[Any, Any]:
        # special case for 'draw:fill-image' pseudo style
        # not family and style_element.__class__.__name__ == "DrawFillImage"
        style_container = self.styles.get_element("office:styles")
        existing = self.styles.get_style("", name)
        return existing, style_container

    def _insert_style_standard(
        self,
        style: StyleBase,
        name: str,
        family: str,
        automatic: bool,
        default: bool,
    ) -> tuple[Any, Any]:
        # Common style
        if name and automatic is False and default is False:
            return self._insert_style_get_common_styles(family, name)
        # Automatic style
        elif automatic is True and default is False:
            return self._insert_style_get_automatic_styles(style, family, name)
        # Default style
        elif automatic is False and default is True:
            return self._insert_style_get_default_styles(style, family, name)
        else:
            raise AttributeError("Invalid combination of arguments")

    def insert_style(
        self,
        style: StyleBase | str,
        name: str = "",
        automatic: bool = False,
        default: bool = False,
    ) -> Any:
        """Insert the given style object into the document.

        The style is inserted according to its family and type (common, automatic,
        or default). If `style` is a string, it's assumed to be an XML style definition.
        If `name` is not provided for a common style, it tries to use the style's
        internal name.

        All styles can't be used as default styles. Default styles are
        allowed for the following families: paragraph, text, section, table,
        table-column, table-row, table-cell, table-page, chart, drawing-page,
        graphic, presentation, control and ruby.

        Args:
            style: The `StyleBase` object to insert, or a string representing an
                XML style definition.
            name: An optional name for the style. If empty, a unique name might be
                generated or the style's inherent name used.
            automatic: If `True`, the style is inserted as an automatic style.
            default: If `True`, the style is inserted as a default style,
                replacing any existing default style of the same family.
                `name` and `display_name` are ignored in this case.

        Returns:
            The name of the inserted style (str).

        Raises:
            TypeError: If the provided `style` is not a `StyleBase` object or a string.
            ValueError: If an invalid style is provided (e.g., unknown family).
            AttributeError: If an invalid combination of `automatic` and `default`
                arguments is provided (they are mutually exclusive).
        """

        # if style is a str, assume it is the Style definition
        if isinstance(style, str):
            style_element: StyleBase = Element.from_tag(style)  # type: ignore
        else:
            style_element = style
        if not isinstance(style_element, Element):
            raise TypeError(f"Unknown Style type: '{style!r}'")

        # Get family and name
        family = style_element.family
        if not name:
            name = self._pseudo_style_attribute(style_element, "name")

        # Master page style
        if family == "master-page":
            existing, style_container = self._insert_style_get_master_page(family, name)
        # Font face declarations
        elif family == "font-face":
            if default:
                existing, style_container = self._insert_style_get_font_face_default(
                    family, name
                )
            else:
                existing, style_container = self._insert_style_get_font_face(
                    family, name
                )
        # page layout style
        elif family == "page-layout":
            existing, style_container = self._insert_style_get_page_layout(family, name)
        # Common style
        elif family in FAMILY_MAPPING:
            existing, style_container = self._insert_style_standard(
                style_element, name, family, automatic, default
            )
        elif not family and style_element.__class__.__name__ == "DrawFillImage":
            # special case for 'draw:fill-image' pseudo style
            existing, style_container = self._insert_style_get_draw_fill_image(name)
        # Invalid style
        else:
            raise ValueError(
                "Invalid style: "
                f"{style_element}, tag:{style_element.tag}, family:{family}"
            )

        # Insert it!
        if existing is not None:
            style_container.delete(existing)
        style_container.append(style_element)
        return self._pseudo_style_attribute(style_element, "name")

    def get_styled_elements(self, name: str = "") -> list[Element]:
        """Search for elements (paragraphs, tables, etc.) using a given style name.

        This method performs a brute-force search across the document's content
        and style parts.

        Args:
            name: The style name to search for. If empty, all styled elements are returned.

        Returns:
            A list of `Element` objects that are associated with the specified style.
        """
        # Header, footer, etc. have styles too
        return self.content.root.get_styled_elements(
            name
        ) + self.styles.root.get_styled_elements(name)

    def show_styles(
        self,
        automatic: bool = True,
        common: bool = True,
        properties: bool = False,
    ) -> str:
        """Provide a formatted string summary of styles in the document.

        Args:
            automatic: If `True`, include automatic styles in the output.
            common: If `True`, include common (non-automatic) styles.
            properties: If `True`, include the individual properties
                of each style in the output.

        Returns:
            A human-readable summary of the document's styles.
        """
        infos = []
        for style in self.get_styles():
            try:
                name = style.name  # type: ignore[attr-defined]
            except AttributeError:
                print("Style error:")
                print(style.__class__)
                print(style.serialize())
                raise
            if style.__class__.__name__ == "DrawFillImage":
                family = ""
            else:
                family = str(style.family)
            parent = style.parent
            is_auto = parent and parent.tag == "office:automatic-styles"
            if (is_auto and automatic is False) or (not is_auto and common is False):
                continue
            is_used = bool(self.get_styled_elements(name))
            infos.append(
                {
                    "type": "auto  " if is_auto else "common",
                    "used": "y" if is_used else "n",
                    "family": family,
                    "parent": self._pseudo_style_attribute(style, "parent_style") or "",
                    "name": name or "",
                    "display_name": self._pseudo_style_attribute(style, "display_name")
                    or "",
                    "properties": style.get_properties() if properties else None,
                }
            )
        if not infos:
            return ""
        # Sort by family and name
        infos.sort(key=itemgetter("family", "name"))
        # Show common and used first
        infos.sort(key=itemgetter("type", "used"), reverse=True)
        max_family = str(max(len(x["family"]) for x in infos))  # type: ignore
        max_parent = str(max(len(x["parent"]) for x in infos))  # type: ignore
        formater = (
            "%(type)s used:%(used)s family:%(family)-0"
            + max_family
            + "s parent:%(parent)-0"
            + max_parent
            + "s name:%(name)s"
        )
        output = []
        for info in infos:
            line = formater % info
            if info["display_name"]:
                line += " display_name:" + info["display_name"]  # type: ignore
            output.append(line)
            if info["properties"]:
                for name, value in info["properties"].items():  # type: ignore
                    output.append(f"   - {name}: {value}")
        output.append("")
        return "\n".join(output)

    def delete_styles(self) -> int:
        """Remove all style information from content and all styles.

        First, it removes all references to styles from elements within the
        document. Then, it deletes all supposedly orphaned styles. Default
        styles are not deleted.

        Returns:
            The number of deleted styles.
        """
        # First remove references to styles
        for element in self.get_styled_elements():
            for attribute in (
                "text:style-name",
                "draw:style-name",
                "draw:text-style-name",
                "table:style-name",
                "style:page-layout-name",
            ):
                with contextlib.suppress(KeyError):
                    element.del_attribute(attribute)
        # Then remove supposedly orphaned styles
        deleted = 0
        for style in self.get_styles():
            try:
                name = style.name  # type: ignore[attr-defined]
            except AttributeError:
                continue
                # Don't delete default styles
            if name is None:
                continue
            # elif type(style) is odf_master_page:
            #    # Don't suppress header and footer, just styling was removed
            #    continue
            style.delete()
            deleted += 1
        return deleted

    def _copy_image_from_document(self, document: Document, url: str) -> None:
        """Copy image from another document.

        Args:
            document: The source `Document` object from which to copy image.
            url: url of the image in the source document.
        """
        image_content = document.get_part(url)
        if not isinstance(image_content, bytes):
            return
        self.set_part(url, image_content)
        media_type = document.manifest.get_media_type(url) or "application/octet-stream"
        self.manifest.add_full_path(url, media_type)

    def merge_styles_from(self, document: Document) -> None:
        """Copy all styles from another document into this document.

        Existing styles with the same type and name will be replaced.
        Only unique styles will be preserved. This operation also copies
        any images referenced by master page styles or fill images.

        Args:
            document: The source `Document` object from which to merge styles.
        """
        for style in document.get_styles():
            tagname = style.tag
            family = style.family
            if family is None:
                continue
            if hasattr(style, "name"):
                stylename = style.name
            else:
                stylename = None
            container = style.parent
            if container is None:
                continue
            upper_container = container.parent
            if upper_container is None:
                continue
            container_name = container.tag
            # The destination part
            if upper_container.tag == "office:document-styles":
                part: Content | Styles = self.styles
            elif upper_container.tag == "office:document-content":
                part = self.content
            else:
                raise NotImplementedError(upper_container.tag)
            # Implemented containers
            if container_name not in {
                "office:styles",
                "office:automatic-styles",
                "office:master-styles",
                "office:font-face-decls",
            }:
                raise NotImplementedError(container_name)
            dest = part.get_element(f"//{container_name}")
            if not dest:
                continue
            # Implemented style types
            # if tagname not in registered_styles:
            #    raise NotImplementedError(tagname)
            duplicate = part.get_style(family, stylename)
            if duplicate is not None:
                duplicate.delete()
            dest.append(style)
            # Copy images from the header/footer
            if tagname == "style:master-page":
                images = cast(
                    list[DrawImage], style.get_elements("descendant::draw:image")
                )
                for image in images:
                    self._copy_image_from_document(document, image.url)
            elif tagname == "draw:fill-image":
                draw_fill_image = cast(DrawFillImage, style)
                self._copy_image_from_document(document, draw_fill_image.url)

    def add_page_break_style(self) -> None:
        """Ensure the document contains the style required for a manual page break.

        This method adds or verifies the existence of a paragraph style named
        "odfdopagebreak" with the property `fo:break-after="page"`.
        Once this style is present, a manual page break can be added to the
        document using `document.body.append(PageBreak())`.

        Note: This style uses the property 'fo:break-after'; another
        possibility could be the property 'fo:break-before'.
        """
        if existing := self.get_style(  # noqa: SIM102
            family="paragraph",
            name_or_element="odfdopagebreak",
        ):
            if properties := existing.get_properties():  # noqa: SIM102
                if properties["fo:break-after"] == "page":
                    return
        style = (
            '<style:style style:family="paragraph" style:parent-style-name="Standard" '
            'style:name="odfdopagebreak">'
            '<style:paragraph-properties fo:break-after="page"/></style:style>'
        )
        self.insert_style(style, automatic=False)

    def get_style_properties(
        self, family: str, name: str, area: str | None = None
    ) -> dict[str, str] | None:
        """Return the properties of the required style as a dictionary.

        Args:
            family: The style family (e.g., 'paragraph', 'text').
            name: The name of the style.
            area: An optional string specifying a sub-area of properties (e.g.,
                'paragraph', 'text', 'table-cell').

        Returns:
            A dictionary of style properties (key-value pairs), or `None` if
            the style is not found.
        """
        style = self.get_style(family, name)
        if style is None:
            return None
        return style.get_properties(area=area)  # type: ignore

    def _get_table(self, table: int | str) -> Table | None:
        if not isinstance(table, (int, str)):
            raise TypeError(f"Table parameter must be int or str: {table!r}")
        if isinstance(table, int):
            return self.body.get_table(position=table)
        return self.body.get_table(name=table)

    def get_cell_style_properties(
        self, table: str | int, coord: tuple | list | str
    ) -> dict[str, str]:
        """Return the style properties of a table cell in an ODS document.

        Properties are retrieved from the cell's own style, or from its row's
        style, or from its column's default cell style, in that order of
        precedence.

        Args:
            table: The name (str) or index (int) of the table.
            coord: The coordinates of the cell (e.g., "A1", (0, 0)).

        Returns:
            A dictionary of style properties (key-value pairs) for the cell.
            Returns an empty dictionary if the table or cell is not found,
            or if no styles are applicable.
        """

        if not (sheet := self._get_table(table)):
            return {}
        cell = sheet.get_cell(coord, clone=False)
        if cell.style:
            return (
                self.get_style_properties("table-cell", cell.style, "table-cell") or {}
            )
        try:
            row = sheet.get_row(cell.y, clone=False, create=False)  # type: ignore
            if row.style:  # noqa: SIM102
                if props := self.get_style_properties(
                    "table-row", row.style, "table-cell"
                ):
                    return props
            column = sheet.get_column(cell.x)  # type: ignore
            style = column.default_cell_style
            if style:  # noqa: SIM102
                if props := self.get_style_properties(
                    "table-cell", style, "table-cell"
                ):
                    return props
        except ValueError:
            pass
        return {}

    def get_cell_background_color(
        self,
        table: str | int,
        coord: tuple | list | str,
        default: str = "#ffffff",
    ) -> str:
        """Return the background color of a table cell in an ODS document.

        The color is retrieved from the cell's style properties (cell, row, or column).
        If no background color is explicitly defined, the `default` value is returned.

        Args:
            table: The name (str) or index (int) of the table.
            coord: The coordinates of the cell (e.g., "A1", (0, 0)).
            default: The default color to return if no background color is defined
                (defaults to "#ffffff").

        Returns:
            The background color as a hexadecimal string (e.g., "#RRGGBB").
        """
        found = self.get_cell_style_properties(table, coord).get("fo:background-color")
        return found or default

    def get_table_style(
        self,
        table: str | int,
    ) -> StyleBase | None:
        """Return the `StyleBase` instance associated with the table.

        Args:
            table: The name (str) or index (int) of the table.

        Returns:
            The `StyleBase` object for the table, or `None` if the table
            is not found or has no style.
        """
        if not (sheet := self._get_table(table)):
            return None
        return self.get_style("table", sheet.style)

    def get_table_displayed(self, table: str | int) -> bool:
        """Return the `table:display` property of the table's style.

        This property indicates whether the table should be displayed in a
        graphical interface. This method replaces the broken `Table.displayd()`
        method from previous `odfdo` versions.

        Args:
            table: The name (str) or index (int) of the table.

        Returns:
            `True` if the table is set to be displayed, `False` otherwise.
        """
        style = self.get_table_style(table)
        if not style:
            # should not happen, but assume that a table without style is
            # displayed by default
            return True
        properties = style.get_properties() or {}
        property_str = str(properties.get("table:display", "true"))
        return Boolean.decode(property_str)

    def _unique_style_name(self, base: str) -> str:
        """Generate a unique style name based on a given base string.

        The generated name will be of the form "base_X", where X is an
        incrementing integer that ensures the name is not already in use
        within the document's styles.

        Args:
            base: The base string for generating the unique name.

        Returns:
            A unique style name string.
        """
        current = {style.name for style in self.get_styles() if hasattr(style, "name")}
        idx = 0
        while True:
            name = f"{base}_{idx}"
            if name in current:
                idx += 1
                continue
            return name

    def set_table_displayed(self, table: str | int, displayed: bool) -> None:
        """Set the `table:display` property of the table's style.

        This controls whether the table should be displayed in a graphical
        interface. If the table does not have an existing style, a new
        automatic style is created for it. This method replaces the broken
        `Table.displayd()` method from previous `odfdo` versions.

        Args:
            table: The name (str) or index (int) of the table.
            displayed: A boolean flag; `True` to display the table, `False` to hide it.
        """
        orig_style = self.get_table_style(table)
        if not orig_style:
            name = self._unique_style_name("ta")
            orig_style = Element.from_tag(  # type:ignore[assignment]
                f'<style:style style:name="{name}" style:family="table" '
                'style:master-page-name="Default">'
                '<style:table-properties table:display="true" '
                'style:writing-mode="lr-tb"/></style:style>'
            )
            self.insert_style(orig_style, automatic=True)  # type:ignore
        new_style = orig_style.clone  # type: ignore[union-attr]
        new_name = self._unique_style_name("ta")
        new_style.name = new_name  # type:ignore
        self.insert_style(new_style, automatic=True)  # type:ignore
        sheet = self._get_table(table)
        sheet.style = new_name  # type: ignore
        properties = {"table:display": Boolean.encode(displayed)}
        new_style.set_properties(properties)  # type: ignore

    def get_language(self) -> str:
        """Get the default language of the document from its styles.

        Note: The language value in the metadata might differ.

        Returns:
            The default language as a string (e.g., "en-US", "fr-FR").
        """
        return self.styles.default_language

    def set_language(self, language: str) -> None:
        """Set the default language of the document, updating both styles and metadata.

        Args:
            language: The language code as a string (e.g., "en-US", "fr-FR").
                Must conform to RFC 3066.

        Raises:
            TypeError: If the provided language code does not conform to RFC 3066.
        """
        language = str(language)
        if not is_RFC3066(language):
            raise TypeError(
                'Language must be "xx" lang or "xx-YY" lang-COUNTRY code (RFC3066)'
            )
        self.styles.default_language = language
        self.meta.language = language

    @property
    def language(self) -> str | None:
        """Get or set the default language of the document.

        When getting, it returns the default language as a string (e.g., "en-US"),
        or `None` if not set.

        When setting, it accepts a language code as a string (e.g., "en-US", "fr-FR")
        to update both the styles and metadata of the document.

        Returns:
            The default language as a string (e.g., "en-US"), or `None` if not set.
        """
        return self.get_language()

    @language.setter
    def language(self, language: str) -> None:
        return self.set_language(language)
